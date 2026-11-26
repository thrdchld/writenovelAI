"""Versioned, agent-agnostic JSON CLI interface for Novel Engine.

Provides read-only, deterministic story inspection, temporal context retrieval,
character profiles, timeline extraction, scoped search, and structured chapter
validation for any AI agent with Python/terminal access, without depending on AGY.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from . import project
from .audit import deterministic_audit

SCHEMA_VERSION = 1
DEFAULT_SEARCH_LIMIT = 20
MAX_SEARCH_LIMIT = 200
OPERATIONS = ("status", "context", "character", "timeline", "search", "validate")
SEARCH_SCOPES = ("all", "chronological", "global")

_PLACEHOLDER_MARKERS = frozenset({
    "todo", "tbd", "placeholder", "belum ditulis",
    "isi di sini", "n/a", "...", "-", "kosong",
})
_PLACEHOLDER_PREFIX_RE = re.compile(
    r"^(?:todo|tbd|placeholder|belum ditulis|isi di sini)\s*(?:[:\-]|$)",
    re.I,
)
_CHAPTER_RANGE_RE = re.compile(r"chapter-(\d+)-to-(\d+)", re.I)

_GLOBAL_CORE_CATEGORIES = {
    "00-premise.md": "global_core",
    "01-concept.md": "global_core",
    "02-characters.md": "global_character_profile",
    "03-world-and-rules.md": "global_core",
    "04-story-outline.md": "global_outline",
    "05-decision-log.md": "global_decision_log",
}
_CHAPTER_FOLDER_CATEGORIES = {
    "manuscript": "chapter_manuscript",
    "state-updates": "chapter_state_update",
    "blueprint": "chapter_blueprint",
    "continuity": "chapter_continuity",
}


class AgentError(Exception):
    """Structured error emitted as a versioned JSON failure envelope."""

    def __init__(self, code: str, message: str, exit_code: int = 1):
        super().__init__(message)
        self.code = code
        self.message = message
        self.exit_code = exit_code


class _JsonArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that raises AgentError instead of printing to stdout/stderr."""

    def error(self, message: str) -> None:
        raise AgentError("INVALID_ARGUMENTS", message, exit_code=2)

    def exit(self, status: int = 0, message: str | None = None) -> None:
        if status != 0:
            raise AgentError(
                "INVALID_ARGUMENTS",
                (message or "Argumen tidak valid.").strip(),
                exit_code=2,
            )
        raise SystemExit(0)


def _is_placeholder_line(line: str) -> bool:
    s = re.sub(r"^(?:[-*>]\s*)+", "", line.strip())
    s = s.strip("[]() ").lower()
    if not s or s in _PLACEHOLDER_MARKERS:
        return True
    return bool(_PLACEHOLDER_PREFIX_RE.match(s))


def _is_meaningful_content(text: str) -> bool:
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


