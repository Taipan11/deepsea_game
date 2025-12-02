# tests/test_dice.py
import pytest
import random

from src.dice import Dice


def test_invalid_num_dice_raises():
    """
    Non-régression : on doit continuer à refuser num_dice <= 0.
    """
    with pytest.raises(ValueError):
        Dice(num_dice=0)

    with pytest.raises(ValueError):
        Dice(num_dice=-1)


def test_invalid_faces_raises():
    """
    Non-régression : on doit continuer à refuser faces <= 0.
    """
    with pytest.raises(ValueError):
        Dice(faces=0)

    with pytest.raises(ValueError):
        Dice(faces=-3)


def test_roll_individual_length_and_range():
    """
    Non-régression :
    - roll_individual doit renvoyer exactement num_dice résultats
    - chaque résultat doit être entre 1 et faces (inclus).
    """
    d = Dice(num_dice=3, faces=6)

    results = d.roll_individual()

    assert len(results) == 3
    for value in results:
        assert 1 <= value <= 6


def test_roll_sum_in_range():
    """
    Non-régression :
    - roll() doit renvoyer une somme cohérente :
      entre num_dice et num_dice * faces.
    """
    d = Dice(num_dice=2, faces=3)

    total = d.roll()

    assert 2 <= total <= 6  # 2 * 1 <= sum <= 2 * 3


def test_dice_uses_provided_rng_deterministically():
    """
    Non-régression importante :
    si on fournit un RNG seedé, les résultats doivent être déterministes
    et basés sur CE RNG, pas sur random global.

    Si un jour on modifie Dice pour ne plus utiliser self.rng, ce test échouera.
    """
    seed = 12345
    rng = random.Random(seed)
    d = Dice(num_dice=2, faces=3, rng=rng)

    # premier tirage via Dice
    results_from_dice = d.roll_individual()

    # pour comparer, on recrée un RNG avec la même seed
    # et on simule ce que Dice est censé faire
    rng2 = random.Random(seed)
    expected = [rng2.randint(1, 3) for _ in range(2)]

    assert results_from_dice == expected


def test_str_representation():
    """
    Non-régression : __str__ doit rester du type 'XdY'.
    """
    d = Dice(num_dice=2, faces=3)
    assert str(d) == "2d3"

    d2 = Dice(num_dice=4, faces=6)
    assert str(d2) == "4d6"
