#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pengelola penulisan novel: siapkan konteks lalu jalankan Antigravity CLI."""
from pathlib import Path
import argparse
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
STORIES_DIR = ROOT / "stories"
CORE_FILES = ["00-premise.md", "01-concept.md", "02-characters.md",
              "03-world-and-rules.md", "04-story-outline.md", "05-decision-log.md"]
LIMIT_HINTS = ("quota", "rate limit", "rate_limit", "resource_exhausted", "429",
               "usage limit", "daily limit", "limit exceeded", "capacity",
               "exhausted", "billing", "too many requests", "insufficient quota")


def read_text(path):
    try:
        return path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return ""


def chapter_number(path):
    match = re.search(r"chapter-(\d+)", path.stem, re.I)
    return int(match.group(1)) if match else None


def get_blueprints(story):
    result = {}
    folder = story / "blueprint"
    if not folder.is_dir():
        return result
    for path in sorted(folder.glob("chapter-*.md")):
        number = chapter_number(path)
        if number is not None and "-to-" not in path.stem:
            result[number] = read_text(path)
    # Mendukung dokumen gabungan seperti chapter-007-to-030.md.
    for path in sorted(folder.glob("chapter-*-to-*.md")):
        content = read_text(path)
        matches = list(re.finditer(r"(?m)^##\s*Bab\s+(\d+)\s*[—–-].*$", content, re.I))
        for i, match in enumerate(matches):
            number = int(match.group(1))
            if number not in result:
                end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                result[number] = content[match.start():end].strip()
    return result


def get_numbers(story):
    numbers = set(get_blueprints(story))
    outline = read_text(story / "04-story-outline.md")
    numbers.update(int(m.group(1)) for m in re.finditer(r"(?mi)^#{1,4}\s*Bab\s+(\d+)\b", outline))
    manuscript = story / "manuscript"
    if manuscript.is_dir():
        for path in manuscript.glob("chapter-*.md"):
            n = chapter_number(path)
            if n is not None:
                numbers.add(n)
    return sorted(numbers)


def manuscript_path(story, number):
    return story / "manuscript" / f"chapter-{number:03d}.md"


def state_path(story, number):
    return story / "state-updates" / f"chapter-{number:03d}.md"


def is_written(story, number):
    path = manuscript_path(story, number)
    return path.is_file() and bool(read_text(path))


def title_for(story, number):
    text = get_blueprints(story).get(number, "")
    for line in text.splitlines():
        m = re.match(r"^#\s*Blueprint Bab\s+\d+\s*[—–-]\s*(.+)$", line.strip(), re.I)
        if not m:
            m = re.match(r"^##\s*Bab\s+\d+\s*[—–-]\s*(.+)$", line.strip(), re.I)
        if m:
            return m.group(1).strip()
    return ""


def show_status(story):
    numbers = get_numbers(story)
    print(f"\nNOVEL: {story.name}")
    print("-" * 64)
    if not numbers:
        print("Belum ditemukan outline atau blueprint bab.")
        return
    done = 0
    for n in numbers:
        written = is_written(story, n)
        done += int(written)
        title = title_for(story, n)
        suffix = f" | {title}" if title else ""
        print(f"Bab {n:02d} [{'SUDAH DITULIS' if written else 'BELUM DITULIS'}]{suffix}")
    print("-" * 64)
    print(f"Progress file naskah: {done}/{len(numbers)} bab")
    print("Status ini memeriksa keberadaan file, bukan kelulusan audit.")


def parse_selection(raw, available):
    selected = set()
    try:
        for part in raw.replace(" ", "").split(","):
            if not part:
                raise ValueError
            if "-" in part:
                a, b = part.split("-", 1)
                start, end = int(a), int(b)
                if start > end:
                    raise ValueError
                selected.update(range(start, end + 1))
            else:
                selected.add(int(part))
    except ValueError:
        return None
    return sorted(selected) if selected and selected.issubset(set(available)) else None


