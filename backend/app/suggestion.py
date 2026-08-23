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


# How much coverage of the job ad's OWN core requirements vs its OWN
# nice-to-haves counts toward match_pct. Chosen so covering 100% of a
# job's core requirements clears the ">= 80 → 可以申請" cutoff on its
# own — CORE_WEIGHT*100 = 80 — regardless of how many of its nice-to-haves
# are missing (that lands exactly at 80 when the job also lists a
# nice-to-have section the candidate doesn't meet; it lands higher, up to
# 100, when the job has no nice-to-have section at all — see the
# core-coverage-empty note below for why that's not double counted the
# other way). Covering 100% of a job's nice-to-haves with NONE of its
# actual core requirements stays at NICE_WEIGHT*100 = 20, well under the
# "缺口較大" (< 50) cutoff — nice-to-haves can't paper over what a job
# actually asks for.
CORE_WEIGHT = 0.8
NICE_WEIGHT = 0.2


def compute_match(
    job_core_skills: list[str],
    job_nice_skills: list[str],
    required_categories: list[str],
    user_skills: list[str],
    user_track: str,
) -> MatchResult:
    """job_core_skills/job_nice_skills are the PASTED JOB AD's own
    requirements vs nice-to-haves (split from how the ad itself is
    written — see matching.split_core_and_nice), not derived from
    user_skills. "Core" is a property of the job ad, not of whichever
    title happens to be selected — comparing core-to-core suitability is
    the whole point of the split.
    """
    job_core_set = set(job_core_skills)
    job_nice_set = set(job_nice_skills)
    required_set = job_core_set | job_nice_set
    user_set = set(user_skills)

    matched = sorted(required_set & user_set)
    gap = sorted(required_set - user_set)

    if not required_set:
        # Nothing recognisable was detected anywhere in the pasted text —
        # there's no basis to claim any coverage at all.
        return MatchResult(match_pct=0.0, matched=[], gap=[], same_track=True, suggestion=build_suggestion(0.0, True))

    # core_coverage empty→0 (NOT 1): unlike the job's nice-to-have section,
    # which most real ads simply don't have (empty there is the norm, and
    # shouldn't count against a candidate — see nice_coverage below), an
    # empty CORE means nothing was recognisable as a stated requirement,
    # which is either a very sparse ad or a section-split gone wrong —
    # either way, not evidence of a good match, so it must not default to
    # "fully covered". nice_coverage empty→1 stays as-is: no nice-to-have
    # section is the common case and shouldn't be held against anyone.
    core_coverage = len(job_core_set & user_set) / len(job_core_set) if job_core_set else 0.0
    nice_coverage = len(job_nice_set & user_set) / len(job_nice_set) if job_nice_set else 1.0

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
