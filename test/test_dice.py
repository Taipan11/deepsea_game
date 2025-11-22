# tests/test_dice.py
import random
from dice import Dice


def test_default_dice_roll_range():
    dice = Dice()  # 2 dés, 3 faces
    # 2 dés de 1 à 3 => min 2, max 6
    for _ in range(50):
        result = dice.roll()
        assert 2 <= result <= 6


def test_custom_dice_roll_range():
    dice = Dice(num_dice=1, faces=6)
    for _ in range(50):
        result = dice.roll()
        assert 1 <= result <= 6


def test_dice_is_deterministic_with_seed():
    rng = random.Random(123)
    dice = Dice(num_dice=2, faces=3, rng=rng)

    # Si on relance avec le même seed et la même config, on obtient la même séquence
    results1 = [dice.roll() for _ in range(5)]

    rng2 = random.Random(123)
    dice2 = Dice(num_dice=2, faces=3, rng=rng2)
    results2 = [dice2.roll() for _ in range(5)]

    assert results1 == results2
