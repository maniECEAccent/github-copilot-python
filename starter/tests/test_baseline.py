import copy

import pytest

from app import CURRENT, app
import sudoku_logic


@pytest.fixture(autouse=True)
def reset_game_state():
    CURRENT['puzzle'] = None
    CURRENT['solution'] = None
    yield
    CURRENT['puzzle'] = None
    CURRENT['solution'] = None


def is_complete_sudoku_board(board):
    """Return True when the board is a valid completed 9x9 Sudoku solution."""
    for row in board:
        if sorted(row) != list(range(1, 10)):
            return False

    for col_index in range(sudoku_logic.SIZE):
        column = [board[row_index][col_index] for row_index in range(sudoku_logic.SIZE)]
        if sorted(column) != list(range(1, 10)):
            return False

    for row_start in range(0, sudoku_logic.SIZE, 3):
        for col_start in range(0, sudoku_logic.SIZE, 3):
            box = []
            for row_index in range(row_start, row_start + 3):
                for col_index in range(col_start, col_start + 3):
                    box.append(board[row_index][col_index])
            if sorted(box) != list(range(1, 10)):
                return False

    return True


def test_index_route_returns_html_page():
    """The landing page should render the app's HTML shell."""
    client = app.test_client()

    response = client.get('/')

    assert response.status_code == 200
    assert response.mimetype == 'text/html'
    assert 'Sudoku Game' in response.get_data(as_text=True)


def test_new_game_route_generates_puzzle_and_sets_current_state():
    """The /new route should produce a 9x9 puzzle and store it in the app's in-memory state."""
    client = app.test_client()

    response = client.get('/new?clues=35')
    payload = response.get_json()

    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert 'puzzle' in payload

    puzzle = payload['puzzle']
    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert sum(1 for row in puzzle for value in row if value == sudoku_logic.EMPTY) == 81 - 35

    assert CURRENT['puzzle'] == puzzle
    assert CURRENT['solution'] is not None
    assert len(CURRENT['solution']) == sudoku_logic.SIZE
    assert is_complete_sudoku_board(CURRENT['solution'])


def test_new_game_route_exposes_solution_for_ui_hints():
    """Client-side hint logic needs the full solution alongside the puzzle."""
    client = app.test_client()

    response = client.get('/new?difficulty=easy')
    payload = response.get_json()

    assert response.status_code == 200
    assert 'solution' in payload
    assert payload['solution'] == CURRENT['solution']


def test_check_solution_without_current_game_returns_error():
    """The /check route should reject a solution check when no game has started."""
    client = app.test_client()

    response = client.post('/check', json={'board': [[0 for _ in range(9)] for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_check_solution_accepts_correct_board():
    """A board matching the stored solution should be accepted with no incorrect positions."""
    client = app.test_client()
    client.get('/new?clues=35')
    solution = copy.deepcopy(CURRENT['solution'])

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}


def test_check_solution_reports_incorrect_positions():
    """The /check route should return each mismatched cell coordinate when the submitted board differs."""
    client = app.test_client()
    client.get('/new?clues=35')
    solution = copy.deepcopy(CURRENT['solution'])
    solution[0][0] = 1 if solution[0][0] != 1 else 2

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == [[0, 0]]


def test_check_solution_ignores_empty_cells_when_reporting_incorrect_positions():
    """Empty cells should not be reported as incorrect just because they are blank."""
    client = app.test_client()
    client.get('/new?clues=35')
    solution = copy.deepcopy(CURRENT['solution'])
    solution[0][0] = 0
    solution[1][1] = solution[1][1] + 1 if solution[1][1] < 9 else 1

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == [[1, 1]]


def test_generate_puzzle_returns_solved_board_and_expected_number_of_clues():
    """The Sudoku generator should create a valid solved board and remove cells to produce the requested clue count."""
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)
    assert is_complete_sudoku_board(solution)
    assert sum(1 for row in puzzle for value in row if value == sudoku_logic.EMPTY) == 81 - 35


def test_create_empty_board_and_is_safe_match_current_logic():
    """The utility functions should build empty boards and detect conflicts in row, column, and box checks."""
    empty = sudoku_logic.create_empty_board()
    assert len(empty) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in empty)
    assert all(value == sudoku_logic.EMPTY for row in empty for value in row)

    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    board[0][1] = 1
    board[1][0] = 9
    assert sudoku_logic.is_safe(board, 0, 2, 5) is False
    assert sudoku_logic.is_safe(board, 0, 2, 3) is True

    copied = sudoku_logic.deep_copy(board)
    assert copied == board
    assert copied is not board
    copied[0][0] = 8
    assert board[0][0] == 5


def test_fill_board_solves_a_blank_board():
    """fill_board should complete an empty board into a valid Sudoku solution."""
    board = sudoku_logic.create_empty_board()
    solved = sudoku_logic.fill_board(board)

    assert solved is True
    assert is_complete_sudoku_board(board)
