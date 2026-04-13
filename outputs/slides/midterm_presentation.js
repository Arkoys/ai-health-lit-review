const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");

// Icons
const { FaSearch, FaFilter, FaChartBar, FaTable, FaCheckCircle, FaTimesCircle, FaGlobe, FaUniversity } = require("react-icons/fa");
const { MdHealthAndSafety, MdPolicy, MdScience } = require("react-icons/md");
const { HiLightBulb } = require("react-icons/hi");

const iconCache = {};
async function iconToBase64Png(IconComponent, color, size = 256) {
  const key = `${color}-${size}`;
  if (iconCache[key]) return iconCache[key];
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  const base64 = "image/png;base64," + pngBuffer.toString("base64");
  iconCache[key] = base64;
  return base64;
}

// ── Palette ──────────────────────────────────────────────────────────────────
// Deep teal/navy for health AI academic feel
const P = {
  navy:    "0F2A3F",
  teal:    "0D7C7C",
  light:   "F0F7F7",
  accent:  "14A8A8",
  white:   "FFFFFF",
  gray:    "64748B",
  lightGray:"E2E8F0",
  text:    "1E293B",
  amber:   "F59E0B",
  green:   "10B981",
  red:     "EF4444",
};

async function makeSlide(pres, slideFn) {
  const slide = pres.addSlide();
  await slideFn(slide);
  return slide;
}

// ── Shared helpers ───────────────────────────────────────────────────────────
function titleSlide(slide, { title, subtitle, footnote }) {
  // Full dark background
  slide.background = { color: P.navy };

  // Accent bar left
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 5.625,
    fill: { color: P.teal }, line: { color: P.teal }
  });

  // Title
  slide.addText(title, {
    x: 0.6, y: 1.4, w: 8.8, h: 1.4,
    fontSize: 38, bold: true, color: P.white,
    fontFace: "Trebuchet MS", margin: 0
  });

  // Subtitle
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.6, y: 3.0, w: 8.8, h: 0.8,
      fontSize: 20, color: P.accent,
      fontFace: "Calibri", margin: 0
    });
  }

  // Footnote
  if (footnote) {
    slide.addText(footnote, {
      x: 0.6, y: 4.8, w: 8.8, h: 0.4,
      fontSize: 11, color: P.gray, fontFace: "Calibri", margin: 0
    });
  }
}

function contentSlide(slide, { title, badge }) {
  // Light background
  slide.background = { color: P.light };

  // Top accent bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.06,
    fill: { color: P.teal }, line: { color: P.teal }
  });

  // Title
  slide.addText(title, {
    x: 0.4, y: 0.25, w: 9.2, h: 0.65,
    fontSize: 28, bold: true, color: P.navy,
    fontFace: "Trebuchet MS", margin: 0
  });

  // Badge (e.g. slide number) top right
  if (badge) {
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 9.0, y: 0.22, w: 0.65, h: 0.45,
      fill: { color: P.teal }, line: { color: P.teal },
      rectRadius: 0.08
    });
    slide.addText(badge, {
      x: 9.0, y: 0.22, w: 0.65, h: 0.45,
      fontSize: 13, bold: true, color: P.white,
      fontFace: "Calibri", align: "center", valign: "middle", margin: 0
    });
  }
}

function card(slide, pres, { x, y, w, h, fillColor, accentColor, children }) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: fillColor || P.white },
    line: { color: P.lightGray, width: 0.5 },
    shadow: { type: "outer", color: "000000", blur: 4, offset: 1, angle: 135, opacity: 0.08 }
  });
  // Left accent line
  if (accentColor) {
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.07, h,
      fill: { color: accentColor }, line: { color: accentColor }
    });
  }
}

