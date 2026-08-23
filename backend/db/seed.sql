-- Starter data for the 5 titles shown as buttons on the front end
-- (see Blueprint Sheet 01 — the other 4 rungs of the 3x3 ladder are left
-- here for a future V2 that surfaces more of the ladder on the front end).

INSERT INTO skills (name, category) VALUES
    ('MS Office', '文員'),
    ('Data Entry', '文員'),
    ('Filing', '文員'),
    ('Basic Bookkeeping', '文員'),
    ('Team Supervision', '文員'),
    ('Vendor Coordination', '文員'),
    ('Budget Tracking', '文員'),
    ('Process Improvement', '文員'),
    ('Department Budget Management', '文員'),
    ('Policy Development', '文員'),
    ('Cross-dept Coordination', '文員'),

    ('Communication', '客戶服務'),
    ('CRM System', '客戶服務'),
    ('Complaint Handling', '客戶服務'),
    ('Team Leadership', '客戶服務'),
    ('SLA Management', '客戶服務'),
    ('Escalation Handling', '客戶服務'),
    ('Training', '客戶服務'),
    ('Customer Experience Strategy', '客戶服務'),
    ('KPI/Budget Management', '客戶服務'),
    ('Stakeholder Management', '客戶服務'),

    ('Troubleshooting', 'IT'),
    ('Windows/Networking Basics', 'IT'),
    ('Ticketing System', 'IT'),
    ('System Administration', 'IT'),
    ('Vendor Management', 'IT'),
    ('Team Coordination', 'IT'),
    ('ITIL', 'IT'),
    ('IT Infrastructure Strategy', 'IT'),
    ('Budget/Vendor Contract', 'IT'),
    ('Security Governance', 'IT'),

    ('Python', 'Software Dev'),
    ('Git', 'Software Dev'),
    ('Data Structures', 'Software Dev'),
    ('Algorithms', 'Software Dev'),

    -- Added from real-data analysis: 60 real IT job ads (2 pages) from a
    -- job board, a curated ~60-term candidate list checked against actual
    -- frequency, keeping only what genuinely appeared. See
    -- backend/scripts/analyze_job_ads.py.
    -- Tagged 'IT' because the source dataset is IT-only — English/Mandarin/
    -- Cantonese in particular aren't really IT-exclusive skills in real
    -- life, so this tagging is a scope simplification tied to where the
    -- frequency data came from, not a claim that these only matter for IT.
    ('English', 'IT'),                -- 70% of ads (42/60)
    ('Mandarin', 'IT'),                -- 33% (20/60)
    ('Cantonese', 'IT'),               -- 28% (17/60)
    ('Linux', 'IT'),                   -- 23% (14/60)
    ('Cybersecurity', 'IT'),           -- 17% (10/60)
    ('Windows Server', 'IT'),          -- 17% (10/60)
    ('SQL', 'IT'),                     -- 15% (9/60)
    ('Azure', 'IT');                   -- 13% (8/60)

-- Second round: added from a much larger real-data analysis (~28,800 real
-- job ads across 30 industries from a job board) covering the three
-- domains this app's titles actually span, not just IT — same methodology
-- as above (curated candidates, kept only what genuinely appeared at
-- meaningful frequency). See backend/scripts/analyze_job_ads.py. Category
-- tagging follows the same "tied to where the frequency data came from,
-- not a claim of exclusivity" convention as the first round.
INSERT INTO skills (name, category) VALUES
    ('AI', 'IT'),                      -- 30% of information_communication_technology ads (1133/3800)
    ('Project Management', 'IT'),      -- 16% (606/3800)
    ('Agile', 'IT'),                   -- 14% (514/3800)
    ('AWS', 'IT'),                     -- 10% (364/3800)
    ('DevOps', 'IT'),                  -- 9% (340/3800)
    ('CI/CD', 'IT'),                   -- 9% (339/3800)
    ('Machine Learning', 'IT'),        -- 8% (304/3800)
    ('Business Analysis', 'IT'),       -- 8% (290/3800)
    ('Docker', 'IT'),                  -- 7% (265/3800)
    ('Help Desk', 'IT'),               -- 3% (99/3800) — kept despite the low
                                        -- % for how directly it names what
                                        -- the IT Support title already is

    ('Excel', '文員'),                  -- 39% of administration_office_support ads (1049/2701)
    ('Word', '文員'),                   -- 39% (1046/2701)
    ('PowerPoint', '文員'),             -- 20% (527/2701)
    ('Human Resources', '文員'),        -- 17% (455/2701)
    ('Compliance', '文員'),             -- 12% (317/2701)
    ('Attention to Detail', '文員'),    -- 12% (311/2701)
    ('Correspondence', '文員'),         -- 11% (288/2701)
    ('Office Administration', '文員'),  -- 10% (277/2701)
    ('Procurement', '文員'),            -- 10% (259/2701)
    ('Report Writing', '文員'),         -- 9% (245/2701)

    ('Customer Service', '客戶服務'),    -- 50% of call_centre_customer_service ads (315/625)
    ('Call Handling', '客戶服務'),       -- 7% (44/625)
    ('Live Chat Support', '客戶服務'),   -- 4% (27/625)
    ('Problem Solving', '客戶服務'),     -- 3% (20/625)
    ('Empathy', '客戶服務'),             -- 2% (10/625)
    ('Customer Retention', '客戶服務'),  -- 1% (9/625)
    ('Cross-selling', '客戶服務'),       -- 1% (8/625)
    ('Product Knowledge', '客戶服務');   -- 1% (8/625)

