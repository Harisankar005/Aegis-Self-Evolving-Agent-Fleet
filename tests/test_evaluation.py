def test_hybrid_evaluation(evaluator):
    prediction = "AI improves diagnostics"
    reference = "AI helps in medical diagnosis"

    score = evaluator.evaluate(prediction, reference)

    assert 0 <= score <= 1


def test_evaluation_consistency(evaluator):
    prediction = "same output"
    reference = "same output"

    score1 = evaluator.evaluate(prediction, reference)
    score2 = evaluator.evaluate(prediction, reference)

    assert abs(score1 - score2) < 0.1  # bounded variance