// ── MAIN ─────────────────────────────────────────────────────────────────────
async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.title = "AI Health Literature Review — Midterm Presentation";
  pres.author = "Arkoys";

  // ─── SLIDE 1: TITLE ───────────────────────────────────────────────────────
  const s1 = pres.addSlide();
  s1.background = { color: P.navy };
  s1.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 5.625,
    fill: { color: P.teal }, line: { color: P.teal }
  });
  s1.addShape(pres.shapes.RECTANGLE, {
    x: 0.18, y: 1.3, w: 3.5, h: 0.04,
    fill: { color: P.accent }, line: { color: P.accent }
  });
  s1.addText("AI Health Literature Review", {
    x: 0.6, y: 0.7, w: 9.0, h: 0.9,
    fontSize: 36, bold: true, color: P.white,
    fontFace: "Trebuchet MS", margin: 0
  });
  s1.addText("Midterm Presentation", {
    x: 0.6, y: 1.5, w: 9.0, h: 0.7,
    fontSize: 24, color: P.accent, fontFace: "Trebuchet MS", margin: 0
  });
  s1.addText("Review Question, Search Strategy & Methodology", {
    x: 0.6, y: 2.2, w: 9.0, h: 0.5,
    fontSize: 16, color: P.gray, fontFace: "Calibri", margin: 0
  });
  s1.addText("Arkoys  ·  2026-04-13", {
    x: 0.6, y: 4.9, w: 9.0, h: 0.4,
    fontSize: 12, color: P.gray, fontFace: "Calibri", margin: 0
  });

  // ─── SLIDE 2: REVIEW QUESTION ────────────────────────────────────────────
  const s2 = pres.addSlide();
  s2.background = { color: P.light };
  s2.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: P.teal }, line: { color: P.teal } });
  s2.addText("1. Review Question", {
    x: 0.4, y: 0.22, w: 8.4, h: 0.65,
    fontSize: 28, bold: true, color: P.navy, fontFace: "Trebuchet MS", margin: 0
  });
  s2.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 8.8, y: 0.18, w: 0.8, h: 0.45,
    fill: { color: P.teal }, line: { color: P.teal }, rectRadius: 0.08
  });
  s2.addText("01", {
    x: 8.8, y: 0.18, w: 0.8, h: 0.45,
    fontSize: 13, bold: true, color: P.white, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0
  });

  // Main question box
  s2.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.0, w: 9.2, h: 1.4,
    fill: { color: P.navy }, line: { color: P.navy },
    shadow: { type: "outer", color: "000000", blur: 5, offset: 2, angle: 135, opacity: 0.12 }
  });
  s2.addText(
    "\"What methods and frameworks exist for evaluating health AI systems in real-world deployment contexts, and how do governance structures shape their implementation, sustainability, and societal impact?\"",
    {
      x: 0.55, y: 1.08, w: 8.9, h: 1.24,
      fontSize: 15.5, italic: true, color: P.white,
      fontFace: "Calibri", margin: 0, valign: "middle"
    }
  );

  // Why well-scoped
  s2.addText("Why this question is well-scoped:", {
    x: 0.4, y: 2.55, w: 4.0, h: 0.4,
    fontSize: 14, bold: true, color: P.navy, fontFace: "Trebuchet MS", margin: 0
  });

  const reasons = [
    { label: "Too broad", text: '"AI in healthcare" — unmanageable, zero focus', color: P.red },
    { label: "Too narrow", text: '"How does the NHS evaluate AI chatbots?" — too specific', color: P.amber },
    { label: "Our question", text: "Links evaluation methods AND governance — inseparable in real-world health AI", color: P.green },
  ];
  reasons.forEach((r, i) => {
    const yPos = 3.0 + i * 0.72;
    s2.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y: yPos, w: 9.2, h: 0.62,
      fill: { color: P.white }, line: { color: P.lightGray, width: 0.5 },
      shadow: { type: "outer", color: "000000", blur: 3, offset: 1, angle: 135, opacity: 0.06 }
    });
    s2.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y: yPos, w: 0.08, h: 0.62,
      fill: { color: r.color }, line: { color: r.color }
    });
    s2.addText(r.label, {
      x: 0.6, y: yPos + 0.04, w: 1.5, h: 0.28,
      fontSize: 10, bold: true, color: r.color, fontFace: "Calibri", margin: 0
    });
    s2.addText(r.text, {
      x: 0.6, y: yPos + 0.28, w: 8.8, h: 0.3,
      fontSize: 12, color: P.text, fontFace: "Calibri", margin: 0
    });
  });

  // PhD connection
  s2.addShape(pres.shapes.RECTANGLE, {
    x: 5.3, y: 2.55, w: 4.3, h: 0.4,
    fill: { color: P.teal }, line: { color: P.teal }
  });
  s2.addText("PhD Supervisor Keywords: 5 thematic groups", {
    x: 5.35, y: 2.55, w: 4.2, h: 0.4,
    fontSize: 11, bold: true, color: P.white, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0
  });

  // ─── SLIDE 3: SEARCH STRATEGY — SOURCES ─────────────────────────────────
  const s3 = pres.addSlide();
  s3.background = { color: P.light };
  s3.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: P.teal }, line: { color: P.teal } });
  s3.addText("2. Search Strategy — Sources", {
    x: 0.4, y: 0.22, w: 8.4, h: 0.65,
    fontSize: 28, bold: true, color: P.navy, fontFace: "Trebuchet MS", margin: 0
  });
  s3.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 8.8, y: 0.18, w: 0.8, h: 0.45,
    fill: { color: P.teal }, line: { color: P.teal }, rectRadius: 0.08
  });
  s3.addText("02", {
    x: 8.8, y: 0.18, w: 0.8, h: 0.45,
    fontSize: 13, bold: true, color: P.white, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0
  });

  // Sources table
  const sources = [
    ["arXiv", "Preprint server", "cs.AI, cs.LG, cs.CL, cs.CY, q-bio, eess.AS, cs.CV", "50/day"],
    ["PubMed / PMC", "Biomedical DB", "AI + health/clinical/medical", "30/day"],
    ["NeurIPS Proceedings", "Conference", "AI/ML 2020–2024", "20/session"],
    ["Manual / Other", "Conferences, blogs", "Relevant health AI & governance", "Ongoing"],
  ];

  const headerRow = [
    { text: "Source", options: { bold: true, color: P.white, fill: { color: P.navy }, align: "center" } },
    { text: "Type", options: { bold: true, color: P.white, fill: { color: P.navy }, align: "center" } },
    { text: "Coverage", options: { bold: true, color: P.white, fill: { color: P.navy }, align: "center" } },
    { text: "Limit", options: { bold: true, color: P.white, fill: { color: P.navy }, align: "center" } },
  ];

  const dataRows = sources.map((row, i) =>
    row.map(cell => ({
      text: cell,
      options: { fill: { color: i % 2 === 0 ? P.white : "F8F9FA" }, align: "left", fontSize: 12 }
    }))
  );

  s3.addTable([headerRow, ...dataRows], {
    x: 0.4, y: 1.0, w: 9.2, h: 1.8,
    colW: [2.2, 1.8, 3.4, 1.0],
    border: { pt: 0.5, color: P.lightGray },
    fontFace: "Calibri",
  });

  // Keyword groups
  s3.addText("5 Keyword Thematic Groups", {
    x: 0.4, y: 3.0, w: 9.2, h: 0.4,
    fontSize: 16, bold: true, color: P.navy, fontFace: "Trebuchet MS", margin: 0
  });

  const groups = [
    { n: "1", label: "AI Evaluation & Validation", color: "0369A1" },
    { n: "2", label: "Participatory Governance", color: "7C3AED" },
    { n: "3", label: "Adaptive Governance & Regulation", color: "059669" },
    { n: "4", label: "Evidence & Implementation", color: "D97706" },
    { n: "5", label: "Clinical / Health AI Specific", color: "BE185D" },
  ];

  groups.forEach((g, i) => {
    const xPos = 0.4 + i * 1.88;
    s3.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: xPos, y: 3.5, w: 1.78, h: 1.5,
      fill: { color: g.color }, line: { color: g.color },
      rectRadius: 0.1,
      shadow: { type: "outer", color: "000000", blur: 4, offset: 1, angle: 135, opacity: 0.1 }
    });
    s3.addText("G" + g.n, {
      x: xPos, y: 3.55, w: 1.78, h: 0.35,
      fontSize: 11, bold: true, color: P.white, fontFace: "Calibri",
      align: "center", valign: "middle", margin: 0
    });
    const labelLines = g.label.split(" ");
    labelLines.forEach((line, li) => {
      s3.addText(line, {
        x: xPos + 0.08, y: 3.95 + li * 0.38, w: 1.62, h: 0.36,
        fontSize: 10, bold: false, color: P.white, fontFace: "Calibri",
        align: "center", valign: "top", margin: 0
      });
    });
  });

  // Results count
  s3.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 6.5, y: 5.1, w: 3.1, h: 0.42,
    fill: { color: P.navy }, line: { color: P.navy }, rectRadius: 0.08
  });
  s3.addText("Total in DB: 33 papers (as of 2026-04-13)", {
    x: 6.5, y: 5.1, w: 3.1, h: 0.42,
    fontSize: 11, bold: true, color: P.white, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0
  });

  // ─── SLIDE 4: INCLUSION / EXCLUSION ─────────────────────────────────────
  const s4 = pres.addSlide();
  s4.background = { color: P.light };
  s4.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: P.teal }, line: { color: P.teal } });
  s4.addText("3. Inclusion / Exclusion Criteria", {
    x: 0.4, y: 0.22, w: 8.4, h: 0.65,
    fontSize: 28, bold: true, color: P.navy, fontFace: "Trebuchet MS", margin: 0
  });
  s4.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 8.8, y: 0.18, w: 0.8, h: 0.45,
    fill: { color: P.teal }, line: { color: P.teal }, rectRadius: 0.08
  });
  s4.addText("03", {
    x: 8.8, y: 0.18, w: 0.8, h: 0.45,
    fontSize: 13, bold: true, color: P.white, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0
  });

  // Include column
  s4.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 0.95, w: 4.4, h: 0.42,
    fill: { color: P.green }, line: { color: P.green }
  });
  s4.addText("INCLUDE  ✅", {
    x: 0.4, y: 0.95, w: 4.4, h: 0.42,
    fontSize: 13, bold: true, color: P.white, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0
  });

  const includeItems = [
    "Peer-reviewed papers (journals, peer-reviewed conferences)",
    "AI systems applied to healthcare (clinical, medical)",
    "Contains evaluation method OR governance framework",
    "Date: 2020–2026 (+ seminal works)",
    "Language: English (French acceptable)",
    "Open access preferred; paywall OK if relevant",
  ];
  includeItems.forEach((item, i) => {
    s4.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y: 1.45 + i * 0.66, w: 4.4, h: 0.58,
      fill: { color: P.white }, line: { color: P.lightGray, width: 0.5 }
    });
    s4.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y: 1.45 + i * 0.66, w: 0.06, h: 0.58,
      fill: { color: P.green }, line: { color: P.green }
    });
    s4.addText(item, {
      x: 0.55, y: 1.45 + i * 0.66, w: 4.2, h: 0.58,
      fontSize: 11, color: P.text, fontFace: "Calibri",
      valign: "middle", margin: 0
    });
  });

  // Exclude column
  s4.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 0.95, w: 4.4, h: 0.42,
    fill: { color: P.red }, line: { color: P.red }
  });
  s4.addText("EXCLUDE  ❌", {
    x: 5.2, y: 0.95, w: 4.4, h: 0.42,
    fontSize: 13, bold: true, color: P.white, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0
  });

  const excludeItems = [
    "Opinion pieces, editorials, letters to the editor",
    "Pure technical ML — no health dimension, no evaluation",
    "AI outside clinical context (finance, agriculture...)",
    "Pre-2020 (except seminal governance works)",
    "Non-English without English abstract",
    "No abstract available (cannot screen)",
  ];
  excludeItems.forEach((item, i) => {
    s4.addShape(pres.shapes.RECTANGLE, {
      x: 5.2, y: 1.45 + i * 0.66, w: 4.4, h: 0.58,
      fill: { color: P.white }, line: { color: P.lightGray, width: 0.5 }
    });
    s4.addShape(pres.shapes.RECTANGLE, {
      x: 5.2, y: 1.45 + i * 0.66, w: 0.06, h: 0.58,
      fill: { color: P.red }, line: { color: P.red }
    });
    s4.addText(item, {
      x: 5.35, y: 1.45 + i * 0.66, w: 4.2, h: 0.58,
      fontSize: 11, color: P.text, fontFace: "Calibri",
      valign: "middle", margin: 0
    });
  });

  // Priority bar at bottom
  s4.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 5.05, w: 9.2, h: 0.48,
    fill: { color: P.navy }, line: { color: P.navy }
  });
  s4.addText("Priority 2 (top): 2+ themes + empirical   ·   Priority 1 (high): 1 theme + empirical   ·   Priority 0 (normal): theoretical only", {
    x: 0.5, y: 5.05, w: 9.0, h: 0.48,
    fontSize: 10.5, color: P.white, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0
  });

  // ─── SLIDE 5: PRISMA FLOW ─────────────────────────────────────────────────
  const s5 = pres.addSlide();
  s5.background = { color: P.light };
  s5.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: P.teal }, line: { color: P.teal } });
  s5.addText("4. PRISMA-Style Flow Diagram", {
    x: 0.4, y: 0.22, w: 8.4, h: 0.65,
    fontSize: 28, bold: true, color: P.navy, fontFace: "Trebuchet MS", margin: 0
  });
  s5.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 8.8, y: 0.18, w: 0.8, h: 0.45,
    fill: { color: P.teal }, line: { color: P.teal }, rectRadius: 0.08
  });
  s5.addText("04", {
    x: 8.8, y: 0.18, w: 0.8, h: 0.45,
    fontSize: 13, bold: true, color: P.white, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0
  });

  // Funnel boxes
  const stages = [
    { label: "IDENTIFICATION", count: "~2,700", sub: "arXiv · PubMed · NeurIPS · Manual", color: "0369A1" },
    { label: "SCREENING", count: "~300–400", sub: "Title + abstract → deduplicated", color: "0D7C7C" },
    { label: "FULL TEXT READ", count: "~80–100", sub: "Apply inclusion/exclusion", color: "059669" },
    { label: "INCLUDED", count: "~40–50", sub: "Final synthesis (target: 30–50)", color: "BE185D" },
  ];

  stages.forEach((s, i) => {
    const yPos = 0.95 + i * 1.1;
    const wBox = 8.2 - i * 0.6;
    const xBox = (10 - wBox) / 2;

    s5.addShape(pres.shapes.RECTANGLE, {
      x: xBox, y: yPos, w: wBox, h: 0.92,
      fill: { color: s.color }, line: { color: s.color },
      shadow: { type: "outer", color: "000000", blur: 4, offset: 1, angle: 135, opacity: 0.1 }
    });
    s5.addText(s.label, {
      x: xBox + 0.2, y: yPos + 0.1, w: 2.5, h: 0.35,
      fontSize: 11, bold: true, color: P.white, fontFace: "Calibri", margin: 0
    });
    s5.addText(s.count, {
      x: xBox + 0.2, y: yPos + 0.42, w: 2.5, h: 0.42,
      fontSize: 22, bold: true, color: P.white, fontFace: "Trebuchet MS", margin: 0
    });
    s5.addText(s.sub, {
      x: xBox + 2.8, y: yPos + 0.22, w: wBox - 3.2, h: 0.5,
      fontSize: 10.5, color: "FFFFFFCC", fontFace: "Calibri",
      valign: "middle", margin: 0
    });

    // Arrow
    if (i < 3) {
      s5.addShape(pres.shapes.LINE, {
        x: 5.0, y: yPos + 0.92, w: 0, h: 0.18,
        line: { color: P.gray, width: 1.5 }
      });
    }
  });

  // Current status box
  s5.addShape(pres.shapes.RECTANGLE, {
    x: 7.5, y: 1.0, w: 2.2, h: 0.06,
    fill: { color: P.accent }, line: { color: P.accent }
  });
  s5.addShape(pres.shapes.RECTANGLE, {
    x: 7.3, y: 1.15, w: 2.5, h: 2.5,
    fill: { color: P.white }, line: { color: P.lightGray, width: 0.5 },
    shadow: { type: "outer", color: "000000", blur: 4, offset: 1, angle: 135, opacity: 0.08 }
  });
  s5.addText("Current Status", {
    x: 7.35, y: 1.2, w: 2.4, h: 0.35,
    fontSize: 10, bold: true, color: P.navy, fontFace: "Calibri",
    align: "center", margin: 0
  });
  const statusLines = [
    "Identified: ~2,700",
    "In DB: 33 papers",
    "Fully read: ~10",
    "In synthesis: 3",
  ];
  statusLines.forEach((line, i) => {
    s5.addText(line, {
      x: 7.35, y: 1.6 + i * 0.42, w: 2.4, h: 0.38,
      fontSize: 9.5, color: P.text, fontFace: "Calibri",
      align: "center", margin: 0
    });
  });

  // ─── SLIDE 6: DATA EXTRACTION TABLE ──────────────────────────────────────
  const s6 = pres.addSlide();
  s6.background = { color: P.light };
  s6.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: P.teal }, line: { color: P.teal } });
  s6.addText("5. Data Extraction Table (Draft)", {
    x: 0.4, y: 0.22, w: 8.4, h: 0.65,
    fontSize: 28, bold: true, color: P.navy, fontFace: "Trebuchet MS", margin: 0
  });
  s6.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 8.8, y: 0.18, w: 0.8, h: 0.45,
    fill: { color: P.teal }, line: { color: P.teal }, rectRadius: 0.08
  });
  s6.addText("05", {
    x: 8.8, y: 0.18, w: 0.8, h: 0.45,
    fontSize: 13, bold: true, color: P.white, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0
  });

  // Column headers
  const colHeaders = [
    [{ text: "Paper", options: { bold: true, color: P.white, fill: { color: P.navy } } }],
    [{ text: "Authors / Year", options: { bold: true, color: P.white, fill: { color: P.navy } } }],
    [{ text: "Country", options: { bold: true, color: P.white, fill: { color: P.navy } } }],
    [{ text: "Eval. Method", options: { bold: true, color: P.white, fill: { color: P.navy } } }],
    [{ text: "Governance Dimension", options: { bold: true, color: P.white, fill: { color: P.navy } } }],
    [{ text: "Main Finding", options: { bold: true, color: P.white, fill: { color: P.navy } } }],
  ];

  const tableRows = [
    [
      { text: "Jin Tian et al.\n\"From Pilot Trap to Institutional Capacity\"", options: { fill: { color: P.white }, fontSize: 9, bold: true, color: P.navy } },
      { text: "Jin Tian et al.\n2026", options: { fill: { color: P.white }, fontSize: 9 } },
      { text: "China", options: { fill: { color: P.white }, fontSize: 9 } },
      { text: "Qualitative case study, 18-month longitudinal", options: { fill: { color: P.white }, fontSize: 9 } },
      { text: "6-module governance framework (institutional carrier, infra, regulatory/ethics, coordination, scaling, lifecycle)", options: { fill: { color: P.white }, fontSize: 9 } },
      { text: "Governance capacity develops DURING implementation — \"pilot trap\" is governance failure, not technical failure", options: { fill: { color: P.white }, fontSize: 9 } },
    ],
    [
      { text: "Schrepel\n\"Adaptive Regulation\"", options: { fill: { color: "F8F9FA" }, fontSize: 9, bold: true, color: P.navy } },
      { text: "Schrepel\n2026", options: { fill: { color: "F8F9FA" }, fontSize: 9 } },
      { text: "EU", options: { fill: { color: "F8F9FA" }, fontSize: 9 } },
      { text: "14-criterion doctrinal coding across 4 dimensions", options: { fill: { color: "F8F9FA" }, fontSize: 9 } },
      { text: "Modular architecture, distributed sensing, pluralistic triggers, networked institutional memory", options: { fill: { color: "F8F9FA" }, fontSize: 9 } },
      { text: "Adaptive regulation better than \"future-proof\" law; blueprint for adaptive digital regulation", options: { fill: { color: "F8F9FA" }, fontSize: 9 } },
    ],
    [
      { text: "Lnenicka et al.\n\"AI Policymaking\"", options: { fill: { color: P.white }, fontSize: 9, bold: true, color: P.navy } },
      { text: "Lnenicka et al.\n2026", options: { fill: { color: P.white }, fontSize: 9 } },
      { text: "8 European\ncountries", options: { fill: { color: P.white }, fontSize: 9 } },
      { text: "Multi-country comparative case study, document analysis", options: { fill: { color: P.white }, fontSize: 9 } },
      { text: "AI integration across 6 policy cycle stages", options: { fill: { color: P.white }, fontSize: 9 } },
      { text: "Agenda setting high; implementation/evaluation low. No country has full lifecycle integration", options: { fill: { color: P.white }, fontSize: 9 } },
    ],
  ];

  s6.addTable(
    [...colHeaders.map(h => h.concat(Array(5).fill({}))), ...tableRows.map(row => row.concat(Array(6 - row.length).fill({})))].slice(0, 1 + tableRows.length),
    {
      x: 0.3, y: 0.95, w: 9.4,
      colW: [2.0, 1.3, 0.9, 1.7, 1.8, 1.8],
      rowH: 0.48,
      border: { pt: 0.5, color: P.lightGray },
      fontFace: "Calibri",
    }
  );

  // Better: build table manually with header + data
  s6.addTable([
    [
      { text: "Paper", options: { bold: true, color: P.white, fill: { color: P.navy } } },
      { text: "Authors / Year", options: { bold: true, color: P.white, fill: { color: P.navy } } },
      { text: "Country", options: { bold: true, color: P.white, fill: { color: P.navy } } },
      { text: "Eval. Method", options: { bold: true, color: P.white, fill: { color: P.navy } } },
      { text: "Governance Dimension", options: { bold: true, color: P.white, fill: { color: P.navy } } },
      { text: "Main Finding", options: { bold: true, color: P.white, fill: { color: P.navy } } },
    ],
    [
      { text: "Jin Tian et al.\n(2026)", options: { fill: { color: P.white }, fontSize: 8.5, bold: true, color: P.navy } },
      { text: "China", options: { fill: { color: P.white }, fontSize: 8.5 } },
      { text: "Qualitative case study, 18-month longitudinal", options: { fill: { color: P.white }, fontSize: 8 } },
      { text: "6-module governance framework: institutional carrier, infra, regulatory/ethics, coordination, scaling, lifecycle oversight", options: { fill: { color: P.white }, fontSize: 8 } },
      { text: "Governance capacity develops DURING implementation. \"Pilot trap\" = governance failure, not technical failure", options: { fill: { color: P.white }, fontSize: 8 } },
    ],
    [
      { text: "Schrepel\n(2026)", options: { fill: { color: "F0F4F4" }, fontSize: 8.5, bold: true, color: P.navy } },
      { text: "EU", options: { fill: { color: "F0F4F4" }, fontSize: 8.5 } },
      { text: "14-criterion doctrinal coding, 4 dimensions", options: { fill: { color: "F0F4F4" }, fontSize: 8 } },
      { text: "Modular architecture, distributed sensing, pluralistic triggers, networked institutional memory", options: { fill: { color: "F0F4F4" }, fontSize: 8 } },
      { text: "Adaptive regulation > \"future-proof\" law. Blueprint for EU digital regulation", options: { fill: { color: "F0F4F4" }, fontSize: 8 } },
    ],
    [
      { text: "Lnenicka et al.\n(2026)", options: { fill: { color: P.white }, fontSize: 8.5, bold: true, color: P.navy } },
      { text: "8 European\ncountries", options: { fill: { color: P.white }, fontSize: 8.5 } },
      { text: "Multi-country comparative, document analysis", options: { fill: { color: P.white }, fontSize: 8 } },
      { text: "AI-enabled policy actions across 6 policy stages", options: { fill: { color: P.white }, fontSize: 8 } },
      { text: "Agenda setting high; implementation/evaluation low. No country has full lifecycle AI integration", options: { fill: { color: P.white }, fontSize: 8 } },
    ],
  ], {
    x: 0.3, y: 0.95, w: 9.4,
    colW: [1.5, 1.1, 1.3, 1.5, 2.2, 1.8],
    rowH: 0.7,
    border: { pt: 0.5, color: P.lightGray },
    fontFace: "Calibri",
    valign: "middle",
  });

  // Legend
  s6.addText("Theme codes:  ", {
    x: 0.3, y: 4.7, w: 1.2, h: 0.3,
    fontSize: 9, bold: true, color: P.navy, fontFace: "Calibri", margin: 0
  });
  const themeCodes = [
    { code: "AI_EVAL", color: "0369A1" },
    { code: "PARTICIPATORY_GOV", color: "7C3AED" },
    { code: "ADAPTIVE_REG", color: "059669" },
    { code: "EVIDENCE_IMPL", color: "D97706" },
    { code: "CLINICAL_HEALTH", color: "BE185D" },
  ];
  themeCodes.forEach((t, i) => {
    s6.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 1.5 + i * 1.5, y: 4.72, w: 1.4, h: 0.3,
      fill: { color: t.color }, line: { color: t.color }, rectRadius: 0.06
    });
    s6.addText(t.code, {
      x: 1.5 + i * 1.5, y: 4.72, w: 1.4, h: 0.3,
      fontSize: 8, bold: true, color: P.white, fontFace: "Calibri",
      align: "center", valign: "middle", margin: 0
    });
  });

  s6.addText("+ Add more rows (5–10 papers recommended for final presentation)", {
    x: 0.3, y: 5.1, w: 9.0, h: 0.35,
    fontSize: 10, italic: true, color: P.gray, fontFace: "Calibri", margin: 0
  });

  // ─── SLIDE 7: KEY FINDINGS + NEXT STEPS ─────────────────────────────────
  const s7 = pres.addSlide();
  s7.background = { color: P.light };
  s7.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: P.teal }, line: { color: P.teal } });
  s7.addText("6. Key Findings & Next Steps", {
    x: 0.4, y: 0.22, w: 8.4, h: 0.65,
    fontSize: 28, bold: true, color: P.navy, fontFace: "Trebuchet MS", margin: 0
  });
  s7.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 8.8, y: 0.18, w: 0.8, h: 0.45,
    fill: { color: P.teal }, line: { color: P.teal }, rectRadius: 0.08
  });
  s7.addText("06", {
    x: 8.8, y: 0.18, w: 0.8, h: 0.45,
    fontSize: 13, bold: true, color: P.white, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0
  });

  // Left column — Key Findings
  s7.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 0.95, w: 4.4, h: 0.4,
    fill: { color: P.navy }, line: { color: P.navy }
  });
  s7.addText("Key Findings (Emerging Pattern)", {
    x: 0.4, y: 0.95, w: 4.4, h: 0.4,
    fontSize: 12, bold: true, color: P.white, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0
  });

  const findings = [
    { title: "Governance develops during implementation", body: "Not pre-existing capacity but emerges through operational tensions — Jin Tian et al." },
    { title: "Pilot trap is a governance failure", body: "AI projects fail to sustain because organizational accountability boundaries are unclear" },
    { title: "Adaptive regulation > static \"future-proof\" law", body: "Schrepel: modular architecture + distributed sensing + pluralistic triggers" },
    { title: "Implementation & evaluation = lowest AI integration", body: "Lnenicka et al.: all 8 EU countries weak at implementation/evaluation stages" },
  ];

  findings.forEach((f, i) => {
    const yPos = 1.45 + i * 0.95;
    s7.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y: yPos, w: 4.4, h: 0.82,
      fill: { color: P.white }, line: { color: P.lightGray, width: 0.5 },
      shadow: { type: "outer", color: "000000", blur: 3, offset: 1, angle: 135, opacity: 0.06 }
    });
    s7.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y: yPos, w: 0.07, h: 0.82,
      fill: { color: P.teal }, line: { color: P.teal }
    });
    s7.addText(f.title, {
      x: 0.56, y: yPos + 0.05, w: 4.15, h: 0.32,
      fontSize: 10.5, bold: true, color: P.navy, fontFace: "Calibri", margin: 0
    });
    s7.addText(f.body, {
      x: 0.56, y: yPos + 0.38, w: 4.15, h: 0.4,
      fontSize: 9.5, color: P.gray, fontFace: "Calibri", margin: 0
    });
  });

  // Right column — Next Steps
  s7.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 0.95, w: 4.4, h: 0.4,
    fill: { color: P.teal }, line: { color: P.teal }
  });
  s7.addText("Next Steps", {
    x: 5.2, y: 0.95, w: 4.4, h: 0.4,
    fontSize: 12, bold: true, color: P.white, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0
  });

  const nextSteps = [
    "Expand DB to 50–80 papers (target: 30–50 in final synthesis)",
    "Fill data extraction table: populate 5–10 rows",
    "Systematic PRISMA: formal flow with exact counts",
    "Analyze cross-theme papers (intersection G1+G2, G3+G4...)",
    "Draft synthesis narrative: identify recurring patterns",
    "Prepare final literature review document",
  ];

  nextSteps.forEach((step, i) => {
    const yPos = 1.45 + i * 0.68;
    s7.addShape(pres.shapes.OVAL, {
      x: 5.3, y: yPos + 0.12, w: 0.28, h: 0.28,
      fill: { color: P.accent }, line: { color: P.accent }
    });
    s7.addText(String(i + 1), {
      x: 5.3, y: yPos + 0.12, w: 0.28, h: 0.28,
      fontSize: 10, bold: true, color: P.white, fontFace: "Calibri",
      align: "center", valign: "middle", margin: 0
    });
    s7.addText(step, {
      x: 5.68, y: yPos + 0.05, w: 3.85, h: 0.58,
      fontSize: 10, color: P.text, fontFace: "Calibri", margin: 0, valign: "middle"
    });
  });

  // ─── SLIDE 8: CLOSING ────────────────────────────────────────────────────
  const s8 = pres.addSlide();
  s8.background = { color: P.navy };
  s8.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 5.625,
    fill: { color: P.teal }, line: { color: P.teal }
  });
  s8.addShape(pres.shapes.RECTANGLE, {
    x: 0.18, y: 2.2, w: 3.5, h: 0.04,
    fill: { color: P.accent }, line: { color: P.accent }
  });
  s8.addText("Thank you", {
    x: 0.6, y: 1.2, w: 9.0, h: 1.0,
    fontSize: 42, bold: true, color: P.white, fontFace: "Trebuchet MS", margin: 0
  });
  s8.addText("Questions & Discussion", {
    x: 0.6, y: 2.35, w: 9.0, h: 0.6,
    fontSize: 22, color: P.accent, fontFace: "Calibri", margin: 0
  });
  s8.addText("Review Question: What methods exist for evaluating health AI systems in real-world deployment contexts, and how do governance structures shape their implementation, sustainability, and societal impact?", {
    x: 0.6, y: 3.2, w: 8.8, h: 1.0,
    fontSize: 13, italic: true, color: "94A3B8", fontFace: "Calibri", margin: 0
  });
  s8.addText("Project: github.com/Arkoys/ai-health-lit-review  ·  2026-04-13", {
    x: 0.6, y: 4.9, w: 9.0, h: 0.4,
    fontSize: 11, color: P.gray, fontFace: "Calibri", margin: 0
  });

  // Save
  const outPath = "/home/agent/ai-health-lit-review/outputs/slides/MIDTERM_PRESENTATION_2026-04-13.pptx";
  await pres.writeFile({ fileName: outPath });
  console.log("Saved:", outPath);
}

main().catch(err => { console.error(err); process.exit(1); });