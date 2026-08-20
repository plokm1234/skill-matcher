import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// Title is always a row of 5 buttons — see Skill Matcher Blueprint Sheet 02.
// These 5 title_name values must match backend/db/seed.sql.
const TITLES = ["文員", "客戶服務助理", "IT Support", "行政經理", "IT Manager"];

// Self-authored, not scraped — see Blueprint Sheet 02 for why.
// Each needs its own `key` — without one, every demo chip fell back to the
// same `undefined` and all 5 lit up together once any one was picked.
const DEMO_EXAMPLES = [
  {
    key: "cross-low",
    label: "Software Developer",
    jobText:
      "We are looking for a Software Developer with strong experience in Python, Git, Data Structures and Algorithms. You will design and maintain backend systems, write clean testable code, and collaborate with cross-functional teams.",
  },
  {
    key: "same-high",
    label: "IT Support Officer",
    jobText:
      "IT Support Assistant needed to handle daily Troubleshooting and Ticketing System duties. Communication and Complaint Handling skills required when supporting non-technical staff.",
  },
  {
    key: "cross-high",
    label: "IT Support Assistant",
    jobText:
      "IT Support Officer needed to provide first-line Troubleshooting, handle Windows/Networking Basics issues, and log all requests through our internal Ticketing System.",
  },
  {
    key: "same-mid",
    label: "Admin Officer",
    jobText:
      "Admin Officer required to handle daily Data Entry and office Filing, while also taking on Team Supervision and Vendor Coordination responsibilities.",
  },
  {
    key: "same-low",
    label: "Administration Manager",
    jobText:
      "Administration Manager responsible for Department Budget Management, Policy Development, and Cross-dept Coordination across the organization.",
  },
];

// Job Description options: "自己貼" plus the 5 demo examples, all one row —
// few enough choices that they don't need a separate mode toggle.
const JOB_OPTIONS = [{ key: "manual", label: "自己貼" }, ...DEMO_EXAMPLES];

async function getJson(url, opts) {
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error(`request failed (${res.status})`);
  return res.json();
}

export default function JobMatcher() {
  const [title, setTitle] = useState(TITLES[0]);
  const [titleSkills, setTitleSkills] = useState([]);

  const [jobOption, setJobOption] = useState(null);
  const [jobText, setJobText] = useState("");
  const [requiredSkills, setRequiredSkills] = useState([]);

  const [result, setResult] = useState(null);
  const [revealIndex, setRevealIndex] = useState(0);
  const [showSummary, setShowSummary] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Title skills preview — fetched whenever the selected title changes.
  useEffect(() => {
    getJson(`${API_BASE}/title-skills?title=${encodeURIComponent(title)}`)
      .then((d) => setTitleSkills(d.skills))
      .catch(() => setTitleSkills([]));
  }, [title]);

  async function previewRequiredSkills(text) {
    if (!text.trim()) {
      setRequiredSkills([]);
      return;
    }
    try {
      const d = await getJson(`${API_BASE}/required-skills`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_text: text }),
      });
      setRequiredSkills(d.skills);
    } catch {
      setRequiredSkills([]);
    }
  }

  function pickJobOption(opt) {
    setJobOption(opt.key);
    setResult(null);
    setShowSummary(false);
    if (opt.key === "manual") {
      setJobText("");
      setRequiredSkills([]);
    } else {
      setJobText(opt.jobText);
      previewRequiredSkills(opt.jobText);
    }
  }

  async function handleExtract() {
    setLoading(true);
    setError(null);
    setResult(null);
    setShowSummary(false);
    try {
      const d = await getJson(`${API_BASE}/extract`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, job_text: jobText }),
      });
      setResult(d);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // Extract doesn't create the skill chips — they're already on screen the
  // moment title/job description are picked. It only flips each one's CSS
  // state from "pending" to tick/cross, one at a time.
  useEffect(() => {
    if (!result) return;
    setRevealIndex(0);
    const timer = setInterval(() => {
      setRevealIndex((i) => {
        const next = i + 1;
        if (next >= requiredSkills.length) {
          clearInterval(timer);
          setTimeout(() => setShowSummary(true), 400);
        }
        return next;
      });
    }, 220);
    return () => clearInterval(timer);
  }, [result]);

  return (
    <div className="matcher">
      <div className="matcher-sheet">
      <h1>Skill Matcher</h1>

      <div className="field">
        <label>職位 Title</label>
        <div className="chip-row title-row">
          <button
            className="chip chip-disabled"
            disabled
            type="button"
            title="未支援自訂職位title"
          >
            自己貼
          </button>
          {TITLES.map((t) => (
            <button
              key={t}
              className={`chip ${title === t ? "chip-active" : ""}`}
              onClick={() => setTitle(t)}
              type="button"
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="field">
        <label>Job Description</label>
        <div className="chip-row job-row">
          {JOB_OPTIONS.map((opt) => (
            <button
              key={opt.key}
              className={`chip ${jobOption === opt.key ? "chip-active" : ""}`}
              onClick={() => pickJobOption(opt)}
              type="button"
            >
              {opt.label}
            </button>
          ))}
        </div>

        {jobOption === "manual" && (
          <textarea
            rows={8}
            autoFocus
            placeholder="貼上 Job Description...(建議淨貼職位要求部分)"
            value={jobText}
            onChange={(e) => setJobText(e.target.value)}
            onBlur={(e) => previewRequiredSkills(e.target.value)}
          />
        )}
      </div>

      <button
        className="extract-btn"
        onClick={handleExtract}
        disabled={loading || !jobText}
        type="button"
      >
        {loading ? "Extracting..." : "Extract"}
      </button>

      {error && <p className="error">{error}</p>}

      {(titleSkills.length > 0 || requiredSkills.length > 0) && (
        <div className="compare">
          <div className="compare-col">
            <h3>你嘅Skills</h3>
            <div className="chip-list">
              {titleSkills.map((s) => (
                <span key={s} className="skill-chip">{s}</span>
              ))}
            </div>
          </div>
          <div className="compare-col">
            <h3>呢份Job要求嘅Skills</h3>
            <div className="chip-list">
              {requiredSkills.map((skill, i) => {
                // Before Extract runs, result is null and every chip just
                // sits in the plain "pending" state — Extract's only job
                // is to flip this classification on, one chip at a time.
                if (!result) {
                  return <span key={skill} className="skill-chip pending">{skill}</span>;
                }
                const revealed = i < revealIndex;
                const isMatch = result.matched.includes(skill);
                const cls = revealed ? `revealed ${isMatch ? "is-match" : "is-gap"}` : "pending";
                return (
                  <span key={skill} className={`skill-chip ${cls}`}>
                    {skill}
                    {revealed && (isMatch ? " ✓" : " ✕")}
                  </span>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {result && showSummary && (
        <div className={`result ${showSummary ? "result-in" : ""}`}>
          <h2>Match: {result.match_pct}%</h2>
          <p className="suggestion">建議: {result.suggestion}</p>
        </div>
      )}
      </div>
    </div>
  );
}
