# Chapter 13 — Risks, Assumptions, Dependencies, and Constraints

## Research Foundations

Risk analysis supports decisions by making uncertainty visible. This chapter uses established ideas
from ISO 31000 and the Project Management Institute as background, but presents a deliberately small
educational model. The taxonomy is an organizing aid, not a universal standard.

## Professional Practice

A Sales Engineer should preserve provenance, state uncertainty honestly, and invite accountable
roles to judge consequence and response. A register informs a decision; it does not make one.

## Educational Heuristic

Use six separate questions: **might it happen?** (risk), **are we treating it as true?**
(assumption), **do we rely on it?** (dependency), **must we respect it?** (constraint), **has it
already happened?** (issue), and **has it been established?** (unknown). A decision is a documented
choice among alternatives. Related does not mean interchangeable.

## Subjective Professional Judgment

Likelihood, impact, ownership, and response adequacy depend on context and stakeholder judgment.
The program therefore preserves two qualitative dimensions and never multiplies them, colors them,
or ranks candidates with a hidden total.

## Learning Objectives

Learners can classify records, write cause–event–consequence statements, trace risks to prior work,
plan validation and responses, identify ownership gaps, compare applicability, and recognize
residual risk without invented precision.

## What Is Risk?

A **risk** is an uncertain future event or condition that could affect an objective. It is not a
synonym for everything undesirable.

## Risks vs. Issues

An **issue** already exists or has occurred. Harbor Street staff currently copy confirmed lessons
between artifacts: that supported current-state condition is `ISS-001`. A future failure of a
candidate interface is a risk.

## Risks vs. Assumptions

An **assumption** is treated as true for analysis but is not fully established. `ASM-001` says the
calendar can receive confirmed lessons programmatically. It remains unvalidated rather than being
silently promoted to fact. **Unknown != Risk**: an unknown can create or conceal a risk, but needs a
future event and consequence to become a risk statement.

## Risks vs. Dependencies

A **dependency** is something an approach relies on. Budget approval, defined inquiry states, and
technical ownership are dependencies with their own status, consequence, and resolution action.
Their uncertain failure to arrive on time can be the cause of a risk.

## Risks vs. Constraints

A **constraint** is an established boundary. **Constraint != Risk.** “No approved budget has yet
been established” is a customer constraint and unresolved commercial dependency. “If funding is
not approved before implementation, scope may be delayed or reduced” would be the related risk.
The register separately labels laboratory constraints such as determinism and no assumed API.

## Unknowns

Unknown means evidence has not established an answer. It does not mean absent or infeasible:
`UNKNOWN != ABSENT` and `UNKNOWN != NOT_FEASIBLE`. “The calendar has no API” is unsupported while
interface availability is only unknown.

## Cause–Event–Consequence Statements

`RISK-001` preserves the logic:

- **Cause:** calendar interface capabilities remain unverified.
- **Event:** the integration cannot exchange confirmed lesson information as designed.
- **Consequence:** redesign, continued manual entry, or additional cost may result.

All three fields are required, while the rendered prose can vary.

## Risk Categories

The small taxonomy includes technical, operational, data, security, privacy, organizational,
adoption, commercial, schedule, maintenance, integration, process, and value realization. A risk
may use multiple categories. Categories help retrieval; they are neither rankings nor standards.

## Likelihood and Impact

`LOW`, `MODERATE`, and `HIGH` communicate a contextual qualitative evaluation. `UNKNOWN` says the
evidence cannot support one; `NOT_EVALUATED` says analysis has not occurred. Likelihood and impact
remain separate and carry an explanation. No aggregate score is calculated.

## Risk Responses

Responses are avoid, reduce, transfer, accept, investigate, contingency, or not planned. Transfer
may share contractual responsibility but never makes consequences disappear. Each response states
an action, trigger, expected effect, remaining uncertainty, and responsible role—or **NOT
ESTABLISHED** when authority is unknown. A planned response does not automatically close a risk.

## Mitigation and Contingency

Mitigation occurs before an event to reduce likelihood or consequence: conduct a proof of concept
before committing to integration. Contingency occurs if it happens: use the documented manual
scheduling handoff if the selected calendar provides no supported interface.

## Residual Risk

After a proof of concept, a supported interface may still impose limits, duplicate-delivery
behavior, or operational constraints. Mitigation does not imply zero risk.

## Risk Ownership

Ownership is recorded only when established. `RISK-001` and unresolved technology dependencies say
“NOT ESTABLISHED”; the fixture does not invent organizational authority.

## Assumption Validation

An assumption can be unvalidated, validation planned, validated, disproved, or not yet validatable.
A validation action should identify observable evidence and a role when established.

