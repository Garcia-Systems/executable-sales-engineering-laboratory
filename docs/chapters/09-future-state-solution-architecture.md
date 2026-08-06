# Chapter 9 — Future-State Solution Architecture

> Architecture begins with responsibilities and boundaries, not product names.

## Research Foundations

This chapter uses established systems ideas: boundaries make a system's scope explicit; views help
different concerns remain distinguishable; and decisions retain reasons and alternatives. The
executable model applies these ideas narrowly to an evidence-traceable sales-engineering exercise.

## Professional Practice

Solution architecture explains how responsibilities cooperate to satisfy needs. A practitioner
makes the boundary, actors, logical components, information movement, assumptions, dependencies,
and unresolved questions inspectable before selecting implementation technology.

## Educational Heuristic

The component categories and qualitative comparison dimensions are teaching aids, not a universal
architecture standard. They create useful questions; they do not replace organizational methods.

## Subjective Professional Judgment

Where to draw a boundary, how finely to divide responsibilities, and which tradeoffs matter require
contextual judgment. The engine validates authored facts and links. It does not decide that one
candidate is correct.

## Learning Objectives

After executing this chapter, you can distinguish architecture levels; identify actors, external
systems, components, connections, and flows; trace components to capabilities and requirements;
compare alternatives; and detect incomplete, unjustified, or feasibility-dependent designs.

## What Is Solution Architecture?

Solution architecture is a coherent account of responsibilities, boundaries, interactions, and
decisions that could satisfy established needs. It is not a fashionable-technology inventory. A
logical chain such as **Prospective Student → Inquiry Management → Follow-Up Tracking → Lesson
Scheduling → Music Instructor** is more useful initially than unsupported choices of frameworks,
databases, clouds, containers, or protocols.

## Business vs. Logical vs. Integration vs. Physical Architecture

| View | Question | Chapter 9 treatment |
| --- | --- | --- |
| Business / process | Who does what? | Reuses established roles and workflow evidence. |
| Logical | What responsibilities exist? | Primary focus: inquiry, follow-up, and scheduling. |
| Integration | How is information exchanged? | Names connections and flows; retains unknown mechanisms. |
| Physical / technology | Which products and infrastructure implement it? | Explicitly deferred unless evidence justifies it. |

Logical architecture is not a database schema, API contract, or deployment topology.

## System Boundaries

`INSIDE SOLUTION BOUNDARY` means the candidate owns a logical responsibility. `EXTERNAL` means it
interacts with something outside that responsibility. The existing calendar is an evidenced current
resource; calling its interface unknown neither invents an API nor declares integration impossible.

## Actors

The scenario represents Prospective Student / Parent, Authorized Staff, and Music Instructor as
actors. Actors are not implementation components. Their stakeholder identifiers retain the link to
Chapter 4 rather than copying disconnected stakeholder claims.

## Components

Components describe cohesive responsibilities. `USER_INTERFACE`, `WORKFLOW`, `DATA`,
`INTEGRATION`, `EXTERNAL_SYSTEM`, `REPORTING`, and `IDENTITY` are transparent educational labels.
Every component needs a capability, requirement, constraint, or architectural-necessity reason.

## Information Flows

A flow names its source-to-destination connection, information, and purpose. Examples include
Lesson Inquiry, Inquiry Record, Inquiry Status and Contact History, Confirmed Appointment, and
Instructor Schedule Information. These are information concepts, not detailed schemas.

## Architecture Decisions

Lightweight ADRs retain an identifier, candidate decision, reason, alternatives, and candidate
status. `ADR-001` makes inquiry status a distinct responsibility because `REQ-001` and `CAP-001`
depend on maintained state. It is not presented as customer approval.

## Architecture Alternatives

`ARCH-001` derives from `APP-001`, `APP-002`, and `APP-003`: standardize the workflow, configure the
existing spreadsheet, and investigate existing-tool integration. `ARCH-002` derives from
`APP-005`: explore a unified custom workflow. These candidates are compared, never ranked.

## Requirement and Capability Traceability

The generated report retains this inspectable chain:

