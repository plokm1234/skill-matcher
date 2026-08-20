from dataclasses import dataclass


@dataclass
class MatchResult:
    match_pct: float
    matched: list[str]
    gap: list[str]
    same_track: bool
    suggestion: str


def dominant_category(skill_categories: list[str]) -> str | None:
    """Return the most common category among a list of skill categories.

    Mirrors the SQL GROUP BY / ORDER BY / LIMIT 1 query in Blueprint
    Sheet 05 — used here for the in-process version; the same query
    can run directly against Postgres once job ads are persisted.
    """
    if not skill_categories:
        return None
    counts: dict[str, int] = {}
    for category in skill_categories:
        counts[category] = counts.get(category, 0) + 1
    return max(counts, key=counts.get)


def build_suggestion(match_pct: float, same_track: bool) -> str:
    """Rule-based verdict — deterministic, no AI, no learning-resource
    lookup. See Blueprint Sheet 02 for the decision table and the
    reasoning for splitting on track before splitting on score.
    """
    if not same_track:
        if match_pct < 50:
            return (
                "呢個屬於轉行(career change),"
                "預期需要大量時間學習新skill先追得上"
            )
        return "雖然唔同track,但你已有一定transferable skill,轉行門檻相對低"

    if match_pct >= 80:
        return "核心skill已match,值得申請"
    if match_pct >= 50:
        return "核心skill已match,補底缺少嗰幾個會更有把握"
    return "缺口較大,建議先加強缺少嘅核心skill"


def compute_match(
    required_skills: list[str],
    required_categories: list[str],
    user_skills: list[str],
    user_track: str,
) -> MatchResult:
    required_set = set(required_skills)
    user_set = set(user_skills)

    matched = sorted(required_set & user_set)
    gap = sorted(required_set - user_set)

    match_pct = round(len(matched) / len(required_set) * 100, 1) if required_set else 0.0
    same_track = dominant_category(required_categories) == user_track

    suggestion = build_suggestion(match_pct, same_track)

    return MatchResult(
        match_pct=match_pct,
        matched=matched,
        gap=gap,
        same_track=same_track,
        suggestion=suggestion,
    )
