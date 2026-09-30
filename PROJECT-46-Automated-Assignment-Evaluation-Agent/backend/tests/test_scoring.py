import pytest
from backend.app.agents.scoring_agent import scoring_agent


def test_calculate_letter_grades():
    assert scoring_agent.calculate_letter_grade(98.5) == "A+"
    assert scoring_agent.calculate_letter_grade(94.0) == "A"
    assert scoring_agent.calculate_letter_grade(91.2) == "A-"
    assert scoring_agent.calculate_letter_grade(88.0) == "B+"
    assert scoring_agent.calculate_letter_grade(84.5) == "B"
    assert scoring_agent.calculate_letter_grade(81.0) == "B-"
    assert scoring_agent.calculate_letter_grade(78.0) == "C+"
    assert scoring_agent.calculate_letter_grade(72.0) == "C"
    assert scoring_agent.calculate_letter_grade(64.0) == "D"
    assert scoring_agent.calculate_letter_grade(52.0) == "F"


def test_deterministic_scoring_enforces_bounds_and_exact_sum():
    criterion_evals = [
        {"criterion_id": 1, "criterion_name": "Understanding", "max_points": 20.0, "score": 17.5, "rationale": "Strong concepts"},
        {"criterion_id": 2, "criterion_name": "Implementation", "max_points": 30.0, "score": 26.0, "rationale": "Working pipeline"},
        {"criterion_id": 3, "criterion_name": "Code Quality", "max_points": 20.0, "score": 18.0, "rationale": "Clean modules"},
        {"criterion_id": 4, "criterion_name": "Testing", "max_points": 15.0, "score": 12.5, "rationale": "Passed unit tests"},
        {"criterion_id": 5, "criterion_name": "Documentation", "max_points": 15.0, "score": 14.0, "rationale": "Clear report"},
    ]

    result = scoring_agent.compute_evaluation_score(criterion_evals, expected_total_points=100.0)

    # 17.5 + 26.0 + 18.0 + 12.5 + 14.0 = 88.0
    assert result["total_score"] == 88.0
    assert result["max_possible_score"] == 100.0
    assert result["percentage"] == 88.0
    assert result["letter_grade"] == "B+"
    assert len(result["criterion_scores"]) == 5


def test_deterministic_scoring_clips_overflown_and_negative_scores():
    criterion_evals = [
        {"criterion_id": 1, "criterion_name": "Understanding", "max_points": 20.0, "score": 25.0},  # Over max
        {"criterion_id": 2, "criterion_name": "Implementation", "max_points": 30.0, "score": -5.0}, # Negative
    ]

    result = scoring_agent.compute_evaluation_score(criterion_evals, expected_total_points=50.0)

    # 20.0 (clipped from 25.0) + 0.0 (clipped from -5.0) = 20.0
    assert result["total_score"] == 20.0
    assert result["max_possible_score"] == 50.0
    assert result["percentage"] == 40.0
    assert result["letter_grade"] == "F"
    assert result["criterion_scores"][0]["score"] == 20.0
    assert result["criterion_scores"][1]["score"] == 0.0
