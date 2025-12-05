# filepath: test/test_ai_player.py
from src.ai_player import (
    AIPlayer,
    AIPlayerNormal,
    AIPlayerCautious,
    AIPlayerAdventurous,
)
from src.space import Space
from src.ruin_tile import RuinTile


# =========================
# Helpers
# =========================

def make_space_with_top(level: int, value: int = 0) -> Space:
    """Crée une case avec une seule tuile (niveau donné)."""
    s = Space(is_submarine=False)
    s.add_ruin(RuinTile(level=level, value=value))
    return s


# =========================
#  Types / base
# =========================

def test_ai_players_are_instances_of_ai_and_player():
    normal = AIPlayerNormal(name="N")
    cautious = AIPlayerCautious(name="C")
    adventurous = AIPlayerAdventurous(name="A")

    for ai in (normal, cautious, adventurous):
        # hérite bien de AIPlayer
        assert isinstance(ai, AIPlayer)
        # flag is_ai à True
        assert ai.is_ai is True


# =========================
#  AIPlayerNormal
# =========================

def test_normal_ai_direction_when_going_back_always_true():
    ai = AIPlayerNormal()
    ai.going_back = True

    # peu importe l'air, elle continue à remonter
    for air in [1, 5, 10, 25]:
        assert ai.choose_direction(air_remaining=air) is True


def test_normal_ai_direction_no_treasure_never_go_back():
    ai = AIPlayerNormal()
    ai.going_back = False
    # pas de trésor
    assert ai.carrying_count == 0

    for air in [1, 5, 10, 25]:
        assert ai.choose_direction(air_remaining=air) is False


def test_normal_ai_direction_with_treasure_uses_danger_threshold():
    ai = AIPlayerNormal()
    ai.going_back = False

    # On simule 2 trésors
    ai.carrying = [RuinTile(level=1, value=1), RuinTile(level=1, value=2)]
    assert ai.carrying_count == 2

    # danger_threshold = 5 + 2 * carrying_count = 9
    # air <= 9  => remonte
    assert ai.choose_direction(air_remaining=9) is True
    assert ai.choose_direction(air_remaining=5) is True

    # air > 9 => continue de descendre
    assert ai.choose_direction(air_remaining=10) is False
    assert ai.choose_direction(air_remaining=15) is False


def test_normal_ai_action_no_ruin_means_A():
    ai = AIPlayerNormal()
    space = Space(is_submarine=False)  # vide

    assert ai.choose_action(space, air_remaining=10) == "A"


def test_normal_ai_action_when_going_back_and_low_air_is_A():
    ai = AIPlayerNormal()
    ai.going_back = True
    ai.carrying = [RuinTile(level=1, value=1)] * 2  # 2 trésors

    space = make_space_with_top(level=1)

    # seuil : 3 + carrying_count = 5
    assert ai.choose_action(space, air_remaining=5) == "A"
    assert ai.choose_action(space, air_remaining=4) == "A"

    # au-dessus, elle peut encore ramasser
    assert ai.choose_action(space, air_remaining=6) == "B"


def test_normal_ai_action_very_low_air_and_heavy_load_is_A():
    ai = AIPlayerNormal()
    ai.going_back = False
    ai.carrying = [RuinTile(level=1, value=1)] * 3  # 3 trésors

    space = make_space_with_top(level=2)

    # safe_threshold = 3, carrying_count >= 3
    assert ai.choose_action(space, air_remaining=3) == "A"
    assert ai.choose_action(space, air_remaining=2) == "A"

    # avec un peu plus d'air, elle reste gourmande
    assert ai.choose_action(space, air_remaining=4) == "B"


def test_normal_ai_action_default_is_greedy_B():
    ai = AIPlayerNormal()
    ai.going_back = False
    ai.carrying = [RuinTile(level=1, value=1)]  # 1 trésor

    space = make_space_with_top(level=1)

    # conditions de prudence non remplies => elle prend
    assert ai.choose_action(space, air_remaining=10) == "B"


# =========================
#  AIPlayerCautious
# =========================

def test_cautious_ai_direction_no_treasure_goes_back_when_air_low():
    ai = AIPlayerCautious()
    ai.going_back = False
    ai.carrying = []

    # seuil : air <= 16 -> remonte
    assert ai.choose_direction(air_remaining=16) is True
    assert ai.choose_direction(air_remaining=10) is True
    assert ai.choose_direction(air_remaining=5) is True

    # air plus haut : continue de descendre
    assert ai.choose_direction(air_remaining=20) is False
    assert ai.choose_direction(air_remaining=25) is False


