"""Reusable Chapter 0 customer-supplied facts."""

from sales_lab.domain.customer_situation import CustomerSituation
from sales_lab.domain.discovery import (
    Assumption,
    CustomerStatement,
    UnknownInformation,
    VerifiedFact,
)
from sales_lab.services.investigation import DiscoveryEvidence


def harbor_street_music_situation() -> CustomerSituation:
    """Return the fixed Harbor Street Music introductory situation."""
    return CustomerSituation(
        organization_name="Harbor Street Music",
        industry="community music retail and education",
        stated_concern="Lesson inquiries sometimes require repeated follow-up.",
        current_process=(
            "Inquiries are entered into a shared spreadsheet.",
            "Confirmed appointments are copied manually into a separate calendar.",
        ),
        known_constraints=("The organization has not yet approved a software budget.",),
        source_notes=("Information supplied during an introductory conversation.",),
    )


def harbor_street_music_discovery() -> DiscoveryEvidence:
    """Return Chapter 1 evidence without interpreting the customer's statement."""
    return DiscoveryEvidence(
        customer_statements=(CustomerStatement("Students keep slipping through the cracks."),),
        verified_facts=(
            VerifiedFact("Inquiries are entered into a shared spreadsheet."),
            VerifiedFact("Confirmed appointments are copied manually into a separate calendar."),
        ),
        assumptions=(
            Assumption("Scheduling is broken."),
            Assumption("Automation is needed."),
        ),
        unknown_information=(UnknownInformation("The frequency and meaning of missed inquiries."),),
    )
