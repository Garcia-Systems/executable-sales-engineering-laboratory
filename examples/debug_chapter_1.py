"""Learner-owned breakpoint path for Chapter 1."""

from sales_lab.domain import CustomerStatement, Observation, VerifiedFact
from sales_lab.reports.markdown import render_initial_discovery_assessment
from sales_lab.services.investigation import (
    DiscoveryEvidence,
    build_initial_discovery_assessment,
    investigation_questions,
)

statement = CustomerStatement("Students keep slipping through the cracks.")  # Breakpoint 1
observation = Observation("A shared spreadsheet was displayed during discovery.")  # Breakpoint 2
fact = VerifiedFact("The customer confirmed that inquiries are entered in the spreadsheet.")
evidence = DiscoveryEvidence(
    customer_statements=(statement,), observations=(observation,), verified_facts=(fact,)
)
questions = investigation_questions(evidence)  # Breakpoint 3
assessment = build_initial_discovery_assessment(evidence)
report = render_initial_discovery_assessment(assessment)  # Breakpoint 4
if __name__ == "__main__":
    print(report, end="")  # noqa: T201
