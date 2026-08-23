from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import database
from .matching import extract_description_block, match_skills, split_core_and_nice
from .models import ExtractRequest, ExtractResponse
from .suggestion import compute_match

app = FastAPI(title="Skill Matcher")

app.add_middleware(
    CORSMiddleware,
    # GitHub Pages origin — see Blueprint Sheet 03 for why this boundary
    # exists (frontend and API are on different origins by design).
    allow_origins=[
        "https://plokm1234.github.io",
        "http://localhost:5173",  # local frontend dev
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class RequiredSkillsRequest(BaseModel):
    job_text: str


def _job_core_and_nice_skills(job_text: str, skills_dict: dict[str, list[str]]) -> tuple[list[str], list[str]]:
    """The pasted job ad's OWN core (required) vs nice-to-have skills —
    split from how the ad itself is written (matching.split_core_and_nice),
    not derived from any selected title. Shared by /required-skills and
    /extract so both use the exact same classification."""
    cleaned = extract_description_block(job_text)
    core_text, nice_text = split_core_and_nice(cleaned)
    core_skills = match_skills(core_text, skills_dict)
    nice_skills = match_skills(nice_text, skills_dict) if nice_text else []
    nice_skills = [s for s in nice_skills if s not in core_skills]
    return core_skills, nice_skills


@app.get("/titles")
def titles():
    return database.get_job_titles()


@app.get("/title-skills")
def title_skills(title: str):
    """Skills implied by a job title — shown under the Title row so the
    user sees what they're being compared with before hitting Extract.
    Query param (not a path param) because title_name can contain '/'
    (e.g. '行政主任/主管'). Core and nice-to-have are split here — the
    front end labels each one explicitly (and uses the same split to tag
    whichever of the pasted job ad's required skills fall into this
    title's own skill set)."""
    try:
        core_skills, nice_skills, track = database.get_title_skills(title)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"core_skills": core_skills, "nice_skills": nice_skills, "track": track}


@app.post("/required-skills")
def required_skills(req: RequiredSkillsRequest):
    """The pasted job ad's own core (required) vs nice-to-have skills,
    independent of any title — shown under Job Description so both sides
    are visible before Extract."""
    skills_dict = database.get_all_skills()
    core_skills, nice_skills = _job_core_and_nice_skills(req.job_text, skills_dict)
    return {"core_skills": core_skills, "nice_skills": nice_skills}


@app.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest):
    try:
        title_core_skills, title_nice_skills, user_track = database.get_title_skills(req.title)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    skills_dict = database.get_all_skills()
    categories = database.get_skill_categories()

    job_core_skills, job_nice_skills = _job_core_and_nice_skills(req.job_text, skills_dict)
    required = job_core_skills + job_nice_skills
    required_categories = [categories[s] for s in required if s in categories]

    user_skills = title_core_skills + title_nice_skills
    result = compute_match(job_core_skills, job_nice_skills, required_categories, user_skills, user_track)

    return ExtractResponse(
        match_pct=result.match_pct,
        matched=result.matched,
        gap=result.gap,
        same_track=result.same_track,
        suggestion=result.suggestion,
    )
