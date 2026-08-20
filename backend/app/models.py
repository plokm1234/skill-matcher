from pydantic import BaseModel


class ExtractRequest(BaseModel):
    title: str
    job_text: str


class ExtractResponse(BaseModel):
    match_pct: float
    matched: list[str]
    gap: list[str]
    same_track: bool
    suggestion: str
