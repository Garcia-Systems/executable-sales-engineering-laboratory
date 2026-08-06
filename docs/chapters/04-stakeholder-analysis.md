# Chapter 4 — Stakeholder Analysis

## Research Foundations

Stakeholder analysis begins from a modest systems principle: a technical system operates within a
social and organizational setting. ISO/IEC/IEEE 29148 distinguishes stakeholders and their needs
before requirements are specified. This chapter applies that principle without pretending that a
short discovery exercise can measure power, politics, or individual behavior.

## Professional Practice

A Sales Engineer must understand who performs the current work, owns its outcome, supplies
information, uses its systems, approves change, receives outputs, and will be affected. That map is
built before requirements or solution design so that one interviewee's perspective is not mistaken
for the organization's complete needs.

## Educational Heuristic

Follow evidence from **business process → process participants → stakeholder roles →
responsibilities → evidence → perspective gaps → stakeholder report**. The map is a prompt for
better investigation, not a numeric ranking.

## Subjective Professional Judgment

Choosing where one role ends and another begins requires judgment. Record the evidence and gaps so
another practitioner can challenge that choice. Do not predict support, opposition, buying
probability, or political influence from a title.

## Learning Objectives

After this chapter, you can identify evidence-supported roles; distinguish roles, participation,
and authority; connect roles to current-process steps; preserve provenance; distinguish unknown
from no; and identify perspectives still requiring discovery.

## Why Stakeholders Matter

A simple lesson inquiry crosses customer, operational, managerial, and instructor perspectives.
Ignoring one can hide work, ownership, authority, system use, or impacts. Stakeholder analysis asks
**who needs to be understood before defining what the system needs to do?**

## Roles vs. Individuals

The model primarily records `StakeholderRole`, not a named employee. People change jobs, several
people can share a role, and one person can hold several roles. Organizational responsibilities
usually survive those changes. A person's identity should appear only when it is educationally
necessary and supported by evidence.

## Responsibilities

The executable categories are `PERFORMS_WORK`, `OWNS_OUTCOME`, `APPROVES_CHANGE`,
`PROVIDES_INFORMATION`, `USES_SYSTEM`, `RECEIVES_OUTPUT`, `AFFECTED_BY_CHANGE`, and
`TECHNICAL_SUPPORT`. A role may have several. Absence from a category means **Not Established**,
not false. No score implies that one role is more valuable than another.

## Process Participation

`ProcessParticipation` references the exact Chapter 3 identifiers: `inquiry`, `spreadsheet`,
`review`, `contact`, `decision`, and `calendar`. Participation in a step does not prove authority to
approve a change. Chapter 3's undocumented declined branch remains outside invented assignments.

## Decision Authority

`AuthorityState.UNKNOWN` differs from `AuthorityState.NO`. “We do not know who approves purchases”
describes missing evidence. “The manager cannot approve purchases” is a negative assertion that
would itself require evidence. Harbor Street Music records manager spending authority as unknown.

## Evidence and Assumptions

Every responsibility, participation, relationship, and authority entry carries an evidence
identifier. The report resolves that identifier to a statement and source. Technology support is
not assigned to an imaginary IT department: **Technology Ownership: Unknown** is an explicit map
node supported by the discovery gap.

## Missing Perspectives

The deterministic gap list covers technology ownership, final spending authority, instructor
follow-up, success ownership, additional schedulers, and handling incorrect calendar information.
Each gap owns its follow-up question; the service does not generate unrelated conversation.

## Harbor Street Music Walkthrough

The prospective student or parent submits an inquiry and accepts or declines. Front desk staff
enter, review, and follow up on inquiries and create confirmed calendar entries. The store manager
owns the overall lesson-program outcome and discusses process changes, but final spending authority
is unknown. The instructor teaches scheduled lessons and depends on accurate schedule information;
instructor follow-up participation is unknown. Technology ownership remains unknown.

## Stakeholder Matrix

Run the example to produce the matrix. “Established” means an evidence-linked responsibility is
present; “Not Established” means it was not established; and “Unknown” preserves an explicit
open authority question. These terms deliberately avoid forced yes/no claims.

```console
sales-lab stakeholders
```

## Mermaid Diagram

The same structured relationships generate the Mermaid graph, preventing a second hand-maintained
map from drifting. Solid arrows are established relationships; the dotted technology arrow marks
an explicit unknown.

## Executable Example

From an installed checkout run `sales-lab stakeholders`. The output includes ordered roles,
responsibilities, process-step links, authority, relationships, evidence, gaps, gap-derived
questions, limitations, the matrix, and Mermaid source. It stops before requirements and design.

## Debugging Laboratory

Run `python examples/debug_chapter_4.py` or choose **Debug Chapter 4 Stakeholders** in VS Code.
Set breakpoints on the assignments marked “Breakpoint,” rather than relying on line numbers. Inspect
`stakeholders`, `responsibilities`, `authority`, `evidence`, and `perspective_gaps`; then step into
`analyze_stakeholders` and report rendering. Frozen dataclasses and their tuples must remain
unchanged. Repeated runs must preserve ordering and output.

## Exercises

1. Discovery says, “Sarah updates the spreadsheet when she works the front desk.” Should the map
   primarily represent Sarah or Front Desk Staff? Prefer the role: it is reusable across staffing
   changes and multiple role occupants; retain Sarah only as provenance when appropriate.
2. Model “We do not know who approves purchases,” then compare it with “The manager cannot approve
   purchases.” The first is `UNKNOWN`; the second is `NO` only when supported by evidence.
3. Locate each process participation in the Chapter 3 process. Explain why the instructor's use of
   a schedule does not establish instructor participation in inquiry follow-up.
4. Add one evidence-backed responsibility and its evidence record. Verify stable matrix and report
   output without adding a score.
5. Add a perspective gap and follow-up question. Confirm that no stakeholder is invented to fill it.

## Chapter Summary

We now understand the current process and the people involved. The next question is: **What does
the organization actually require from a solution?** That belongs in Chapter 5.

## Glossary

- **Stakeholder role:** an organizational capacity with responsibilities, distinct from a person.
- **Responsibility:** evidence-supported work, ownership, authority, information, use, receipt,
  impact, or technical support associated with a role.
- **Process participation:** an evidenced role-to-current-process-step association.
- **Decision authority:** explicit knowledge about who can make a specified decision.
- **Perspective gap:** a missing viewpoint or fact paired with a discovery question.
- **Evidence provenance:** the traceable source supporting an assertion.

## References / Suggested Reading

- ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements
  engineering* (suggested reading; consult the official ISO or IEEE catalog).
- IIBA, *A Guide to the Business Analysis Body of Knowledge (BABOK Guide), Version 3*, sections on
  stakeholder analysis and elicitation (suggested reading).
- Project Management Institute, *A Guide to the Project Management Body of Knowledge (PMBOK
  Guide)*, stakeholder domain material (suggested reading).
