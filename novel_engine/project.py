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


def parse_character_profile(text):
    """Split character summary into public/general profile and private secrets."""
    raw_sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in raw_sentences if s.strip()]

    public_parts = []
    secrets_parts = []

    secret_keywords = (
        "rahasia", "diam", "sembunyi", "janji", "privat", "motif",
        "tidak menceritakan", "tidak memberitahu", "takut", "memilih diam",
        "menyembunyikan", "mengetahui bahwa", "secret", "hidden", "vow", "oath"
    )

    for s in sentences:
        s_lower = s.lower()
        if any(k in s_lower for k in secret_keywords):
            secrets_parts.append(s)
        else:
            public_parts.append(s)

    public_info = " ".join(public_parts) if public_parts else text
    return public_info, secrets_parts


def extract_author_secrets(story):
    """Dynamically extract canonical author-only secrets from decision-log and/or concept documents."""
    secrets = []
    if not story:
        return secrets

    dl_path = story / "05-decision-log.md"
    dl_text = read(dl_path)
    if dl_text:
        sections = re.split(r"(?mi)^##\s+", dl_text)
        for sec in sections:
            sec_strip = sec.strip()
            if not sec_strip or sec_strip.lower().startswith("decision log") or sec_strip.lower().startswith("belum diputuskan"):
                continue
            lines = sec_strip.splitlines()
            title = lines[0].strip()
            keputusan_match = re.search(r"(?mi)^[-*]\s*(\*\*)?Keputusan:?(\*\*)?\s*([^\n]+(?:\n(?!\s*[-*]\s*(\*\*|\w+:)|\s*##)[^\n]+)*)", sec_strip)
            if keputusan_match:
                kep = " ".join(keputusan_match.group(3).split())
                secrets.append(f"{title}: {kep}")
            elif len(lines) > 1:
                body = " ".join(" ".join(lines[1:]).split())
                if body:
                    secrets.append(f"{title}: {body}")

    if not secrets:
        concept_path = story / "01-concept.md"
        c_text = read(concept_path)
        if c_text:
            sections = re.split(r"(?mi)^##\s+", c_text)
            for sec in sections:
                sec_strip = sec.strip()
                if not sec_strip:
                    continue
                header = sec_strip.splitlines()[0].strip()
                if any(k in header.lower() for k in ("mekanisme misteri", "akhir yang dituju", "kebenaran cerita", "resolusi")):
                    body = " ".join(sec_strip.splitlines()[1:]).strip()
                    if body:
                        secrets.append(f"{header}: {' '.join(body.split())}")

    return secrets


def normalize_character_name(raw_name, known_names):
    """Normalize character name by matching known characters or capitalizing."""
    s = raw_name.strip()
    if not s:
        return ""
    for k in known_names:
        if s.lower() == k.lower():
            return k
    if s.islower():
        return s[0].upper() + s[1:]
    return s


def match_characters_in_clause(clause, candidate_chars):
    """Accurately match characters in a clause, supporting multi-word names without collision."""
    matched = []
    clause_lower = clause.lower()

    # 1. Full name match (longest names first)
    for name in sorted(candidate_chars, key=len, reverse=True):
        pat = rf"\b{re.escape(name.lower())}\b"
        if re.search(pat, clause_lower):
            if name not in matched:
                matched.append(name)
    if matched:
        return matched

    # 2. Distinctive single-word match if unique across candidate_chars
    char_words = {}
    all_words_freq = {}
    for name in candidate_chars:
        words = [w.lower() for w in re.findall(r"\w+", name) if len(w) >= 3]
        char_words[name] = words
        for w in set(words):
            all_words_freq[w] = all_words_freq.get(w, 0) + 1

    for name in sorted(candidate_chars, key=len, reverse=True):
        for w in char_words.get(name, []):
            if all_words_freq.get(w, 0) == 1:
                if re.search(rf"\b{re.escape(w)}\b", clause_lower):
                    if name not in matched:
                        matched.append(name)
                    break
    return matched


