# tests/test_board.py
from src.board import Board
from src.space import Space


def test_default_board_has_submarine_at_zero():
    board = Board.create_default()
    assert board.size > 1
    assert board.get_space(0).is_submarine


def test_board_str_does_not_crash():
    board = Board.create_default()
    s = str(board)
    assert "SUB" in s


def test_serialization_round_trip():
    board = Board.create_default(shuffle_tiles=False)
    data = board.to_dict()
    board2 = Board.from_dict(data)

    assert board2.size == board.size
    assert board2.get_space(0).is_submarine
    # On vérifie par exemple qu’il y a le même nombre de ruines:
    total_ruins_1 = sum(sp.ruin_count for sp in board)
    total_ruins_2 = sum(sp.ruin_count for sp in board2)
    assert total_ruins_1 == total_ruins_2
