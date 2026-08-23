from dataclasses import dataclass


@dataclass
class MatchResult:
    match_pct: float
    matched: list[str]
    gap: list[str]
    same_track: bool
    suggestion: str


def is_same_track(required_categories: list[str], user_track: str) -> bool:
    """Whether the job ad's required skills belong mainly to the user's
    selected track.

    Deliberately a STRICT MAJORITY check, not "most common category" —
    every matched skill is, by construction, tagged with user_track's own
    category (it came from the user's own skill set), so once match% >=
    50%, user_track can at best TIE for most-common; it can never be
    outnumbered. A plurality/max() rule therefore only ever resolves
    the interesting "cross-track but decent overlap" case as a tie, and
    Postgres's GROUP BY without ORDER BY doesn't guarantee which side of
    a tie you get — this surfaced as a real bug against the live DB (see
    Blueprint Sheet 07 / project history) even though fixed-order unit
    test fixtures happened to mask it. Requiring a strict majority makes
    a tie resolve to cross-track deterministically, independent of query
    result ordering.
    """
    if not required_categories:
        return True
    track_count = required_categories.count(user_track)
    return track_count > len(required_categories) / 2


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
        return "你已有一定transferable skill,轉行門檻相對低"

    if match_pct >= 80:
        return "核心skill已match,可以申請"
    if match_pct >= 50:
        return "核心skill已match,補底缺少嗰幾個會更有把握"
    return "缺口較大,建議先加強缺少嘅核心skill"


# How much core-skill coverage vs nice-to-have coverage counts toward
# match_pct. Chosen so the two boundary cases line up exactly with
# build_suggestion's existing thresholds: 100% core coverage alone lands at
# CORE_WEIGHT*100 = 80, which is exactly the ">= 80 → 可以申請" cutoff — a
# candidate who has every core skill for the role should clear that bar
# regardless of how many nice-to-haves they're missing. 100% nice-to-have
# coverage alone (no core skills at all) lands at NICE_WEIGHT*100 = 20,
# staying well under the "缺口較大" (< 50) cutoff — nice-to-haves can't
# paper over a missing core skill set.
CORE_WEIGHT = 0.8
NICE_WEIGHT = 0.2


def compute_match(
    required_skills: list[str],
    required_categories: list[str],
    core_skills: list[str],
    nice_skills: list[str],
    user_track: str,
) -> MatchResult:
    required_set = set(required_skills)
    core_set = set(core_skills)
    nice_set = set(nice_skills)
    user_set = core_set | nice_set

    matched = sorted(required_set & user_set)
    gap = sorted(required_set - user_set)

    # Coverage is "of the skills this title actually calls for at this
    # tier, how many does the job ad also ask for" — not the reverse — so
    # an empty tier (no core skills defined, or none of the nice-to-haves
    # apply) counts as fully covered rather than dividing by zero.
    core_coverage = len(core_set & required_set) / len(core_set) if core_set else 1.0
    nice_coverage = len(nice_set & required_set) / len(nice_set) if nice_set else 1.0

    match_pct = round((core_coverage * CORE_WEIGHT + nice_coverage * NICE_WEIGHT) * 100, 1)
    same_track = is_same_track(required_categories, user_track)

    suggestion = build_suggestion(match_pct, same_track)

    return MatchResult(
        match_pct=match_pct,
        matched=matched,
        gap=gap,
        same_track=same_track,
        suggestion=suggestion,
    )
