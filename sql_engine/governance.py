from dataclasses import dataclass

from sql_engine.validator import SqlValidationResult


@dataclass
class GovernanceDecision:
    allowed: bool
    status: str
    reason: str
    approval_ticket: str | None = None


class QueryGovernance:
    def decide(self, validation: SqlValidationResult, require_approval: bool = False) -> GovernanceDecision:
        if not validation.is_valid:
            return GovernanceDecision(
                allowed=False,
                status="blocked",
                reason="Validation blocked this query before execution.",
            )
        if validation.requires_approval or require_approval:
            ticket = "APR-SIM-001"
            return GovernanceDecision(
                allowed=False,
                status="approval_required",
                reason="Query is valid but requires simulated human approval before execution.",
                approval_ticket=ticket,
            )
        return GovernanceDecision(
            allowed=True,
            status="approved",
            reason="Query passed validation and governance checks.",
        )
