# tests/test_player.py
import pytest

from src.player import Player
from src.ruin_tile import RuinTile


# =========================
#  Helpers
# =========================

def make_tile(level=1, value=1) -> RuinTile:
    return RuinTile(level=level, value=value)


# =========================
#  État initial & reset
# =========================

def test_player_initial_state():
    p = Player(name="Mehdi", is_ai=False)

    assert p.name == "Mehdi"
    assert p.is_ai is False

    # état de manche
    assert p.position == 0
    assert p.going_back is False
    assert p.has_returned is False

    # trésors
    assert p.carrying == []
    assert p.score_tiles == []

    # propriétés dérivées
    assert p.carrying_count == 0
    assert p.total_score == 0
    assert p.is_on_submarine is True


def test_reset_for_new_round():
    p = Player(name="Test")

    # on triche un peu pour mettre un état non trivial
    p.position = 5
    p.going_back = True
    p.has_returned = True
    p.carrying = [make_tile(level=1, value=2)]

    p.reset_for_new_round()

    assert p.position == 0
    assert p.going_back is False
    assert p.has_returned is False
    assert p.carrying == []
    # reset de manche ne touche pas le score définitif
    assert p.score_tiles == []


def test_reset_for_new_game_clears_score_and_round_state():
    p = Player(name="Test")

    p.position = 3
    p.carrying = [make_tile(value=2)]
    p.score_tiles = [make_tile(value=5)]
    p.going_back = True
    p.has_returned = True

    p.reset_for_new_game()

    # état de manche
    assert p.position == 0
    assert p.going_back is False
    assert p.has_returned is False
    assert p.carrying == []

    # score effacé
    assert p.score_tiles == []
    assert p.total_score == 0


# =========================
#  Position & direction
# =========================

def test_move_to_valid_position():
    p = Player(name="Test")
    p.move_to(5)
    assert p.position == 5
    assert p.is_on_submarine is False


def test_move_to_negative_raises():
    p = Player(name="Test")

    with pytest.raises(ValueError):
        p.move_to(-1)


def test_start_going_back_and_continue_descending():
    p = Player(name="Test")

    p.start_going_back()
    assert p.going_back is True

    p.continue_descending()
    assert p.going_back is False


def test_mark_as_returned_sets_flag_and_position_zero():
    p = Player(name="Test")
    p.position = 7
    p.going_back = True

    p.mark_as_returned()

    assert p.has_returned is True
    assert p.position == 0
    assert p.is_on_submarine is True


# =========================
#  Gestion des trésors
# =========================

def test_take_ruin_adds_tile_to_carrying():
    p = Player(name="Test")
    t1 = make_tile(value=3)

    p.take_ruin(t1)

    assert p.carrying == [t1]
    assert p.carrying_count == 1


def test_drop_ruin_removes_specific_tile_if_present():
    p = Player(name="Test")
    t1 = make_tile(value=1)
    t2 = make_tile(value=2)
    p.carrying = [t1, t2]

    p.drop_ruin(t1)

    assert p.carrying == [t2]


def test_drop_ruin_silently_ignores_missing_tile():
    p = Player(name="Test")
    t1 = make_tile(value=1)
    t2 = make_tile(value=2)
    p.carrying = [t1]

    # t2 n'est pas porté
    p.drop_ruin(t2)

    # rien n'a changé, pas d'exception
    assert p.carrying == [t1]


def test_drop_all_carrying_returns_and_clears():
    p = Player(name="Test")
    t1 = make_tile(value=1)
    t2 = make_tile(value=2)
    p.carrying = [t1, t2]

    dropped = p.drop_all_carrying()

    assert dropped == [t1, t2]
    assert p.carrying == []
    assert p.carrying_count == 0


