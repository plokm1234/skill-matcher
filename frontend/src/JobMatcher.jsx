import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// Title is always a row of 5 buttons in both modes — see Skill Matcher
// Blueprint Sheet 02. These 5 title_name values must match backend/db/seed.sql.
const TITLES = ["文員", "客戶服務助理", "IT Support", "行政經理", "IT Manager"];

// Self-authored, not scraped — see Blueprint Sheet 02 for why. Title and
// job description are independent 5-choice selectors, so these examples
// only carry job text; pick any Title button to pair with one.
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

export default function JobMatcher() {
  const [title, setTitle] = useState(TITLES[0]);
  const [mode, setMode] = useState("demo"); // "demo" | "manual"
  const [jobText, setJobText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function handleModeToggle(newMode) {
    setMode(newMode);
    setJobText(""); // intentional, scoped to this handler — see Blueprint Sheet 02
    setResult(null);
  }

  async function handleExtract() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/extract`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, job_text: jobText }),
      });
      if (!res.ok) throw new Error(`request failed (${res.status})`);
      setResult(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

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
      </div>

      <div className="field">
        <div className="mode-toggle">
          <button
            className={mode === "manual" ? "chip-active" : ""}
            onClick={() => handleModeToggle("manual")}
            type="button"
          >
            自己貼
          </button>
          <button
            className={mode === "demo" ? "chip-active" : ""}
            onClick={() => handleModeToggle("demo")}
            type="button"
          >
            玩 Demo
          </button>
        </div>

        <label>Job Description</label>
        {mode === "manual" ? (
          <textarea
            rows={8}
            placeholder="貼上 Job Description...(建議淨貼職位要求部分)"
            value={jobText}
            onChange={(e) => setJobText(e.target.value)}
          />
        ) : (
          <div className="chip-row">
            {DEMO_EXAMPLES.map((ex) => (
              <button
                key={ex.label}
                className={`chip ${jobText === ex.jobText ? "chip-active" : ""}`}
                onClick={() => setJobText(ex.jobText)}
                type="button"
              >
                {ex.label}
              </button>
            ))}
          </div>
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

      {result && (
        <div className="result">
          <h2>Match: {result.match_pct}%</h2>
          {result.matched.map((s) => (
            <p key={s} className="matched">✓ {s}</p>
          ))}
          {result.gap.map((s) => (
            <p key={s} className="gap">✕ {s} (missing)</p>
          ))}
          <p className="suggestion">建議: {result.suggestion}</p>
        </div>
      )}
    </div>
  );
}
