# Coding Protocol — Three-Gap Framework Empirical Validation

**Project:** AI Health Literature Review
**Version:** 1.0
**Date:** 2026-06-02
**Corpus:** Priority 3 papers (n=87), structured for PhD literature review
**Coder:** LLM-assisted coding (GPT-4 class), with manual verification on 10% sample

---

## 1. Purpose

This protocol operationalizes the three-gap framework (Ecological Validity Gap,
Governance Capacity Deficit, Pilot Trap) into a structured coding instrument
applied to the full Priority 3 corpus. The goal is to **empirically test**
whether the three gaps co-occur and interact in the literature, rather than
asserting that they do a priori.

The findings of this structured analysis will determine:
- Whether the three-gap framework is supported by the evidence
- Which gap is most frequently documented
- Which causal pathways (interactions) are dominant
- What the regulatory comparison in Phase 2 should be focused on

---

## 2. Operationalized Definitions

### Gap 1 — Ecological Validity Gap

**Construct definition:** The paper critiques or documents failures of
evaluation methodology to reflect real-world clinical complexity. The paper
argues that the way AI is evaluated (in studies) systematically diverges
from the way AI performs (in deployment).

**Code as 1 if the paper contains EITHER:**
- (a) A documented failure of validation methodology to reflect real-world
  clinical conditions, OR
- (b) An explicit critique of evaluation practices that argues they are
  insufficient for real-world deployment, OR
- (c) An empirical demonstration that controlled-validation performance does
  not predict deployment performance.

**Indicators (any one is sufficient):**
- Single-site validation only
- Retrospective-only evaluation (no prospective or RCT)
- Lack of external validation (no multi-site / multi-cohort)
- Poor or absent subgroup analysis (e.g., by demographics, comorbidity, severity)
- Algorithmic drift concerns (model performance degradation over time)
- Overreliance on accuracy/AUC metrics without clinical outcomes
- Limited generalizability explicitly discussed
- Mention of "dataset shift", "domain shift", "distribution shift"
- Mention of "external validity", "ecological validity", "real-world
  performance" in a critical context

**Code as 0 if:**
- The paper describes an AI system with rigorous evaluation but does not
  critique the evaluation methodology, OR
- The paper reports retrospective metrics without claiming they are
  sufficient, OR
- The paper is purely technical (architecture, training method) with no
  evaluation reflection.

**Edge case — code 0 even if AUC is reported:** A paper that reports
"we achieved 0.95 AUC" without discussing what AUC does and does not capture
is NOT coded as Gap 1. Gap 1 requires the paper to *critique* the evaluation
method, not merely *use* it.

**Edge case — code 1 if drift is mentioned as a structural problem:** A
paper that lists "algorithmic drift" as a *problem the field faces* (not
merely a technical footnote) is coded 1.

---

### Gap 2 — Governance Capacity Deficit

**Construct definition:** The paper documents inadequate governance
infrastructure, organizational readiness, accountability mechanisms,
monitoring capacity, or institutional preparedness for AI deployment. The
paper argues that health systems are not organizationally ready for the
AI they are being asked to deploy.

**Code as 1 if the paper contains EITHER:**
- (a) A documented failure of governance infrastructure to support AI
  deployment, OR
- (b) An explicit argument that current organizational capacity is
  insufficient, OR
- (c) An empirical observation that AI deployment is constrained by
  governance gaps (not technical gaps), OR
- (d) A framework or argument for what governance capacity *should* look
  like, presented in the context of documenting that it currently *does not*
  exist.