def collect_context(story, number):
    pieces = []
    candidates = [ROOT / "AI_INSTRUCTIONS.md", ROOT / "docs" / "05-writing-standard.md",
                  story / "README.md"]
    candidates += [story / name for name in CORE_FILES]
    for path in candidates:
        content = read_text(path)
        if content:
            pieces.append((str(path.relative_to(ROOT)), content))

    blueprint = get_blueprints(story).get(number, "")
    if blueprint:
        pieces.append((f"blueprint Bab {number}", blueprint))
    else:
        pieces.append(("PERINGATAN", "Blueprint bab ini tidak ditemukan. Gunakan outline dan laporkan kekurangan konteks; jangan mengarang peristiwa inti."))

    previous = manuscript_path(story, number - 1)
    if number > 1 and previous.is_file() and read_text(previous):
        pieces.append((str(previous.relative_to(ROOT)), read_text(previous)))

    for folder_name in ("continuity", "state-updates"):
        folder = story / folder_name
        if not folder.is_dir():
            continue
        files = sorted(folder.glob("*.md"))
        if folder_name == "state-updates":
            # Jangan bocorkan state dari bab masa depan ke bab yang sedang ditulis.
            files = [path for path in files
                     if chapter_number(path) is None or chapter_number(path) < number]
        for path in files[-8:]:
            content = read_text(path)
            if content:
                pieces.append((str(path.relative_to(ROOT)), content))
    return pieces


def build_prompt(story, number, pieces, target, state_target, rewrite):
    action = "TULIS ULANG" if rewrite else "TULIS"
    sections = [
        f"# {action} BAB {number:03d}", "",
        f"Proyek: {story.name}",
        f"File naskah tujuan: {target.relative_to(ROOT)}",
        f"File state update tujuan: {state_target.relative_to(ROOT)}", "",
        "## Tugas utama",
        f"Tulis prosa lengkap Bab {number} berdasarkan blueprint dan konteks di bawah.",
        "Baca seluruh sumber sebelum mulai menulis.",
        "Blueprint mengendalikan fungsi bab, urutan peristiwa, sebab-akibat, fakta, batas pengetahuan tokoh, dan perubahan di akhir bab.",
        "Tulis sebagai novel yang enak dibaca, bukan parafrasa atau daftar ulang blueprint.",
        "Gunakan paragraf normal. Hindari bahasa puitis yang dipaksakan, dialog penjelas, repetisi, dan cliffhanger buatan.",
        "Jangan menambah tokoh penting, rahasia, bukti, twist, atau fakta kanon tanpa dasar.",
        "Jangan mengubah bab lain, outline, blueprint, atau keputusan cerita.", "",
        "## Setelah menulis",
        f"Simpan naskah lengkap ke {target.relative_to(ROOT)}.",
        f"Buat state update faktual ke {state_target.relative_to(ROOT)}.",
        "State update hanya mencatat hal yang benar-benar terjadi dalam naskah: perubahan keadaan tokoh, waktu/lokasi, pengetahuan tiap tokoh, fakta baru, benda/dokumen penting, perubahan hubungan, dan pertanyaan terbuka.",
        "Jangan mengisi state update berdasarkan rencana blueprint jika peristiwa itu tidak muncul dalam naskah.",
        "Jangan menyatakan bab lolos audit. Laporkan file yang dibuat dan kendala jika ada.",
        "Jika ada konflik dokumen yang menghalangi penulisan inti bab, jangan menebak atau mengubah kanon; laporkan konflik tersebut.", "",
        "## Konteks wajib dibaca"
    ]
    for label, content in pieces:
        sections.extend(["", f"### Sumber: {label}", "", content])
    return "\n".join(sections).rstrip() + "\n"


def detect_limit(message):
    lowered = message.lower()
    return any(hint in lowered for hint in LIMIT_HINTS)


