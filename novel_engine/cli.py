import argparse
from pathlib import Path
from .project import ROOT, resolve_story, chapter_numbers, blueprints, manuscript, state_update, build_context, build_memory, read
from .audit import deterministic_audit, outline_audit_prompt\nfrom .agy import run_batch


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
    args = parser.parse_args(argv)
    try:
        story = resolve_story(args.story)
        if args.command in (None, "status"):
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
    except (ValueError, FileExistsError) as exc:
        parser.error(str(exc))
    return 0
