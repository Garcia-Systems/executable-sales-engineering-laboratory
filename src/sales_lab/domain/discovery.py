"""Immutable information categories used during initial discovery."""

from dataclasses import dataclass


def _validate_text(value: str) -> None:
    if not value.strip():
        msg = "text must not be blank"
        raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class CustomerStatement:
    """A customer's words, recorded without interpretation."""

    text: str

    def __post_init__(self) -> None:
        """Validate the recorded text."""
        _validate_text(self.text)


@dataclass(frozen=True, slots=True)
class Observation:
    """Something directly noticed by the sales engineer."""

    text: str

    def __post_init__(self) -> None:
        """Validate the recorded text."""
        _validate_text(self.text)


@dataclass(frozen=True, slots=True)
class VerifiedFact:
    """Information supported by evidence and verified for this engagement."""

    text: str

    def __post_init__(self) -> None:
        """Validate the recorded text."""
        _validate_text(self.text)


@dataclass(frozen=True, slots=True)
class Assumption:
    """An unverified belief that must not be treated as fact."""

    text: str

    def __post_init__(self) -> None:
        """Validate the recorded text."""
        _validate_text(self.text)


@dataclass(frozen=True, slots=True)
class InvestigationQuestion:
    """A neutral prompt intended to gather evidence."""

    text: str

    def __post_init__(self) -> None:
        """Validate the recorded text."""
        _validate_text(self.text)


@dataclass(frozen=True, slots=True)
class ProblemHypothesis:
    """A possible business problem that remains unverified."""

    text: str

    def __post_init__(self) -> None:
        """Validate the recorded text."""
        _validate_text(self.text)


@dataclass(frozen=True, slots=True)
class UnknownInformation:
    """A named evidence gap, not an inferred fact."""

    text: str

    def __post_init__(self) -> None:
        """Validate the recorded text."""
        _validate_text(self.text)