def test_cautious_ai_direction_with_treasure_is_very_early():
    ai = AIPlayerCautious()
    ai.going_back = False
    ai.carrying = [RuinTile(level=1, value=1)] * 2  # 2 trésors

    # danger_threshold = 14 + 2 * 2 = 18
    assert ai.choose_direction(air_remaining=18) is True
    assert ai.choose_direction(air_remaining=10) is True

    # au-delà du seuil, elle continue
    assert ai.choose_direction(air_remaining=19) is False
    assert ai.choose_direction(air_remaining=25) is False


def test_cautious_ai_action_no_ruin_A():
    ai = AIPlayerCautious()
    space = Space(is_submarine=False)

    assert ai.choose_action(space, air_remaining=20) == "A"


def test_cautious_ai_action_never_pick_when_going_back():
    ai = AIPlayerCautious()
    ai.going_back = True
    ai.carrying = []

    space = make_space_with_top(level=1)
    assert ai.choose_action(space, air_remaining=20) == "A"


def test_cautious_ai_action_stop_after_two_treasures():
    ai = AIPlayerCautious()
    ai.going_back = False
    ai.carrying = [RuinTile(level=1, value=1)] * 2

    space = make_space_with_top(level=1)
    assert ai.choose_action(space, air_remaining=20) == "A"


def test_cautious_ai_action_stop_when_air_low():
    ai = AIPlayerCautious()
    ai.going_back = False
    ai.carrying = [RuinTile(level=1, value=1)]  # 1 trésor

    space = make_space_with_top(level=1)

    # air <= 12 -> ne prend plus
    assert ai.choose_action(space, air_remaining=12) == "A"
    assert ai.choose_action(space, air_remaining=10) == "A"

    # au-dessus : elle peut encore prendre
    assert ai.choose_action(space, air_remaining=13) == "B"


def test_cautious_ai_prefers_shallow_treasures():
    ai = AIPlayerCautious()
    ai.going_back = False
    ai.carrying = []

    shallow_space = make_space_with_top(level=2)
    deep_space = make_space_with_top(level=3)

    assert ai.choose_action(shallow_space, air_remaining=20) == "B"
    assert ai.choose_action(deep_space, air_remaining=20) == "A"


# =========================
#  AIPlayerAdventurous
# =========================

def test_adventurous_ai_direction_risky_threshold():
    ai = AIPlayerAdventurous()
    ai.going_back = False
    ai.carrying = [RuinTile(level=1, value=1)] * 2  # 2 trésors

    # danger_threshold = 2 + 1 * carrying_count = 4
    # air <= 4 -> remonte
    assert ai.choose_direction(air_remaining=4) is True
    assert ai.choose_direction(air_remaining=3) is True

    # air > 4 -> continue de descendre (très risqué)
    assert ai.choose_direction(air_remaining=5) is False
    assert ai.choose_direction(air_remaining=10) is False


def test_adventurous_ai_action_no_ruin_A():
    ai = AIPlayerAdventurous()
    space = Space(is_submarine=False)

    assert ai.choose_action(space, air_remaining=20) == "A"


def test_adventurous_ai_action_greedy_while_descending():
    ai = AIPlayerAdventurous()
    ai.going_back = False
    ai.carrying = []

    space = make_space_with_top(level=4)
    # même avec un gros trésor, elle prend
    assert ai.choose_action(space, air_remaining=10) == "B"


def test_adventurous_ai_action_when_going_back_still_greedy_if_air_high():
    ai = AIPlayerAdventurous()
    ai.going_back = True
    ai.carrying = [RuinTile(level=1, value=1)]

    space = make_space_with_top(level=2)

    # air > 5 -> elle peut encore ramasser
    assert ai.choose_action(space, air_remaining=6) == "B"
    assert ai.choose_action(space, air_remaining=10) == "B"

    # air <= 5 -> elle arrête
    assert ai.choose_action(space, air_remaining=5) == "A"
    assert ai.choose_action(space, air_remaining=3) == "A"


# =========================
#  Non-régression : pas d'effet de bord
# =========================

def test_ai_choices_do_not_modify_state():
    """
    Non-régression importante : choose_direction / choose_action
    ne doivent pas modifier l'état interne (going_back / carrying).
    """
    ai = AIPlayerNormal()
    ai.going_back = False
    ai.carrying = [RuinTile(level=1, value=1)]

    space = make_space_with_top(level=1)

    old_going_back = ai.going_back
    old_carrying = list(ai.carrying)

    _ = ai.choose_direction(air_remaining=10)
    _ = ai.choose_action(space, air_remaining=10)

    assert ai.going_back == old_going_back
    assert ai.carrying == old_carrying