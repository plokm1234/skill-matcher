from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/titles")
def titles():
    return database.get_job_titles()


@app.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest):
    try:
        user_skills, user_track = database.get_title_skills(req.title)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    skills_dict = database.get_all_skills()
    categories = database.get_skill_categories()

    cleaned = extract_description_block(req.job_text)
    required = match_skills(cleaned, skills_dict)
    required_categories = [categories[s] for s in required if s in categories]

    result = compute_match(required, required_categories, user_skills, user_track)

    return ExtractResponse(
        match_pct=result.match_pct,
        matched=result.matched,
        gap=result.gap,
        same_track=result.same_track,
        suggestion=result.suggestion,
    )
