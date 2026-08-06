"""Immutable facts describing a customer situation before discovery."""

from dataclasses import dataclass


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        msg = f"{field_name} must not be blank"
        raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class CustomerSituation:
    """Customer-supplied facts, without analysis or recommendations."""

    organization_name: str
    industry: str
    stated_concern: str
    current_process: tuple[str, ...]
    known_constraints: tuple[str, ...]
    source_notes: tuple[str, ...]

    def __post_init__(self) -> None:
        """Reject missing text while retaining the supplied wording and order."""
        _require_text(self.organization_name, "organization_name")
        _require_text(self.industry, "industry")
        _require_text(self.stated_concern, "stated_concern")
        for field_name in ("current_process", "known_constraints", "source_notes"):
            values = getattr(self, field_name)
            if not values:
                msg = f"{field_name} must not be empty"
                raise ValueError(msg)
            for value in values:
                _require_text(value, field_name)
