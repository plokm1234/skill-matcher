import pytest

from app.suggestion import compute_match

# job_core/job_nice here stand in for a pasted JOB AD's own Requirements
# vs Nice-to-have sections (what matching.split_core_and_nice would
# extract from real text) — "core" is a property of the job ad itself,
# not derived from any title. user_skills is a title's full skill set
# (core + nice-to-have combined, from db/seed.sql's job_title_skills).

CLERK_SKILLS = ["MS Office", "Data Entry", "Filing", "Basic Bookkeeping"]
CS_ASSISTANT_SKILLS = ["Communication", "Complaint Handling", "CRM System"]
IT_SUPPORT_CORE = ["Troubleshooting", "Windows/Networking Basics"]
IT_SUPPORT_NICE = ["Ticketing System"]
IT_SUPPORT_SKILLS = IT_SUPPORT_CORE + IT_SUPPORT_NICE

CASES = [
    # (job_core, job_nice, categories, user_skills, user_track, expected_same_track, min_pct, max_pct)
    (
        ["Python", "Git", "Data Structures"],
        [],
        ["Software Dev", "Software Dev", "Software Dev"],
        CLERK_SKILLS,
        "文員",
        False,
        0,
        49.9,
    ),
    (
        ["Communication", "Complaint Handling"],
        ["Troubleshooting", "Ticketing System"],
        ["客戶服務", "客戶服務", "IT", "IT"],
        CS_ASSISTANT_SKILLS,
        "客戶服務",
        False,
        50,
        100,
    ),
    (
        IT_SUPPORT_CORE,
        IT_SUPPORT_NICE,
        ["IT", "IT", "IT"],
        IT_SUPPORT_SKILLS,
        "IT",
        True,
        80,
        100,
    ),
    (
        ["Data Entry", "Filing", "Team Supervision", "Vendor Coordination"],
        [],
        ["文員", "文員", "文員", "文員"],
        CLERK_SKILLS,
        "文員",
        True,
        50,
        79.9,
    ),
    (
        ["Department Budget Management", "Policy Development", "Cross-dept Coordination"],
        [],
        ["文員", "文員", "文員"],
        CLERK_SKILLS,
        "文員",
        True,
        0,
        49.9,
    ),
]


@pytest.mark.parametrize(
    "job_core,job_nice,categories,user_skills,user_track,expected_same_track,min_pct,max_pct",
    CASES,
)
def test_covers_all_five_suggestion_branches(
    job_core, job_nice, categories, user_skills, user_track, expected_same_track, min_pct, max_pct
):
    result = compute_match(job_core, job_nice, categories, user_skills, user_track)
    assert result.same_track == expected_same_track
    assert min_pct <= result.match_pct <= max_pct
    assert result.suggestion  # every branch produces non-empty text


def test_all_of_the_jobs_core_requirements_matched_clears_the_apply_threshold():
    # A job ad whose Requirements section is fully covered clears the
    # ">= 80 → 可以申請" bar even when its Nice-to-have section is not —
    # missing a candidate is missing a bonus, not a requirement.
    result = compute_match(
        IT_SUPPORT_CORE,
        IT_SUPPORT_NICE,
        ["IT", "IT"],
        IT_SUPPORT_CORE,  # doesn't have the nice-to-have skill
        "IT",
    )
    assert result.match_pct >= 80


def test_nice_to_have_alone_cannot_paper_over_a_missing_core_skill_set():
    # A job ad whose Requirements section matched nothing at all (empty
    # job_core — e.g. the ad's actual requirements didn't hit our skill
    # dictionary) must stay well under the "可以申請" bar even if the
    # candidate happens to have everything in its Nice-to-have section.
    result = compute_match(
        [],
        IT_SUPPORT_NICE,
        ["IT"],
        IT_SUPPORT_SKILLS,
        "IT",
    )
    assert result.match_pct < 50


def test_nothing_detected_scores_zero_not_a_false_positive_average():
    result = compute_match([], [], [], CLERK_SKILLS, "文員")
    assert result.match_pct == 0.0
    assert result.matched == []
    assert result.gap == []


def test_cross_track_low_score_is_framed_as_career_change_not_dismissed():
    result = compute_match(
        ["Python", "Git"], [], ["Software Dev", "Software Dev"], CLERK_SKILLS, "文員"
    )
    assert "轉行" in result.suggestion or "career change" in result.suggestion


@pytest.mark.parametrize("order", [
    ["IT", "IT", "客戶服務", "客戶服務"],
    ["客戶服務", "客戶服務", "IT", "IT"],
    ["IT", "客戶服務", "IT", "客戶服務"],
    ["客戶服務", "IT", "客戶服務", "IT"],
])
def test_exact_category_tie_is_cross_track_regardless_of_list_order(order):
    # A 50/50 split between the user's own track and another category is a
    # tie by count — same_track must resolve to False no matter what order
    # the categories arrive in (Postgres's GROUP BY gives no order guarantee).
    result = compute_match(
        ["Troubleshooting", "Ticketing System"],
        ["Communication", "Complaint Handling"],
        order,
        CS_ASSISTANT_SKILLS,
        "客戶服務",
    )
    assert result.same_track is False