def run_agy(prompt):
    executable = shutil.which("agy")
    if not executable:
        print("\nERROR: perintah agy tidak ditemukan di PATH.")
        print("Pastikan Antigravity CLI terpasang dan bisa dijalankan dari Termux.")
        return "missing"

    print("\nAntigravity sedang menulis. Tunggu sampai proses selesai...")
    try:
        process = subprocess.Popen(
            [executable, "-p", prompt, "--output-format", "json"],
            cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace"
        )
        stdout, stderr = process.communicate()
    except OSError as error:
        print(f"\nGagal menjalankan agy: {error}")
        return "error"

    data = None
    try:
        data = json.loads(stdout.strip()) if stdout.strip() else None
    except json.JSONDecodeError:
        pass

    status = str(data.get("status", "")).upper() if isinstance(data, dict) else ""
    error_text = str(data.get("error") or "") if isinstance(data, dict) else ""
    combined = "\n".join(x for x in (error_text, stderr, stdout) if x)

    if process.returncode != 0 or status == "ERROR":
        if detect_limit(combined):
            print("\nPERINGATAN: BATAS PENGGUNAAN AGY TERDETEKSI.")
            print("Proses multi-bab dihentikan. Bab yang sudah selesai tetap tersimpan.")
            print("Coba lagi setelah limit pulih; bab berikutnya belum dijalankan.")
        else:
            print("\nAGY GAGAL MENYELESAIKAN TUGAS.")
        if error_text:
            print(error_text)
        if stderr.strip():
            print(stderr.strip()[-5000:])
        if not error_text and not stderr.strip() and stdout.strip():
            print(stdout.strip()[-5000:])
        return "limit" if detect_limit(combined) else "error"

    if status and status not in ("SUCCESS", "COMPLETED"):
        print(f"\nStatus AGY tidak dikenali: {status}")
        if stderr.strip():
            print(stderr.strip()[-3000:])
        return "error"

    if stderr.strip():
        print("\nPesan/peringatan AGY:")
        print(stderr.strip()[-3000:])
    return "success"


def write_one(story, number):
    target = manuscript_path(story, number)
    state_target = state_path(story, number)
    already_written = is_written(story, number)
    rewrite = False

    if already_written:
        print(f"\nBab {number} sudah memiliki naskah.")
        if input("Mau rewrite? (y = ya, lainnya = lewati): ").strip().lower() != "y":
            print(f"Bab {number} dilewati.")
            return "skipped"
        rewrite = True

    pieces = collect_context(story, number)
    prompt = build_prompt(story, number, pieces, target, state_target, rewrite)
    workbench = story / "workbench"
    workbench.mkdir(parents=True, exist_ok=True)
    prompt_file = workbench / f"write-chapter-{number:03d}.md"
    prompt_file.write_text(prompt, encoding="utf-8")
    target.parent.mkdir(parents=True, exist_ok=True)
    state_target.parent.mkdir(parents=True, exist_ok=True)

    before_stat = target.stat() if target.exists() else None
    result = run_agy(prompt)
    if result != "success":
        print(f"Prompt tetap tersimpan: {prompt_file.relative_to(ROOT)}")
        return result

    if not target.is_file() or not read_text(target):
        print("\nAGY selesai, tetapi file naskah tidak ditemukan atau kosong.")
        print("Kemungkinan tindakan tulis ditolak oleh permission CLI. Periksa konfigurasi izin AGY.")
        print(f"Prompt tersimpan: {prompt_file.relative_to(ROOT)}")
        return "not_written"

    after_stat = target.stat()
    if rewrite and before_stat and (
        before_stat.st_mtime_ns == after_stat.st_mtime_ns and
        before_stat.st_size == after_stat.st_size
    ):
        print("\nFile tidak berubah; rewrite belum bisa diverifikasi.")
        print("Pastikan AGY benar-benar mengedit file naskah.")
        return "not_written"

    print(f"\nBab {number} berhasil ditulis: {target.relative_to(ROOT)}")
    if state_target.is_file() and read_text(state_target):
        print(f"State update dibuat: {state_target.relative_to(ROOT)}")
    else:
        print("PERINGATAN: state update belum dibuat. Kontinuitas bab berikutnya mungkin kurang lengkap.")
    return "success"


