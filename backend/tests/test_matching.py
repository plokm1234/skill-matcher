from app.matching import extract_description_block, match_skills, split_core_and_nice

SKILLS = {
    "Java": [],
    "JavaScript": ["js"],
    "Python": [],
    "SQL": ["mysql", "postgresql"],
    "Machine Learning": [],
    "REST API": [],
    "Communication": [],
    "Troubleshooting": [],
    "Ticketing System": [],
    "Complaint Handling": [],
}


def test_word_boundary_avoids_java_javascript_false_positive():
    matched = match_skills("We need a JavaScript developer with React experience.", SKILLS)
    assert "JavaScript" in matched
    assert "Java" not in matched


def test_multiword_skill_matches_as_a_whole_phrase():
    matched = match_skills("Experience with machine learning and REST API design.", SKILLS)
    assert "Machine Learning" in matched
    assert "REST API" in matched


def test_alias_matches_canonical_skill():
    matched = match_skills("Comfortable writing PostgreSQL queries.", SKILLS)
    assert "SQL" in matched


def test_non_latin_alias_matches():
    # Added after the real-data analysis (backend/scripts/analyze_job_ads.py)
    # surfaced how common Chinese-language requirements are in real IT job
    # ads (English 70%, Mandarin 33%, Cantonese 28% of 60 real postings) —
    # aliases aren't just for alternate English spellings.
    skills = {"Cantonese": ["廣東話", "canto"], "Mandarin": ["普通話", "putonghua"]}
    matched = match_skills("流利廣東話及普通話,良好英語會話能力", skills)
    assert "Cantonese" in matched
    assert "Mandarin" in matched


def test_latin_term_matches_with_no_space_before_cjk_text():
    # Same root cause, other direction: an English term directly butted up
    # against Chinese text with no space ("linux同mysql,java開發") is
    # completely normal in bilingual HK job ads, but \b doesn't fire at a
    # Latin/CJK boundary either — "x" next to "同" looks like no boundary
    # at all to Python's \w-based \b.
    skills = {"Linux": [], "Java": [], "JavaScript": ["js"]}
    matched = match_skills("需要熟悉linux同javascript開發經驗", skills)
    assert "Linux" in matched
    assert "JavaScript" in matched
    assert "Java" not in matched  # still shouldn't match inside "javascript"


# Structural fixtures below mirror two distinct page-chrome patterns real
# job boards commonly use (Blueprint Sheet 02): a page of navigation /
# related-listing noise, a "job description" marker, the real content, then
# an end marker followed by more noise. All text — including the company
# and site names — is invented, not copied from any real posting or site.

NAV_HEAVY_PASTE = """
Sample Job Board
Company Profiles
Learning
Search location
Full-time  Part-time  Contract

Bright Harbour Elevator (HK) Limited
電梯助理技工 / 技工
Kwun Tong
4 - 9 yr(s)
14d ago

Northline Elevator Services Ltd
Registered Lift / Escalator Engineer
Kowloon Bay
6 - 11 yr(s)
14d ago

Jobs Description

Company Overview

Job Highlights

Responsibilities

Handle daily customer enquiries and resolve complaints in a timely manner

Log every request through our ticketing system

Requirements

Strong communication and troubleshooting skills

At least 2 years' experience in a customer-facing role

Apply Now

Similar Jobs

Harborview Recruitment
Customer Service Officer
1d ago

Alden Consultancy Limited
Engineer / Senior Engineer
9d ago

Job Seekers
Find Jobs
Browse Jobs
© Copyright 2026 Sample Job Board Limited. All rights reserved.
"""

FOOTER_HEAVY_PASTE = """
Skip to main content
Keyword: all jobs
customer service jobs in Hong Kong

Company A
Customer Service Assistant
Kwai Chung
Medical Insurance

Company B
IT Support Officer
Hong Kong
Paid time off

Return to Search Result

Full job description

Who We Are

We are a growing team looking for a hands-on Customer Service Assistant.

What You'll Do

Handle complaint handling and troubleshooting for incoming support tickets
Maintain clear communication with customers via our ticketing system

Application Process

Job Type: Full-time
Return to Search Result

Career advice
Browse jobs
© 2026 Sample Job Search
"""


def test_extract_description_block_strips_nav_heavy_noise():
    result = extract_description_block(NAV_HEAVY_PASTE)
    matched = match_skills(result, SKILLS)
    assert "Communication" in matched
    assert "Troubleshooting" in matched
    # related-listing company names should not leak into the extracted block
    assert "Northline Elevator" not in result
    assert "Similar Jobs" not in result


def test_extract_description_block_strips_footer_heavy_noise():
    result = extract_description_block(FOOTER_HEAVY_PASTE)
    matched = match_skills(result, SKILLS)
    assert "Complaint Handling" in matched
    assert "Ticketing System" in matched
    assert "Medical Insurance" not in result


def test_extract_description_block_falls_back_to_full_text_without_marker():
    raw = "Looking for a Python developer with SQL experience."
    assert extract_description_block(raw) == raw


def test_split_core_and_nice_separates_on_nice_to_have_marker():
    core, nice = split_core_and_nice(
        "Requires Python and SQL. Nice to have: Docker and AWS experience."
    )
    assert match_skills(core, SKILLS) == ["Python", "SQL"]
    assert match_skills(nice, SKILLS) == []  # Docker/AWS aren't in the SKILLS fixture
    assert "Python" not in nice
    assert "SQL" not in nice


def test_split_core_and_nice_recognises_preferred_and_bonus_variants():
    for marker in ["Preferred:", "Bonus:", "Advantageous:", "Nice to have:"]:
        core, nice = split_core_and_nice(f"Must know Python. {marker} Java experience.")
        assert match_skills(core, SKILLS) == ["Python"]
        assert match_skills(nice, SKILLS) == ["Java"]


def test_split_core_and_nice_requires_a_colon_to_avoid_false_positives():
    # These words show up constantly in ordinary prose that has nothing to
    # do with a "nice to have" section — without requiring a trailing
    # colon, "plus" here would wrongly split the ad and dump the genuine
    # Requirements section (mentioning SQL) into the nice-to-have bucket,
    # silently downgrading a real core skill.
    core, nice = split_core_and_nice(
        "Salary: HK$20,000 plus year-end bonus. "
        "Requirements: Strong Python and SQL skills required."
    )
    assert match_skills(core, SKILLS) == ["Python", "SQL"]
    assert nice == ""


def test_split_core_and_nice_treats_whole_text_as_core_without_a_marker():
    core, nice = split_core_and_nice("Looking for a Python developer with SQL experience.")
    assert set(match_skills(core, SKILLS)) == {"Python", "SQL"}
    assert nice == ""
