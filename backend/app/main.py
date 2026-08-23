from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import database
from .matching import extract_description_block, match_skills
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
    """Skills detected in a job description, independent of any title —
    shown under Job Description so both sides are visible before Extract."""
    skills_dict = database.get_all_skills()
    cleaned = extract_description_block(req.job_text)
    return {"skills": match_skills(cleaned, skills_dict)}


@app.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest):
    try:
        core_skills, nice_skills, user_track = database.get_title_skills(req.title)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    skills_dict = database.get_all_skills()
    categories = database.get_skill_categories()

    cleaned = extract_description_block(req.job_text)
    required = match_skills(cleaned, skills_dict)
    required_categories = [categories[s] for s in required if s in categories]

    result = compute_match(required, required_categories, core_skills, nice_skills, user_track)

    return ExtractResponse(
        match_pct=result.match_pct,
        matched=result.matched,
        gap=result.gap,
        same_track=result.same_track,
        suggestion=result.suggestion,
    )