def delete_chapter(story, number):
    target = manuscript_path(story, number)
    if not target.is_file():
        print("Naskah bab ini belum ada.")
        return
    print(f"\nFile yang akan dihapus: {target.relative_to(ROOT)}")
    if input("Ketik HAPUS untuk mengonfirmasi: ").strip() == "HAPUS":
        target.unlink()
        print("Naskah dihapus. Blueprint dan state update tidak ikut dihapus.")
    else:
        print("Dibatalkan. File tetap aman.")


def select_story():
    stories = sorted(p for p in STORIES_DIR.iterdir() if p.is_dir()) if STORIES_DIR.is_dir() else []
    if not stories:
        print("Folder stories kosong atau tidak ditemukan.")
        return None
    if len(stories) == 1:
        return stories[0]
    print("\nPILIH NOVEL")
    for i, story in enumerate(stories, 1):
        print(f"{i}. {story.name}")
    raw = input("Pilihan: ").strip()
    if raw.isdigit() and 1 <= int(raw) <= len(stories):
        return stories[int(raw) - 1]
    print("Pilihan tidak valid.")
    return None


def choose_one(story):
    available = get_numbers(story)
    if not available:
        print("Tidak ada daftar bab.")
        return None
    selected = parse_selection(input("Nomor bab: ").strip(), available)
    if selected is None or len(selected) != 1:
        print("Masukkan satu nomor bab yang tersedia.")
        return None
    return selected[0]


def choose_many(story):
    available = get_numbers(story)
    if not available:
        print("Tidak ada daftar bab.")
        return None
    print("Format pilihan: 1-5 atau 1,3,5-7")
    selected = parse_selection(input("Bab yang mau ditulis: ").strip(), available)
    if selected is None:
        print("Pilihan tidak valid atau ada nomor bab yang tidak tersedia.")
        return None
    print("Urutan: " + ", ".join(str(n) for n in selected))
    if input("Mulai penulisan berurutan? (y/t): ").strip().lower() != "y":
        print("Dibatalkan.")
        return None
    return selected


def write_many(story, numbers):
    completed, skipped = [], []
    for index, number in enumerate(numbers, 1):
        print("\n" + "=" * 64)
        print(f"PROSES BAB {number} ({index}/{len(numbers)})")
        print("=" * 64)
        result = write_one(story, number)
        if result == "success":
            completed.append(number)
        elif result == "skipped":
            skipped.append(number)
        else:
            print("\nPenulisan batch dihentikan. Bab berikutnya tidak dijalankan.")
            if result == "limit":
                print("Limit AGY tercapai. Jalankan batch lagi setelah limit pulih.")
            break
    print("\nRINGKASAN SESI")
    print("Selesai:", ", ".join(map(str, completed)) if completed else "-")
    print("Dilewati:", ", ".join(map(str, skipped)) if skipped else "-")
    show_status(story)



def resolve_story(slug=None):
    if slug:
        story = STORIES_DIR / slug
        if story.is_dir():
            return story
        print(f"Proyek novel tidak ditemukan: {slug}")
        return None
    stories = sorted(p for p in STORIES_DIR.iterdir() if p.is_dir()) if STORIES_DIR.is_dir() else []
    if len(stories) == 1:
        return stories[0]
    if not stories:
        print("Folder stories kosong atau tidak ditemukan.")
    else:
        print("Ada beberapa proyek. Tentukan dengan --story NAMA_FOLDER.")
    return None


