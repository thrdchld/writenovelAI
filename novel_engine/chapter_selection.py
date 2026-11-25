"""Utilities shared by the core engine and optional AI-agent adapters."""


def parse_chapter_numbers(raw, available):
    """Parse chapter numbers such as '1', '1-5', or '1-3,7'.

    Returns a sorted list, or None when the input is malformed or references
    chapters outside the supplied available set.
    """
    if not isinstance(raw, str) or not raw.strip():
        return None

    allowed = set(available)
    chosen = set()
    try:
        for part in raw.replace(" ", "").split(","):
            if not part:
                return None
            if "-" in part:
                if part.count("-") != 1:
                    return None
                left, right = part.split("-", 1)
                start, end = int(left), int(right)
                if start < 1 or end < 1 or start > end:
                    return None
                chosen.update(range(start, end + 1))
            else:
                number = int(part)
                if number < 1:
                    return None
                chosen.add(number)
    except (ValueError, TypeError):
        return None

    return sorted(chosen) if chosen and chosen.issubset(allowed) else None
