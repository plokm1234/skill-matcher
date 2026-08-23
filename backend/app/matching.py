import re

# Section-header phrases that mark where the real job description starts,
# validated against two independently-styled real postings — see Skill
# Matcher Blueprint Sheet 02.
_START_MARKER = re.compile(r"jobs?\s*description", re.IGNORECASE)

# Markers that reliably follow the description block on job boards.
_END_MARKERS = [
    "apply now",
    "similar jobs",
    "return to search result",
    "report job",
]


def extract_description_block(raw_text: str) -> str:
    """Trim page chrome (nav, related-jobs widgets, footers) from a raw
    copy-pasted job board page down to the actual description block.

    Anchors on the phrase "job description" (matches "Jobs Description",
    "Full job description", etc.) as the start, and the first known
    end-of-content marker after that as the end. Falls back to the full
    text when no start marker is found — some sites may not use this
    exact phrasing, and a full-text fallback is safer than guessing.
    """
    start_match = _START_MARKER.search(raw_text)
    start = start_match.end() if start_match else 0

    lower = raw_text.lower()
    end_candidates = [
        lower.find(marker, start)
        for marker in _END_MARKERS
        if lower.find(marker, start) > start
    ]
    end = min(end_candidates) if end_candidates else len(raw_text)

    return raw_text[start:end].strip()


def match_skills(text: str, skills: dict[str, list[str]]) -> list[str]:
    """Find which skills are mentioned in `text`.

    Walks the skill dictionary outward into the text (not the reverse),
    using a boundary-aware regex per skill/alias — this is what lets a
    multi-word skill like "machine learning" match as a whole phrase
    without any tokenization or n-gram bookkeeping. See Blueprint Sheet 04
    for why this direction was chosen over token-first hashing.

    Uses lookaround assertions instead of \\b. Python's \\b treats every
    Han character as a \\w character, so it never fires inside a run of
    Chinese text OR between a Latin term and adjacent Chinese text —
    "話" next to "及" in "廣東話及普通話" has no boundary, and neither
    does "x" next to "同" in "linux同mysql" (a completely ordinary way to
    write it in a bilingual HK job ad, no space needed). The lookarounds
    below only care whether a LATIN letter/digit is directly adjacent —
    which still blocks "java" from matching inside "javascript" (adjacent
    "s" is a Latin letter) — while treating any CJK-adjacent position as
    a valid boundary either way.

    `skills` maps a canonical skill name to its list of aliases
    (the canonical name itself does not need to be repeated in the list).
    """
    lowered = text.lower()
    matched = []
    for canonical, aliases in skills.items():
        candidates = [canonical, *aliases]
        for term in candidates:
            pattern = r"(?<![A-Za-z0-9])" + re.escape(term.lower()) + r"(?![A-Za-z0-9])"
            if re.search(pattern, lowered):
                matched.append(canonical)
                break
    return matched