def prepare_context_file(story, number):
    available = get_numbers(story)
    if number not in available:
        print(f"Bab {number} tidak ditemukan dalam outline, blueprint, atau daftar naskah proyek.")
        return 2
    pieces = collect_context(story, number)
    sections = [
        f"# Paket konteks Bab {number:03d}",
        f"Proyek: {story.name}",
        f"Nomor bab: {number}",
        f"Target naskah: {manuscript_path(story, number).relative_to(ROOT)}",
        f"Target State Update: {state_path(story, number).relative_to(ROOT)}",
        "",
        "Paket ini disiapkan Python untuk dibaca AI. AI tetap bertanggung jawab menilai konteks, menulis prosa, dan menyimpan hasil.",
        "Jangan mengubah kanon, outline, blueprint, atau bab lain ketika menulis bab ini.",
        "State Update dari bab setelah bab target sengaja tidak disertakan.",
    ]
    for label, content in pieces:
        sections.extend(["", f"## Sumber: {label}", "", content])
    workbench = story / "workbench"
    workbench.mkdir(parents=True, exist_ok=True)
    output = workbench / f"context-chapter-{number:03d}.md"
    output.write_text("\\n".join(sections).rstrip() + "\\n", encoding="utf-8")
    print(f"Paket konteks dibuat: {output.relative_to(ROOT)}")
    print("Baca file tersebut sebelum menulis. Setelah menulis, jalankan --verify.")
    return 0


def verify_chapter(story, number):
    manuscript = manuscript_path(story, number)
    state = state_path(story, number)
    if not manuscript.is_file() or not read_text(manuscript):
        print(f"BELUM VALID: naskah Bab {number} tidak ditemukan atau kosong.")
        print(f"Target: {manuscript.relative_to(ROOT)}")
        return 1
    print(f"OK: naskah ditemukan dan tidak kosong: {manuscript.relative_to(ROOT)}")
    if state.is_file() and read_text(state):
        print(f"OK: State Update ditemukan: {state.relative_to(ROOT)}")
    else:
        print(f"PERINGATAN: State Update belum ada atau kosong: {state.relative_to(ROOT)}")
    print("Verifikasi ini hanya memeriksa keberadaan file, bukan kualitas atau kelulusan audit.")
    return 0


def command_line():
    parser = argparse.ArgumentParser(
        description="Pengelola proyek novel: ambil konteks, lihat status, dan verifikasi naskah."
    )
    parser.add_argument("--story", help="Nama folder proyek di stories/, misalnya gang-yang-hilang-dari-peta")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--status", action="store_true", help="Tampilkan status bab tanpa menu interaktif")
    group.add_argument("--context", type=int, metavar="BAB", help="Siapkan paket konteks bab untuk dibaca AI")
    group.add_argument("--verify", type=int, metavar="BAB", help="Verifikasi file naskah dan State Update")
    args = parser.parse_args()

    if not (args.status or args.context is not None or args.verify is not None):
        interactive_main()
        return 0

    story = resolve_story(args.story)
    if story is None:
        return 2
    if args.status:
        show_status(story)
        return 0
    if args.context is not None:
        return prepare_context_file(story, args.context)
    return verify_chapter(story, args.verify)


def interactive_main():
    story = select_story()
    if story is None:
        return
    while True:
        print("\n" + "=" * 64)
        print(f" PENGELOLA NOVEL: {story.name}")
        print("=" * 64)
        print("1. Lihat status semua bab")
        print("2. Tulis / rewrite satu bab")
        print("3. Tulis beberapa bab berurutan")
        print("4. Hapus naskah bab")
        print("5. Ganti novel")
        print("0. Keluar")
        choice = input("\nPilih menu: ").strip()

        if choice == "1":
            show_status(story)
        elif choice == "2":
            show_status(story)
            number = choose_one(story)
            if number is not None:
                write_one(story, number)
        elif choice == "3":
            show_status(story)
            numbers = choose_many(story)
            if numbers:
                write_many(story, numbers)
        elif choice == "4":
            show_status(story)
            number = choose_one(story)
            if number is not None:
                delete_chapter(story, number)
        elif choice == "5":
            selected = select_story()
            if selected is not None:
                story = selected
        elif choice == "0":
            print("Keluar.")
            break
        else:
            print("Pilihan tidak dikenal.")


if __name__ == "__main__":
    try:
        sys.exit(command_line())
    except KeyboardInterrupt:
        print("\nDihentikan.")
        sys.exit(130)
