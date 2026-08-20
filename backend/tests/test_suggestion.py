import pytest

from app.suggestion import compute_match

# The 5 self-authored demo job ads from Blueprint Sheet 02 — one per
# suggestion branch. Kept here as the shared fixture for both the demo
# "try example" buttons on the front end and this regression suite.

CLERK_SKILLS = ["MS Office", "Data Entry", "Filing", "Basic Bookkeeping"]
CS_ASSISTANT_SKILLS = ["Communication", "CRM System", "Complaint Handling"]
IT_SUPPORT_SKILLS = ["Troubleshooting", "Windows/Networking Basics", "Ticketing System"]

CASES = [
    # (required_skills, required_categories, user_skills, user_track, expected_same_track, min_pct, max_pct)
    (
        ["Python", "Git", "Data Structures"],
        ["Software Dev", "Software Dev", "Software Dev"],
        CLERK_SKILLS,
        "文員",
        False,
        0,
        49.9,
    ),
    (
        ["Troubleshooting", "Ticketing System", "Communication", "Complaint Handling"],
        ["IT", "IT", "客戶服務", "客戶服務"],
        CS_ASSISTANT_SKILLS,
        "客戶服務",
        False,
        50,
        100,
    ),
    (
        ["Troubleshooting", "Windows/Networking Basics", "Ticketing System"],
        ["IT", "IT", "IT"],
        IT_SUPPORT_SKILLS,
        "IT",
        True,
        80,
        100,
    ),
    (
        ["Data Entry", "Filing", "Team Supervision", "Vendor Coordination"],
        ["文員", "文員", "文員", "文員"],
        CLERK_SKILLS,
        "文員",
        True,
        50,
        79.9,
    ),
    (
        ["Department Budget Management", "Policy Development", "Cross-dept Coordination"],
        ["文員", "文員", "文員"],
        CLERK_SKILLS,
        "文員",
        True,
        0,
        49.9,
    ),
]


@pytest.mark.parametrize(
    "required,categories,user_skills,user_track,expected_same_track,min_pct,max_pct",
    CASES,
)
def test_covers_all_five_suggestion_branches(
    required, categories, user_skills, user_track, expected_same_track, min_pct, max_pct
):
    result = compute_match(required, categories, user_skills, user_track)
    assert result.same_track == expected_same_track
    assert min_pct <= result.match_pct <= max_pct
    assert result.suggestion  # every branch produces non-empty text


def test_cross_track_low_score_is_framed_as_career_change_not_dismissed():
    result = compute_match(
        ["Python", "Git"], ["Software Dev", "Software Dev"], CLERK_SKILLS, "文員"
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
        ["Troubleshooting", "Ticketing System", "Communication", "Complaint Handling"],
        order,
        CS_ASSISTANT_SKILLS,
        "客戶服務",
    )
    assert result.same_track is False