def test_secure_carried_treasures_moves_to_score():
    p = Player(name="Test")
    t1 = make_tile(value=3)
    t2 = make_tile(value=5)

    p.carrying = [t1, t2]
    p.score_tiles = [make_tile(value=1)]  # déjà 1 point

    p.secure_carried_treasures()

    # trésors portés vidés
    assert p.carrying == []
    # score_tiles contient les anciens + les nouveaux
    assert t1 in p.score_tiles and t2 in p.score_tiles
    assert len(p.score_tiles) == 3
    # total_score = 1 + 3 + 5 = 9
    assert p.total_score == 9


def test_secure_carried_treasures_noop_when_empty():
    p = Player(name="Test")
    p.score_tiles = [make_tile(value=4)]

    p.secure_carried_treasures()

    assert p.score_tiles  # inchangé
    assert p.total_score == 4


def test_drop_one_ruin_behaviour():
    p = Player(name="Test")
    t1 = make_tile(value=1)
    t2 = make_tile(value=2)
    p.carrying = [t1, t2]

    dropped = p.drop_one_ruin()
    assert dropped == t2  # LIFO
    assert p.carrying == [t1]

    dropped2 = p.drop_one_ruin()
    assert dropped2 == t1
    assert p.carrying == []

    dropped3 = p.drop_one_ruin()
    assert dropped3 is None
    assert p.carrying == []


# =========================
#  Représentations
# =========================

def test_str_contains_name_role_position_and_score():
    p = Player(name="Alice", is_ai=False)
    p.position = 3
    p.carrying = [make_tile(value=2)]
    p.score_tiles = [make_tile(value=5)]

    s = str(p)

    assert "Alice" in s
    assert "Humain" in s
    assert "Case 3" in s
    assert "Trésors portés: 1" in s
    assert "Score: 5" in s


# =========================
#  Sérialisation
# =========================

def test_to_dict_contains_all_main_fields():
    p = Player(name="Bob", player_id=42, is_ai=True)
    p.position = 5
    p.going_back = True
    p.has_returned = False
    p.carrying = [make_tile(level=2, value=7)]
    p.score_tiles = [make_tile(level=3, value=10)]

    data = p.to_dict()

    assert data["name"] == "Bob"
    assert data["player_id"] == 42
    assert data["is_ai"] is True
    assert data["position"] == 5
    assert data["going_back"] is True
    assert data["has_returned"] is False

    assert isinstance(data["carrying"], list)
    assert isinstance(data["score_tiles"], list)
    assert len(data["carrying"]) == 1
    assert len(data["score_tiles"]) == 1

    # structure d'une tuile sérialisée
    tile_data = data["carrying"][0]
    assert "level" in tile_data
    assert "value" in tile_data


def test_from_dict_recreates_player_state():
    original = Player(name="Charlie", player_id=7, is_ai=False)
    original.position = 4
    original.going_back = True
    original.has_returned = False
    original.carrying = [make_tile(level=1, value=2)]
    original.score_tiles = [make_tile(level=2, value=5), make_tile(level=3, value=8)]

    data = original.to_dict()
    clone = Player.from_dict(data)

    # champs de base
    assert clone.name == "Charlie"
    assert clone.player_id == 7
    assert clone.is_ai is False

    # état
    assert clone.position == 4
    assert clone.going_back is True
    assert clone.has_returned is False

    # trésors
    assert len(clone.carrying) == 1
    assert clone.carrying[0].level == 1
    assert clone.carrying[0].value == 2

    assert len(clone.score_tiles) == 2
    assert [t.value for t in clone.score_tiles] == [5, 8]
    assert clone.total_score == 13


def test_from_dict_non_regression_lists_are_not_shared():
    """
    Non-régression : les listes carrying/score_tiles doivent être recopiées,
    pas partagées entre les instances.
    """
    p1 = Player(name="Dana")
    p1.carrying = [make_tile(value=1)]
    p1.score_tiles = [make_tile(value=2)]

    data = p1.to_dict()
    p2 = Player.from_dict(data)

    # on modifie p2, p1 ne doit pas être impacté
    p2.carrying.append(make_tile(value=99))
    p2.score_tiles.clear()

    assert len(p1.carrying) == 1
    assert len(p1.score_tiles) == 1