**Indicators (any one is sufficient):**
- Missing accountability structures
- Weak or absent post-market monitoring
- Regulatory assumptions of capacity (e.g., "the AI Act assumes hospital
  compliance structures that don't exist")
- Governance built *during* deployment rather than *before* deployment
- Organizational coordination failures (e.g., unclear roles between
  clinicians, IT, AI vendor, administration)
- Maturity model / readiness assessment that documents current low maturity
- Mention of "institutional capacity", "organizational readiness", "AI
  governance", "post-market surveillance" in a critical context
- Argument that health systems need to *build* capacity to deploy AI

**Code as 0 if:**
- The paper proposes a governance framework in the abstract without
  documenting a current deficit, OR
- The paper describes AI regulation as a legal/policy problem without
  addressing the organizational/institutional capacity dimension, OR
- The paper is purely technical with no governance discussion.

**Edge case — distinguish from Gap 3:** Gap 2 is about *capacity to
govern AI* (does the institution have the structures to oversee AI?).
Gap 3 is about *ability to scale AI into routine practice* (does the
institution successfully implement AI?). A paper about clinical AI
adoption barriers is Gap 3; a paper about whether the institution can
*monitor* deployed AI is Gap 2.

**Edge case — distinguish from Gap 1:** Gap 1 is about *evaluation
methodology* (is the validation rigorous enough to be trusted?).
Gap 2 is about *governance structures* (does the institution have the
capacity to act on what evaluation tells us?). They are related (a
governance deficit may produce an ecological validity gap) but
operationally distinct.

---

### Gap 3 — Pilot Trap

**Construct definition:** The paper documents failures in translating AI
systems from pilot projects into routine clinical practice. The paper
argues that AI systems frequently demonstrate value in pilots but fail
to scale, sustain, or integrate into clinical workflow.

**Code as 1 if the paper contains EITHER:**
- (a) A documented failure of an AI pilot to scale to routine practice, OR
- (b) An explicit argument that the gap between pilot success and routine
  deployment is a structural problem, OR
- (c) An empirical demonstration of scale-up / sustainability / adoption
  failure, OR
- (d) An analysis of barriers to clinical AI implementation that goes
  beyond technical accuracy to include workflow, organizational, or
  sustainability factors.

**Indicators (any one is sufficient):**
- Scale-up failures (pilot succeeds, deployment fails)
- Workflow integration problems (AI doesn't fit clinician workflow)
- Sustainability challenges (pilot funding ends, system abandoned)
- Implementation barriers (cultural, organizational, financial, training)
- Adoption failures despite positive pilot outcomes
- Mention of "pilot trap", "pilotitis", "implementation gap", "adoption
  gap", "sustainability"
- Use of NASSS framework or similar implementation science frameworks
- Argument that clinical AI implementation requires more than technical
  accuracy

**Code as 0 if:**
- The paper reports a successful deployment without discussing
  generalizability of the success, OR
- The paper is purely about AI development with no implementation
  discussion, OR
- The paper focuses on pre-deployment validation (that is Gap 1) without
  discussing post-deployment outcomes.

**Edge case — distinguish from Gap 2:** Gap 2 is about *governance
capacity* (institutional structures to oversee AI). Gap 3 is about
*implementation success* (whether AI actually gets used in clinical
practice). A paper about *why clinicians don't trust AI* is Gap 3; a
paper about *who is responsible when AI fails* is Gap 2.

**Edge case — distinguish from Gap 1:** Gap 1 is about *evaluation
quality*. Gap 3 is about *deployment success*. A paper that proves
AI works in a controlled trial but doesn't discuss real-world deployment
is Gap 1 only. A paper that discusses why real-world deployment fails
(even if the controlled results were good) is Gap 3.

---

### Interaction Variable

**Construct definition:** The paper explicitly argues that one gap
contributes to or causes another gap. This is a SECOND-ORDER coding
(only coded after the three primary gaps are coded).

**Code as 1 if the paper contains EITHER:**
- (a) An explicit causal or contributing argument linking one gap to
  another, OR
- (b) A theoretical model or empirical observation that implies a
  causal pathway between gaps.

**Possible interactions to code (binary, multiple may apply):**
- Gap 1 → Gap 2 (evaluation failure causes governance deficit)
- Gap 1 → Gap 3 (evaluation failure causes pilot trap)
- Gap 2 → Gap 3 (governance deficit causes pilot trap)
- Gap 2 → Gap 1 (governance deficit produces weak evaluation) — rare
- Gap 3 → Gap 2 (pilot failure reveals governance gap) — feedback loop
- Gap 3 → Gap 1 (deployment failure prompts re-evaluation) — feedback loop
- Multi-gap interaction (3+ gaps in single causal chain)

**Code as 0 if:**
- The paper documents multiple gaps but does not link them causally, OR
- The paper only describes one gap.

**Edge case — temporal vs causal:** A paper saying "after the pilot
failed, the institution built governance" is a feedback interaction
(Gap 3 → Gap 2), not absence of interaction. A paper saying "pilot
failure and governance deficit both occurred" with no linkage is Gap
3 + Gap 2 present, but no interaction.

**Edge case — explicit vs implicit linkage:** "Explicit" includes (a)
direct causal language ("X causes Y", "X drives Y", "X leads to Y")
AND (b) strong implicit linkage through a proposed framework that
models one gap as producing or constraining another (e.g., the FDA's
"lifecycle approach" implicitly links evaluation gaps to governance
needs). Code the latter with `coder_confidence = medium`.

**Edge case — feedback loops:** When a paper documents BOTH a forward
causal claim (Gap A → Gap B) AND a feedback claim (Gap B → Gap A),
code the forward direction as the primary `interaction_directions`
entry and the feedback direction in the `notes` field. This avoids
double-counting multi-directional interactions.

---

## 3. Coding Procedure

### Step 1 — Input
For each paper, the coder receives:
- Title
- Authors
- Year
- Abstract (full text)
- Source venue

### Step 2 — Output Format
The coder outputs a JSON object:

```json
{
  "paper_id": "arxiv:2401.12345",
  "title": "...",
  "year": 2024,
  "gap1_ecological_validity": 0,
  "gap1_evidence": "Verbatim quote from abstract supporting the coding (max 200 chars). 'N/A' if gap1=0.",
  "gap1_indicators": ["retrospective-only", "no external validation"],
  "gap2_governance_capacity": 1,
  "gap2_evidence": "...",
  "gap2_indicators": ["missing accountability structures"],
  "gap3_pilot_trap": 0,
  "gap3_evidence": "N/A",
  "gap3_indicators": [],
  "interaction_present": 1,
  "interaction_directions": ["gap1→gap2"],
  "interaction_evidence": "...",
  "coder_confidence": "high|medium|low",
  "notes": "Free-text observation or flag for human review."
}
```

### Step 3 — Confidence Rating
- **High:** Clear evidence in abstract; indicators unambiguously present.
- **Medium:** Some evidence but ambiguous; abstract doesn't address
  context needed for full confidence.
- **Low:** Abstract is sparse; coding is best-guess; flagged for manual
  review.

### Step 4 — Verification
- 10% of papers (n=9) are independently re-coded manually.
- Agreement rate computed per gap.
- Disagreements are resolved by re-reading the abstract and refining the
  coding rule if needed.

---

## 4. Decision Rules for Edge Cases

| Situation | Code | Rationale |
|-----------|------|-----------|
| Paper proposes a governance framework but doesn't document a current deficit | Gap 2 = 0 | Framework proposals are Gap 2 only if they document a deficit to be addressed |
| Paper mentions "regulatory compliance" as a checkbox item, not as a problem | Gap 2 = 0 | Compliance without critique is not a governance deficit |
| Paper shows high AUC in retrospective study without external validation | Gap 1 = 0 *unless* paper explicitly notes this as a limitation | Reporting results ≠ critiquing methodology |
| Paper discusses barriers to clinical AI adoption (cultural, workflow) | Gap 3 = 1 | Adoption barriers are pilot-trap indicators |
| Paper reports both a successful pilot AND a successful scale-up | Gap 3 = 0 | Successful scale-up is the *absence* of the pilot trap |
| Paper documents a feedback loop ("pilot failure revealed governance gap") | Interaction = 1 with direction Gap 3 → Gap 2 | Feedback loops are causal claims |
| Abstract is too short to code confidently | Confidence = low; flag for full-text review | Preserve uncertainty rather than guess |
| Paper is a pure technical contribution (new architecture, new training method) | All gaps = 0 | No governance/evaluation/implementation discussion in abstract |

---

## 5. Quality Control

1. **Inter-coder agreement:** Manual verification of 9 papers (~10%)
   independently re-coded. Agreement rate computed as % of (gap1, gap2, gap3,
   interaction) tuples matching.
2. **Confidence distribution:** Reported in results. Papers coded as "low"
   confidence are flagged for full-text review if disagreements are systematic.
3. **Saturation check:** After coding 30, 60, 87 papers, recompute the
   frequency distribution. If frequencies stabilize (i.e., last 27 papers
   don't shift the dominant gap), coding can be considered saturated.
4. **Transparency:** All raw codings, including low-confidence ones, are
   published in the supplementary file. The reader can see what was coded
   and on what basis.

---

## 6. Limitations of This Protocol

1. **Abstract-level coding:** Full-text review would be more rigorous, but
   abstract-level is the standard for systematic content analysis at this
   scale (n=87). Low-confidence papers are flagged.
2. **Binary coding:** A 0/1 coding loses nuance (e.g., a paper might
   strongly document one gap and weakly document another). For this
   analysis, binary is sufficient to test the framework. Future work could
   use 0/1/2 ordinal coding.
3. **LLM-as-coder:** The coder is an LLM, not a human domain expert.
   Verification on 10% mitigates but does not eliminate this. Codings are
   reproducible (same input → same output) but may miss tacit knowledge
   that a human expert would apply.
4. **English-only:** All papers in the corpus are English-language. The
   framework may not generalize to non-English health AI governance
   literature.

---

## 7. Pilot Test

Before bulk coding, this protocol will be applied to 5 "gold standard"
papers selected to span the gap space:

1. **Pham (2025) — Ethical and legal framework** — Expected: Gap 2 = 1, possibly Gap 1 = 1, Gap 3 = 0. This is a regulatory/governance review.
2. **Tian (2026) — Pilot Trap** — Expected: Gap 3 = 1, Gap 2 = 1, possibly Gap 1 = 0. This is the canonical pilot-trap paper.
3. **FDA Perspective on AI regulation** — Expected: Gap 2 = 1 (regulatory capacity assumptions), Gap 1 = 0 or 1, Gap 3 = 0. This is a regulatory perspective.
4. **OpenMRF** — Expected: Gap 1 = 1 (reproducibility / validation framework), Gap 2 = 0, Gap 3 = 0. This is a technical infrastructure paper.
5. **TRAC-Pain** — Expected: All gaps = 0 (clinical protocol paper, no governance discussion).

The 5 pilot codings will be reviewed before bulk coding begins.
