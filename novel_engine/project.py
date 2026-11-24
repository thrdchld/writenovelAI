from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
STORIES = ROOT / "stories"
CORE = ("00-premise.md", "01-concept.md", "02-characters.md",
        "03-world-and-rules.md", "04-story-outline.md", "05-decision-log.md")


def display_path(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read(path):
    try:
        return path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return ""


def chapter_no(path):
    match = re.search(r"chapter-(\d+)", Path(path).stem, re.I)
    return int(match.group(1)) if match else None


def manuscript(story, number):
    return story / "manuscript" / f"chapter-{number:03d}.md"


def state_update(story, number):
    return story / "state-updates" / f"chapter-{number:03d}.md"


def blueprints(story):
    result = {}
    folder = story / "blueprint"
    if not folder.is_dir():
        return result
    for path in sorted(folder.glob("chapter-*.md")):
        n = chapter_no(path)
        if n is not None and "-to-" not in path.stem and read(path):
            result[n] = read(path)
    for path in sorted(folder.glob("chapter-*-to-*.md")):
        content = read(path)
        heads = list(re.finditer(r"(?mi)^##\s*Bab\s+(\d+)\s*[—–-].*$", content))
        for i, head in enumerate(heads):
            n = int(head.group(1))
            if n not in result:
                end = heads[i + 1].start() if i + 1 < len(heads) else len(content)
                result[n] = content[head.start():end].strip()
    return result


def outline_numbers(story):
    content = read(story / "04-story-outline.md")
    found = set()
    for line in content.splitlines():
        match = re.match(r"^\|\s*(\d+)\s*\|", line)
        if match:
            found.add(int(match.group(1)))
        match = re.match(r"^#{1,4}\s*Bab\s+(\d+)\b", line, re.I)
        if match:
            found.add(int(match.group(1)))
    return found


def chapter_numbers(story):
    nums = outline_numbers(story) | set(blueprints(story))
    for folder in ("manuscript", "state-updates"):
        path = story / folder
        if path.is_dir():
            nums.update(n for p in path.glob("chapter-*.md")
                        if (n := chapter_no(p)) is not None)
    return sorted(nums)


def resolve_story(slug=None):
    if slug:
        path = STORIES / slug
        if path.is_dir():
            return path
        raise ValueError(f"Proyek tidak ditemukan: {slug}")
    found = sorted(p for p in STORIES.iterdir() if p.is_dir()) if STORIES.is_dir() else []
    if len(found) == 1:
        return found[0]
    if not found:
        raise ValueError("Belum ada proyek di folder stories/.")
    raise ValueError("Ada beberapa proyek. Gunakan --story SLUG.")


def build_memory(story, before_chapter=None):
    """Build source-backed memory; no AI-generated facts are invented or cached."""
    sections = []
    sources = []
    for name in CORE:
        p = story / name
        if p.is_file():
            sources.append((p, None))
    for folder in ("continuity", "state-updates"):
        directory = story / folder
        if directory.is_dir():
            for path in sorted(directory.glob("*.md")):
                n = chapter_no(path)
                if before_chapter is None:
                    sources.append((path, None))
                elif folder == "state-updates":
                    if n is not None and n < before_chapter:
                        sources.append((path, None))
                elif folder == "continuity":
                    if n is not None and n < before_chapter:
                        sources.append((path, None))
                    elif n is None:
                        warn = f"[PERINGATAN KONTINUITAS: Berkas tanpa nomor bab — gunakan hanya fakta sebelum Bab {before_chapter}]"
                        sources.append((path, warn))
    for item in sources:
        path, warn = item
        content = read(path)
        if content:
            header = f"## SOURCE: {display_path(path)}"
            if warn:
                header += f" {warn}"
            sections.extend([header, "", content, ""])
    return "\n".join(sections).strip()


def extract_blueprint_boundaries(blueprint_text):
    """Extract character knowledge, reader knowledge, and withheld information from blueprint."""
    char_knowledge = []
    reader_knowledge = []
    withheld_info = []
    present_chars = []
    for line in blueprint_text.splitlines():
        line_clean = line.strip()
        if re.search(r"\bTokoh hadir\b", line_clean, re.I):
            val = re.sub(r"^[-*]\s*(\*\*)?Tokoh hadir:?(\*\*)?\s*", "", line_clean, flags=re.I)
            present_chars.extend([c.strip() for c in re.split(r"[,;]", val) if c.strip()])
        elif re.search(r"\bYang diketahui tokoh\b", line_clean, re.I):
            char_knowledge.append(re.sub(r"^[-*]\s*(\*\*)?Yang diketahui tokoh:?(\*\*)?\s*", "", line_clean, flags=re.I))
        elif re.search(r"\bYang diketahui pembaca\b", line_clean, re.I):
            reader_knowledge.append(re.sub(r"^[-*]\s*(\*\*)?Yang diketahui pembaca:?(\*\*)?\s*", "", line_clean, flags=re.I))
        elif re.search(r"\bInformasi yang ditahan\b", line_clean, re.I):
            withheld_info.append(re.sub(r"^[-*]\s*(\*\*)?Informasi yang ditahan:?(\*\*)?\s*", "", line_clean, flags=re.I))
        elif re.search(r"\bHal yang tidak boleh disimpulkan\b", line_clean, re.I):
            reader_knowledge.append("JANGAN DISIMPULKAN PEMBACA: " + re.sub(r"^[-*]\s*(\*\*)?Hal yang tidak boleh disimpulkan[^:]*:?(\*\*)?\s*", "", line_clean, flags=re.I))
    return {
        "character_knowledge": char_knowledge,
        "reader_knowledge": reader_knowledge,
        "withheld_info": withheld_info,
        "present_characters": present_chars
    }


def detect_source_conflicts(story, number):
    """Detect structural or data source conflicts for the target chapter."""
    conflicts = []
    if number > 1:
        prev_m = manuscript(story, number - 1)
        if not read(prev_m):
            conflicts.append(f"Naskah Bab {number - 1} belum tersedia di {display_path(prev_m)}. Penulisan Bab {number} berisiko kehilangan kesinambungan langsung dari bab sebelumnya.")
        prev_s = state_update(story, number - 1)
        if not read(prev_s):
            conflicts.append(f"State Update Bab {number - 1} belum tersedia di {display_path(prev_s)}. Catatan fakta kanon dari bab sebelumnya belum terekam.")
    bps = blueprints(story)
    if number not in bps:
        conflicts.append(f"Blueprint khusus Bab {number} tidak ditemukan di folder blueprint. Outline saja bukan izin untuk mengarang detail adegan.")
    st = state_update(story, number)
    ms = manuscript(story, number)
    if read(st) and not read(ms):
        conflicts.append(f"Terdeteksi orphan state: State Update Bab {number} sudah ada tetapi naskah belum tersedia.")
    return conflicts


def build_context(story, number, rewrite=False):
    if number not in chapter_numbers(story):
        raise ValueError(f"Bab {number} tidak ditemukan dalam outline/blueprint.")
    target = manuscript(story, number)
    state_target = state_update(story, number)
    if (target.exists() or state_target.exists()) and not rewrite:
        existing = ", ".join(display_path(x) for x in (target, state_target) if x.exists())
        raise FileExistsError(f"File target sudah ada: {existing}. Rewrite perlu persetujuan eksplisit.")

    bp = blueprints(story).get(number, "")
    bp_bounds = extract_blueprint_boundaries(bp) if bp else {
        "character_knowledge": [], "reader_knowledge": [], "withheld_info": [], "present_characters": []
    }
    conflicts = detect_source_conflicts(story, number)

    chunks = [
        f"# PAKET KONTEKS BAB {number:03d}", "",
        f"Proyek: {story.name}",
        f"Target naskah: {display_path(target)}",
        f"Target State Update: {display_path(state_target)}",
        f"Mode: {'REWRITE' if rewrite else 'PENULISAN BARU'}",
    ]

    # Explicit conflict warnings (if any)
    if conflicts:
        chunks.extend([
            "",
            "## PERINGATAN KONFLIK SUMBER",
            "",
            "> [!WARNING] TERDETEKSI INKONSISTENSI / KETIADAAN BERKAS SUMBER:",
        ])
        for conf in conflicts:
            chunks.append(f"- {conf}")
        chunks.extend([
            "> Laporkan atau pertimbangkan dampak konflik di atas. Jangan menebak fakta yang belum terkonfirmasi.",
            ""
        ])

    # 1. Instruksi Penulisan (Writer Instructions)
    chunks.extend([
        "",
        "## 1. INSTRUKSI PENULISAN (AI WRITER)",
        "",
        f"Anda bertindak sebagai **Penulis Prosa (Writer)** untuk Bab {number:03d}.",
        "Tugas utama Anda:",
        f"1. Tulis prosa lengkap Bab {number:03d} dan simpan ke `{display_path(target)}`.",
        f"2. Buat State Update faktual berdasarkan peristiwa yang benar-benar terjadi di naskah dan simpan ke `{display_path(state_target)}`.",
        "",
        "### Prinsip 3 Lapis Pengetahuan (Wajib Dipatuhi):",
        "1. **Pengetahuan Penulis (Author Macro Knowledge):**",
        "   - Informasi pada Bagian 2 (Kanon dan Arah Cerita) disediakan **HANYA untuk Anda sebagai penulis** guna menjaga arah cerita, sebab-akibat, dan fungsi planting-payoff.",
        "   - **JANGAN PERNAH membocorkan rahasia masa depan ke dalam narasi, dialog, atau monolog batin karakter sebelum ada jalur informasi yang sah di bab ini.**",
        "2. **Batas Pengetahuan Karakter (Character Knowledge):**",
        "   - Karakter **HANYA boleh mengetahui apa yang secara sah terdaftar dalam batas pengetahuan bab ini** (lihat Bagian 4).",
        "   - Karakter TIDAK TAHU rahasia masa lalu atau masa depan tanpa bukti lapangan nyata. Jangan membuat tokoh melompat mengambil kesimpulan tanpa dasar.",
        "3. **Batas Informasi Pembaca (Reader Knowledge):**",
        "   - Pembaca hanya boleh menerima informasi yang diizinkan untuk diungkap pada bab ini (lihat Bagian 5).",
        "   - Rahasia yang ditahan (*withheld*) **WAJIB tetap menjadi misteri bagi pembaca**.",
        "",
        "### Standar Pelaksanaan:",
        "- Tulis prosa alami dengan paragraf normal (hindari satu kalimat per baris).",
        "- Kembangkan dialog, suasana, dan gerak kecil secara leluasa selama tidak melanggar batasan adegan.",
    ])

    # 2. Kanon dan Arah Cerita (Pengetahuan Khusus Penulis)
    chunks.extend([
        "",
        "## 2. KANON DAN ARAH CERITA (PENGETAHUAN KHUSUS PENULIS)",
        "",
        "> [!IMPORTANT] INFORMASI INI HANYA UNTUK PENULIS (AUTHOR MACRO KNOWLEDGE).",
        "> Bagian ini memuat kebenaran objektif dunia cerita dan peta jalan makro untuk menjaga kausalitas.",
        "> Karakter cerita TIDAK MENGETAHUI rahasia atau kejadian masa depan di bagian ini kecuali dinyatakan eksplisit pada Bagian 4.",
        ""
    ])
    core_parts = [
        ("Premis Proyek", story / "00-premise.md"),
        ("Konsep Cerita & Mekanisme Misteri", story / "01-concept.md"),
        ("Dunia dan Aturan Cerita", story / "03-world-and-rules.md"),
        ("Keputusan Kanon & Arah Akhir (Decision Log)", story / "05-decision-log.md"),
    ]
    for label, path in core_parts:
        c = read(path)
        if c:
            chunks.extend([f"### {label} — {display_path(path)}", "", c, ""])

    outline_path = story / "04-story-outline.md"
    outline_content = read(outline_path)
    if outline_content:
        chunks.extend([
            f"### Peta Jalan Makro & Rangkaian Sebab-Akibat — {display_path(outline_path)}",
            "",
            "> [!NOTE] PETA JALAN MAKRO (ROADMAP PENGARANG):",
            "> Rangkaian bab dan ringkasan sebab-akibat di bawah ini disediakan agar penulis memahami arah payoff dan konsistensi makro cerita.",
            "> Peristiwa dan judul bab-bab mendatang BUKAN fakta yang boleh diungkap dalam prosa bab target.",
            "",
            outline_content,
            ""
        ])

    # 3. Konteks Bab Target (Blueprint)
    chunks.extend([
        "",
        f"## 3. KONTEKS BAB TARGET (BLUEPRINT BAB {number})",
        "",
        f"> [!TIP] ACUAN UTAMA BAB {number}:",
        "> Blueprint ini mengendalikan urutan adegan, tujuan dramatis, dan batasan bab target.",
        ""
    ])
    if bp:
        chunks.extend([bp, ""])
    else:
        chunks.extend([
            "PERINGATAN: Blueprint khusus untuk bab ini tidak ditemukan.",
            "Outline saja bukan izin untuk mengarang detail struktural.",
            ""
        ])

    # 4. Batas Pengetahuan Karakter
    chunks.extend([
        "",
        f"## 4. BATAS PENGETAHUAN KARAKTER BAB {number}",
        "",
        "> [!IMPORTANT] BATAS PENGETAHUAN KARAKTER:",
        "> Tokoh dalam bab ini HANYA mengetahui fakta yang didukung bukti nyata pada bab ini.",
        "> Dugaan tokoh tidak boleh diperlakukan sebagai kebenaran mutlak.",
        ""
    ])
    if bp_bounds["character_knowledge"]:
        chunks.append("### Fakta yang Diketahui Tokoh pada Bab Ini:")
        for item in bp_bounds["character_knowledge"]:
            chunks.append(f"- {item}")
        chunks.append("")
    if bp_bounds["withheld_info"]:
        chunks.append("### Fakta yang BELUM Diketahui / Ditahan dari Tokoh:")
        for item in bp_bounds["withheld_info"]:
            chunks.append(f"- {item}")
        chunks.append("")
    if bp_bounds["present_characters"]:
        chunks.extend([
            "### Karakter yang Hadir dalam Bab Ini:",
            f"- {', '.join(bp_bounds['present_characters'])}",
            "- Karakter lain yang belum hadir tidak boleh berinteraksi atau mempengaruhi adegan secara langsung.",
            ""
        ])
    char_sheet = read(story / "02-characters.md")
    if char_sheet:
        chunks.extend([
            f"### Profil Karakter Relevan — {display_path(story / '02-characters.md')}",
            "",
            char_sheet,
            ""
        ])

    # 5. Batas Informasi Pembaca
    chunks.extend([
        "",
        f"## 5. BATAS INFORMASI PEMBACA BAB {number}",
        "",
        "> [!IMPORTANT] BATAS INFORMASI PEMBACA:",
        "> Jaga tensi naratif. Jangan memberikan informasi lebih banyak daripada yang diizinkan untuk bab ini.",
        ""
    ])
    if bp_bounds["reader_knowledge"]:
        chunks.append("### Informasi yang Boleh Diperlihatkan kepada Pembaca:")
        for item in bp_bounds["reader_knowledge"]:
            chunks.append(f"- {item}")
        chunks.append("")
    if bp_bounds["withheld_info"]:
        chunks.append("### Informasi yang WAJIB DITAHAN dari Pembaca:")
        for item in bp_bounds["withheld_info"]:
            chunks.append(f"- {item}")
        chunks.append("")

    # 6. Konteks Kontinuitas dan Rekam Peristiwa
    chunks.extend([
        "",
        "## 6. KONTEKS KONTINUITAS DAN REKAM PERISTIWA",
        "",
    ])
    # Collect state updates up to number - 1
    su_folder = story / "state-updates"
    su_files = []
    if su_folder.is_dir():
        for p in sorted(su_folder.glob("*.md")):
            n = chapter_no(p)
            if n is not None and n < number:
                su_files.append(p)
    if su_files:
        chunks.append("### State Updates Bab Sebelumnya:")
        for su_p in su_files:
            c = read(su_p)
            if c:
                chunks.extend(["", f"#### {display_path(su_p)}", "", c])
        chunks.append("")
    else:
        chunks.extend([
            "### State Updates Sebelumnya:",
            f"Belum ada State Update sebelum Bab {number} (bab pembuka / bab awal).",
            ""
        ])

    # Continuity folder safe items
    cont_folder = story / "continuity"
    if cont_folder.is_dir():
        for cp in sorted(cont_folder.glob("*.md")):
            cn = chapter_no(cp)
            if cn is not None and cn < number:
                c = read(cp)
                if c:
                    chunks.extend([f"### Kontinuitas: {display_path(cp)}", "", c, ""])
            elif cn is None:
                c = read(cp)
                if c:
                    chunks.extend([
                        f"### Kontinuitas Umum: {display_path(cp)}",
                        f"> [!WARNING] Catatan kontinuitas tanpa nomor bab — gunakan hanya fakta sebelum Bab {number}.",
                        "",
                        c,
                        ""
                    ])

    # Previous chapter manuscript
    prev = manuscript(story, number - 1)
    if number > 1 and read(prev):
        chunks.extend([
            f"### Naskah Bab Sebelumnya — {display_path(prev)}",
            "",
            read(prev),
            ""
        ])

    # 7. Panduan Penulisan Prosa
    writing_standard = read(ROOT / "docs/05-writing-standard.md")
    if writing_standard:
        chunks.extend([
            "",
            f"## 7. PANDUAN PENULISAN PROSA — {display_path(ROOT / 'docs/05-writing-standard.md')}",
            "",
            writing_standard,
            ""
        ])

    return "\n".join(chunks).rstrip() + "\n"