def extract_blueprint_boundaries(blueprint_text, story=None):
    """Extract character knowledge, reader knowledge, and withheld information from blueprint with scene identity and character isolation."""
    known_chars = []
    non_present_profiles = {}
    if story:
        c_text = read(story / "02-characters.md")
        if c_text:
            for m in re.finditer(r"(?mi)^##\s*([^\n—–-]+)", c_text):
                name = m.group(1).strip()
                if name and name.lower() not in [k.lower() for k in known_chars] and not name.startswith("#"):
                    known_chars.append(name)
            sections = re.split(r"(?mi)^##\s*", c_text)
            for sec in sections:
                if sec.strip():
                    lines = sec.strip().splitlines()
                    header = lines[0].strip()
                    c_name = re.split(r"[—–-]", header)[0].strip()
                    body = " ".join(l.strip() for l in lines[1:] if l.strip())
                    if c_name and body and not c_name.startswith("#"):
                        pub_info, sec_parts = parse_character_profile(body)
                        non_present_profiles[c_name] = {
                            "header": header,
                            "summary": body,
                            "public_info": pub_info,
                            "secrets_info": sec_parts
                        }

    # Split blueprint into scenes
    matches = list(re.finditer(r"(?mi)^(#{2,3}\s*Adegan\s+\d+[^:\n]*)$", blueprint_text))
    scene_blocks = []
    if matches:
        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(blueprint_text)
            penutup = re.search(r"(?mi)^#{2,3}\s*(Penutup|Batasan|Kesiapan)", blueprint_text[start:end])
            if penutup:
                end = start + penutup.start()
            title = re.sub(r"^#{2,3}\s*", "", m.group(1)).strip()
            scene_blocks.append((title, blueprint_text[start:end].strip()))
    else:
        scene_blocks.append(("Adegan Bab", blueprint_text.strip()))

    all_present_characters = []
    seen_present = set()
    scenes = []
    ambiguous_notes = []
    char_knowledge = {}  # name -> {"diketahui": [], "diduga": [], "disalahpahami": [], "belum_diketahui": []}
    reader_knowledge = []  # list of (scene_title, text)
    withheld_from_reader = []  # list of (scene_title, text)
    caution_for_reader = []  # list of (scene_title, text)

    # First pass: collect characters mentioned in Tokoh hadir
    for title, content in scene_blocks:
        for line in content.splitlines():
            l_strip = line.strip()
            if re.search(r"^[-*]\s*(\*\*)?(tokoh hadir|karakter hadir|tokoh)\b", l_strip, re.I):
                raw_val = re.sub(r"^[-*]\s*(\*\*)?[^:]+:?(\*\*)?\s*", "", l_strip)
                for part in re.split(r"[,;]", raw_val):
                    p_name = part.strip()
                    if p_name:
                        norm = normalize_character_name(p_name, known_chars)
                        if norm.lower() not in seen_present:
                            seen_present.add(norm.lower())
                            all_present_characters.append(norm)
                        if norm not in known_chars:
                            known_chars.append(norm)

    # If no present characters found from Tokoh hadir, check POV or known characters
    if not all_present_characters:
        pov_match = re.search(r"(?mi)^[-*]\s*(\*\*)?POV:?(\*\*)?\s*([^\n]+)", blueprint_text)
        if pov_match:
            pov_name = pov_match.group(3).strip()
            if pov_name and pov_name.lower() not in seen_present:
                norm = normalize_character_name(pov_name, known_chars)
                seen_present.add(norm.lower())
                all_present_characters.append(norm)

    # Second pass: process each scene
    for title, content in scene_blocks:
        scene_present = []
        scene_other_lines = []
        for line in content.splitlines():
            l_strip = line.strip()
            if not l_strip or l_strip.startswith(("# Adegan", "## Adegan", "### Adegan")):
                continue

            if re.search(r"^[-*]\s*(\*\*)?(tokoh hadir|karakter hadir|tokoh)\b", l_strip, re.I):
                raw_val = re.sub(r"^[-*]\s*(\*\*)?[^:]+:?(\*\*)?\s*", "", l_strip)
                for part in re.split(r"[,;]", raw_val):
                    p_name = part.strip()
                    if p_name:
                        norm = normalize_character_name(p_name, known_chars)
                        if norm not in scene_present:
                            scene_present.append(norm)

            elif re.search(r"^[-*]\s*(\*\*)?(yang diketahui tokoh|batas pengetahuan|pengetahuan tokoh)\b", l_strip, re.I):
                raw_val = re.sub(r"^[-*]\s*(\*\*)?[^:]+:?(\*\*)?\s*", "", l_strip)
                clauses = [c.strip() for c in raw_val.split(";") if c.strip()]
                prev_attributed = []
                for clause in clauses:
                    matched = match_characters_in_clause(clause, known_chars)
                    if not matched and prev_attributed:
                        matched = list(prev_attributed)

                    if matched:
                        prev_attributed = matched
                        cl_lower = clause.lower()
                        if any(k in cl_lower for k in ("salah paham", "keliru", "menyangka", "salah mengira")):
                            cat = "disalahpahami"
                        elif any(k in cl_lower for k in ("menduga", "curiga", "mengira", "asumsi", "dugaan")):
                            cat = "diduga"
                        elif any(k in cl_lower for k in ("belum tahu", "tidak tahu", "belum melihat", "belum dapat memastikan", "bukan isi berkas", "belum menyadari")):
                            cat = "belum_diketahui"
                        else:
                            cat = "diketahui"

                        for c_name in matched:
                            char_knowledge.setdefault(c_name, {
                                "diketahui": [], "diduga": [], "disalahpahami": [], "belum_diketahui": []
                            })[cat].append((title, clause))
                    else:
                        ambiguous_notes.append((title, f"Catatan pengetahuan bersama/perlu pemeriksaan: {clause}"))

            elif re.search(r"^[-*]\s*(\*\*)?(yang diketahui pembaca|informasi pembaca|diperlihatkan kepada pembaca)\b", l_strip, re.I):
                val = re.sub(r"^[-*]\s*(\*\*)?[^:]+:?(\*\*)?\s*", "", l_strip)
                reader_knowledge.append((title, val))

            elif re.search(r"^[-*]\s*(\*\*)?(informasi yang ditahan|ditahan dari pembaca|ditahan)\b", l_strip, re.I):
                val = re.sub(r"^[-*]\s*(\*\*)?[^:]+:?(\*\*)?\s*", "", l_strip)
                withheld_from_reader.append((title, val))

            elif re.search(r"^[-*]\s*(\*\*)?(hal yang tidak boleh disimpulkan|jangan disimpulkan|tidak boleh disimpulkan)\b", l_strip, re.I):
                val = re.sub(r"^[-*]\s*(\*\*)?[^:]+:?(\*\*)?\s*", "", l_strip)
                caution_for_reader.append((title, val))

            elif re.search(r"^[-*]\s*(\*\*)?(lokasi dan waktu|waktu|lokasi|tujuan adegan|tujuan|situasi awal|urutan kejadian|urutan|perubahan setelah adegan|perubahan|detail wajib|ruang pengembangan prosa|ruang prosa):?(\*\*)?", l_strip, re.I):
                pass
            else:
                scene_other_lines.append(l_strip)

        scenes.append({
            "title": title,
            "present_characters": scene_present,
            "other_lines": scene_other_lines
        })

    # Deduplicate all present characters while preserving order
    deduped_present = []
    seen = set()
    for c in all_present_characters:
        if c.lower() not in seen:
            seen.add(c.lower())
            deduped_present.append(c)

    # Determine non-present characters
    non_present_characters = [c for c in known_chars if c.lower() not in seen]

    return {
        "scenes": scenes,
        "all_present_characters": deduped_present,
        "non_present_characters": non_present_characters,
        "non_present_profiles": non_present_profiles,
        "character_knowledge": char_knowledge,
        "reader_knowledge": reader_knowledge,
        "withheld_from_reader": withheld_from_reader,
        "caution_for_reader": caution_for_reader,
        "ambiguous_notes": ambiguous_notes
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
    bp_bounds = extract_blueprint_boundaries(bp, story=story) if bp else {
        "scenes": [], "all_present_characters": [], "non_present_characters": [], "non_present_profiles": {},
        "character_knowledge": {}, "reader_knowledge": [], "withheld_from_reader": [],
        "caution_for_reader": [], "ambiguous_notes": []
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

    # 4. Batas Pengetahuan Setiap Karakter
    chunks.extend([
        "",
        f"## 4. BATAS PENGETAHUAN SETIAP KARAKTER BAB {number}",
        "",
        "> [!IMPORTANT] PRINSIP ISOLASI PENGETAHUAN KARAKTER:",
        "> 1. Pengetahuan satu karakter bersifat pribadi dan TIDAK OTOMATIS diketahui karakter lain.",
        "> 2. Tokoh hanya mengetahui fakta yang didukung bukti nyata pada bab ini. Dugaan tidak boleh dinaikkan menjadi fakta kanon.",
        "> 3. Informasi yang tidak disebutkan dalam sumber ditandai sebagai '(Belum ditentukan dalam blueprint)', bukan diasumsikan diketahui.",
        "",
        "### A. Karakter yang Hadir dalam Bab Ini:",
        ""
    ])
    present_list = bp_bounds["all_present_characters"]
    if present_list:
        for c_name in present_list:
            c_data = bp_bounds["character_knowledge"].get(c_name, {
                "diketahui": [], "diduga": [], "disalahpahami": [], "belum_diketahui": []
            })
            chunks.append(f"#### {c_name}")

            # Diketahui
            chunks.append("- **Fakta yang diketahui:**")
            if c_data["diketahui"]:
                for sc_title, text in c_data["diketahui"]:
                    chunks.append(f"  - *{sc_title}:* {text}")
            else:
                chunks.append("  - *(Belum ditentukan dalam blueprint)*")

            # Diduga
            chunks.append("- **Fakta yang diduga:**")
            if c_data["diduga"]:
                for sc_title, text in c_data["diduga"]:
                    chunks.append(f"  - *{sc_title}:* {text}")
            else:
                chunks.append("  - *(Belum ditentukan dalam blueprint)*")

            # Disalahpahami
            chunks.append("- **Fakta yang disalahpahami:**")
            if c_data["disalahpahami"]:
                for sc_title, text in c_data["disalahpahami"]:
                    chunks.append(f"  - *{sc_title}:* {text}")
            else:
                chunks.append("  - *(Belum ditentukan dalam blueprint)*")

            # Belum diketahui
            chunks.append("- **Fakta yang belum diketahui:**")
            if c_data["belum_diketahui"]:
                for sc_title, text in c_data["belum_diketahui"]:
                    chunks.append(f"  - *{sc_title}:* {text}")
            else:
                chunks.append("  - *(Belum ditentukan dalam blueprint)*")
            chunks.append("")
    else:
        chunks.extend(["*(Belum ada karakter yang terdaftar secara eksplisit)*", ""])

    # Non-present characters
    chunks.extend([
        "### B. Karakter yang Tidak Hadir dalam Bab Ini:",
        ""
    ])
    non_present_list = bp_bounds["non_present_characters"]
    non_profiles = bp_bounds["non_present_profiles"]
    if non_present_list:
        for npc in non_present_list:
            if npc in non_profiles:
                prof = non_profiles[npc]
                header = prof["header"]
                public_info = prof.get("public_info", prof.get("summary", ""))
                secrets_info = prof.get("secrets_info", [])

                chunks.extend([
                    f"#### {header} (Tidak Hadir di Bab Ini)",
                    f"- **Profil Umum & Hubungan (Referensi Kanon):** {public_info}",
                ])
                if secrets_info:
                    chunks.append("- **Rahasia Pribadi / Motif Tersembunyi (Isolasi Ketat):**")
                    for s_item in secrets_info:
                        chunks.append(f"  - {s_item}")
                else:
                    chunks.append("- **Rahasia Pribadi / Motif Tersembunyi:** *(Tidak ada rahasia pribadi spesifik yang tercatat)*")

                chunks.extend([
                    "- **Batas Isolasi Karakter:**",
                    f"  > [!CAUTION] ISOLASI RAHASIA {npc.upper()}:",
                    f"  > Hubungan umum dan peran publik {npc} dapat diketahui oleh tokoh hadir sesuai relasi mereka.",
                    f"  > Namun, rahasia pribadi, memori tersembunyi, atau motif internal {npc} DILARANG dibocorkan ke dalam pikiran, dialog, atau persepsi karakter yang hadir pada bab ini!",
                    ""
                ])
            else:
                chunks.extend([
                    f"#### {npc} (Tidak Hadir di Bab Ini)",
                    f"- **Status:** Tokoh ini tidak hadir dalam Bab {number}.",
                    f"- **Batas Akses:** Hubungan umum tetap berlaku, namun informasi pribadi atau aktivitas {npc} di luar bab ini tidak diketahui karakter hadir.",
                    ""
                ])
    else:
        chunks.extend(["*(Seluruh karakter utama terdaftar hadir dalam bab ini)*", ""])

    if bp_bounds["ambiguous_notes"]:
        chunks.extend([
            "### C. Catatan Pengetahuan Ambigu / Perlu Pemeriksaan:",
            ""
        ])
        for sc_title, note in bp_bounds["ambiguous_notes"]:
            chunks.append(f"- *{sc_title}:* {note}")
        chunks.append("")

    other_scene_notes = []
    for sc in bp_bounds.get("scenes", []):
        for ol in sc.get("other_lines", []):
            other_scene_notes.append((sc["title"], ol))
    if other_scene_notes:
        chunks.extend([
            "### D. Catatan Adegan Tambahan dari Blueprint:",
            ""
        ])
        for sc_title, line in other_scene_notes:
            chunks.append(f"- *{sc_title}:* {line}")
        chunks.append("")

    # 5. Batas Informasi Pembaca
    chunks.extend([
        "",
        f"## 5. BATAS INFORMASI PEMBACA BAB {number}",
        "",
        "> [!IMPORTANT] BATAS INFORMASI PEMBACA:",
        "> Pembedaan tegas antara apa yang telah diperlihatkan, apa yang boleh diungkap, dan apa yang harus ditahan demi menjaga tensi misteri.",
        "",
        "### Informasi yang Sudah Diketahui Pembaca:",
    ])
    if number == 1:
        chunks.extend([
            "- Pembaca baru membuka novel; belum ada peristiwa dari bab sebelumnya.",
            ""
        ])
    else:
        chunks.extend([
            f"- Pembaca telah mengikuti kejadian dan pengungkapan yang telah ditampilkan pada Bab 1 s.d. {number - 1}.",
            ""
        ])

    chunks.append("### Informasi yang Boleh Diperlihatkan kepada Pembaca pada Bab Ini:")
    if bp_bounds["reader_knowledge"]:
        for sc_title, val in bp_bounds["reader_knowledge"]:
            chunks.append(f"- *{sc_title}:* {val}")
    else:
        chunks.append("- *(Belum ditentukan dalam blueprint)*")
    if bp_bounds["caution_for_reader"]:
        for sc_title, val in bp_bounds["caution_for_reader"]:
            chunks.append(f"- *{sc_title} [PERINGATAN]:* JANGAN DISIMPULKAN PEMBACA: {val}")
    chunks.append("")

    chunks.append("### Informasi yang HARUS DITAHAN dari Pembaca pada Bab Ini:")
    if bp_bounds["withheld_from_reader"]:
        for sc_title, val in bp_bounds["withheld_from_reader"]:
            chunks.append(f"- *{sc_title}:* {val}")
    else:
        chunks.append("- *(Belum ditentukan dalam blueprint)*")
    chunks.extend([
        "> [!NOTE] Penahanan ini berlaku bagi pembaca. Informasi yang ditahan dari pembaca tidak otomatis berarti tokoh POV juga tidak mengetahuinya (misalnya karakter POV mungkin mengetahui alasan tindakannya, namun narasi sengaja menahan penjelasan lengkap kepada pembaca pada bab ini).",
        "",
        "### Rahasia yang HANYA DIKETAHUI PENULIS (Author-Only Secrets):",
    ])
    author_secrets = extract_author_secrets(story)
    if author_secrets:
        for s in author_secrets:
            chunks.append(f"- {s}")
    else:
        chunks.append("- *(Tidak ada rahasia khusus yang tercatat dalam dokumen kanon)*")
    chunks.extend([
        "> [!WARNING] RAHASIA PENULIS DI ATAS DILARANG DIUNGKAP KEPADA PEMBACA ATAU DIJADIKAN FAKTA YANG DIKETAHUI KARAKTER PADA BAB INI.",
        ""
    ])

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
