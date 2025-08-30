from src.core.constants import CRITICALITY_MULTIPLIERS


def compute_overall_score(issues: list, environment: str = "test") -> int:
    score = 100
    deltas = {"critical": -30, "high": -15, "medium": -7, "low": -2}
    multiplier = CRITICALITY_MULTIPLIERS.get(environment, 1.0)
    for issue in issues:
        criticality = issue.get("criticality", "low")
        delta = deltas[criticality] * multiplier
        score += delta
    return max(0, min(100, score))
