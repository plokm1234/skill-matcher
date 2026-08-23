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

// Small outline icons for the sample page's meta rows — plain inline SVG,
// no icon library needed for four shapes.
const ICON_PROPS = {
  className: "sample-ad-icon",
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: "2",
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

const IconPin = () => (
  <svg {...ICON_PROPS}>
    <path d="M12 21s-7-7.58-7-12a7 7 0 1 1 14 0c0 4.42-7 12-7 12z" />
    <circle cx="12" cy="9" r="2.5" />
  </svg>
);

const IconBriefcase = () => (
  <svg {...ICON_PROPS}>
    <rect x="2" y="7" width="20" height="14" rx="2" />
    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
  </svg>
);

const IconClock = () => (
  <svg {...ICON_PROPS}>
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
  </svg>
);

const IconSalary = () => (
  <svg {...ICON_PROPS}>
    <circle cx="12" cy="12" r="10" />
    <path d="M12 6v12M15.5 9.5c0-1.4-1.6-2.5-3.5-2.5S8.5 8.1 8.5 9.5s1.6 2 3.5 2 3.5.6 3.5 2-1.6 2.5-3.5 2.5-3.5-1.1-3.5-2.5" />
  </svg>
);

const IconInfo = () => (
  <svg {...ICON_PROPS} className="sample-ad-icon sample-ad-icon-info">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="16" x2="12" y2="11" />
    <circle cx="12" cy="8" r="0.5" fill="currentColor" stroke="none" />
  </svg>
);

const IconBuilding = () => (
  <svg {...ICON_PROPS}>
    <rect x="4" y="2" width="16" height="20" rx="1" />
    <path d="M9 22v-6h6v6" />
    <path d="M9 6h.01M15 6h.01M9 10h.01M15 10h.01M9 14h.01M15 14h.01" />
  </svg>
);

const IconUsers = () => (
  <svg {...ICON_PROPS}>
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
  </svg>
);

// Sample page header + description — written in the same shape a real
// job board posting uses (title / company / location / category /
// employment type / salary / posted-age / application-volume badge, then
// a "Jobs Description" section, then a "Company profile" section), but
// every value here is invented, not copied from any real ad or company.
const SAMPLE_AD = {
  title: "IT Support Officer (Fresh Graduates Welcome)",
  company: "Demo Corp Limited",
  location: "Hong Kong",
  category: "Help Desk & IT Support (Information & Communication Technology)",
  employmentType: "Full time",
  salary: "Salary undisclosed",
  postedAge: "Posted 12d ago",
  volumeBadge: "High application volume",
  overview:
    "Demo Corp Limited is looking for an IT Support Officer to handle daily technical support duties.",
  responsibilities: [
    "Handle daily Troubleshooting and log requests via our Ticketing System",
    "Provide first-line support to non-technical staff",
  ],
  requirements: [
    "Strong Communication and Complaint Handling skills",
    "Fresh graduates welcome",
  ],
  industry: "Information Technology Services",
  employeeCount: "51-200 employees",
  companyBlurb: "Demo Corp Limited provides IT support services to businesses across Hong Kong.",
};

export default function JobMatcher() {
  const [page, setPage] = useState("main"); // "main" | "sample"

  const [title, setTitle] = useState(TITLES[0]);
  const [coreSkills, setCoreSkills] = useState([]);
  const [niceSkills, setNiceSkills] = useState([]);

  const [jobOption, setJobOption] = useState(null);
  const [jobText, setJobText] = useState("");
  const [requiredSkills, setRequiredSkills] = useState([]);

  const [result, setResult] = useState(null);
  const [revealIndex, setRevealIndex] = useState(0);
  const [showSummary, setShowSummary] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Title skills preview — fetched whenever the selected title changes.
  // Core/nice-to-have are kept separate (not flattened into one list) so
  // both this column and the required-skills column can label each chip
  // explicitly instead of leaving the split implicit in the match%.
  useEffect(() => {
    getJson(`${API_BASE}/title-skills?title=${encodeURIComponent(title)}`)
      .then((d) => {
        setCoreSkills(d.core_skills);
        setNiceSkills(d.nice_skills);
      })
      .catch(() => {
        setCoreSkills([]);
        setNiceSkills([]);
      });
  }, [title]);

  // A required skill is only "core" or "nice-to-have" relative to the
  // selected title's own skill set — one that falls outside both (e.g. a
  // Python job ad pasted while IT Support is selected) gets no tier tag,
  // it's just cross-track gap material.
  function tierOf(skill) {
    if (coreSkills.includes(skill)) return "core";
    if (niceSkills.includes(skill)) return "nice";
    return null;
  }

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

  // Grouped for rendering — just core vs everything else (nice-to-have
  // and cross-track skills merged into one "其他" bucket for display; the
  // nice-to-have/other distinction still matters for match_pct on the
  // backend, it's just not worth a third visual group here). Each entry
  // keeps its original index (origIndex) so the reveal animation still
  // ticks through skills in detection order even though they're laid out
  // in two groups rather than one flat list. This runs as soon as
  // requiredSkills is populated (right after a demo is picked or pasted
  // text is blurred), not gated on Extract.
  const requiredWithTier = requiredSkills.map((skill, origIndex) => ({
    skill,
    origIndex,
    tier: tierOf(skill),
  }));
  const coreRequired = requiredWithTier.filter((r) => r.tier === "core");
  const otherRequired = requiredWithTier.filter((r) => r.tier !== "core");

  function renderRequiredChip({ skill, origIndex }) {
    if (!result) {
      return <span key={skill} className="skill-chip pending">{skill}</span>;
    }
    const revealed = origIndex < revealIndex;
    const isMatch = result.matched.includes(skill);
    const cls = revealed ? `revealed ${isMatch ? "is-match" : "is-gap"}` : "pending";
    return (
      <span key={skill} className={`skill-chip ${cls}`}>
        {skill}
        {revealed && (isMatch ? " ✓" : " ✕")}
      </span>
    );
  }

  return (
    <div className="matcher">
      {/* Sheet "3" of the 4-layer fan — a real full-size rotated sheet,
          same bottom-left origin as every other layer, not a floating
          label. Its own rotation is what pushes its top-right corner out
          past .sheet-active's flat edge, exactly like layers 1/2 already
          do. Most of the rectangle sits underneath .sheet-active, so only
          the exposed corner is ever visible or clickable; clicking it
          turns the page. */}
      <button
        className="page-flip-sheet"
        onClick={() => setPage(page === "main" ? "sample" : "main")}
        type="button"
        aria-label={page === "main" ? "下一頁:示範Job Ad" : "返回 Skill Matcher"}
      >
        <span className="page-flip-sheet-label">
          {page === "main" ? "示範Job Ad ›" : "‹ 返回上一頁"}
        </span>
      </button>

      {/* Sheet "3": the main tool. Always rendered (state must stay mounted
          across a page flip) — .sheet-active/.sheet-inactive decides
          whether it's the flat front card or the rotated peek behind it. */}
      <div className={`sheet ${page === "main" ? "sheet-active" : "sheet-inactive"}`}>
      <h1>Skill Matcher</h1>
      <p className="notice">
        Demo使用免費伺服器,載入可能要等耐少少。
      </p>

      <div className="field">
        <label>你的職位 Title</label>
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
        <label>目標職位 Job Description</label>
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

      {(coreSkills.length > 0 || niceSkills.length > 0 || requiredSkills.length > 0) && (
        <div className="compare">
          <div className="compare-col">
            <h3>你嘅Skills</h3>
            {coreSkills.length > 0 && (
              <>
                <p className="tier-label tier-label-core">核心 Skills</p>
                <div className="chip-list">
                  {coreSkills.map((s) => (
                    <span key={s} className="skill-chip tier-core">{s}</span>
                  ))}
                </div>
              </>
            )}
            {niceSkills.length > 0 && (
              <>
                <p className="tier-label tier-label-other">其他 Skills</p>
                <div className="chip-list">
                  {niceSkills.map((s) => (
                    <span key={s} className="skill-chip tier-nice">{s}</span>
                  ))}
                </div>
              </>
            )}
          </div>
          <div className="compare-col">
            <h3>呢份Job要求嘅Skills</h3>
            {coreRequired.length > 0 && (
              <>
                <p className="tier-label tier-label-core">核心 Skills</p>
                <div className="chip-list">{coreRequired.map(renderRequiredChip)}</div>
              </>
            )}
            {otherRequired.length > 0 && (
              <>
                <p className="tier-label tier-label-other">其他 Skills</p>
                <div className="chip-list">{otherRequired.map(renderRequiredChip)}</div>
              </>
            )}
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

      {/* Sheet "2": the sample page. Previously .matcher::after — a plain
          decorative rotated rectangle with no content — is now this real
          element, so the "middle sheet" of the 3-sheet stack is what
          actually holds page 2, instead of a link buried inside sheet 3. */}
      <div className={`sheet ${page === "sample" ? "sheet-active" : "sheet-inactive"}`}>
      <h1>示範Job Ad</h1>
      <p className="notice">
        呢頁仿造真實job board嘅版面,教你貼job description時應該揀邊一部分。
      </p>

      <div className="sample-ad-mock">
        <div className="sample-ad-header">
          <h2 className="sample-ad-job-title">{SAMPLE_AD.title}</h2>
          <div className="sample-ad-company-row">
            <span className="sample-ad-company">
              {SAMPLE_AD.company}
              <span className="sample-ad-verified" title="Verified">✓</span>
            </span>
            <span className="sample-ad-view-all">View all jobs</span>
          </div>
          <div className="sample-ad-meta-list">
            <div className="sample-ad-meta-row">
              <IconPin />
              <span>{SAMPLE_AD.location}</span>
            </div>
            <div className="sample-ad-meta-row">
              <IconBriefcase />
              <span>{SAMPLE_AD.category}</span>
            </div>
            <div className="sample-ad-meta-row">
              <IconClock />
              <span>{SAMPLE_AD.employmentType}</span>
            </div>
            <div className="sample-ad-meta-row">
              <IconSalary />
              <span>{SAMPLE_AD.salary}</span>
              <IconInfo />
            </div>
          </div>
          <div className="sample-ad-posted-row">
            <span>{SAMPLE_AD.postedAge}</span>
            <span className="sample-ad-dot">·</span>
            <span className="sample-ad-volume">{SAMPLE_AD.volumeBadge}</span>
          </div>
        </div>


        <div className="sample-ad-copy-target">
          <span className="copy-badge">👇 貼呢part</span>
          <p className="sample-ad-overview">{SAMPLE_AD.overview}</p>
          <p className="sample-ad-subhead">Responsibilities</p>
          <ul>
            {SAMPLE_AD.responsibilities.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
          <p className="sample-ad-subhead">Requirements</p>
          <ul>
            {SAMPLE_AD.requirements.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>

        <div className="sample-ad-company-profile">
          <h4 className="sample-ad-section-label">Company profile</h4>
          <div className="sample-ad-profile-name-row">
            <span>{SAMPLE_AD.company}</span>
            <span className="sample-ad-verified" title="Verified">✓</span>
          </div>
          <div className="sample-ad-meta-list">
            <div className="sample-ad-meta-row">
              <IconBuilding />
              <span>{SAMPLE_AD.industry}</span>
            </div>
            <div className="sample-ad-meta-row">
              <IconUsers />
              <span>{SAMPLE_AD.employeeCount}</span>
            </div>
          </div>
          <p className="sample-ad-profile-blurb">{SAMPLE_AD.companyBlurb}</p>
        </div>
      </div>
      </div>
    </div>
  );
}
