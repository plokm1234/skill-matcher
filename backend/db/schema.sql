-- Skill Matcher V1 schema — see Blueprint Sheet 05 for the design rationale
-- (junction tables for the two many-to-many relationships, category column
-- used for the cross-track suggestion logic in Sheet 02).

CREATE TABLE skills (
    skill_id   SERIAL PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE,
    category   TEXT NOT NULL          -- e.g. 'Software Dev', 'Admin', 'Customer Service', 'IT'
);

CREATE TABLE skill_aliases (
    alias_id   SERIAL PRIMARY KEY,
    skill_id   INTEGER NOT NULL REFERENCES skills(skill_id),
    alias      TEXT NOT NULL
);
CREATE INDEX idx_skill_aliases_alias ON skill_aliases (alias);

CREATE TABLE job_ads (
    job_id      SERIAL PRIMARY KEY,
    title       TEXT,
    description TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE job_ad_skills (             -- junction: job_ads <-> skills
    job_id   INTEGER REFERENCES job_ads(job_id),
    skill_id INTEGER REFERENCES skills(skill_id),
    PRIMARY KEY (job_id, skill_id)
);

CREATE TABLE job_titles (
    title_id   SERIAL PRIMARY KEY,
    title_name TEXT UNIQUE NOT NULL,     -- shown on the front-end button row
    track      TEXT NOT NULL,            -- '文員' / '客戶服務' / 'IT'
    level      TEXT NOT NULL             -- 'Junior' / 'Mid' / 'Senior'
);

CREATE TABLE job_title_skills (          -- junction: job_titles <-> skills
    title_id INTEGER REFERENCES job_titles(title_id),
    skill_id INTEGER REFERENCES skills(skill_id),
    PRIMARY KEY (title_id, skill_id)
);

CREATE VIEW skill_demand_summary AS
    SELECT s.name, s.category, COUNT(*) AS demand_count
    FROM job_ad_skills js
    JOIN skills s ON js.skill_id = s.skill_id
    GROUP BY s.name, s.category;
