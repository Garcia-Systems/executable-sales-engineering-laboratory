"""Mermaid views for transparent customer-success learning loops."""


def render_success_loop() -> str:
    """Render the supported evidence-to-correction loop."""
    return """flowchart LR
  Requirement[Requirement] --> SuccessCriterion[Success Criterion]
  SuccessCriterion --> Delivery[Implementation]
  Delivery --> Adoption[Adoption Evidence]
  Adoption --> Process[Process Evidence]
  Process --> Outcome[Outcome Evidence]
  Outcome --> Value[Value Validation]
  Value --> Review[Customer Success Review]
  Review --> Correct[Corrective Action]
  Correct --> Process
"""


def render_success_lifecycle() -> str:
    """Render only lifecycle transitions represented by validation statuses."""
    return """stateDiagram-v2
  [*] --> Planned
  Planned --> ReadyToMeasure
  ReadyToMeasure --> MeasurementInProgress
  MeasurementInProgress --> Supported
  MeasurementInProgress --> PartiallySupported
  MeasurementInProgress --> NotSupported
  MeasurementInProgress --> Inconclusive
  Supported --> Review
  PartiallySupported --> Review
  NotSupported --> Review
  Inconclusive --> Review
  Review --> ReadyToMeasure
"""
