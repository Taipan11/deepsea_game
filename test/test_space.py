import pytest

from src.space import Space
from src.ruin_tile import RuinTile


# ---------- Helpers ----------

def make_tile(level=1, value=1) -> RuinTile:
    return RuinTile(level=level, value=value)


# ---------- __post_init__ ----------

def test_submarine_cannot_have_ruins():
    t = make_tile()
    with pytest.raises(ValueError):
        Space(is_submarine=True, ruins=[t])


def test_max_stack_size_respected_on_init():
    t1 = make_tile()
    t2 = make_tile()
    with pytest.raises(ValueError):
        Space(is_submarine=False, ruins=[t1, t2], max_stack_size=1)


def test_regular_space_initial_state():
    s = Space(is_submarine=False)
    assert s.is_submarine is False
    assert s.ruins == []
    assert s.max_stack_size is None
    assert s.is_empty is True
    assert s.has_ruin is False
    assert s.top_ruin is None


def test_submarine_initial_state():
    s = Space(is_submarine=True)
    assert s.is_submarine is True
    assert s.ruins == []
    assert s.is_empty is True
    assert s.has_ruin is False


# ---------- Propriétés utiles ----------

def test_has_ruin_and_ruin_count():
    s = Space()
    assert s.has_ruin is False
    assert s.ruin_count == 0

    t1 = make_tile(value=1)
    t2 = make_tile(value=2)
    s.ruins = [t1, t2]

    assert s.has_ruin is True
    assert s.ruin_count == 2
    assert s.is_empty is False


def test_top_ruin_returns_last_tile():
    s = Space()
    t1 = make_tile(value=1)
    t2 = make_tile(value=2)
    s.ruins = [t1, t2]

    assert s.top_ruin is t2


# ---------- add_ruin / push_ruin / pop_ruin ----------

def test_add_ruin_on_submarine_raises():
    s = Space(is_submarine=True)
    t = make_tile()

    with pytest.raises(ValueError):
        s.add_ruin(t)


def test_add_ruin_respects_max_stack_size():
    s = Space(is_submarine=False, max_stack_size=2)
    t1 = make_tile(value=1)
    t2 = make_tile(value=2)
    t3 = make_tile(value=3)

    s.add_ruin(t1)
    s.add_ruin(t2)
    assert s.ruins == [t1, t2]

    with pytest.raises(ValueError):
        s.add_ruin(t3)


def test_add_ruin_without_limit():
    s = Space(is_submarine=False, max_stack_size=None)
    t1 = make_tile(value=1)
    t2 = make_tile(value=2)

    s.add_ruin(t1)
    s.add_ruin(t2)

    assert s.ruins == [t1, t2]
    assert s.ruin_count == 2


def test_push_ruin_does_not_check_max_stack_size():
    """
    push_ruin ne vérifie pas max_stack_size : on peut dépasser la limite.
    """
    s = Space(is_submarine=False, max_stack_size=1)
    t1 = make_tile(value=1)
    t2 = make_tile(value=2)

    s.add_ruin(t1)
    # pile 'pleine' pour add_ruin, mais push_ruin doit passer
    s.push_ruin(t2)

    assert s.ruins == [t1, t2]
    assert s.ruin_count == 2


def test_pop_ruin_on_non_empty_space():
    s = Space()
    t1 = make_tile(value=1)
    t2 = make_tile(value=2)
    s.ruins = [t1, t2]

    popped = s.pop_ruin()
    assert popped is t2
    assert s.ruins == [t1]

    popped2 = s.pop_ruin()
    assert popped2 is t1
    assert s.ruins == []
    assert s.is_empty is True


def test_pop_ruin_on_empty_space_returns_none():
    s = Space()
    popped = s.pop_ruin()
    assert popped is None
    assert s.ruins == []


# ---------- remove_all_ruins / pop_all_ruins_as_single ----------

def test_remove_all_ruins_returns_copy_and_clears():
    s = Space()
    t1 = make_tile(level=1, value=1)
    t2 = make_tile(level=1, value=2)
    s.ruins = [t1, t2]

    tiles = s.remove_all_ruins()

    assert tiles == [t1, t2]
    assert s.ruins == []
    assert s.is_empty is True


def test_pop_all_ruins_as_single_on_empty_returns_none():
    s = Space()
    result = s.pop_all_ruins_as_single()
    assert result is None
    assert s.ruins == []


def test_pop_all_ruins_as_single_combines_value_and_max_level():
    s = Space()
    t1 = make_tile(level=1, value=2)
    t2 = make_tile(level=2, value=5)
    t3 = make_tile(level=3, value=10)
    s.ruins = [t1, t2, t3]

    combined = s.pop_all_ruins_as_single()

    # case vidée
    assert s.ruins == []
    assert s.is_empty is True

    # tuile combinée correctement
    assert isinstance(combined, RuinTile)
    assert combined.value == 2 + 5 + 10
    assert combined.level == 3  # max des niveaux


# ---------- __str__ ----------

def test_str_submarine():
    s = Space(is_submarine=True)
    assert str(s) == "SUB"


def test_str_empty_non_submarine():
    s = Space(is_submarine=False)
    assert str(s) == "."


def test_str_single_ruin_uses_ruintile_str():
    t = make_tile(level=2, value=7)
    s = Space(is_submarine=False, ruins=[t])

    assert str(s) == str(t)


def test_str_multiple_ruins_shows_countR():
    s = Space()
    s.ruins = [make_tile(), make_tile(), make_tile()]

    assert str(s) == "3R"


# ---------- Sérialisation ----------

def test_to_dict_structure():
    t1 = make_tile(level=1, value=0)
    t2 = make_tile(level=2, value=5)
    s = Space(is_submarine=False, max_stack_size=3, ruins=[t1, t2])

    data = s.to_dict()

    assert data["is_submarine"] is False
    assert data["max_stack_size"] == 3
    assert isinstance(data["ruins"], list)
    assert len(data["ruins"]) == 2
    assert set(data["ruins"][0].keys()) >= {"level", "value"}


def test_from_dict_recreates_space():
    t1 = make_tile(level=1, value=0)
    t2 = make_tile(level=2, value=5)
    original = Space(is_submarine=False, max_stack_size=3, ruins=[t1, t2])

    data = original.to_dict()
    clone = Space.from_dict(data)

    assert clone.is_submarine is False
    assert clone.max_stack_size == 3
    assert len(clone.ruins) == 2
    assert [tile.level for tile in clone.ruins] == [1, 2]
    assert [tile.value for tile in clone.ruins] == [0, 5]


def test_from_dict_non_regression_ruins_list_not_shared():
    """
    Vérifie qu'on recrée une nouvelle liste de ruines,
    et pas une référence partagée.
    """
    s1 = Space(is_submarine=False, ruins=[make_tile(value=1)])
    data = s1.to_dict()
    s2 = Space.from_dict(data)

    s2.ruins.append(make_tile(value=99))

    assert len(s1.ruins) == 1
    assert len(s2.ruins) == 2
