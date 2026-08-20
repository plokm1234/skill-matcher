import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// Title is always a row of 5 buttons — see Skill Matcher Blueprint Sheet 02.
// These 5 title_name values must match backend/db/seed.sql.
const TITLES = ["文員", "客戶服務助理", "IT Support", "行政經理", "IT Manager"];

// Self-authored, not scraped — see Blueprint Sheet 02 for why.
const DEMO_EXAMPLES = [
  {
    label: "跨track · 低分",
    jobText:
      "We are looking for a Software Developer with strong experience in Python, Git, Data Structures and Algorithms. You will design and maintain backend systems, write clean testable code, and collaborate with cross-functional teams.",
  },
  {
    label: "跨track · 高分",
    jobText:
      "IT Support Assistant needed to handle daily Troubleshooting and Ticketing System duties. Communication and Complaint Handling skills required when supporting non-technical staff.",
  },
  {
    label: "同track · 高match",
    jobText:
      "IT Support Officer needed to provide first-line Troubleshooting, handle Windows/Networking Basics issues, and log all requests through our internal Ticketing System.",
  },
  {
    label: "同track · 中match",
    jobText:
      "Admin Officer required to handle daily Data Entry and office Filing, while also taking on Team Supervision and Vendor Coordination responsibilities.",
  },
  {
    label: "同track · 低match",
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
  const [comparisonItems, setComparisonItems] = useState([]);
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
    setComparisonItems([]);
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
    setShowSummary(false);
    try {
      const d = await getJson(`${API_BASE}/extract`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, job_text: jobText }),
      });
      setResult(d);
      const matchedSet = new Set(d.matched);
      const base = requiredSkills.length ? requiredSkills : [...d.matched, ...d.gap];
      setComparisonItems(base.map((skill) => ({ skill, isMatch: matchedSet.has(skill) })));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // Staggered reveal: tick/cross appear one at a time, then the centered
  // match%/suggestion summary fades in below.
  useEffect(() => {
    if (!comparisonItems.length) return;
    setRevealIndex(0);
    const timer = setInterval(() => {
      setRevealIndex((i) => {
        const next = i + 1;
        if (next >= comparisonItems.length) {
          clearInterval(timer);
          setTimeout(() => setShowSummary(true), 400);
        }
        return next;
      });
    }, 220);
    return () => clearInterval(timer);
  }, [comparisonItems]);

  return (
    <div className="matcher">
      <h1>Skill Matcher</h1>

      <div className="field">
        <label>職位 Title</label>
        <div className="chip-row">
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
        {titleSkills.length > 0 && (
          <p className="skill-preview">你嘅Skills: {titleSkills.join(" · ")}</p>
        )}
      </div>

      <div className="field">
        <label>Job Description</label>
        <div className="chip-row">
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

        {requiredSkills.length > 0 && (
          <p className="skill-preview">呢份Job要求: {requiredSkills.join(" · ")}</p>
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

      {comparisonItems.length > 0 && (
        <div className="compare">
          <div className="compare-col">
            <h3>你嘅Skills</h3>
            {titleSkills.map((s) => (
              <p key={s}>{s}</p>
            ))}
          </div>
          <div className="compare-col">
            <h3>呢份Job要求嘅Skills</h3>
            {comparisonItems.map((item, i) => (
              <p key={item.skill} className={i < revealIndex ? "revealed" : "pending"}>
                {item.skill}
                {i < revealIndex && (
                  <span className={item.isMatch ? "tick" : "cross"}>
                    {item.isMatch ? " ✓" : " ✕"}
                  </span>
                )}
              </p>
            ))}
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
  );
}
