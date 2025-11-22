# tests/test_player.py
from src.ruin_tile import RuinTile
from player import Player


def test_new_player_has_zero_score_and_is_at_submarine():
    p = Player(name="Alice")
    p.reset_for_new_game()
    assert p.total_score == 0
    assert p.position == 0
    assert p.is_on_submarine


def test_take_and_secure_treasures():
    p = Player(name="Bob")
    p.reset_for_new_game()

    t1 = RuinTile(level=1, value=0)
    t2 = RuinTile(level=2, value=5)

    p.take_ruin(t1)
    p.take_ruin(t2)

    assert p.carrying_count == 2
    assert p.total_score == 0

    p.mark_as_returned()
    p.secure_carried_treasures()

    assert p.carrying_count == 0
    assert p.total_score == 5  # 0 + 5


def test_drop_all_carrying():
    p = Player(name="Charlie")
    p.reset_for_new_game()

    t1 = RuinTile(1, 0)
    t2 = RuinTile(2, 4)
    p.take_ruin(t1)
    p.take_ruin(t2)

    dropped = p.drop_all_carrying()
    assert len(dropped) == 2
    assert p.carrying_count == 0


def test_serialization_round_trip():
    p = Player(name="Dana", player_id=1, is_ai=False)
    p.reset_for_new_game()

    p.take_ruin(RuinTile(1, 0))
    p.mark_as_returned()
    p.secure_carried_treasures()

    data = p.to_dict()
    p2 = Player.from_dict(data)

    assert p2.name == p.name
    assert p2.player_id == p.player_id
    assert p2.is_ai == p.is_ai
    assert p2.total_score == p.total_score