```text
Discovery Evidence → Stakeholder → Requirement → Capability → Gap
→ Solution Approach → Architecture Component → Information Flow
```

For example, `E2 → staff → REQ-001 → CAP-001 → Chapter 7 gap → APP-001/002/003 →
CMP-SHEET → FLOW-002`. Objects and identifiers from earlier chapters are composed rather than
rewritten as independent claims.

## Architecture Coverage

Validation distinguishes three findings:

- **Uncovered Capability:** a required capability has no supporting component.
- **Unjustified Component:** no requirement, capability, constraint, or dependency explains it.
- **Unknown Dependency:** feasibility of something on which the candidate depends is unestablished.

Disconnected components and missing references are also reported or rejected. This is intentionally
not exhaustive graph analysis.

## Unknown Dependencies

The existing-tool candidate depends on a possible calendar exchange, while interface availability
is unknown. The correct next action is validation. **Unknown interface != impossible integration.**
No “Spreadsheet REST API” or calendar API is invented.

## Avoiding Overengineering

The overengineering experiment adds a Machine Learning Recommendation Engine and Real-Time
Analytics Pipeline without support. Both are flagged as unjustified; the engine makes no claim
that either technology is inherently bad. Technical sophistication is not solution quality.

## Harbor Street Music Walkthrough

Run `sales-lab architecture`. Inspect candidate boundaries and actors, follow flows through logical
responsibilities, compare rationale-backed qualitative states, and review unknown dependencies.
Neither candidate is labeled best or recommended. No totals or arbitrary scores are calculated.

## Mermaid Architecture Diagrams

The CLI report generates each diagram from immutable components, connections, and flows. Unknown
dependency flows use a dotted arrow. A separate comparison diagram says “Compare, do not rank,” so
documentation cannot silently promote a candidate.

## Executable Experiments

1. Use `add_components` to add unsupported technical components and validate the returned copy.
2. Use `remove_component` to remove the sole `CAP-004` support and validate the returned copy.

The original frozen candidate remains unchanged in both experiments.

## Debugging Laboratory

Run `python examples/debug_chapter_9.py` or select **Debug Chapter 9 Architecture** in VS Code.
Step through Requirement → Capability → Architecture Component → Connection → Information Flow →
Coverage Validation. Inspect `architecture`, `components`, `connections`, `information_flows`,
`capability_links`, `uncovered_capabilities`, `unjustified_components`, and
`unknown_dependencies`.

## Exercises

### Exercise A

An engineer proposes Kubernetes. What requirement or architectural constraint requires it? If none
exists, conclude **technology choice not yet justified**.

### Exercise B

The design assumes an existing calendar API, but discovery has not established it. Classify this as
an **unknown dependency requiring validation**, not automatically impossible.

### Exercise C

Remove the only component supporting an established capability. Expected: **uncovered capability**.

### Exercise D

Add a recommendation engine without a supporting requirement. Expected: **unjustified architecture
component**.

### Exercise E

Explain why a simpler candidate may sometimes have fewer dependencies, lower operational
complexity, easier explanation, and potentially easier maintenance. Then explain why the correct
tradeoff still depends on evidence and context.

## Chapter Summary

We now have coherent candidate architectures whose components can be traced back to business needs.

The next question is: **How would the systems and components actually communicate?**

That belongs in Chapter 10.

## Glossary

- **Actor:** a person or role interacting with responsibilities.
- **Boundary:** the explicit division between solution-owned and external elements.
- **Component:** a cohesive logical responsibility or necessary external resource.
- **Connection:** a directed relationship between architecture endpoints.
- **Information flow:** named information moving over a connection for a purpose.
- **ADR:** a record of a decision, its reason, alternatives, and status.
- **Unknown dependency:** a required dependency whose feasibility is unestablished.

## References / Suggested Reading

- ISO/IEC/IEEE 42010, *Systems and software engineering — Architecture description*.
- Michael Nygard, “Documenting Architecture Decisions.”
- The Open Group, *The TOGAF Standard*, architecture views and viewpoints.

Consult the official publications for normative definitions; this chapter's taxonomy remains an
educational simplification.
