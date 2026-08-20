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
    ('Algorithms', 'Software Dev');

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

INSERT INTO job_title_skills (title_id, skill_id)
SELECT t.title_id, s.skill_id FROM job_titles t, skills s
WHERE (t.title_name = '文員' AND s.name IN ('MS Office', 'Data Entry', 'Filing', 'Basic Bookkeeping'))
   OR (t.title_name = '行政主任/主管' AND s.name IN ('Team Supervision', 'Vendor Coordination', 'Budget Tracking', 'Process Improvement'))
   OR (t.title_name = '行政經理' AND s.name IN ('Department Budget Management', 'Policy Development', 'Cross-dept Coordination'))
   OR (t.title_name = '客戶服務助理' AND s.name IN ('Communication', 'CRM System', 'Complaint Handling'))
   OR (t.title_name = '客戶服務主任' AND s.name IN ('Team Leadership', 'SLA Management', 'Escalation Handling', 'Training'))
   OR (t.title_name = '客戶服務經理' AND s.name IN ('Customer Experience Strategy', 'KPI/Budget Management', 'Stakeholder Management'))
   OR (t.title_name = 'IT Support' AND s.name IN ('Troubleshooting', 'Windows/Networking Basics', 'Ticketing System'))
   OR (t.title_name = 'IT Officer' AND s.name IN ('System Administration', 'Vendor Management', 'Team Coordination', 'ITIL'))
   OR (t.title_name = 'IT Manager' AND s.name IN ('IT Infrastructure Strategy', 'Budget/Vendor Contract', 'Security Governance'));
