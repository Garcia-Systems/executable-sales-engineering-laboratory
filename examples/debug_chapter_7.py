"""Debugging laboratory for Chapter 7 current capability gap analysis."""

from sales_lab.examples.harbor_street_music import (
    harbor_street_music_capability_map,
    harbor_street_music_current_capability_inventory,
    harbor_street_music_requirements,
    harbor_street_music_stakeholder_map,
)
from sales_lab.services.capabilities import analyze_capabilities
from sales_lab.services.gaps import analyze_gaps

required_capabilities = analyze_capabilities(
    harbor_street_music_requirements(),
    harbor_street_music_stakeholder_map(),
    harbor_street_music_capability_map(),
)
current_resources = harbor_street_music_current_capability_inventory()
analysis = analyze_gaps(required_capabilities, current_resources)

for assessment in analysis.assessments:
    required_capability = next(
        item
        for item in required_capabilities.capability_map.capabilities
        if item.identifier == assessment.capability_id
    )
    evidence = tuple(
        item for item in current_resources.evidence if item.identifier in assessment.evidence_ids
    )
    gap_type = assessment.gap_type
    follow_up_questions = tuple(
        question
        for question in analysis.follow_up_questions
        if question == assessment.follow_up_question
    )
    breakpoint()  # noqa: T100 - this file is intentionally an interactive debugging laboratory.