def _is_within(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except (ValueError, OSError):
        return False


def _add_source(sources: list[str], path: Path) -> None:
    rel = project.display_path(path)
    if rel not in sources:
        sources.append(rel)


def _classify_story_document(path: Path, story_root: Path) -> dict[str, Any]:
    """Deterministically classify a file in a story directory for temporal boundaries."""
    rel_parts = path.resolve().relative_to(story_root.resolve()).parts
    name = path.name

    if len(rel_parts) == 1 and name in _GLOBAL_CORE_CATEGORIES:
        return {
            "doc_category": _GLOBAL_CORE_CATEGORIES[name],
            "is_chapter_numbered": False,
            "chapter": None,
            "chapter_range": None,
            "max_chapter": None,
        }

    if len(rel_parts) >= 2 and rel_parts[0] in _CHAPTER_FOLDER_CATEGORIES:
        folder = rel_parts[0]
        range_match = _CHAPTER_RANGE_RE.search(path.stem)
        if range_match:
            start_ch = int(range_match.group(1))
            end_ch = int(range_match.group(2))
            lo, hi = (start_ch, end_ch) if start_ch <= end_ch else (end_ch, start_ch)
            return {
                "doc_category": f"{_CHAPTER_FOLDER_CATEGORIES[folder]}_range",
                "is_chapter_numbered": True,
                "chapter": lo,
                "chapter_range": [lo, hi],
                "max_chapter": hi,
            }
        n = project.chapter_no(path)
        if n is not None:
            return {
                "doc_category": _CHAPTER_FOLDER_CATEGORIES[folder],
                "is_chapter_numbered": True,
                "chapter": n,
                "chapter_range": None,
                "max_chapter": n,
            }
        if folder == "continuity":
            return {
                "doc_category": "unnumbered_continuity",
                "is_chapter_numbered": False,
                "chapter": None,
                "chapter_range": None,
                "max_chapter": None,
            }

    return {
        "doc_category": "unnumbered_document",
        "is_chapter_numbered": False,
        "chapter": None,
        "chapter_range": None,
        "max_chapter": None,
    }


def classify_source_conflict(conflict_text: str, story: Path, chapter: int) -> dict[str, Any]:
    """Deterministically classify a conflict string from project.detect_source_conflicts.

    Severity rules (never guessed):
    - ORPHAN_STATE_CONFLICT -> HIGH (blocking): State Update exists without a manuscript.
    - PREVIOUS_STATE_UPDATE_MISSING -> HIGH (blocking): canonical continuity record from chapter N-1 is absent.
    - BLUEPRINT_MISSING -> HIGH (blocking): chapter blueprint is absent.
    - PREVIOUS_MANUSCRIPT_MISSING -> MEDIUM (non-blocking warning): direct prose of chapter N-1 is absent,
      but canonical continuity may still be satisfied if State Update N-1 exists.
    - SOURCE_CONFLICT_WARNING -> MEDIUM (non-blocking warning): fallback for unrecognized conflict messages.
    """
    low = conflict_text.lower()
    if "orphan state" in low:
        return {
            "code": "ORPHAN_STATE_CONFLICT",
            "severity": "HIGH",
            "blocking": True,
            "message": conflict_text,
            "source": project.display_path(project.state_update(story, chapter)),
            "rationale": "State Update ada tanpa naskah bab sehingga status bab tidak konsisten.",
        }
    if "state update bab" in low and "belum tersedia" in low:
        return {
            "code": "PREVIOUS_STATE_UPDATE_MISSING",
            "severity": "HIGH",
            "blocking": True,
            "message": conflict_text,
            "source": project.display_path(project.state_update(story, chapter - 1)) if chapter > 1 else None,
            "rationale": "Rantai kontinuitas kanon dari bab sebelumnya belum terekam sehingga konsistensi bab ini belum dapat dijamin.",
        }
    if "naskah bab" in low and "belum tersedia" in low:
        return {
            "code": "PREVIOUS_MANUSCRIPT_MISSING",
            "severity": "MEDIUM",
            "blocking": False,
            "message": conflict_text,
            "source": project.display_path(project.manuscript(story, chapter - 1)) if chapter > 1 else None,
            "rationale": "Peringatan kesinambungan prosa: naskah bab sebelumnya belum tersedia, tetapi tidak memblokir jika State Update bab sebelumnya dan berkas bab target lengkap.",
        }
    if "blueprint khusus bab" in low and "tidak ditemukan" in low:
        return {
            "code": "BLUEPRINT_MISSING",
            "severity": "HIGH",
            "blocking": True,
            "message": conflict_text,
            "source": project.display_path(story / "blueprint"),
            "rationale": "Blueprint bab target wajib tersedia sebagai acuan adegan dan batas pengetahuan.",
        }
    return {
        "code": "SOURCE_CONFLICT_WARNING",
        "severity": "MEDIUM",
        "blocking": False,
        "message": conflict_text,
        "source": None,
        "rationale": "Peringatan konflik sumber yang perlu ditinjau.",
    }


def resolve_story_safe(slug: str | None = None) -> Path:
    """Resolve a story directory strictly confined within project.STORIES."""
    stories_root = project.STORIES.resolve()
    if slug is not None:
        cleaned = slug.strip()
        if not cleaned:
            raise AgentError("INVALID_ARGUMENTS", "Slug cerita tidak boleh kosong.", exit_code=2)
        if "/" in cleaned or "\\" in cleaned or cleaned in (".", "..") or ".." in cleaned:
            raise AgentError(
                "PATH_OUT_OF_BOUNDS",
                f"Slug cerita tidak valid atau keluar dari folder stories/: {slug}",
                exit_code=1,
            )
        candidate = (stories_root / cleaned)
        if not _is_within(candidate, stories_root) or candidate.resolve() == stories_root:
            raise AgentError(
                "PATH_OUT_OF_BOUNDS",
                f"Akses di luar folder stories/ ditolak: {slug}",
                exit_code=1,
            )
        if not candidate.is_dir():
            raise AgentError("STORY_NOT_FOUND", f"Cerita tidak ditemukan: {cleaned}", exit_code=1)
        return candidate

    if not stories_root.is_dir():
        raise AgentError("STORY_NOT_FOUND", "Belum ada proyek di folder stories/.", exit_code=1)
    found = sorted(p for p in stories_root.iterdir() if p.is_dir())
    if len(found) == 1:
        return found[0]
    if not found:
        raise AgentError("STORY_NOT_FOUND", "Belum ada proyek di folder stories/.", exit_code=1)
    raise AgentError(
        "STORY_AMBIGUOUS",
        "Ada beberapa proyek di stories/. Tentukan cerita dengan --story SLUG.",
        exit_code=1,
    )


def _validate_chapter_number(chapter: int) -> int:
    if not isinstance(chapter, int) or chapter < 1:
        raise AgentError("INVALID_ARGUMENTS", "Nomor bab harus berupa bilangan bulat >= 1.", exit_code=2)
    return chapter
def _parse_characters_document(story: Path) -> tuple[list[dict[str, Any]], Path | None]:
    char_path = story / "02-characters.md"
    if not char_path.is_file() or not _is_within(char_path, story):
        return [], None
    content = project.read(char_path)
    if not content:
        return [], char_path

    entries: list[dict[str, Any]] = []
    sections = re.split(r"(?mi)^##\s+", content)
    for sec in sections:
        sec_strip = sec.strip()
        if not sec_strip:
            continue
        lines = sec_strip.splitlines()
        header = lines[0].strip()
        if header.startswith("#"):
            continue
        name = re.split(r"[—–-]", header, maxsplit=1)[0].strip()
        body = "\n".join(l.strip() for l in lines[1:] if l.strip())
        if not name:
            continue
        parsed = project.parse_character_profile(body)
        entries.append({
            "name": name,
            "header": header,
            "raw_profile": body,
            "parsed": parsed,
        })
    return entries, char_path


def _extract_state_update_timeline(path: Path, chapter: int) -> dict[str, Any]:
    text = project.read(path)
    title = None
    recorded_time = None
    location = None
    pov = None
    events: list[str] = []

    lines = text.splitlines()
    for line in lines:
        s = line.strip()
        if not title and s.startswith("# "):
            title = s[2:].strip()
            continue
        if recorded_time is None:
            m = re.match(r"^(?:[-*]\s*)?(?:\*\*)?(?:waktu kronologis|waktu akhir|waktu|tanggal cerita)(?:\*\*)?\s*:\s*(?:\*\*)?\s*(.+)$", s, re.I)
            if m:
                recorded_time = m.group(1).strip().strip("*").strip()
                continue
        if location is None:
            m = re.match(r"^(?:[-*]\s*)?(?:\*\*)?lokasi(?:\s+tokoh)?(?:\*\*)?\s*:\s*(?:\*\*)?\s*(.+)$", s, re.I)
            if m:
                location = m.group(1).strip().strip("*").strip()
                continue
        if pov is None:
            m = re.match(r"^(?:[-*]\s*)?(?:\*\*)?pov(?:\*\*)?\s*:\s*(?:\*\*)?\s*(.+)$", s, re.I)
            if m:
                pov = m.group(1).strip().strip("*").strip()
                continue

    in_events = False
    for line in lines:
        s = line.strip()
        if re.match(r"^##\s+", s):
            heading = s.lstrip("#").strip().lower()
            in_events = any(k in heading for k in ("peristiwa", "kejadian", "kronologi", "urutan", "fakta baru"))
            continue
        if in_events:
            if s.startswith("###"):
                events.append(s.lstrip("#").strip())
            elif re.match(r"^[-*]\s+", s):
                events.append(re.sub(r"^[-*]\s+", "", s).strip())
            elif re.match(r"^\d+\.\s+", s):
                events.append(re.sub(r"^\d+\.\s+", "", s).strip())

    if not events:
        for line in lines:
            s = line.strip()
            if re.match(r"^[-*]\s+", s):
                bullet = re.sub(r"^[-*]\s+", "", s).strip()
                if not re.match(r"^(?:\*\*)?(?:waktu kronologis|waktu|tanggal|lokasi|pov)(?:\*\*)?\s*:", bullet, re.I):
                    events.append(bullet)

    return {
        "chapter": chapter,
        "source": project.display_path(path),
        "title": title,
        "recorded_time": recorded_time,
        "location": location,
        "pov": pov,
        "events": events,
    }


def _collect_continuity_items(
    story: Path,
    before_chapter: int | None,
    sources: list[str],
) -> list[dict[str, Any]]:
    """Collect continuity files with explicit temporal-boundary verification metadata."""
    items: list[dict[str, Any]] = []
    cont_folder = story / "continuity"
    if not cont_folder.is_dir():
        return items

    for p in sorted(cont_folder.glob("*.md")):
        if not _is_within(p, story):
            continue
        content = project.read(p)
        if not content:
            continue
        n = project.chapter_no(p)
        if before_chapter is not None and n is not None and n >= before_chapter:
            continue

        if n is not None:
            items.append({
                "chapter": n,
                "source": project.display_path(p),
                "content": content,
                "temporal_status": "verified_before_chapter" if before_chapter is not None else "chapter_numbered",
                "temporal_boundary_verified": True,
                "safe_as_prior_fact": True,
                "warning": None,
                "agent_guidance": (
                    f"Berkas kontinuitas bernomor Bab {n} (< Bab {before_chapter}); dapat digunakan sebagai fakta sebelumnya."
                    if before_chapter is not None
                    else f"Berkas kontinuitas bernomor Bab {n}."
                ),
            })
        else:
            if before_chapter is not None:
                warn = (
                    f"Batas temporal berkas kontinuitas tanpa nomor bab belum dapat dipastikan. "
                    f"Jangan perlakukan isinya secara otomatis sebagai fakta yang sudah diketahui sebelum Bab {before_chapter}; "
                    f"verifikasi setiap entri terhadap State Update bab sebelumnya."
                )
            else:
                warn = (
                    "Batas temporal berkas kontinuitas tanpa nomor bab belum dapat dipastikan. "
                    "Jangan mengasumsikan seluruh isinya aman atau sudah diketahui pada semua bab."
                )
            items.append({
                "chapter": None,
                "source": project.display_path(p),
                "content": content,
                "temporal_status": "unverified_temporal",
                "temporal_boundary_verified": False,
                "safe_as_prior_fact": False,
                "warning": warn,
                "agent_guidance": (
                    "Batas temporal belum dapat dipastikan; jangan perlakukan isi berkas ini sebagai "
                    "fakta yang otomatis sudah diketahui pada bab sebelumnya tanpa verifikasi terhadap State Update bernomor bab."
                ),
            })
        _add_source(sources, p)

    return items


def op_status(story: Path) -> tuple[dict[str, Any], list[str]]:
    sources: list[str] = []
    core_files: dict[str, dict[str, Any]] = {}
    for name in project.CORE:
        p = story / name
        exists = p.is_file() and _is_within(p, story)
        core_files[name] = {"exists": exists, "path": project.display_path(p)}
        if exists:
            _add_source(sources, p)

    directories = {
        folder: (story / folder).is_dir()
        for folder in ("blueprint", "manuscript", "state-updates", "continuity", "audits")
    }

    outline_set = project.outline_numbers(story)
    bp_map = project.blueprints(story)
    nums = project.chapter_numbers(story)

    chapters = []
    manuscripts_written = 0
    state_updates_written = 0
    blueprints_available = 0
    completed_chapters = 0

    for n in nums:
        ms_path = project.manuscript(story, n)
        su_path = project.state_update(story, n)
        has_ms = bool(project.read(ms_path))
        has_su = bool(project.read(su_path))
        has_bp = n in bp_map

        if has_ms:
            manuscripts_written += 1
            _add_source(sources, ms_path)
        if has_su:
            state_updates_written += 1
            _add_source(sources, su_path)
        if has_bp:
            blueprints_available += 1
        if has_ms and has_su:
            completed_chapters += 1

        chapters.append({
            "chapter": n,
            "in_outline": n in outline_set,
            "has_blueprint": has_bp,
            "has_manuscript": has_ms,
            "has_state_update": has_su,
            "manuscript_path": project.display_path(ms_path),
            "state_update_path": project.display_path(su_path),
        })

    bp_folder = story / "blueprint"
    if bp_folder.is_dir():
        for bp_file in sorted(bp_folder.glob("chapter-*.md")):
            if _is_within(bp_file, story) and project.read(bp_file):
                _add_source(sources, bp_file)

    total = len(nums)
    data = {
        "story": story.name,
        "story_path": project.display_path(story),
        "structure": {
            "core_files": core_files,
            "directories": directories,
        },
        "chapters": chapters,
        "progress": {
            "total_chapters": total,
            "manuscripts_written": manuscripts_written,
            "state_updates_written": state_updates_written,
            "blueprints_available": blueprints_available,
            "completed_chapters": completed_chapters,
            "completion_ratio": round(completed_chapters / total, 4) if total else 0.0,
        },
    }
    return data, sources
def op_context(story: Path, chapter: int, rewrite: bool = False) -> tuple[dict[str, Any], list[str]]:
    _validate_chapter_number(chapter)
    available = project.chapter_numbers(story)
    if chapter not in available:
        raise AgentError(
            "CHAPTER_NOT_FOUND",
            f"Bab {chapter} tidak ditemukan dalam outline/blueprint cerita '{story.name}'.",
            exit_code=1,
        )

    sources: list[str] = []
    target_ms = project.manuscript(story, chapter)
    target_su = project.state_update(story, chapter)
    has_ms = bool(project.read(target_ms))
    has_su = bool(project.read(target_su))

    core_docs: dict[str, dict[str, str]] = {}
    for name in project.CORE:
        p = story / name
        if p.is_file() and _is_within(p, story):
            content = project.read(p)
            if content:
                core_docs[name] = {
                    "path": project.display_path(p),
                    "content": content,
                }
                _add_source(sources, p)

    bp_map = project.blueprints(story)
    bp_text = bp_map.get(chapter, "")
    bp_folder = story / "blueprint"
    if bp_text and bp_folder.is_dir():
        exact_bp = bp_folder / f"chapter-{chapter:03d}.md"
        if exact_bp.is_file() and _is_within(exact_bp, story):
            _add_source(sources, exact_bp)
        else:
            for combined_bp in sorted(bp_folder.glob("chapter-*-to-*.md")):
                if _is_within(combined_bp, story) and bp_text in project.read(combined_bp):
                    _add_source(sources, combined_bp)
                    break

    bp_bounds = (
        project.extract_blueprint_boundaries(bp_text, story=story)
        if bp_text
        else {
            "scenes": [],
            "all_present_characters": [],
            "non_present_characters": [],
            "non_present_profiles": {},
            "present_profiles": {},
            "character_knowledge": {},
            "reader_knowledge": [],
            "withheld_from_reader": [],
            "caution_for_reader": [],
            "ambiguous_notes": [],
        }
    )

    author_secrets, character_secrets, unclassified_canon, needs_review_canon, public_canon = (
        project.extract_author_secrets(story)
    )

    previous_state_updates: list[dict[str, Any]] = []
    su_folder = story / "state-updates"
    if su_folder.is_dir():
        for p in sorted(su_folder.glob("*.md")):
            if not _is_within(p, story):
                continue
            n = project.chapter_no(p)
            if n is not None and n < chapter:
                content = project.read(p)
                if content:
                    previous_state_updates.append({
                        "chapter": n,
                        "source": project.display_path(p),
                        "content": content,
                    })
                    _add_source(sources, p)

    continuity_notes = _collect_continuity_items(story, before_chapter=chapter, sources=sources)
    unverified_continuity_sources = [
        item["source"] for item in continuity_notes if not item["temporal_boundary_verified"]
    ]

    previous_manuscript = None
    if chapter > 1:
        prev_ms = project.manuscript(story, chapter - 1)
        prev_content = project.read(prev_ms) if _is_within(prev_ms, story) else ""
        if prev_content:
            previous_manuscript = {
                "chapter": chapter - 1,
                "source": project.display_path(prev_ms),
                "content": prev_content,
            }
            _add_source(sources, prev_ms)

    conflicts = project.detect_source_conflicts(story, chapter)
    rendered_context = project.build_context(story, chapter, rewrite=True)

    char_knowledge_json: dict[str, dict[str, list[dict[str, str]]]] = {}
    for char_name, cats in bp_bounds["character_knowledge"].items():
        char_knowledge_json[char_name] = {
            cat: [{"scene": sc, "text": txt} for sc, txt in items]
            for cat, items in cats.items()
        }

    data = {
        "chapter": chapter,
        "mode": "rewrite" if rewrite else ("inspect_existing" if (has_ms or has_su) else "write"),
        "target_manuscript": project.display_path(target_ms),
        "target_state_update": project.display_path(target_su),
        "has_manuscript": has_ms,
        "has_state_update": has_su,
        "has_blueprint": bool(bp_text),
        "temporal_boundary": {
            "chapter": chapter,
            "max_included_state_update_chapter": (
                max(item["chapter"] for item in previous_state_updates)
                if previous_state_updates
                else None
            ),
            "excludes_current_and_future_state_updates": True,
            "has_unverified_continuity": bool(unverified_continuity_sources),
            "unverified_continuity_sources": unverified_continuity_sources,
            "continuity_policy": (
                "Berkas kontinuitas tanpa nomor bab tetap disertakan dengan status unverified_temporal "
                "(safe_as_prior_fact=false); jangan perlakukan isinya secara otomatis sebagai fakta "
                "yang sudah diketahui pada bab sebelumnya."
            ),
        },
        "conflicts": conflicts,
        "core_documents": core_docs,
        "blueprint": bp_text or None,
        "character_boundaries": {
            "present_characters": bp_bounds["all_present_characters"],
            "non_present_characters": bp_bounds["non_present_characters"],
            "present_profiles": bp_bounds["present_profiles"],
            "non_present_profiles": bp_bounds["non_present_profiles"],
            "character_knowledge": char_knowledge_json,
            "reader_knowledge": [
                {"scene": sc, "text": txt} for sc, txt in bp_bounds["reader_knowledge"]
            ],
            "withheld_from_reader": [
                {"scene": sc, "text": txt} for sc, txt in bp_bounds["withheld_from_reader"]
            ],
            "caution_for_reader": [
                {"scene": sc, "text": txt} for sc, txt in bp_bounds["caution_for_reader"]
            ],
            "ambiguous_notes": [
                {"scene": sc, "text": txt} for sc, txt in bp_bounds["ambiguous_notes"]
            ],
        },
        "canon_classification": {
            "author_secrets": author_secrets,
            "character_secrets": character_secrets,
            "public_canon": public_canon,
            "unclassified_canon": unclassified_canon,
            "needs_review_canon": needs_review_canon,
        },
        "previous_state_updates": previous_state_updates,
        "continuity_notes": continuity_notes,
        "previous_manuscript": previous_manuscript,
        "rendered_context": rendered_context,
    }
    return data, sources


def op_character(story: Path, name: str) -> tuple[dict[str, Any], list[str]]:
    query = name.strip()
    if not query:
        raise AgentError("INVALID_ARGUMENTS", "Nama karakter tidak boleh kosong.", exit_code=2)

    entries, char_path = _parse_characters_document(story)
    if not entries or char_path is None:
        raise AgentError(
            "CHARACTER_NOT_FOUND",
            f"Karakter '{query}' tidak ditemukan (02-characters.md kosong atau tidak tersedia).",
            exit_code=1,
        )

    q_lower = query.lower()
    matched = [e for e in entries if e["name"].lower() == q_lower]
    if not matched:
        matched = [e for e in entries if e["header"].lower() == q_lower]
    if not matched:
        pat = re.compile(rf"\b{re.escape(q_lower)}\b", re.I)
        matched = [e for e in entries if pat.search(e["name"])]
    if not matched:
        raise AgentError(
            "CHARACTER_NOT_FOUND",
            f"Karakter '{query}' tidak ditemukan dalam 02-characters.md.",
            exit_code=1,
        )
    if len(matched) > 1:
        names = ", ".join(e["name"] for e in matched)
        raise AgentError(
            "CHARACTER_AMBIGUOUS",
            f"Nama '{query}' cocok dengan beberapa karakter: {names}. Gunakan nama lengkap.",
            exit_code=1,
        )

    entry = matched[0]
    parsed = entry["parsed"]
    sources: list[str] = []
    _add_source(sources, char_path)

    author_secrets, character_secrets, unclassified_canon, needs_review_canon, public_canon = (
        project.extract_author_secrets(story)
    )
    name_pat = re.compile(rf"\b{re.escape(entry['name'])}\b", re.I)
    dl_mentions = {
        "author_secrets": [x for x in author_secrets if name_pat.search(x)],
        "character_secrets": [x for x in character_secrets if name_pat.search(x)],
        "public_canon": [x for x in public_canon if name_pat.search(x)],
        "unclassified_canon": [x for x in unclassified_canon if name_pat.search(x)],
        "needs_review_canon": [x for x in needs_review_canon if name_pat.search(x)],
    }
    if any(dl_mentions.values()):
        dl_path = story / "05-decision-log.md"
        if dl_path.is_file() and _is_within(dl_path, story):
            _add_source(sources, dl_path)

    appearances = []
    for n, bp_text in sorted(project.blueprints(story).items()):
        bounds = project.extract_blueprint_boundaries(bp_text, story=story)
        if any(c.lower() == entry["name"].lower() for c in bounds["all_present_characters"]):
            appearances.append(n)

    data = {
        "name": entry["name"],
        "header": entry["header"],
        "character_known": {
            "public_profile": parsed["public"],
            "character_secrets": parsed["character_secrets"],
        },
        "author_known": {
            "author_secrets": parsed["author_secrets"],
            "unclassified_profile_notes": parsed["unclassified"],
            "needs_review": parsed["needs_review"],
            "decision_log_mentions": dl_mentions,
        },
        "blueprint_appearances": appearances,
        "raw_profile": entry["raw_profile"],
    }
    return data, sources
def op_timeline(story: Path, before_chapter: int | None = None) -> tuple[dict[str, Any], list[str]]:
    if before_chapter is not None:
        _validate_chapter_number(before_chapter)

    sources: list[str] = []
    entries: list[dict[str, Any]] = []
    su_folder = story / "state-updates"
    if su_folder.is_dir():
        candidates: list[tuple[int, Path]] = []
        for p in sorted(su_folder.glob("*.md")):
            if not _is_within(p, story):
                continue
            n = project.chapter_no(p)
            if n is None:
                continue
            if before_chapter is not None and n >= before_chapter:
                continue
            if project.read(p):
                candidates.append((n, p))
        for n, p in sorted(candidates, key=lambda item: item[0]):
            entries.append(_extract_state_update_timeline(p, n))
            _add_source(sources, p)

    continuity_records = _collect_continuity_items(story, before_chapter=before_chapter, sources=sources)
    unverified_continuity_sources = [
        item["source"] for item in continuity_records if not item["temporal_boundary_verified"]
    ]

    temporal_warning = None
    if unverified_continuity_sources:
        temporal_warning = (
            "Terdapat berkas kontinuitas tanpa nomor bab yang batas temporalnya belum dapat dipastikan. "
            "Jangan perlakukan isinya secara otomatis sebagai fakta yang sudah diketahui pada bab sebelumnya."
        )

    data = {
        "before_chapter": before_chapter,
        "entries": entries,
        "continuity_records": continuity_records,
        "total_entries": len(entries),
        "temporal_boundary": {
            "before_chapter": before_chapter,
            "entries_strictly_before_chapter": before_chapter is not None,
            "has_unverified_continuity": bool(unverified_continuity_sources),
            "unverified_continuity_sources": unverified_continuity_sources,
            "warning": temporal_warning,
        },
    }
    return data, sources


def op_search(
    story: Path,
    query: str,
    limit: int = DEFAULT_SEARCH_LIMIT,
    before_chapter: int | None = None,
    scope: str | None = None,
) -> tuple[dict[str, Any], list[str]]:
    cleaned = query.strip()
    if not cleaned:
        raise AgentError("INVALID_ARGUMENTS", "Kata kunci pencarian tidak boleh kosong.", exit_code=2)
    if not isinstance(limit, int) or limit < 1 or limit > MAX_SEARCH_LIMIT:
        raise AgentError(
            "INVALID_ARGUMENTS",
            f"Nilai --limit harus antara 1 dan {MAX_SEARCH_LIMIT}.",
            exit_code=2,
        )
    if before_chapter is not None:
        _validate_chapter_number(before_chapter)

    if scope is None:
        effective_scope = "chronological" if before_chapter is not None else "all"
    else:
        if scope not in SEARCH_SCOPES:
            raise AgentError(
                "INVALID_ARGUMENTS",
                f"Nilai --scope tidak valid: {scope}. Pilihan: {', '.join(SEARCH_SCOPES)}.",
                exit_code=2,
            )
        effective_scope = scope

    q_lower = cleaned.lower()
    story_root = story.resolve()
    matches: list[dict[str, Any]] = []
    sources: list[str] = []
    total_matches = 0
    excluded_unbounded_files: list[str] = []
    unbounded_match_count = 0

    for path in sorted(story_root.rglob("*")):
        if not path.is_file():
            continue
        if not _is_within(path, story_root):
            continue
        rel_parts = path.relative_to(story_root).parts
        if any(part.startswith(".") or part == "workbench" for part in rel_parts):
            continue
        if path.suffix.lower() not in (".md", ".txt"):
            continue

        doc_meta = _classify_story_document(path, story_root)
        is_numbered = doc_meta["is_chapter_numbered"]

        if effective_scope == "chronological":
            if not is_numbered:
                excluded_unbounded_files.append(project.display_path(path))
                continue
            if before_chapter is not None and doc_meta["max_chapter"] >= before_chapter:
                continue
        elif effective_scope == "global":
            if is_numbered:
                continue
        else:  # scope == "all"
            if is_numbered and before_chapter is not None and doc_meta["max_chapter"] >= before_chapter:
                continue

        if is_numbered:
            if before_chapter is not None:
                temporal_status = "verified_before_chapter"
                may_contain_future = False
            else:
                temporal_status = "chapter_numbered"
                may_contain_future = False
        else:
            temporal_status = "unverified_temporal"
            may_contain_future = True

        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue

        file_matched = False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if q_lower in line.lower():
                total_matches += 1
                if may_contain_future:
                    unbounded_match_count += 1
                if len(matches) < limit:
                    matches.append({
                        "file": project.display_path(path),
                        "line": lineno,
                        "snippet": line.strip(),
                        "doc_category": doc_meta["doc_category"],
                        "chapter": doc_meta["chapter"],
                        "chapter_range": doc_meta["chapter_range"],
                        "temporal_status": temporal_status,
                        "may_contain_future_info": may_contain_future,
                    })
                    file_matched = True
        if file_matched:
            _add_source(sources, path)

    if effective_scope == "chronological" and before_chapter is not None:
        all_temporally_bounded = True
        temporal_guarantee = "strict_before_chapter"
        temporal_warning = None
    elif effective_scope == "chronological":
        all_temporally_bounded = True
        temporal_guarantee = "chapter_numbered_only"
        temporal_warning = None
    elif effective_scope == "global":
        all_temporally_bounded = False
        temporal_guarantee = "unbounded_global_only"
        temporal_warning = (
            "Pencarian mode global memindai dokumen tanpa nomor bab (outline, decision log, profil karakter, "
            "dan berkas kontinuitas umum) yang dapat memuat informasi masa depan atau rahasia penulis."
        )
    else:  # scope == "all"
        all_temporally_bounded = False
        if before_chapter is not None:
            temporal_guarantee = "partial_contains_unbounded_documents"
            temporal_warning = (
                f"Dokumen bab bernomor dibatasi sebelum Bab {before_chapter}, tetapi scope 'all' tetap memindai "
                "dokumen global/tanpa nomor bab (outline, decision log, profil karakter, continuity umum) "
                "yang tidak dijamin bebas informasi masa depan. Gunakan --scope chronological untuk batas temporal ketat."
            )
        else:
            temporal_guarantee = "unbounded_all_documents"
            temporal_warning = (
                "Pencarian scope 'all' mencakup dokumen global/tanpa nomor bab yang dapat memuat "
                "informasi masa depan atau rahasia penulis."
            )

    data = {
        "query": cleaned,
        "scope": effective_scope,
        "before_chapter": before_chapter,
        "limit": limit,
        "total_matches": total_matches,
        "returned_matches": len(matches),
        "truncated": total_matches > limit,
        "all_results_temporally_bounded": all_temporally_bounded,
        "temporal_guarantee": temporal_guarantee,
        "temporal_warning": temporal_warning,
        "unbounded_match_count": unbounded_match_count,
        "excluded_unbounded_files_count": len(excluded_unbounded_files),
        "excluded_unbounded_files": excluded_unbounded_files,
        "matches": matches,
    }
    return data, sources
def op_validate(story: Path, chapter: int) -> tuple[dict[str, Any], list[str]]:
    _validate_chapter_number(chapter)
    available = project.chapter_numbers(story)
    if chapter not in available:
        raise AgentError(
            "CHAPTER_NOT_FOUND",
            f"Bab {chapter} tidak ditemukan dalam cerita '{story.name}'.",
            exit_code=1,
        )

    sources: list[str] = []
    ms_path = project.manuscript(story, chapter)
    su_path = project.state_update(story, chapter)
    ms_text = project.read(ms_path) if _is_within(ms_path, story) else ""
    su_text = project.read(su_path) if _is_within(su_path, story) else ""
    bp_map = project.blueprints(story)

    ms_exists = bool(ms_text)
    su_exists = bool(su_text)
    ms_meaningful = _is_meaningful_content(ms_text)
    su_meaningful = _is_meaningful_content(su_text)
    bp_exists = chapter in bp_map

    if ms_exists:
        _add_source(sources, ms_path)
    if su_exists:
        _add_source(sources, su_path)
    outline_path = story / "04-story-outline.md"
    if outline_path.is_file() and _is_within(outline_path, story):
        _add_source(sources, outline_path)

    findings: list[dict[str, Any]] = []
    seen_codes: set[tuple[str, str]] = set()

    def _add_finding(
        severity: str,
        code: str,
        message: str,
        source: str | None = None,
        blocking: bool | None = None,
    ) -> None:
        key = (code, message)
        if key in seen_codes:
            return
        seen_codes.add(key)
        is_blocking = (severity in {"CRITICAL", "HIGH"}) if blocking is None else blocking
        findings.append({
            "severity": severity,
            "code": code,
            "message": message,
            "source": source,
            "blocking": is_blocking,
        })

    if not ms_exists:
        _add_finding("HIGH", "MANUSCRIPT_MISSING", f"Naskah Bab {chapter} tidak ada atau kosong.", project.display_path(ms_path), blocking=True)
    elif not ms_meaningful:
        _add_finding("HIGH", "MANUSCRIPT_PLACEHOLDER", f"Naskah Bab {chapter} hanya berisi heading atau placeholder.", project.display_path(ms_path), blocking=True)

    if not su_exists:
        _add_finding("HIGH", "STATE_UPDATE_MISSING", f"State Update Bab {chapter} tidak ada atau kosong.", project.display_path(su_path), blocking=True)
    elif not su_meaningful:
        _add_finding("HIGH", "STATE_UPDATE_PLACEHOLDER", f"State Update Bab {chapter} hanya berisi heading atau placeholder.", project.display_path(su_path), blocking=True)

    if not bp_exists:
        _add_finding("HIGH", "BLUEPRINT_MISSING", f"Blueprint Bab {chapter} tidak ditemukan.", project.display_path(story / "blueprint"), blocking=True)

    chapter_marker = f"Bab {chapter}:"
    chapter_num_pat = re.compile(rf"\bBab\s+{chapter}\b")
    for severity, code, detail in deterministic_audit(story):
        if code == "OUTLINE_MISSING" or chapter_marker in detail or chapter_num_pat.search(detail):
            if code in ("BLUEPRINT_MISSING", "STATE_UPDATE_MISSING") and any(f["code"] == code for f in findings):
                continue
            _add_finding(
                severity,
                code,
                detail,
                project.display_path(outline_path) if outline_path.is_file() else None,
            )

    conflicts = project.detect_source_conflicts(story, chapter)
    classified_conflicts = [classify_source_conflict(c, story, chapter) for c in conflicts]
    for cc in classified_conflicts:
        if cc["code"] == "BLUEPRINT_MISSING" and any(f["code"] == "BLUEPRINT_MISSING" for f in findings):
            continue
        _add_finding(
            cc["severity"],
            cc["code"],
            cc["message"],
            cc["source"],
            blocking=cc["blocking"],
        )

    by_severity: dict[str, int] = {}
    blocking_findings: list[str] = []
    warning_findings: list[str] = []
    for f in findings:
        sev = f["severity"]
        by_severity[sev] = by_severity.get(sev, 0) + 1
        if f["blocking"]:
            if f["code"] not in blocking_findings:
                blocking_findings.append(f["code"])
        else:
            if f["code"] not in warning_findings:
                warning_findings.append(f["code"])

    is_valid = (
        ms_meaningful
        and su_meaningful
        and bp_exists
        and len(blocking_findings) == 0
    )

    if not is_valid:
        validation_status = "invalid"
        status_reason = (
            f"Validasi Bab {chapter} gagal karena ditemukan temuan/konflik pemblokir: "
            f"{', '.join(blocking_findings)}."
        )
    elif warning_findings:
        validation_status = "valid_with_warnings"
        status_reason = (
            f"Validasi Bab {chapter} lulus tanpa konflik pemblokir, namun terdapat peringatan: "
            f"{', '.join(warning_findings)}."
        )
    else:
        validation_status = "valid"
        status_reason = (
            f"Validasi Bab {chapter} lulus: naskah, State Update, blueprint, dan rantai kontinuitas lengkap tanpa temuan."
        )

    data = {
        "chapter": chapter,
        "valid": is_valid,
        "validation_status": validation_status,
        "status_reason": status_reason,
        "checks": {
            "manuscript_exists": ms_exists,
            "manuscript_meaningful": ms_meaningful,
            "state_update_exists": su_exists,
            "state_update_meaningful": su_meaningful,
            "blueprint_exists": bp_exists,
            "no_blocking_conflicts": not any(cc["blocking"] for cc in classified_conflicts),
        },
        "blocking_findings": blocking_findings,
        "warning_findings": warning_findings,
        "findings": findings,
        "conflicts": conflicts,
        "classified_conflicts": classified_conflicts,
        "summary": {
            "total_findings": len(findings),
            "blocking_count": len(blocking_findings),
            "warning_count": len(warning_findings),
            "by_severity": by_severity,
        },
    }
    return data, sources


def _success_envelope(operation: str, story: str, data: dict[str, Any], sources: list[str]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": True,
        "operation": operation,
        "story": story,
        "data": data,
        "sources": sources,
    }


def _error_envelope(operation: str | None, code: str, message: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": False,
        "operation": operation,
        "error": {
            "code": code,
            "message": message,
        },
    }


def _build_parser() -> _JsonArgumentParser:
    common = _JsonArgumentParser(add_help=False)
    common.add_argument("--story", default=argparse.SUPPRESS, help="Slug folder proyek di stories/")

    parser = _JsonArgumentParser(
        prog="novel-agent",
        description="Versioned JSON interface for AI agents interacting with Novel Engine.",
        parents=[common],
    )
    sub = parser.add_subparsers(dest="operation")

    sub.add_parser("status", parents=[common], help="Status proyek, struktur cerita, dan progres bab")

    p_ctx = sub.add_parser("context", parents=[common], help="Paket konteks temporal untuk bab tertentu")
    p_ctx.add_argument("chapter", type=int, help="Nomor bab (>= 1)")
    p_ctx.add_argument("--rewrite", action="store_true", help="Tandai mode konteks sebagai rewrite")

    p_char = sub.add_parser("character", parents=[common], help="Profil karakter beserta pemisahan pengetahuan penulis/karakter")
    p_char.add_argument("name", help="Nama karakter")

    p_tl = sub.add_parser("timeline", parents=[common], help="Kronologi terekam sebelum bab tertentu")
    p_tl.add_argument("--before", type=int, default=None, help="Batas bab eksklusif (hanya bab < N)")

    p_search = sub.add_parser("search", parents=[common], help="Pencarian kata/frasa terbatas pada folder cerita")
    p_search.add_argument("query", help="Kata atau frasa yang dicari")
    p_search.add_argument("--limit", type=int, default=DEFAULT_SEARCH_LIMIT, help="Batas maksimum hasil")
    p_search.add_argument("--before", type=int, default=None, help="Batas bab eksklusif untuk dokumen bernomor bab")
    p_search.add_argument(
        "--scope",
        default=None,
        choices=SEARCH_SCOPES,
        help="Cakupan pencarian: chronological (hanya dokumen bernomor bab), global (dokumen global/tanpa nomor bab), atau all",
    )

    p_val = sub.add_parser("validate", parents=[common], help="Validasi terstruktur manuskrip dan State Update bab")
    p_val.add_argument("chapter", type=int, help="Nomor bab (>= 1)")

    return parser


def _detect_operation_hint(argv: list[str]) -> str | None:
    skip_next = False
    for token in argv:
        if skip_next:
            skip_next = False
            continue
        if token == "--story":
            skip_next = True
            continue
        if token.startswith("-"):
            continue
        if token in OPERATIONS:
            return token
        return None
    return None


def execute(argv: list[str]) -> tuple[dict[str, Any], int]:
    """Execute an agent command and return (json_envelope, exit_code)."""
    op_hint = _detect_operation_hint(argv)
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
        if not args.operation:
            raise AgentError(
                "INVALID_ARGUMENTS",
                f"Operasi wajib diisi. Pilihan: {', '.join(OPERATIONS)}.",
                exit_code=2,
            )
        operation = args.operation
        story_slug = getattr(args, "story", None)
        story = resolve_story_safe(story_slug)

        if operation == "status":
            data, sources = op_status(story)
        elif operation == "context":
            data, sources = op_context(story, args.chapter, rewrite=args.rewrite)
        elif operation == "character":
            data, sources = op_character(story, args.name)
        elif operation == "timeline":
            data, sources = op_timeline(story, before_chapter=args.before)
        elif operation == "search":
            data, sources = op_search(
                story,
                args.query,
                limit=args.limit,
                before_chapter=args.before,
                scope=args.scope,
            )
        elif operation == "validate":
            data, sources = op_validate(story, args.chapter)
        else:
            raise AgentError("INVALID_ARGUMENTS", f"Operasi tidak dikenal: {operation}", exit_code=2)

        return _success_envelope(operation, story.name, data, sources), 0
    except AgentError as exc:
        return _error_envelope(op_hint, exc.code, exc.message), exc.exit_code
    except Exception as exc:
        print(f"[novel_engine.agent] Unexpected error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return _error_envelope(op_hint, "INTERNAL_ERROR", f"Kesalahan internal: {exc}"), 1


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    envelope, exit_code = execute(raw_argv)
    sys.stdout.write(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())







