def calculate_elo_change(rating_a: int, rating_b: int, score_a: float, k_factor: int = 32) -> tuple[int, int]:
    expected_a = 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))
    expected_b = 1.0 - expected_a

    score_b = 1.0 - score_a

    new_rating_a = round(rating_a + k_factor * (score_a - expected_a))
    new_rating_b = round(rating_b + k_factor * (score_b - expected_b))

    return new_rating_a, new_rating_b