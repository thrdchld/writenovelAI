import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from .project import ROOT, resolve_story, build_context, manuscript, state_update, read
from .audit import outline_audit_prompt, deterministic_audit
from .cli import verify
from .agy import parse_numbers
from .project import chapter_numbers


def request_json(url, payload, headers, timeout=600):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def github_comment(repo, issue_number, message):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    body = json.dumps({"body": message}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }, method="POST")
    with urllib.request.urlopen(req, timeout=30) as response:
        response.read()


def call_model(system, user):
    base = (os.environ.get("NOVEL_AI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    key = os.environ.get("NOVEL_AI_API_KEY")
    model = os.environ.get("NOVEL_AI_MODEL")
    if not key or not model:
        raise RuntimeError("Secrets NOVEL_AI_API_KEY dan NOVEL_AI_MODEL belum diatur.")
    data = request_json(base + "/chat/completions", {
        "model": model,
        "temperature": 0.35,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
    }, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    return data["choices"][0]["message"]["content"]


def extract_json(text):
    decoder = json.JSONDecoder()
    start = text.find("{")
    if start < 0:
        raise ValueError("Respons AI tidak berisi objek JSON.")
    obj, _ = decoder.raw_decode(text[start:])
    return obj


def commit_paths(paths, message):
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], cwd=ROOT, check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd=ROOT, check=True)
    subprocess.run(["git", "add", "--", *[str(p.relative_to(ROOT)) for p in paths]], cwd=ROOT, check=True)
    changed = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
    if changed.returncode == 0:
        raise RuntimeError("Tidak ada perubahan file untuk disimpan.")
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
    subprocess.run(["git", "push"], cwd=ROOT, check=True)
    return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()


def handle(repo, issue_number, command):
    parts = command.strip().split()
    if len(parts) < 2:
        raise ValueError("Format: @novelbot status SLUG | audit SLUG | write SLUG NOMOR_BAB")
    action = parts[1].lower()
    if action == "status" and len(parts) == 3:
        story = resolve_story(parts[2])
        lines = [f"**Status {story.name}**"]
        from .project import chapter_numbers
        for n in chapter_numbers(story):
            lines.append(f"- Bab {n:03d}: {'naskah ada' if read(manuscript(story,n)) else 'belum ditulis'}; {'State Update ada' if read(state_update(story,n)) else 'State Update belum ada'}")
        return "\n".join(lines)

    if action == "audit" and len(parts) == 3:
        story = resolve_story(parts[2])
        findings = deterministic_audit(story)
        prompt = outline_audit_prompt(story)
        report = call_model(
            "Anda auditor novel. Beri temuan berbukti, pisahkan kontradiksi pasti, risiko, dan preferensi. Jangan mengubah sumber.",
            prompt
        )
        out = story / "audits" / "outline-audit.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        summary = ["# Audit Outline oleh AI", "", f"Proyek: {story.name}", "",
                   "## Pemeriksaan deterministik Python"]
        summary.extend([f"- [{a}] {b}: {c}" for a,b,c in findings] or ["- Tidak ada temuan struktural sederhana."])
        summary.extend(["", "## Audit naratif AI", "", report.strip(), ""])
        out.write_text("\n".join(summary), encoding="utf-8")
        sha = commit_paths([out], f"Add AI outline audit for {story.name}")
        return f"Audit selesai dan disimpan di `{out.relative_to(ROOT)}`. Commit: `{sha}`. Audit ini berupa temuan, bukan perubahan canon."

    if action == "write" and len(parts) == 4:
        story = resolve_story(parts[2])
        numbers = parse_numbers(parts[3], chapter_numbers(story))
        if not numbers:
            raise ValueError("Nomor bab tidak valid. Gunakan satu nomor, rentang, atau daftar seperti 1-5,8.")
        completed, skipped = [], []
        for number in numbers:
            target = manuscript(story, number)
            state = state_update(story, number)
            if target.exists() and state.exists():
                skipped.append(number)
                continue
            if target.exists() or state.exists():
                raise RuntimeError(f"Bab {number} memiliki file parsial; tidak ditimpa.")
            try:
                context = build_context(story, number, rewrite=False)
                answer = call_model(
                    "Anda penulis novel profesional. Gunakan hanya fakta dan keputusan yang didukung paket konteks. "
                    "Jangan ubah canon. Tulis prosa natural, paragraf normal. "
                    "Kembalikan HANYA JSON valid dengan dua string: manuscript dan state_update. "
                    "manuscript adalah naskah bab lengkap. state_update hanya fakta yang benar-benar terjadi di naskah.",
                    context + "\n\nKembalikan JSON dengan schema: {\"manuscript\": \"...\", \"state_update\": \"...\"}"
                )
                result = extract_json(answer)
                prose = result.get("manuscript", "").strip()
                update = result.get("state_update", "").strip()
                if not prose or not update:
                    raise ValueError("Respons AI tidak lengkap.")
                target.parent.mkdir(parents=True, exist_ok=True)
                state.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(prose + "\n", encoding="utf-8")
                state.write_text(update + "\n", encoding="utf-8")
                if verify(story, number) != 0:
                    target.unlink(missing_ok=True)
                    state.unlink(missing_ok=True)
                    raise RuntimeError("Verifikasi file gagal; hasil bab ini dibatalkan.")
                sha = commit_paths([target, state], f"Write chapter {number:03d} for {story.name}")
                completed.append((number, sha))
            except Exception as exc:
                done = ", ".join(str(n) for n, _ in completed) or "-"
                raise RuntimeError(f"Batch berhenti pada Bab {number}: {exc}. Bab yang sudah tersimpan: {done}.") from exc
        done_text = ", ".join(f"{n} (commit {sha})" for n, sha in completed) or "-"
        skipped_text = ", ".join(map(str, skipped)) or "-"
        return f"Batch selesai. Bab tersimpan: {done_text}. Bab dilewati karena file sudah ada: {skipped_text}. Hasil tetap perlu audit naratif."
    raise ValueError("Perintah tidak dikenali. Gunakan: @novelbot status SLUG, @novelbot audit SLUG, atau @novelbot write SLUG NOMOR_BAB.")


def main():
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise RuntimeError("GITHUB_EVENT_PATH tidak tersedia.")
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    repo = event["repository"]["full_name"]
    issue = event["issue"]
    number = issue["number"]
    comment = event["comment"]
    owner = event["repository"]["owner"]["login"]
    if comment["user"]["login"].lower() != owner.lower():
        return
    body = comment.get("body", "").strip()
    if not body.lower().startswith("@novelbot"):
        return
    try:
        result = handle(repo, number, body)
    except Exception as exc:
        result = f"**Novelbot gagal:** {type(exc).__name__}: {exc}"
    github_comment(repo, number, result)


if __name__ == "__main__":
    main()
