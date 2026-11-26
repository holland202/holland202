# Public profile verification · 26 November 2026

ChatGPT performed these engineering checks under Chad Holland’s direction. The baseline was [merged PR #4](https://github.com/holland202/holland202/pull/4), main 3057153588a3909cc0a87c858023e2460e9358c4, implementation e6e44e338893e55327eb968a2a507f7c04b050c2. Findings describe the observed responses and tested browser only.

## Findings on the published profile

| Check | Observation |
|---|---|
| Graphics and layout | Signed-out Chromium loaded both SVGs on the live profile. At 1440 × 900 their widths were 846 CSS px. At 390 × 844 both were 308 px wide with no document overflow. The 12-unit captions shrank below 5 CSS px on mobile. |
| Motion | Screenshots about 0.85 s apart differed in the orbit area on both layouts. Reduced motion still produced differences, including in a new browser context with the preference set before navigation. The existing SVG media query alone failed this embedded-image check. |
| New destinations | Anonymous GETs returned 200 and matching page titles for all 23 distinct destinations in the lab, edge, failures and model sections. Coverage included six GitHub projects, the workflow, dashboard, four evidence links, the HF account, three model cards, three datasets and four Space landing pages. This tested navigation, not inference. Two previously successful evidence/workflow URLs returned temporary 503s in a second pass. |
| Existing features | Compared with pre-PR main 74142d7. Older workflows, scripts and checked-in contribution artwork were untouched. The live profile loaded the hero, badges, stats, streak, language, category, 31-day, 3D and GIF images on both viewports. Direct badge requests sometimes returned 403 while GitHub-served images displayed. LinkedIn returned 999 to an automated direct request. The old LDE model link was removed in #4 and returns 401 anonymously. Its public dataset opens. The renamed HF section lost its old fragment. |
| Refresh | Ran the merged generator after merge with normal, anonymous requests to the five allowed public branches. The JSON and both original SVGs were byte-identical to main. Separate commits/main requests matched all five full SHAs and UTC committer days. No publication was warranted. |
| Actions | Public workflow history returned only [pre-merge CI](https://github.com/holland202/holland202/actions/runs/45808080867). Its passing PR job did not exercise publication. Cron is 12:37 UTC daily, before the reported 12:39 UTC merge on the 26th. Hosted schedule, token write permission and actual changed-data push remain unobserved. |
| Publication integrity | Existing tests rejected HTTP failure and a wrong branch. A response with a valid date prefix followed by INVALID was accepted by the merged code. The write job also cloned a moving main after testing a pinned revision. A non-forced push already protects against a competing main update after checkout. |
| Statistics | Keep provider cards, rolling 31-day activity, year calendar and the dated category inventory separate. Units, windows and providers differ. Absolute provider totals could not be reconciled from the displayed cards. |

### Published telemetry independently checked against the public commit endpoint

| Repository | SHA prefix | UTC committer day |
|---|---|---|
| principia-artificialis | 86caa88fe79f | 2026-11-25 |
| sovereign-veritas | da6a96ae91c6 | 2026-11-14 |
| sovereign-memory-layer | 5054809d67c1 | 2026-11-13 |
| veritas-holo | d1291d187a49 | 2026-09-30 |
| veritas-science | 0c0a1b5cfffe | 2026-11-09 |

The draft changes README.md, scripts/research_lab.js, scripts/test_research_lab.js and .github/workflows/research-lab.yml. It adds two generated SVG variants and this report. The refresh job now checks out the tested event SHA. The token is scoped to contents:write in the refresh job and exposed to its publish step only. PRs run a read-only job. Both jobs have five-minute timeouts. There are five bounded anonymous fetches and no added runtime dependencies or tracking.

The unmodified baseline passed 5 Node tests and 11 Python tests. On the draft, 6 Node tests passed, the generator check matched, and all four SVGs parsed. A separate disposable checkout layout exercised the actual CLI with four good responses and one HTTP 429, invalid timestamp, or JSON decoding error. Each invocation exited 1 and SHA-256 of the snapshot and all four SVGs stayed unchanged. This covers bad inputs before writes. Local multi-file writes themselves are sequential. Git publishes them as a commit.

A Chromium preview of the proposed README picture markup at the measured widths selected the mobile telemetry at 390 px and the original at 1440 px. With normal motion the orbit frames differed at both widths. With reduced motion the static asset was selected and both frame pairs were pixel-identical. The narrower graphic and raw JSON link give two ways to read the dates. Actual Android, Safari, screen readers and rendering after an owner merge remain unverified.

## Phase two investigation

Public Principia source revision for this investigation: [86caa88](https://github.com/holland202/principia-artificialis/tree/86caa88fe79f5a67d80f818289c6db44ba3122fb). The entries below are feasibility findings. No experiments or cross-repository changes were made.

| Enhancement and objective | Source inspected, check and result | Scope, negative control and unknowns |
|---|---|---|
| A · Count research outcomes | [Structured evidence cards](https://github.com/holland202/principia-artificialis/tree/86caa88/data/dashboard/cards) distinguish question, protocol, execution, claim and reproduction. Read the two card schemas. They describe selected studies and do not supply a complete lab-wide denominator. | Report UNKNOWN for uncovered or ambiguous totals. Counting rules below. No counter implemented. |
| B · Navigate a dated timeline | The profile dates the owner's start to February 2026. Public records include the [SEC-004 failure](https://github.com/holland202/sovereign-veritas/pull/76), [SEC-005 correction](https://github.com/holland202/sovereign-veritas/pull/98), [TLM-004 results](https://github.com/holland202/principia-artificialis/blob/86caa88/experiments/tiny_lm/RESULTS_TLM004.md) and the profile merge. | February is a self-reported start with month precision. A first-experiment date, complete release inventory and independently sourced reproduction chronology remain unknown. Use separate event IDs for failures and corrections. A merge timestamp dates publication only. No timeline implemented. |
| C · Show public AI collaboration | Read [the public Claude and ChatGPT relay](https://github.com/holland202/principia-artificialis/pull/172#issuecomment-7064637539). The public API returned 49 comments in the inspected response. The note bodies include agent attribution. | Use a proposal link, implementation SHA, review permalink and explicit owner decision as distinct events. Shared-login identity or a bot reply alone cannot establish authorship or approval. Historical attribution completeness is unknown. No activity counter implemented. |
| D · Offer reproducible challenges | [reproduce.json](https://github.com/holland202/principia-artificialis/blob/86caa88/data/dashboard/reproduce.json) contains two entries with claims, sources, prerequisites, steps, expected results, controls and limits. The hash-audit entry includes a pinned ledger and a one-character negative control. | Draft README links to the existing board. Both entries describe original-author checks. No challenge rerun or independent reproduction was counted. Future entries should pin the executable revision as well as the evidence. |
| E · Compare small models on equivalent tasks | Compared the two linked model descriptions and inspected [TLM-004](https://github.com/holland202/principia-artificialis/blob/86caa88/experiments/tiny_lm/RESULTS_TLM004.md). The published matched comparison has two seeds, a width difference and a rescored baseline. Tiny Engine copying and Tiny Stories generation have different endpoints. | No cross-model ranking published. Require identical evaluator, split, task, metric, decoding budget and declared seed policy. Reject mixed endpoints. Hardware, runtime and precision must match for speed comparisons. A shared evaluation for the listed models remains unknown. |
| F · Navigate the existing ecosystem | Read the [constellation records](https://github.com/holland202/principia-artificialis/blob/86caa88/data/dashboard/research_constellation.json), dashboard sections, JavaScript and CSS. Existing fragment links select evidence panels. Styles include mobile breakpoints and a motion preference. | Draft README links the map directly to the constellation. Its local static image fallback works without animation. No new site or dashboard modification. Cross-browser dashboard interaction has not been certified. |

### Proposed counting rules for A

1. Declare the included public registries, revision, coverage date and unit for each metric. Deduplicate by canonical study ID plus hypothesis, prediction or question ID. Retain amendments and links to duplicate reports. Track competing verdicts explicitly.
2. Count a registered hypothesis only with a dated registration before execution. Count predictions held or refuted only against their registered endpoint, scoped run and cited verdict. A failed qualification does not refute every hypothesis in its study. An inconclusive or conflicting verdict stays unresolved.
3. Count an unexecuted experiment only if a record explicitly states its protocol and pending execution status at the snapshot date. Count an open question only if its registry explicitly tracks it as unresolved. Neither silence nor absence of output establishes either status.
4. Count independent reproductions by distinct externally performed run and identified target claim. Require a public report, revision, method, result and documented independence from the original work. Record operator and AI assistance separately. An author rerun, AI review or repeat citation adds no independent run.
5. Report UNKNOWN when coverage, identity, timing, status or independence is unresolved. Zero requires complete enumerated coverage under the stated rules. Publish the included IDs beside each count.

All six investigations share this report in the profile draft. D and F also change README navigation. A, B, C and E have no feature code or experimental runs. The draft PR identifies the actual revision and tests. Owner approval is required to merge. Changes in Principia would require separate authorization.
