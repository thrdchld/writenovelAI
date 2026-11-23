#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Menu sederhana pengelola bab untuk repository writenovelAI."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
STORIES_DIR = ROOT / "stories"
CORE_FILES = ["00-premise.md", "01-concept.md", "02-characters.md",
              "03-world-and-rules.md", "04-story-outline.md", "05-decision-log.md"]


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
    # Dukung blueprint gabungan, misalnya chapter-007-to-030.md.
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
    numbers.update(int(m.group(1)) for m in
                   re.finditer(r"(?mi)^#{1,4}\s*Bab\s+(\d+)\b", outline))
    manuscript = story / "manuscript"
    if manuscript.is_dir():
        for path in manuscript.glob("chapter-*.md"):
            n = chapter_number(path)
            if n is not None:
                numbers.add(n)
    return sorted(numbers)


def manuscript_path(story, number):
    return story / "manuscript" / f"chapter-{number:03d}.md"


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
    print("-" * 56)
    if not numbers:
        print("Belum ditemukan outline atau blueprint bab.")
        return
    done = 0
    for n in numbers:
        path = manuscript_path(story, n)
        exists = path.is_file() and bool(read_text(path))
        done += int(exists)
        label = "SELESAI" if exists else "BELUM"
        title = title_for(story, n)
        suffix = f" - {title}" if title else ""
        print(f"Bab {n:02d} [{label}]{suffix}")
    print("-" * 56)
    print(f"Progress: {done}/{len(numbers)} bab ditulis")


def choose_number(story, prompt):
    numbers = get_numbers(story)
    if not numbers:
        print("Tidak ada daftar bab.")
        return None
    raw = input(prompt).strip()
    if not raw.isdigit() or int(raw) not in numbers:
        print("Nomor bab tidak ditemukan.")
        return None
    return int(raw)


def collect_context(story, number):
    pieces = []
    candidates = [ROOT / "AI_INSTRUCTIONS.md", ROOT / "docs" / "05-writing-standard.md"]
    candidates += [story / name for name in CORE_FILES]
    for path in candidates:
        content = read_text(path)
        if content:
            try:
                label = str(path.relative_to(ROOT))
            except ValueError:
                label = path.name
            pieces.append((label, content))

    blueprint = get_blueprints(story).get(number, "")
    if blueprint:
        pieces.append((f"blueprint Bab {number}", blueprint))
    else:
        pieces.append(("PERINGATAN", "Blueprint bab ini tidak ditemukan. Gunakan outline dan jangan mengarang peristiwa inti."))

    previous = manuscript_path(story, number - 1)
    if number > 1 and previous.is_file() and read_text(previous):
        pieces.append((str(previous.relative_to(ROOT)), read_text(previous)))

    for folder_name in ("continuity", "state-updates"):
        folder = story / folder_name
        if folder.is_dir():
            for path in sorted(folder.glob("*.md"))[-5:]:
                if read_text(path):
                    pieces.append((str(path.relative_to(ROOT)), read_text(path)))
    return pieces


def prepare_chapter(story, number):
    target = manuscript_path(story, number)
    if target.exists() and read_text(target):
        answer = input("Naskah sudah ada. Siapkan instruksi REVISI? (y/t): ").strip().lower()
        if answer != "y":
            print("Dibatalkan. Naskah tidak diubah.")
            return

    pieces = collect_context(story, number)
    target.parent.mkdir(parents=True, exist_ok=True)
    workbench = story / "workbench"
    workbench.mkdir(parents=True, exist_ok=True)
    output = workbench / f"write-chapter-{number:03d}.md"

    sections = [
        f"# Instruksi Penulisan Bab {number:03d}", "",
        f"Proyek: {story.name}",
        f"File tujuan: {target.relative_to(ROOT)}", "",
        "## Tugas",
        f"Tulis atau revisi hanya Bab {number}. Baca seluruh konteks di bawah sebelum menulis.",
        "Ikuti blueprint untuk sebab-akibat, fakta, batas pengetahuan tokoh, dan perubahan bab.",
        "Kembangkan menjadi prosa novel yang alami; jangan menyalin format blueprint menjadi narasi.",
        "Jangan menambah twist, rahasia, bukti, tokoh penting, atau fakta kanon tanpa dasar.",
        "Jaga kesinambungan dengan bab sebelumnya dan jangan mengulangnya sebagai ringkasan.",
        "Simpan hasil akhir langsung ke file tujuan. Jangan mengubah bab lain atau dokumen rancangan.",
        "Jika ada konflik dokumen yang memengaruhi inti cerita, laporkan dan jangan menebak.", "",
        "## Konteks yang wajib dibaca"
    ]
    for label, content in pieces:
        sections.extend(["", f"### Sumber: {label}", "", content])
    output.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")

    print(f"\nInstruksi siap: {output.relative_to(ROOT)}")
    print("\nDi Antigravity, minta:")
    print(f'Baca "{output.relative_to(ROOT)}", ikuti instruksinya, lalu tulis bab ke file tujuan yang tercantum di dalamnya.')
    print("Catatan: Python menyiapkan konteks; Antigravity tetap yang menulis naskah.")


def delete_chapter(story, number):
    target = manuscript_path(story, number)
    if not target.is_file():
        print("Naskah bab ini belum ada.")
        return
    print(f"File yang akan dihapus: {target.relative_to(ROOT)}")
    if input("Ketik HAPUS untuk mengonfirmasi: ").strip() == "HAPUS":
        target.unlink()
        print("Naskah bab dihapus.")
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


def main():
    story = select_story()
    if story is None:
        return
    while True:
        print("\n" + "=" * 56)
        print(f" PENGELOLA NOVEL: {story.name}")
        print("=" * 56)
        print("1. Lihat status semua bab")
        print("2. Siapkan penulisan / revisi bab")
        print("3. Hapus naskah bab")
        print("4. Ganti novel")
        print("0. Keluar")
        choice = input("\nPilih menu: ").strip()
        if choice == "1":
            show_status(story)
        elif choice == "2":
            show_status(story)
            n = choose_number(story, "Nomor bab yang mau ditulis: ")
            if n is not None:
                prepare_chapter(story, n)
        elif choice == "3":
            show_status(story)
            n = choose_number(story, "Nomor bab yang mau dihapus: ")
            if n is not None:
                delete_chapter(story, n)
        elif choice == "4":
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
        main()
    except KeyboardInterrupt:
        print("\nDihentikan.")
        sys.exit(0)
