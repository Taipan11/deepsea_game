# tests/test_board.py
import pytest

from src.board import Board
from src.space import Space
from src.ruin_tile import RuinTile


# =========================
#  Construction / validation
# =========================

def test_board_requires_at_least_one_space():
    """
    Non-régression : un Board sans case doit lever une erreur.
    """
    with pytest.raises(ValueError):
        Board(spaces=[])


def test_board_requires_submarine_at_index_zero():
    """
    Non-régression : la case 0 doit être le sous-marin.
    """
    spaces = [Space(is_submarine=False)]
    with pytest.raises(ValueError):
        Board(spaces=spaces)


def test_valid_board_initialization():
    """
    Cas nominal : un plateau avec un sous-marin et une case de ruine.
    """
    sub = Space(is_submarine=True)
    s1 = Space(is_submarine=False)
    board = Board(spaces=[sub, s1])

    assert board.size == 2
    assert board.submarine_index == 0
    assert board.get_space(0).is_submarine
    assert not board.get_space(1).is_submarine


# =========================
#  create_default
# =========================

def test_create_default_board_basic_properties():
    """
    Non-régression :
    - la case 0 est le sous-marin,
    - toutes les autres cases ne sont pas le sous-marin,
    - chaque case (hors sous-marin) contient exactement 1 tuile de ruine,
    - les niveaux sont non décroissants le long du chemin.
    """
    board = Board.create_default(shuffle_tiles=True)

    # 0 : sous-marin
    assert board.size > 1
    assert board.spaces[0].is_submarine

    # Toutes les autres cases : pas sous-marin, 1 ruine chacune
    levels = []
    for idx, space in enumerate(board.spaces[1:], start=1):
        assert not space.is_submarine, f"La case {idx} ne doit pas être un sous-marin."
        assert space.ruin_count == 1, f"La case {idx} doit contenir exactement 1 ruine."
        levels.append(space.top_ruin.level)

    # Les niveaux doivent être non décroissants (1→2→3→4)
    assert levels == sorted(levels), "Les niveaux de profondeur doivent être non décroissants."


def test_create_default_with_max_stack_size_is_applied():
    """
    Non-régression : max_stack_size doit être appliqué aux nouvelles cases.
    (Même si on n'empile qu'une tuile par case dans cette version.)
    """
    max_stack = 3
    board = Board.create_default(max_stack_size=max_stack)

    for idx, space in enumerate(board.spaces[1:], start=1):
        assert space.max_stack_size == max_stack, f"max_stack_size incorrect sur la case {idx}"


# =========================
#  Accès / propriétés
# =========================

def test_board_size_and_last_index_are_consistent():
    sub = Space(is_submarine=True)
    s1 = Space(is_submarine=False)
    s2 = Space(is_submarine=False)
    board = Board(spaces=[sub, s1, s2])

    assert board.size == 3
    assert board.last_index == 2
    assert board.get_space(board.last_index) is s2


def test_getitem_delegates_to_get_space():
    sub = Space(is_submarine=True)
    s1 = Space(is_submarine=False)
    board = Board(spaces=[sub, s1])

    assert board[0] is sub
    assert board[1] is s1


def test_str_representation_contains_sub_and_separators():
    board = Board(spaces=[
        Space(is_submarine=True),
        Space(is_submarine=False),
    ])

    text = str(board)
    # format général : "SUB - ..."
    assert "SUB" in text
    assert " - " in text


# =========================
#  Sérialisation
# =========================

def test_board_to_dict_and_from_dict_roundtrip():
    """
    Non-régression : to_dict / from_dict doivent être inverses (au sens logique).
    """
    sub = Space(is_submarine=True)
    s1 = Space(is_submarine=False)
    s1.add_ruin(RuinTile(level=1, value=0))

    board = Board(spaces=[sub, s1])

    data = board.to_dict()
    restored = Board.from_dict(data)

    assert restored.size == board.size
    assert restored.spaces[0].is_submarine
    assert not restored.spaces[1].is_submarine
    assert restored.spaces[1].ruin_count == 1
    assert restored.spaces[1].top_ruin.level == 1
    assert restored.spaces[1].top_ruin.value == 0


# =========================
#  compress_path
# =========================

def test_compress_path_keeps_submarine_and_non_empty_spaces():
    """
    Non-régression : compress_path doit garder :
    - toujours la case 0 (sous-marin),
    - uniquement les cases qui contiennent des ruines.
    """
    sub = Space(is_submarine=True)

    s_empty_1 = Space(is_submarine=False)
    s_non_empty_1 = Space(is_submarine=False)
    s_non_empty_1.add_ruin(RuinTile(level=1, value=1))

    s_empty_2 = Space(is_submarine=False)
    s_non_empty_2 = Space(is_submarine=False)
    s_non_empty_2.add_ruin(RuinTile(level=2, value=5))

    board = Board(spaces=[sub, s_empty_1, s_non_empty_1, s_empty_2, s_non_empty_2])

    board.compress_path()

    # le sous-marin est toujours en 0
    assert board.size == 3
    assert board.spaces[0].is_submarine

    # les deux cases restantes doivent être les non vides
    assert board.spaces[1].has_ruin
    assert board.spaces[2].has_ruin

    # aucune case vide après compression
    for space in board.spaces[1:]:
        assert space.has_ruin


# =========================
#  drop_tiles_to_bottom
# =========================

def test_drop_tiles_to_bottom_creates_new_spaces_with_stacks_of_3():
    """
    Non-régression : drop_tiles_to_bottom doit :
    - créer des nouvelles cases à la fin,
    - empiler les tuiles par groupes de stack_size (3 par défaut),
    - conserver le sous-marin et les cases existantes intactes.
    """
    sub = Space(is_submarine=True)
    initial_space = Space(is_submarine=False)
    initial_space.add_ruin(RuinTile(level=1, value=0))

    board = Board(spaces=[sub, initial_space])

    tiles = [
        RuinTile(level=2, value=4),
        RuinTile(level=2, value=5),
        RuinTile(level=2, value=6),
        RuinTile(level=3, value=8),
    ]

    board.drop_tiles_to_bottom(tiles, stack_size=3)

    # On avait 2 cases au départ, on en ajoute 2 :
    # - 1ère nouvelle : 3 tuiles
    # - 2ème nouvelle : 1 tuile
    assert board.size == 4

    # Les deux premières cases doivent être intactes
    assert board.spaces[0].is_submarine
    assert board.spaces[1].ruin_count == 1

    # Nouvelles cases
    new_space_1 = board.spaces[2]
    new_space_2 = board.spaces[3]

    assert new_space_1.ruin_count == 3
    assert new_space_2.ruin_count == 1

    # Elles ne doivent pas être des sous-marins
    assert not new_space_1.is_submarine
    assert not new_space_2.is_submarine