INSERT INTO skill_aliases (skill_id, alias)
SELECT s.skill_id, a.alias FROM skills s
JOIN (VALUES
    ('Mandarin', '普通話'), ('Mandarin', 'Putonghua'),
    ('Cantonese', '廣東話'), ('Cantonese', 'Canto'),
    ('Cybersecurity', 'Cyber Security'), ('Cybersecurity', 'Information Security'),
    ('SQL', 'MySQL'), ('SQL', 'PostgreSQL'), ('SQL', 'SQL Server'), ('SQL', 'MSSQL'),
    ('Azure', 'Microsoft Azure'),
    ('AI', 'Artificial Intelligence'),
    ('Human Resources', 'HR'),
    ('Office Administration', 'Office Admin'),
    ('Report Writing', 'Reporting'),
    -- Bare "CRM" (no "System") is a common real-ad phrasing this alias
    -- catches that the canonical two-word name alone would miss — 7% of
    -- call_centre_customer_service ads (43/625) said just "CRM".
    ('CRM System', 'CRM')
) AS a(skill_name, alias) ON s.name = a.skill_name;

INSERT INTO job_titles (title_name, track, level) VALUES
    ('文員', '文員', 'Junior'),
    ('行政主任/主管', '文員', 'Mid'),
    ('行政經理', '文員', 'Senior'),
    ('客戶服務助理', '客戶服務', 'Junior'),
    ('客戶服務主任', '客戶服務', 'Mid'),
    ('客戶服務經理', '客戶服務', 'Senior'),
    ('IT Support', 'IT', 'Junior'),
    ('IT Officer', 'IT', 'Mid'),
    ('IT Manager', 'IT', 'Senior');

-- Core vs nice-to-have, per title. Core = the skills that actually define
-- whether you can do the job; nice-to-have = valuable but not disqualifying
-- if missing. compute_match() in suggestion.py weights core coverage far
-- more heavily (80%) than nice-to-have coverage (20%) — see Blueprint
-- Sheet 02 for the reasoning behind the split and the weighting.
INSERT INTO job_title_skills (title_id, skill_id, is_core)
SELECT t.title_id, s.skill_id, x.is_core
FROM (VALUES
    ('文員', 'MS Office', TRUE),
    ('文員', 'Data Entry', TRUE),
    ('文員', 'Filing', TRUE),
    ('文員', 'Basic Bookkeeping', FALSE),

    ('行政主任/主管', 'Team Supervision', TRUE),
    ('行政主任/主管', 'Budget Tracking', TRUE),
    ('行政主任/主管', 'Vendor Coordination', FALSE),
    ('行政主任/主管', 'Process Improvement', FALSE),

    ('行政經理', 'Department Budget Management', TRUE),
    ('行政經理', 'Cross-dept Coordination', TRUE),
    ('行政經理', 'Policy Development', FALSE),

    ('客戶服務助理', 'Communication', TRUE),
    ('客戶服務助理', 'Complaint Handling', TRUE),
    ('客戶服務助理', 'CRM System', FALSE),

    ('客戶服務主任', 'Team Leadership', TRUE),
    ('客戶服務主任', 'Escalation Handling', TRUE),
    ('客戶服務主任', 'SLA Management', FALSE),
    ('客戶服務主任', 'Training', FALSE),

    ('客戶服務經理', 'Customer Experience Strategy', TRUE),
    ('客戶服務經理', 'Stakeholder Management', TRUE),
    ('客戶服務經理', 'KPI/Budget Management', FALSE),

    ('IT Support', 'Troubleshooting', TRUE),
    ('IT Support', 'Windows/Networking Basics', TRUE),
    ('IT Support', 'Ticketing System', FALSE),

    ('IT Officer', 'System Administration', TRUE),
    ('IT Officer', 'Team Coordination', TRUE),
    ('IT Officer', 'Vendor Management', FALSE),
    ('IT Officer', 'ITIL', FALSE),

    ('IT Manager', 'IT Infrastructure Strategy', TRUE),
    ('IT Manager', 'Security Governance', TRUE),
    ('IT Manager', 'Budget/Vendor Contract', FALSE)
) AS x(title_name, skill_name, is_core)
JOIN job_titles t ON t.title_name = x.title_name
JOIN skills s ON s.name = x.skill_name;
