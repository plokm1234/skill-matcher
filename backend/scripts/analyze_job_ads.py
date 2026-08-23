"""One-off analysis: how well does a broader, curated skill candidate list
cover a batch of real downloaded job ads, vs the currently seeded dictionary?

The methodology this demonstrates: don't hash-table every word out of
scraped job ads (too noisy — company names, benefits, generic text all
sweep in). Instead, curate a candidate list by domain knowledge, then let
REAL frequency data decide which candidates are actually worth keeping —
see the "X candidates had ZERO hits" line in the output.

Not part of the running app, and not wired into CI. Input data isn't
committed to this repo — job board content shouldn't be redistributed —
so point --csv or --sqlite at your own download.

CSV mode expects at minimum a description column (adjust DESC_COLUMN below
to match your export's column name). SQLite mode expects a table/view with
a description column and, optionally, a category column to split ads by
domain (adjust DESC_COLUMN/CATEGORY_COLUMN below to match your schema).

Usage:
    python scripts/analyze_job_ads.py --csv /path/to/your/job_ads.csv
    python scripts/analyze_job_ads.py --sqlite /path/to/your/job_ads.db \
        --table jobs_latest --category information_communication_technology
"""
import argparse
import csv
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.matching import match_skills  # noqa: E402

DESC_COLUMN = "工作詳細內容"  # CSV column name in the source export — change to match yours
SQLITE_DESC_COLUMN = "job_detail"  # SQLite column name — change to match yours
SQLITE_CATEGORY_COLUMN = "category"  # SQLite column name — change to match yours, or None

# The skills currently seeded in db/seed.sql (name -> aliases). Keep this in
# sync manually if seed.sql's skills change — it's a snapshot for
# comparison, not read from the DB.
CURRENT_SKILLS = {
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
    "MS Office": ["microsoft office"], "Data Entry": [], "Filing": [],
    "Basic Bookkeeping": ["bookkeeping"], "Team Supervision": [],
    "Vendor Coordination": [], "Budget Tracking": [], "Process Improvement": [],
    "Department Budget Management": [], "Policy Development": [],
    "Cross-dept Coordination": [],
    "Communication": [], "CRM System": ["crm"], "Complaint Handling": [],
    "Team Leadership": [], "SLA Management": [], "Escalation Handling": [],
    "Training": [], "Customer Experience Strategy": [],
    "KPI/Budget Management": [], "Stakeholder Management": [],
}

# Broader candidate lists — curated by domain knowledge (common languages,
# platforms, tools, certs), not scraped. Split by the domain each is most
# likely to show up in, so each gets checked against the matching category's
# real ads rather than diluting one combined report.
CANDIDATES_IT = {
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
    "Help Desk": ["helpdesk"], "Hardware Support": [],
    "Software Installation": [],
}

CANDIDATES_ADMIN = {
    "Excel": ["ms excel", "microsoft excel"],
    "PowerPoint": ["ms powerpoint"],
    "Word": ["ms word", "microsoft word"],
    "Outlook": ["ms outlook"],
    "Scheduling": ["diary management", "calendar management"],
    "Minute Taking": ["taking minutes"],
    "Correspondence": [],
    "Record Keeping": ["record-keeping"],
    "Invoicing": [],
    "Procurement": [],
    "Office Administration": ["office admin"],
    "Reception Duties": ["receptionist"],
    "Travel Arrangement": ["travel arrangements"],
    "Document Management": [],
    "Data Management": [],
    "Payroll": [],
    "Human Resources": ["hr"],
    "Recruitment": [],
    "Onboarding": [],
    "Compliance": [],
    "Report Writing": ["reporting"],
    "Multitasking": [],
    "Time Management": [],
    "Attention to Detail": [],
    "Organizational Skills": ["organisational skills"],
    "Chinese Typing": [],
    "English Typing": [],
}

CANDIDATES_CUSTOMER_SERVICE = {
    "Customer Service": [],
    "Call Handling": ["handling calls", "inbound calls", "outbound calls"],
    "Telephone Etiquette": ["phone etiquette"],
    "Live Chat Support": ["live chat"],
    "Email Support": [],
    "Order Processing": [],
    "Upselling": [],
    "Cross-selling": ["cross selling"],
    "Customer Retention": [],
    "Conflict Resolution": [],
    "Problem Solving": [],
    "Product Knowledge": [],
    "Data Entry": [],
    "Multitasking": [],
    "Active Listening": [],
    "Empathy": [],
    "Cantonese": ["廣東話"],
    "Mandarin": ["普通話", "putonghua"],
    "English": [],
}


def load_csv_descriptions(csv_path: str) -> list[str]:
    with open(csv_path, encoding="utf-8-sig") as f:
        return [row[DESC_COLUMN] for row in csv.DictReader(f)]


def load_sqlite_descriptions(db_path: str, table: str, category: str | None) -> list[str]:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        if category and SQLITE_CATEGORY_COLUMN:
            cur.execute(
                f"SELECT {SQLITE_DESC_COLUMN} FROM {table} "
                f"WHERE {SQLITE_CATEGORY_COLUMN} = ? AND {SQLITE_DESC_COLUMN} IS NOT NULL",
                (category,),
            )
        else:
            cur.execute(
                f"SELECT {SQLITE_DESC_COLUMN} FROM {table} WHERE {SQLITE_DESC_COLUMN} IS NOT NULL"
            )
        return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()


def report(title: str, skills: dict, descriptions: list[str]) -> None:
    n = len(descriptions)
    counts = {name: 0 for name in skills}
    for desc in descriptions:
        for skill in match_skills(desc, skills):
            counts[skill] += 1
    print(f"=== {title} ({n} ads) ===")
    for name, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        if count:
            print(f"  {name:30s} {count:4d}/{n} ads ({count / n:.0%})")
    zero_hits = [name for name, c in counts.items() if c == 0]
    if zero_hits:
        print(f"\n  {len(zero_hits)} candidates had ZERO hits (not worth adding "
              f"from this data alone): {', '.join(zero_hits)}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", help="Path to your downloaded job ads CSV")
    parser.add_argument("--sqlite", help="Path to your downloaded job ads SQLite DB")
    parser.add_argument("--table", default="jobs_latest", help="SQLite table/view name (default: jobs_latest)")
    parser.add_argument("--category", help="SQLite category value to filter to a single domain")
    args = parser.parse_args()

    if args.csv:
        descriptions = load_csv_descriptions(args.csv)
        print(f"Loaded {len(descriptions)} job ads from {args.csv}\n")
        report("Currently seeded skills — real coverage", CURRENT_SKILLS, descriptions)
        report("Broader IT candidate list — real frequency", CANDIDATES_IT, descriptions)
    elif args.sqlite:
        descriptions = load_sqlite_descriptions(args.sqlite, args.table, args.category)
        label = args.category or "all categories"
        print(f"Loaded {len(descriptions)} job ads from {args.sqlite} ({label})\n")
        report(f"Currently seeded skills — real coverage ({label})", CURRENT_SKILLS, descriptions)
        report(f"IT candidate list — real frequency ({label})", CANDIDATES_IT, descriptions)
        report(f"Admin/office candidate list — real frequency ({label})", CANDIDATES_ADMIN, descriptions)
        report(f"Customer-service candidate list — real frequency ({label})", CANDIDATES_CUSTOMER_SERVICE, descriptions)
    else:
        parser.error("one of --csv or --sqlite is required")


if __name__ == "__main__":
    main()
