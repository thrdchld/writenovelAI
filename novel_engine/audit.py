from collections import Counter\nfrom .project import read, blueprints, outline_numbers, chapter_numbers, manuscript, state_update, chapter_no


def deterministic_audit(story):
    outline = outline_numbers(story)
    bp = blueprints(story)
    findings = []
    if not (story / "04-story-outline.md").is_file():
        findings.append(("CRITICAL", "OUTLINE_MISSING", "04-story-outline.md tidak ditemukan."))
    for n in sorted(outline - set(bp)):
        findings.append(("HIGH", "BLUEPRINT_MISSING", f"Bab {n}: ada di outline tetapi blueprint tidak ditemukan."))
    for n in sorted(set(bp) - outline):
        findings.append(("MEDIUM", "ORPHAN_BLUEPRINT", f"Bab {n}: blueprint tidak tercantum dalam outline aktif."))
    nums = sorted(outline)
    if nums:
        missing = sorted(set(range(nums[0], nums[-1] + 1)) - set(nums))
        for n in missing:
            findings.append(("MEDIUM", "CHAPTER_GAP", f"Nomor Bab {n} hilang dari outline."))
    for n in chapter_numbers(story):
        if read(manuscript(story, n)) and not read(state_update(story, n)):
            findings.append(("MEDIUM", "STATE_UPDATE_MISSING", f"Bab {n}: naskah ada tetapi State Update belum tersedia."))
        if read(state_update(story, n)) and not read(manuscript(story, n)):
            findings.append(("LOW", "ORPHAN_STATE", f"Bab {n}: State Update ada tanpa naskah."))
    return findings


def outline_audit_prompt(story):
    findings = deterministic_audit(story)
    lines = [
        f"# AUDIT OUTLINE — {story.name}", "",
        "## Temuan deterministik Python",
    ]
    if findings:
        for severity, code, detail in findings:
            lines.append(f"- [{severity}] {code}: {detail}")
    else:
        lines.append("- Tidak ditemukan masalah struktural sederhana oleh pemeriksa Python.")
    lines.extend([
        "", "## Instruksi auditor AI",
        "Audit outline secara menyeluruh dengan memeriksa sebab-akibat, motivasi, character arc, timeline kronologis versus urutan penyajian, pengetahuan tokoh, planting-payoff, keputusan kanon, kewenangan tokoh, dan konsekuensi.",
        "Jangan menganggap temuan Python sebagai kebenaran final; verifikasi terhadap sumber.",
        "Setiap temuan wajib menyebut bab/bagian, bukti sumber, jenis masalah, dampak, dan perbaikan minimum.",
        "Pisahkan KONTRADIKSI PASTI, RISIKO YANG PERLU DITINJAU, dan PREFERENSI SUBJEKTIF.",
        "Jangan mengubah dokumen. Hasilkan usulan dan daftar dependensi bab yang terdampak.",
        "", "## Dokumen sumber", "",
    ])
    for name in ("00-premise.md", "01-concept.md", "02-characters.md",
                 "03-world-and-rules.md", "04-story-outline.md", "05-decision-log.md"):
        content = read(story / name)
        if content:
            lines.extend([f"### {name}", "", content, ""])
    for n, content in sorted(blueprints(story).items()):
        lines.extend([f"### Blueprint Bab {n}", "", content, ""])
    return "\n".join(lines).rstrip() + "\n"
