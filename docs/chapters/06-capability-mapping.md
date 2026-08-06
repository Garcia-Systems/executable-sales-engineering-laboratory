# Chapter 6 — Capability Mapping

## Research Foundations

Capability mapping connects established needs to what an organization must be able to accomplish.
This chapter follows the traceability discipline introduced by requirements engineering and the
business-capability distinction used in business architecture. It uses a deliberately small,
inspectable teaching model rather than claiming a universal taxonomy.

## Professional Practice

Sales Engineers ask **what capability could satisfy this requirement?** before asking which product
might provide it. The chain is **business need → requirement → capability → future solution
options**. Stakeholders must review both the links and the gaps; software coverage alone cannot
choose the correct future solution.

## Educational Heuristic

Name a capability with a vendor-neutral accomplishment, map it explicitly to one or more existing
requirement identifiers, and preserve its evidence trail. Never generate capabilities automatically
from requirement prose.

## Subjective Professional Judgment

People must decide whether a capability boundary is useful, whether several requirements genuinely
share one capability, and what partial coverage means in context. Deterministic code exposes the
inputs and dangling links; it cannot determine organizational truth, priority, or solution fit.

## Learning Objectives

You will define capabilities; distinguish them from requirements and products; create many-to-many
mappings; inspect coverage; find unmapped requirements and unsupported capabilities; and compare
coverage without numeric fit scores or premature selection.

## What Is a Capability?

A capability describes **what the organization must be able to accomplish**. “Shared inquiry-status
tracking” is a capability. It does not decide whether people use a redesigned manual process,
existing configuration, a spreadsheet, scheduling software, a CRM, an integration, or custom code.

## Requirement vs. Capability

`REQ-001` says authorized staff must be able to determine an active inquiry's current status. The
requirement is a normative, evidence-backed need. `CAP-001`, Inquiry Status Tracking, groups the
organizational ability that could satisfy it. A requirement answers *what is required and why*; a
capability provides a stable solution-neutral lens for *what the organization must be able to do*.

## Capability vs. Product

“Confirmed schedule visibility” and “controlled access to lesson information” describe abilities.
“Salesforce CRM,” “Google Calendar integration,” and “OAuth 2.0 authentication” name products or
implementation decisions. Those decisions belong after current capabilities and real gaps are
understood—not in this chapter.

## Capability Categories

The model offers Process, Information, Collaboration, Integration, Control, and Reporting. These
are optional **educational organization mechanisms**, not universal industry standards. Harbor
Street Music uses only categories justified by its explicit capabilities.

## Many-to-Many Mapping

A capability may support several requirements and a requirement may need several capabilities.
`CAP-003` supports both `REQ-001` and `REQ-002`; each also has a more focused capability. Explicit
`CapabilityRequirementLink` records preserve this relationship and their input order.

## Traceability

The executable report follows Capability ← Requirement ← Stakeholder ← Evidence source. For example:
`CAP-001 ← REQ-001 ← Front Desk Staff ← E2 ← Harbor Street Music discovery meeting and Chapter 3
process`. This reuses Chapter 5 requirement objects and Chapter 4 evidence identifiers rather than
copying their statements into an unrelated list.

## Capability Coverage

- **Covered:** explicit mappings currently indicate support for the requirement.
- **Partially Covered:** explicit review says mapped capabilities address only part of it.
- **Not Covered:** an established requirement has no valid capability link.
- **Not Evaluated:** a link exists, but coverage has not been evaluated.

These are qualitative audit states. They are not percentages, product rankings, or proof that a
future solution is correct.

## Capability Gaps

A **Requirement Gap** is an established requirement with no mapped capability. An **Unsupported
Capability** has no established requirement supporting its presence. Invalid links are **Incomplete
Mappings**. The fixed base scenario covers all three established requirements and has no unsupported
capabilities; controlled tests and the experiment demonstrate every gap state.

## Solution-First Thinking

Adding `CAP-999: AI Chatbot` without a requirement produces: “Unsupported capability. No established
requirement currently justifies this capability.” This does not say AI is inherently inappropriate.
It asks which business need and established requirement would justify the idea before technology
enters design.

## Harbor Street Music Walkthrough

The fixture directly reuses Chapter 5's `REQ-001`, `REQ-002`, and `REQ-003`. Explicit capabilities
cover inquiry-status tracking, confirmed-schedule visibility, information sharing, and
constraint-aware option evaluation. The budget capability preserves the precise fact that a budget
has not **yet** been approved; it neither assumes zero budget nor recommends a free product.

## Capability Matrix

Run `sales-lab capabilities`. Rows are capabilities, columns are the actual Chapter 5 requirement
identifiers, and cells say `Supports` or `—`. The inverse coverage table lists capability IDs and a
qualitative state. No pseudo-precise score is generated.

## Mermaid Diagram

The generated diagram follows discovery evidence, current process, and stakeholders into
requirements; requirements lead to named capabilities; capabilities lead only to **Future Solution
Options**. Its explicit boundary is **Capabilities ≠ Products**.

## Executable Experiment

`python examples/debug_chapter_6.py` starts with the valid immutable map, returns a new map containing
the unlinked AI Chatbot idea, validates it, and detects the unsupported capability. The original
tuple remains unchanged.

## Debugging Laboratory

Choose **Debug Chapter 6 Capabilities** in VS Code or run the script above. Step through Requirement
→ Capability Mapping → Traceability Validation → Coverage Analysis → Gap Detection. Inspect
`requirements`, `capability_map.capabilities`, `capability_map.links`, `coverage`, `gaps`, and
`unsupported_capabilities` at the marked breakpoints.

## Exercises

1. **Exercise A:** Classify Salesforce as requirement, capability, or implementation. **Expected:**
   implementation/product.
2. **Exercise B:** Classify “Shared visibility into inquiry status.” **Expected:** capability.
3. **Exercise C:** A stakeholder says “We need AI.” What should the Sales Engineer do next?
   **Expected:** return to discovery and ask what business need or established requirement AI would
   address; do not automatically create an AI capability.
4. Remove the `REQ-003` link and inspect the Requirement Gap. Restore it without selecting a product.
5. Add a dangling link and explain why an incomplete mapping is different from partial coverage.

## Chapter Summary

We understand what capabilities the organization may need. The next question becomes: **What
already exists, and where are the actual gaps?** That belongs in the next chapter.

## Glossary

- **Capability:** what an organization must be able to accomplish.
- **Capability map:** ordered capability definitions and explicit requirement links.
- **Coverage:** a qualitative review state, not a fit score.
- **Requirement Gap:** an established requirement without a mapped capability.
- **Unsupported Capability:** a capability without an established supporting requirement.
- **Incomplete Mapping:** a link with an unknown requirement or capability reference.
- **Solution-first thinking:** introducing technology before a justified need and requirement.

## References / Suggested Reading

- ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements
  engineering* (consult an authorized current copy for normative guidance).
- The Open Group, *TOGAF Standard, 10th Edition*, Business Architecture capability material.
- IIBA, *A Guide to the Business Analysis Body of Knowledge (BABOK Guide), Version 3*, requirements
  analysis, traceability, and solution-evaluation material.
