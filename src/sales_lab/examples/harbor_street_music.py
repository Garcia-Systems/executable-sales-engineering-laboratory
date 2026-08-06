"""Reusable Chapter 0 customer-supplied facts."""

from sales_lab.domain.customer_situation import CustomerSituation


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
