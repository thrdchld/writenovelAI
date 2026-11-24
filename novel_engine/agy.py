import json
import shutil
import subprocess
from .project import build_context, manuscript, state_update, read


def run_one(story, number, rewrite=False):
    target = manuscript(story, number)
    state = state_update(story, number)
    if read(target) and not rewrite:
        print(f"Bab {number}: dilewati, naskah sudah ada.")
        return "skipped"
    prompt = build_context(story, number, rewrite)
    prompt += (
        "\n\n## Instruksi eksekusi AGY\n"
        f"Tulis prosa lengkap Bab {number} dan simpan ke {target}. "
        f"Buat State Update faktual dan simpan ke {state}. "
        "Jangan mengubah outline, blueprint, canon, atau bab lain. "
        "Jangan hanya menampilkan hasil di terminal. Setelah menulis, laporkan file yang benar-benar dibuat."
    )
    executable = shutil.which("agy")
    if not executable:
        print("AGY tidak ditemukan di PATH.")
        return "error"
    result = subprocess.run(
        [executable, "-p", prompt, "--output-format", "json"],
        cwd=str(story.parents[1]), capture_output=True, text=True,
        encoding="utf-8", errors="replace"
    )
    combined = "\n".join((result.stdout, result.stderr)).lower()
    limits = ("quota", "429", "rate limit", "resource_exhausted",
              "usage limit", "daily limit", "billing", "too many requests")
    if result.returncode != 0 or any(x in combined for x in limits):
        print((result.stderr or result.stdout)[-4000:])
        return "error"
    try:
        payload = json.loads(result.stdout.strip())
        if isinstance(payload, dict) and str(payload.get("status", "")).upper() == "ERROR":
            print(str(payload.get("error", payload))[-4000:])
            return "error"
    except (ValueError, TypeError):
        pass
    if not read(target) or not read(state):
        print(f"Bab {number}: AGY selesai tetapi naskah atau State Update belum lengkap.")
        return "incomplete"
    print(f"Bab {number}: naskah dan State Update ditemukan.")
    return "success"


def parse_numbers(raw, available):
    chosen = set()
    try:
        for part in raw.replace(" ", "").split(","):
            if "-" in part:
                start, end = (int(x) for x in part.split("-", 1))
                if start > end:
                    return None
                chosen.update(range(start, end + 1))
            else:
                chosen.add(int(part))
    except (ValueError, TypeError):
        return None
    return sorted(chosen) if chosen and chosen.issubset(set(available)) else None


def run_batch(story, raw, available, rewrite=False):
    numbers = parse_numbers(raw, available)
    if not numbers:
        print("Nomor bab tidak valid atau tidak tersedia.")
        return 2
    for number in numbers:
        result = run_one(story, number, rewrite=rewrite)
        if result not in ("success", "skipped"):
            print(f"Batch dihentikan pada Bab {number}; bab berikutnya tidak dijalankan.")
            return 1
    return 0
