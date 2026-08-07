# Chapter 19: End-to-End Sales Engineering Engagement Simulator

## Research Foundations

This capstone applies the evidence, requirements, architecture, risk, decision, delivery, and
measurement practices introduced in Chapters 0–18. Consult each chapter's references for its
specific professional foundations; this chapter does not invent new authorities.

## Professional Practice

A trustworthy recommendation is traceable to customer evidence. Completing an analysis is not the
same as receiving approval, implementing a solution, achieving adoption, or validating value.

## Educational Heuristic

Follow the chain from evidence to requirement, capability, gap, approach, architecture,
recommendation, proposal scope, and success measure. A missing link is a finding, not permission to
guess.

## Subjective Professional Judgment

Evidence constrains judgment but does not eliminate it. The Chapter 14 recommendation keeps its
professional rationale, tradeoffs, conditions, confidence, and unresolved concerns visible.

## Learning Objectives

Learners execute a deterministic engagement, inspect stage results and dependencies, validate
cross-chapter identifiers, compare isolated scenarios, and explain why later artifacts cannot erase
earlier uncertainty.

## Purpose of the Capstone

Harbor Street Music asks whether its complete analysis can execute while preserving one inspectable
evidence chain. Chapter 19 coordinates the real chapter services rather than recreating their rules.

## Engagement Stages

Situation, investigation, discovery, process, stakeholders, requirements, capabilities, gaps,
approaches, architecture, integrations, automation, value, risks, recommendation, demonstration,
proposal, handoff, and success measurement execute in stable order. Statuses distinguish complete,
complete with findings, blocked, not ready, not applicable, and not executed.

## Orchestration vs. Reimplementation

The orchestration service loads the canonical fixtures and calls each existing analyzer and report
renderer. It owns sequence, dependency checks, trace indexing, and package composition—not chapter
business rules.

## Stage Dependencies

Requirements depend on discovery, process, and stakeholders. Capabilities lead to gaps and
approaches. Architecture enables integration and automation analysis. Value and risk precede the
recommendation. Recommendation and demonstration precede proposal; proposal precedes handoff;
requirements and handoff precede measurement planning.

## Cross-Chapter Invariants

- Requirements require evidence; capabilities require requirements; gaps require capabilities.
- Approaches require gaps; components require capability, requirement, constraint, or dependency.
- Proposal scope requires recommendation traceability; delivery scope cannot silently expand it.
- Measures require intended outcomes or requirements.
- Recommendation is not approval. Approval is not delivery readiness.
- Demonstration is not production readiness. Implementation is not value realization.
- Unknown is not absent, and a missing financial value is not zero.

## End-to-End Traceability

Immutable typed links retain the repository's stable identifiers, including its early `E2` evidence
convention. Compatibility is preferable to renaming public identifiers. Validation surfaces missing,
duplicate, orphaned, or unsupported reasoning as learner-friendly findings.

## Graceful Blocking

Removing an upstream stage marks it blocked. Its dependents report which prerequisite is unavailable;
independent stages can still execute. Programming errors continue to fail loudly.

## Harbor Street Music Engagement

The original inquiry, current spreadsheet and calendar, manual follow-up, stakeholder evidence,
requirements, and no-approved-budget constraint remain unchanged.

## Canonical Findings

The Chapter 14 conditional recommendation is preserved. The Chapter 16 proposal is an unapproved
decision request. Chapter 17 is not ready for delivery while approval and other conditions remain
unresolved. Chapter 18 defines a partially ready measurement plan but reports no operational result
or realized benefit.

## Engagement Package

`sales-lab engagement --output-dir build/engagement` writes chapter reports, customer proposal,
internal traceability, handoff, success plan, capstone summary, engagement flow, and traceability
diagram with stable filenames. Generated build output is not source material.

## Scenario Experiments

- **Integration feasible:** fictional interface, access, ownership, and duplicate evidence changes
  downstream feasibility, risks, recommendation conditions, proposal, readiness, and measurement.
- **No budget approval:** funding remains unknown rather than zero; process and validation work may
  remain possible while purchases stay constrained.
- **Higher scale:** fictional volume can change requirements and value hypotheses without proving a
  custom build is necessary.
- **Premature custom build:** the same unsupported mobile application is detected at capability,
  approach, architecture, proposal, and delivery layers.

All scenario objects are immutable, and the canonical engagement remains unchanged.

## Scenario Comparison

`sales-lab engagement --scenario comparison` shows changed and unchanged stages without a winner,
ranking, score, win probability, or forecast.

## Engagement Diff

Structured diffs identify added evidence, changed assumptions, affected stages, findings, and
unchanged lifecycle conclusions. They do not compare giant report strings.

## Mermaid Diagrams

The engagement diagram is generated from the dependency map. A focused diagram uses actual trace
links beginning with `E2` and continuing through `REQ-001`, `CAP-001`, `APP-001`, `ARCH-001`, and
`REC-001` toward proposal and measurement artifacts.

## Debugging Laboratory

Run `examples/debug_chapter_19.py` with **Debug Chapter 19 Engagement**. Inspect `engagement`,
`stage_results`, `trace_links`, `validation_findings`, `recommendation`, `proposal`, `handoff`, and
`measurement_plan`; then compare `integration_feasible` without relying on line-number breakpoints.

## Exercises

**A.** A recommendation exists but approval is absent. The handoff is not fully ready.

**B.** A capability appears in architecture without a requirement. Report an unjustified component.

**C.** A custom mobile application is inserted into proposal scope. Detect missing requirement,
capability, gap, approach, and recommendation traceability.

**D.** Add integration evidence. Architecture feasibility, integration findings, risk,
recommendation, scope, readiness, and measures may change; earlier facts do not automatically change.

**E.** Why reuse services? One source of truth reduces inconsistency, strengthens tests and
maintenance, aligns reports, and lets improvements propagate.

**F.** Why is a complete engagement not a complete customer project? Analysis may complete while
approval, implementation, adoption, and value realization remain unresolved.

## Volume I Summary

The learner can now listen before proposing; separate facts and assumptions; model current work;
define requirements; map capabilities and gaps; compare approaches; design architecture,
integration, and automation boundaries; analyze value and risk; recommend conditionally;
demonstrate narrow behavior; prepare a decision package; hand off responsibly; plan measurement;
and preserve the evidence chain.

## Glossary

**Engagement stage:** One explicit analytical lifecycle step. **Trace link:** A typed relationship
between structured artifacts. **Blocking:** A dependency outcome that prevents downstream execution.
**Scenario:** An immutable fictional evidence variation. **Realized value:** An outcome supported by
post-implementation measurement, never inferred from a recommendation.

## References / Suggested Reading

Review the references in Chapters 0–18. Suggested internal reading: the requirements, architecture,
decision, proposal, handoff, and customer-success chapters and their executable laboratories.
