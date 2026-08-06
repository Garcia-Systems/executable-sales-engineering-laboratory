"""Fixed educational catalog of neutral discovery questions."""

from sales_lab.domain.discovery_meeting import DiscoveryQuestion, QuestionCategory, QuestionKind

DISCOVERY_QUESTION_CATALOG = (
    DiscoveryQuestion(
        "goals-1",
        QuestionCategory.BUSINESS_GOALS,
        "What prompted this conversation?",
        QuestionKind.OPEN,
    ),
    DiscoveryQuestion(
        "process-1",
        QuestionCategory.CURRENT_PROCESS,
        "How does a lesson inquiry move from arrival to a confirmed appointment?",
        QuestionKind.OPEN,
    ),
    DiscoveryQuestion(
        "people-1", QuestionCategory.PEOPLE, "Who responds to lesson inquiries?", QuestionKind.OPEN
    ),
    DiscoveryQuestion(
        "technology-1",
        QuestionCategory.TECHNOLOGY,
        "Which tools hold inquiry and appointment information today?",
        QuestionKind.OPEN,
    ),
    DiscoveryQuestion(
        "data-1",
        QuestionCategory.DATA,
        "Approximately how many lesson inquiries arrive each week?",
        QuestionKind.OPEN,
    ),
    DiscoveryQuestion(
        "constraints-1",
        QuestionCategory.CONSTRAINTS,
        "Are there documented constraints on the current process?",
        QuestionKind.OPEN,
    ),
    DiscoveryQuestion(
        "success-1",
        QuestionCategory.SUCCESS_MEASURES,
        "How would management measure a successful outcome?",
        QuestionKind.OPEN,
    ),
    DiscoveryQuestion(
        "data-2",
        QuestionCategory.DATA,
        "Does management know how many inquiries are ultimately lost?",
        QuestionKind.CLOSED,
    ),
)


def questions_by_category(category: QuestionCategory) -> tuple[DiscoveryQuestion, ...]:
    """Return catalog entries in their fixed source order."""
    return tuple(
        question for question in DISCOVERY_QUESTION_CATALOG if question.category is category
    )
