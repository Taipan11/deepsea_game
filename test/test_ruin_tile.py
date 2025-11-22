import pytest
from ruin_tile import RuinTile


def test_valid_tile_creation():
    t = RuinTile(level=2, value=7)
    assert t.level == 2
    assert t.value == 7
    assert t.is_shallow
    assert not t.is_deep


def test_invalid_level_raises_error():
    with pytest.raises(ValueError):
        RuinTile(level=0, value=3)
    with pytest.raises(ValueError):
        RuinTile(level=5, value=3)


def test_negative_value_raises_error():
    with pytest.raises(ValueError):
        RuinTile(level=1, value=-1)


def test_serialization_round_trip():
    t = RuinTile(level=3, value=12)
    data = t.to_dict()
    t2 = RuinTile.from_dict(data)
    assert t == t2
