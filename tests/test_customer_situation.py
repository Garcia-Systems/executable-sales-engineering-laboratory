"""Tests for immutable customer facts."""

from dataclasses import FrozenInstanceError

import pytest

from sales_lab.domain import CustomerSituation
from sales_lab.examples.harbor_street_music import harbor_street_music_situation


def test_valid_situation_preserves_tuple_order() -> None:
    """A valid fixture retains its ordered facts."""
    situation = harbor_street_music_situation()
    assert situation.organization_name == "Harbor Street Music"
    assert situation.current_process == (
        "Inquiries are entered into a shared spreadsheet.",
        "Confirmed appointments are copied manually into a separate calendar.",
    )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("organization_name", " ", "organization_name must not be blank"),
        ("industry", "", "industry must not be blank"),
        ("stated_concern", "\t", "stated_concern must not be blank"),
        ("current_process", (), "current_process must not be empty"),
        ("known_constraints", ("",), "known_constraints must not be blank"),
        ("source_notes", (), "source_notes must not be empty"),
    ],
)
def test_required_values_reject_blanks(field: str, value: object, message: str) -> None:
    """Every required scalar and tuple rejects absent text."""
    values = {
        "organization_name": "Organization",
        "industry": "Industry",
        "stated_concern": "Concern",
        "current_process": ("Process",),
        "known_constraints": ("Constraint",),
        "source_notes": ("Note",),
    }
    values[field] = value  # type: ignore[assignment]
    with pytest.raises(ValueError, match=message):
        CustomerSituation(**values)  # type: ignore[arg-type]


def test_situation_is_immutable() -> None:
    """A constructed situation cannot be reassigned."""
    situation = harbor_street_music_situation()
    with pytest.raises(FrozenInstanceError):
        situation.organization_name = "Changed"  # type: ignore[misc]
