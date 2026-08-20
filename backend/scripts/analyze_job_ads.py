"""One-off analysis: how well does a broader, curated skill candidate list
cover a batch of real downloaded job ads, vs the currently seeded dictionary?

The methodology this demonstrates: don't hash-table every word out of
scraped job ads (too noisy — company names, benefits, generic text all
sweep in). Instead, curate a candidate list by domain knowledge, then let
REAL frequency data decide which candidates are actually worth keeping —
see the "X candidates had ZERO hits" line in the output.

Not part of the running app, and not wired into CI. Input CSV isn't
committed to this repo — job board content shouldn't be redistributed —
so point --csv at your own download (expects columns matching JobsDB's
export: at minimum a description column, adjust DESC_COLUMN below for
other sources).

Usage:
    python scripts/analyze_job_ads.py --csv /path/to/your/job_ads.csv
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.matching import match_skills  # noqa: E402

DESC_COLUMN = "工作詳細內容"  # JobsDB export column name — change for other sources

# The skills currently seeded in db/seed.sql, IT subset (name -> aliases).
# Keep this in sync manually if seed.sql's IT skills change — it's a
# snapshot for comparison, not read from the DB.
CURRENT_IT_SKILLS = {
    "Troubleshooting": [],
    "Windows/Networking Basics": ["windows", "networking"],
    "Ticketing System": [],
    "System Administration": ["sysadmin"],
    "Vendor Management": [],
    "Team Coordination": [],
    "ITIL": [],
    "IT Infrastructure Strategy": ["infrastructure"],
    "Budget/Vendor Contract": [],
    "Security Governance": [],
    "English": [], "Mandarin": ["普通話", "putonghua"], "Cantonese": ["廣東話", "canto"],
    "Linux": [], "Cybersecurity": ["cyber security", "information security"],
    "Windows Server": [], "SQL": ["mysql", "postgresql", "sql server"],
    "Azure": ["microsoft azure"],
}

# A broader candidate list — curated by domain knowledge (common languages,
# platforms, tools, certs), not scraped.
CANDIDATES = {
    "Python": [], "Java": [], "JavaScript": ["js"], "TypeScript": [],
    "C#": [], "C++": ["cpp"], "SQL": ["mysql", "postgresql", "sql server"],
    "PHP": [], "Go": ["golang"], "Kotlin": [], "Swift": [],
    "AWS": ["amazon web services"], "Azure": [], "GCP": ["google cloud"],
    "Docker": [], "Kubernetes": ["k8s"], "Linux": [], "Unix": [],
    "CI/CD": [], "Git": [], "Jenkins": [], "Terraform": [], "Ansible": [],
    "React": ["react.js", "reactjs"], "Node.js": ["nodejs"], "Angular": [],
    "Vue": ["vue.js"], ".NET": ["dotnet"], "Spring": [],
    "REST API": ["restful api"], "Microservices": [],
    "Cybersecurity": ["cyber security", "information security"],
    "Penetration Testing": ["pen testing", "pentest"],
    "CISSP": [], "CCNA": [], "CompTIA": [],
    "Machine Learning": ["ml"], "AI": ["artificial intelligence"],
    "Data Analysis": [], "Power BI": [], "Tableau": [],
    "Agile": [], "Scrum": [], "PMP": [], "Project Management": [],
    "Windows Server": [], "Active Directory": [],
    "Network Security": [], "Firewall": [],
    "VMware": [], "Virtualization": [],
    "Oracle": [], "MongoDB": [], "Redis": [],
    "ERP": [], "SAP": [], "CRM": [],
    "Business Analysis": [], "System Analysis": [],
    "Cloud Computing": [], "DevOps": [],
    "Mandarin": ["普通話", "putonghua"], "Cantonese": ["廣東話"],
    "English": [],
}


def load_descriptions(csv_path: str) -> list[str]:
    with open(csv_path, encoding="utf-8-sig") as f:
        return [row[DESC_COLUMN] for row in csv.DictReader(f)]


def report(title: str, skills: dict, descriptions: list[str]) -> None:
    n = len(descriptions)
    counts = {name: 0 for name in skills}
    for desc in descriptions:
        for skill in match_skills(desc, skills):
            counts[skill] += 1
    print(f"=== {title} ===")
    for name, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        if count:
            print(f"  {name:30s} {count:3d}/{n} ads ({count / n:.0%})")
    zero_hits = [name for name, c in counts.items() if c == 0]
    if zero_hits:
        print(f"\n  {len(zero_hits)} candidates had ZERO hits (not worth adding "
              f"from this data alone): {', '.join(zero_hits)}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, help="Path to your downloaded job ads CSV")
    args = parser.parse_args()

    descriptions = load_descriptions(args.csv)
    print(f"Loaded {len(descriptions)} job ads from {args.csv}\n")
    report("Currently seeded IT skills — real coverage", CURRENT_IT_SKILLS, descriptions)
    report("Broader candidate list — real frequency", CANDIDATES, descriptions)


if __name__ == "__main__":
    main()
