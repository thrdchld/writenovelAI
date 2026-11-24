import argparse
from pathlib import Path
from .project import ROOT, resolve_story, chapter_numbers, blueprints, manuscript, state_update, build_context, build_memory, read
from .audit import deterministic_audit, outline_audit_prompt
from .agy import run_batch


def status(story):
    nums = chapter_numbers(story)
    print(f"PROYEK: {story.name}")
    if not nums:
        print("Belum ada bab yang terdeteksi.")
        return
    for n in nums:
        flags = []
        flags.append("NASKAH" if read(manuscript(story, n)) else "BELUM DITULIS")
        flags.append("STATE" if read(state_update(story, n)) else "STATE KOSONG")
        flags.append("BLUEPRINT" if n in blueprints(story) else "BLUEPRINT KOSONG")
        print(f"Bab {n:03d}: {' | '.join(flags)}")
    print(f"Progress naskah: {sum(bool(read(manuscript(story,n))) for n in nums)}/{len(nums)}")


def verify(story, number):
    problems = []
    if not read(manuscript(story, number)):
        problems.append("Naskah tidak ada/kosong.")
    if not read(state_update(story, number)):
        problems.append("State Update tidak ada/kosong.")
    if number not in blueprints(story):
        problems.append("Blueprint tidak ditemukan.")
    if problems:
        print("BELUM LENGKAP:")
        for item in problems:
            print(f"- {item}")
        return 1
    print(f"File Bab {number} lengkap secara struktural. Ini bukan penilaian kualitas naratif.")
    return 0



def interactive_menu(story):
    while True:
        print("\n" + "=" * 56)
        print(f" NOVEL ENGINE: {story.name}")
        print("=" * 56)
        print("1. Lihat status")
        print("2. Lihat memori cerita")
        print("3. Audit struktur outline")
        print("4. Siapkan konteks bab untuk AI")
        print("5. Verifikasi bab")
        print("6. Jalankan AGY (satu/batch berurutan)")
        print("0. Keluar")
        choice = input("Pilih: ").strip()
        if choice == "1":
            status(story)
        elif choice == "2":
            print(build_memory(story))
        elif choice == "3":
            findings = deterministic_audit(story)
            for severity, code, detail in findings:
                print(f"[{severity}] {code}: {detail}")
            if not findings:
                print("Tidak ada masalah struktural sederhana yang terdeteksi.")
            if input("Buat paket audit untuk AI? (y/t): ").strip().lower() == "y":
                out = story / "workbench" / "outline-audit-prompt.md"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(outline_audit_prompt(story), encoding="utf-8")
                print(f"Paket audit: {out.relative_to(ROOT)}")
        elif choice == "4":
            raw = input("Nomor bab: ").strip()
            if raw.isdigit():
                number = int(raw)
                rewrite = False
                if read(manuscript(story, number)):
                    rewrite = input("Naskah sudah ada. Rewrite? (y/t): ").strip().lower() == "y"
                try:
                    out = story / "workbench" / f"context-chapter-{number:03d}.md"
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_text(build_context(story, number, rewrite), encoding="utf-8")
                    print(f"Paket konteks: {out.relative_to(ROOT)}")
                except (ValueError, FileExistsError) as exc:
                    print(exc)
            else:
                print("Nomor bab tidak valid.")
        elif choice == "5":
            raw = input("Nomor bab: ").strip()
            if raw.isdigit():
                verify(story, int(raw))
            else:
                print("Nomor bab tidak valid.")
        elif choice == "6":
            raw = input("Bab (contoh 4 atau 1-5,8): ").strip()
            rewrite = input("Izinkan rewrite bab yang sudah ada? (y/t): ").strip().lower() == "y"
            run_batch(story, raw, chapter_numbers(story), rewrite)
        elif choice == "0":
            return 0
        else:
            print("Pilihan tidak dikenal.")

def main(argv=None):
    parser = argparse.ArgumentParser(description="Novel Engine — memory, context, outline audit, and verification.")
    parser.add_argument("--story", help="Slug folder proyek di stories/")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("status", help="Status naskah, blueprint, dan State Update")
    p = sub.add_parser("context", help="Siapkan paket konteks untuk AI penulis")
    p.add_argument("chapter", type=int)
    p.add_argument("--rewrite", action="store_true")
    p = sub.add_parser("memory", help="Tampilkan memori bersumber sebelum bab tertentu")
    p.add_argument("--before", type=int)
    p = sub.add_parser("audit", help="Jalankan cek deterministik dan siapkan prompt audit AI")
    p.add_argument("--prompt", action="store_true", help="Simpan paket audit AI di workbench")
    p = sub.add_parser("verify", help="Verifikasi kelengkapan file bab")
    p.add_argument("chapter", type=int)
    p = sub.add_parser("agy", help="Jalankan AGY satu bab atau batch berurutan")
    p.add_argument("chapters", help="Nomor, rentang, atau daftar, misalnya 4 atau 1-5,8")
    p.add_argument("--rewrite", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command is None and not args.story:
            choices = sorted(p for p in (ROOT / "stories").iterdir() if p.is_dir())
            if len(choices) > 1:
                print("PILIH PROYEK")
                for i, item in enumerate(choices, 1):
                    print(f"{i}. {item.name}")
                selected = input("Nomor proyek: ").strip()
                if not selected.isdigit() or not 1 <= int(selected) <= len(choices):
                    raise ValueError("Pilihan proyek tidak valid.")
                story = choices[int(selected) - 1]
            else:
                story = resolve_story()
        else:
            story = resolve_story(args.story)
        if args.command is None:
            return interactive_menu(story)
        if args.command == "status":
            status(story)
            return 0
        if args.command == "context":
            output = story / "workbench" / f"context-chapter-{args.chapter:03d}.md"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(build_context(story, args.chapter, args.rewrite), encoding="utf-8")
            print(output.relative_to(ROOT))
            return 0
        if args.command == "memory":
            print(build_memory(story, args.before))
            return 0
        if args.command == "audit":
            findings = deterministic_audit(story)
            if findings:
                for severity, code, detail in findings:
                    print(f"[{severity}] {code}: {detail}")
            else:
                print("Tidak ada masalah struktural sederhana yang terdeteksi.")
            if args.prompt:
                out = story / "workbench" / "outline-audit-prompt.md"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(outline_audit_prompt(story), encoding="utf-8")
                print(f"Prompt audit AI: {out.relative_to(ROOT)}")
            return 1 if any(x[0] == "CRITICAL" for x in findings) else 0
        if args.command == "verify":
            return verify(story, args.chapter)
        if args.command == "agy":
            return run_batch(story, args.chapters, chapter_numbers(story), args.rewrite)
    except (ValueError, FileExistsError) as exc:
        parser.error(str(exc))
    return 0
