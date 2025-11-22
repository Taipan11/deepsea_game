import pytest
from src.ruin_tile import RuinTile
from src.space import Space

def test_submarine_cannot_have_ruins():
    t = RuinTile(level=1, value=0)
    with pytest.raises(ValueError):
        Space(is_submarine=True, ruins=[t])


def test_add_and_pop_ruin():
    s = Space()
    t1 = RuinTile(1, 0)
    t2 = RuinTile(2, 5)

    s.add_ruin(t1)
    s.add_ruin(t2)

    assert s.ruin_count == 2
    assert s.top_ruin == t2

    popped = s.pop_ruin()
    assert popped == t2
    assert s.ruin_count == 1
    assert s.top_ruin == t1


def test_stack_limit():
    s = Space(max_stack_size=2)
    s.add_ruin(RuinTile(1, 0))
    s.add_ruin(RuinTile(1, 1))
    with pytest.raises(ValueError):
        s.add_ruin(RuinTile(1, 2))


def test_serialization_round_trip():
    s = Space(
        is_submarine=False,
        max_stack_size=3,
        ruins=[RuinTile(1, 0), RuinTile(2, 7)],
    )
    data = s.to_dict()
    s2 = Space.from_dict(data)

    assert s2.is_submarine == s.is_submarine
    assert s2.max_stack_size == s.max_stack_size
    assert s2.ruin_count == s.ruin_count
    assert s2.ruins[0] == s.ruins[0]
    assert s2.ruins[1] == s.ruins[1]
