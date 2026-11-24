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
    sources = [story / name for name in CORE]
    for folder in ("continuity", "state-updates"):
        directory = story / folder
        if directory.is_dir():
            for path in sorted(directory.glob("*.md")):
                n = chapter_no(path)
                if before_chapter is None or n is None or n < before_chapter:
                    sources.append(path)
    for path in sources:
        content = read(path)
        if content:
            sections.extend([f"## SOURCE: {display_path(path)}", "", content, ""])
    return "\n".join(sections).strip()


def build_context(story, number, rewrite=False):
    if number not in chapter_numbers(story):
        raise ValueError(f"Bab {number} tidak ditemukan dalam outline/blueprint.")
    target = manuscript(story, number)
    if target.exists() and not rewrite:
        raise FileExistsError(f"Naskah sudah ada: {display_path(target)}. Rewrite perlu persetujuan eksplisit.")
    parts = [
        ("Instruksi AI", ROOT / "AI_INSTRUCTIONS.md"),
        ("Panduan blueprint adegan", ROOT / "docs/02-scene-blueprint.md"),
        ("Panduan kontinuitas", ROOT / "docs/03-continuity.md"),
        ("Standar prosa", ROOT / "docs/05-writing-standard.md"),
        ("Kontrak kerja", ROOT / "docs/06-ai-operating-contract.md"),
        ("README proyek", story / "README.md"),
    ]
    chunks = [f"# PAKET KONTEKS BAB {number:03d}", "",
              f"Proyek: {story.name}",
              f"Target naskah: {display_path(target)}",
              f"Target State Update: {display_path(state_update(story, number))}",
              "Gunakan sumber di bawah sebagai sumber kebenaran. Bedakan KANON, WAJIB, FLEKSIBEL, dan BELUM DIPUTUSKAN.",
              "Jangan menyimpulkan fakta yang tidak didukung sumber. Jika ada konflik yang memengaruhi cerita, laporkan dan jangan menebak.",
              "State Update bab setelah target tidak boleh digunakan.",
              "Mode: REWRITE" if rewrite else "Mode: PENULISAN BARU"]
    for label, path in parts:
        content = read(path)
        if content:
            chunks.extend(["", f"## {label} — {display_path(path)}", "", content])
    memory = build_memory(story, before_chapter=number)
    if memory:
        chunks.extend(["", "## MEMORI CERITA BERDASARKAN SUMBER", "", memory])
    bp = blueprints(story).get(number, "")
    if bp:
        chunks.extend(["", f"## BLUEPRINT BAB {number}", "", bp])
    else:
        chunks.extend(["", "## PERINGATAN", "", "Blueprint khusus tidak ditemukan. Outline saja bukan izin untuk mengarang detail struktural."])
    prev = manuscript(story, number - 1)
    if number > 1 and read(prev):
        chunks.extend(["", "## NASKAH BAB SEBELUMNYA", "", read(prev)])
    return "\n".join(chunks).rstrip() + "\n"
