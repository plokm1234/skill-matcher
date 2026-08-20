import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get("DATABASE_URL")


@contextmanager
def get_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set — point it at your Neon Postgres "
            "instance (see README) after running db/schema.sql and db/seed.sql."
        )
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()


def get_all_skills() -> dict[str, list[str]]:
    """canonical skill name -> list of aliases, for match_skills()."""
    with get_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT s.name, array_agg(a.alias) FILTER (WHERE a.alias IS NOT NULL) AS aliases
            FROM skills s
            LEFT JOIN skill_aliases a ON a.skill_id = s.skill_id
            GROUP BY s.name
        """)
        return {row["name"]: row["aliases"] or [] for row in cur.fetchall()}


def get_skill_categories() -> dict[str, str]:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT name, category FROM skills")
        return dict(cur.fetchall())


def get_title_skills(title_name: str) -> tuple[list[str], str]:
    """Returns (skill names for this title, its track)."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT track FROM job_titles WHERE title_name = %s", (title_name,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"unknown job title: {title_name!r}")
        track = row[0]

        cur.execute(
            """
            SELECT s.name FROM job_title_skills jts
            JOIN skills s ON s.skill_id = jts.skill_id
            JOIN job_titles t ON t.title_id = jts.title_id
            WHERE t.title_name = %s
            """,
            (title_name,),
        )
        skills = [r[0] for r in cur.fetchall()]
        return skills, track


def get_job_titles() -> list[dict]:
    with get_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT title_name, track, level FROM job_titles ORDER BY track, level")
        return cur.fetchall()