## Dependency Management

Each dependency records what relies on it, current status, evidence, effect if unmet, owner, and next
action. The service surfaces unresolved dependencies missing either an owner or action.

## Approach-Specific Risk Profiles

Configure-existing, buy, build, and status-quo views show explicit applicability per risk. Data
quality spans several change approaches; maintenance ownership applies to custom build; integration
feasibility applies only to approaches that propose it. The matrix does not declare one profile
safer overall.

## Risk and Value

Chapter 12's `BEN-001` hypothesizes reduced manual effort. `RISK-001` shows that infeasible
integration could prevent that benefit, while `RISK-004` shows that a missing baseline could make it
impossible to demonstrate. No financial value is recalculated.

## Harbor Street Music Walkthrough

The canonical analysis reuses `E2` manual copying, `E5` unknown technology ownership, `E7` budget
constraint, Chapter 10 interface uncertainty, Chapter 11 data readiness, and Chapter 12 baseline
unknowns. It explicitly authors four risks rather than mining free text.

## Risk Register

The register includes integration feasibility, inquiry data quality, custom maintenance ownership,
and value demonstration. Budget remains a constraint/dependency. Existing manual copying remains
an issue. Risks retain authored identifier order—not importance order.

## Traceability

A full path remains inspectable:

`E2 → REQ-004 → CAP-004 → GAP-004 → APP-003 → ARCH-001 → FLOW-004 → INT-003 → ASM-001 → RISK-001 → RESP-001 → RES-001`

This connects discovery, requirement, capability, gap, approach, design, premise, risk, response,
and residual risk.

## Mermaid Diagrams

The report generates both a relationship flowchart from populated model relationships and the
implemented lifecycle: Identified → Under Review → Response Planned → Mitigated or Accepted, with
supported review and closure transitions.

## Executable Experiments

`assumption_disproved_experiment` adds experimental evidence, creates a new disproved assumption,
changes selected-configuration feasibility, updates the related risk consequence, and makes the
manual contingency relevant. `mitigation_added_experiment` adds a proof-of-concept response and
residual risk to a new register. Both retain their original analysis unchanged; neither changes a
numeric score.

## Debugging Laboratory

Run `python examples/debug_chapter_13.py` or select **Debug Chapter 13 Risks**. Step through
architecture/integration/automation → assumption/dependency → risk → cause/event/consequence →
response → residual risk. Inspect `risk`, `cause`, `event`, `consequence`, `likelihood`, `impact`,
`assumptions`, `dependencies`, `constraints`, `response`, `residual_risk`, and
`validation_findings`.

## Exercises

### Exercise A
Classify “The current process uses two separate tools.” **Expected:** current-state issue or fact,
depending on context.

### Exercise B
Classify “The calendar probably has an API.” **Expected:** unvalidated assumption.

### Exercise C
Classify “No software budget has been approved.” **Expected:** constraint, unresolved dependency,
or established fact—not automatically a risk.

### Exercise D
Rewrite “The calendar API is unknown.” **Possible answer:** Because calendar capabilities are
unknown, the proposed integration may not be feasible, which could require redesign or continued
manual work.

### Exercise E
A mitigation exists. Is the risk gone? **Expected:** not necessarily; residual risk may remain.

### Exercise F
Why avoid arbitrary totals? **Expected themes:** qualitative context differs, totals imply
unsupported precision, stakeholder priorities differ, evidence may be incomplete, and decision
makers need the causes and consequences.

## Chapter Summary

We now understand the major uncertainties, dependencies, constraints, and risks associated with
each candidate approach.

The next question is: **How should a Sales Engineer compare alternatives and make a transparent
recommendation without hiding judgment inside a score?** That belongs in Chapter 14.

## Glossary

- **Assumption:** premise treated as true but not fully established.
- **Constraint:** established boundary.
- **Contingency:** action used if a risk occurs.
- **Decision:** documented choice among alternatives.
- **Dependency:** prerequisite relied upon.
- **Issue:** existing or occurred problem.
- **Mitigation:** pre-event action intended to reduce likelihood or effect.
- **Residual risk:** uncertainty remaining after a response.
- **Risk:** uncertain future event or condition affecting an objective.
- **Unknown:** information not yet established.

## References / Suggested Reading

- International Organization for Standardization, *ISO 31000:2018 Risk management — Guidelines*.
- Project Management Institute, *A Guide to the Project Management Body of Knowledge (PMBOK® Guide)*,
  Seventh Edition, 2021.
- United Kingdom Government, *The Orange Book: Management of Risk — Principles and Concepts*, 2023.
