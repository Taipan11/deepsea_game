# tests/test_ai_player.py
from src.ai_player import AIPlayer
from src.ruin_tile import RuinTile
from src.space import Space


def test_ai_starts_descending_from_submarine():
    ai = AIPlayer(name="Bot")
    ai.reset_for_new_game()
    assert ai.is_on_submarine

    # Air confortable, premier tour -> descend
    goes_back = ai.choose_direction(air_remaining=20)
    assert goes_back is False
    assert ai.going_back is False


def test_ai_decides_to_go_back_when_air_is_low():
    ai = AIPlayer(name="Bot")
    ai.reset_for_new_game()
    ai.position = 3  # quelque part dans le chemin

    goes_back = ai.choose_direction(air_remaining=2)
    assert goes_back is True
    assert ai.going_back is True


def test_ai_decides_to_pickup_when_safe():
    ai = AIPlayer(name="Bot")
    ai.reset_for_new_game()
    space = Space()
    space.add_ruin(RuinTile(level=1, value=0))

    action = ai.choose_action(space, air_remaining=10)
    assert action == "B"  # ramasse


def test_ai_refuses_to_pickup_when_air_low():
    ai = AIPlayer(name="Bot", min_air_to_pickup=3)
    ai.reset_for_new_game()
    space = Space()
    space.add_ruin(RuinTile(level=1, value=0))

    action = ai.choose_action(space, air_remaining=2)
    assert action == "A"  # ne prend pas le risque


def test_ai_serialization_round_trip():
    ai = AIPlayer(
        name="Bot",
        player_id=42,
        risk_carry_limit=2,
        critical_air_threshold=4,
        min_air_to_pickup=2,
    )
    ai.reset_for_new_game()
    ai.position = 5
    ai.take_ruin(RuinTile(1, 0))

    data = ai.to_dict()
    ai2 = AIPlayer.from_dict(data)

    assert ai2.name == ai.name
    assert ai2.player_id == ai.player_id
    assert ai2.risk_carry_limit == ai.risk_carry_limit
    assert ai2.critical_air_threshold == ai.critical_air_threshold
    assert ai2.min_air_to_pickup == ai.min_air_to_pickup
    assert ai2.position == ai.position
    assert ai2.carrying_count == ai.carrying_count
