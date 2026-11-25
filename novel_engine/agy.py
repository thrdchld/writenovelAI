import json
import re
import shutil
import subprocess
from .project import build_context, manuscript, state_update, read
from .chapter_selection import parse_chapter_numbers as parse_numbers

_PLACEHOLDER_MARKERS = frozenset({
    "todo", "tbd", "placeholder", "belum ditulis",
    "isi di sini", "n/a", "...", "-", "kosong",
})
_PLACEHOLDER_PREFIX_RE = re.compile(
    r"^(?:todo|tbd|placeholder|belum ditulis|isi di sini)\s*(?:[:\-]|$)",
    re.I,
)


def _is_placeholder_line(line):
    s = re.sub(r"^(?:[-*>]\s*)+", "", line.strip())
    s = s.strip("[]() ").lower()
    if not s or s in _PLACEHOLDER_MARKERS:
        return True
    return bool(_PLACEHOLDER_PREFIX_RE.match(s))


def _is_meaningful_content(text):
    """Return True if text has non-empty, non-placeholder body content."""
    if not text or not text.strip():
        return False
    cleaned = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    body_lines = []
    for line in cleaned.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or re.fullmatch(r"[-*_]{3,}", s):
            continue
        body_lines.append(s)
    if not body_lines:
        return False
    return any(not _is_placeholder_line(line) for line in body_lines)


def run_one(story, number, rewrite=False):
    target = manuscript(story, number)
    state = state_update(story, number)
    if not rewrite and target.exists():
        if _is_meaningful_content(read(target)) and _is_meaningful_content(read(state)):
            print(f"Bab {number}: dilewati, naskah dan State Update sudah ada.")
            return "skipped"
        print(f"Bab {number}: file parsial terdeteksi. Perbaiki naskah/State Update sebelum melanjutkan.")
        return "incomplete"
    if not rewrite and state.exists():
        print(f"Bab {number}: State Update ada tanpa naskah. Tidak ditimpa.")
        return "incomplete"
    target.parent.mkdir(parents=True, exist_ok=True)
    state.parent.mkdir(parents=True, exist_ok=True)
    before = target.stat() if target.exists() else None
    before_state = state.stat() if state.exists() else None
    story_root = story.resolve()
    rel_target = target.resolve().relative_to(story_root)
    rel_state = state.resolve().relative_to(story_root)
    prompt = build_context(story, number, rewrite)
    prompt += (
        "\n\n## Instruksi eksekusi AGY\n"
        f"Tulis prosa lengkap Bab {number} dan simpan ke {rel_target}. "
        f"Buat State Update faktual dan simpan ke {rel_state}. "
        "Jangan mengubah outline, blueprint, canon, atau bab lain. "
        "Jangan hanya menampilkan hasil di terminal. Setelah menulis, laporkan file yang benar-benar dibuat."
    )
    executable = shutil.which("agy")
    if not executable:
        print("AGY tidak ditemukan di PATH.")
        return "error"
    result = subprocess.run(
        [executable, "-p", prompt, "--mode", "accept-edits", "--output-format", "json"],
        cwd=str(story_root), capture_output=True, text=True,
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
    except (ValueError, TypeError):
        print(f"Bab {number}: respons AGY bukan JSON valid.")
        return "error"
    if not isinstance(payload, dict):
        print(f"Bab {number}: format respons AGY tidak valid.")
        return "error"
    if str(payload.get("status", "")).upper() != "SUCCESS":
        print(str(payload.get("error", payload))[-4000:])
        return "error"
    denied = payload.get("denied_actions", [])
    if denied:
        print(f"Bab {number}: AGY memiliki aksi yang ditolak: {denied}")
        return "error"
    if not _is_meaningful_content(read(target)) or not _is_meaningful_content(read(state)):
        print(f"Bab {number}: AGY selesai tetapi naskah atau State Update belum lengkap.")
        return "incomplete"
    if rewrite and before and target.stat().st_mtime_ns == before.st_mtime_ns and target.stat().st_size == before.st_size:
        print(f"Bab {number}: file naskah tidak berubah; rewrite tidak dapat diverifikasi.")
        return "incomplete"
    if rewrite and before_state and state.stat().st_mtime_ns == before_state.st_mtime_ns and state.stat().st_size == before_state.st_size:
        print(f"Bab {number}: file State Update tidak berubah; rewrite tidak dapat diverifikasi.")
        return "incomplete"
    print(f"Bab {number}: naskah dan State Update ditemukan.")
    return "success"


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
