import copy
import random

SIZE = 9
EMPTY = 0

# Difficulty levels: (min_clues, max_clues)
DIFFICULTY_LEVELS = {
    'easy': (40, 50),
    'medium': (30, 40),
    'hard': (17, 25)
}

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    """Check if placing num at (row, col) is valid according to Sudoku rules."""
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    """Fill the board completely using backtracking with randomized candidate selection."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def count_solutions(board, limit=2):
    """
    Count the number of solutions for a given puzzle, stopping at 'limit'.
    Returns the count (1, 2, or more) without necessarily finding all solutions.
    This is much faster than finding all solutions when there are many.
    """
    def solve_and_count(brd, max_count):
        """Backtracking helper to count solutions."""
        nonlocal solution_count
        
        # Early termination if we've found enough solutions
        if solution_count > max_count:
            return
        
        # Find next empty cell
        for row in range(SIZE):
            for col in range(SIZE):
                if brd[row][col] == EMPTY:
                    for num in range(1, SIZE + 1):
                        if is_safe(brd, row, col, num):
                            brd[row][col] = num
                            solve_and_count(brd, max_count)
                            brd[row][col] = EMPTY
                    return
        
        # No empty cells found—valid solution found
        solution_count += 1
    
    solution_count = 0
    test_board = deep_copy(board)
    solve_and_count(test_board, limit)
    return solution_count

def remove_cells_with_uniqueness_check(board, target_clues):
    """
    Remove cells from a completed board to create a puzzle with exactly one solution.
    Stop when the target number of clues is reached or when removing another cell
    would compromise uniqueness (result in 0 or multiple solutions).
    """
    puzzle = deep_copy(board)
    cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(cells)
    
    current_clues = SIZE * SIZE
    
    for row, col in cells:
        if current_clues <= target_clues:
            break
        
        if puzzle[row][col] != EMPTY:
            # Try removing this cell
            backup = puzzle[row][col]
            puzzle[row][col] = EMPTY
            current_clues -= 1
            
            # Check if puzzle still has exactly one solution
            solution_count = count_solutions(puzzle)
            
            if solution_count == 1:
                # Keep it removed
                pass
            else:
                # Restore the cell if uniqueness is compromised
                puzzle[row][col] = backup
                current_clues += 1
    
    return puzzle

def generate_puzzle(difficulty='medium'):
    """
    Generate a Sudoku puzzle with exactly one solution.

    Args:
        difficulty: 'easy', 'medium', 'hard', or an integer clue count

    Returns:
        (puzzle, solution) tuple where:
        - puzzle: 9x9 board with removed cells (playable puzzle)
        - solution: 9x9 complete solved board
    """
    # Accept a literal clue target (e.g. generate_puzzle(35)).
    if isinstance(difficulty, int):
        target_clues = max(17, min(81, difficulty))
    else:
        difficulty = str(difficulty).lower()
        if difficulty not in DIFFICULTY_LEVELS:
            difficulty = 'medium'

        min_clues, max_clues = DIFFICULTY_LEVELS[difficulty]
        target_clues = random.randint(min_clues, max_clues)

    # Generate complete valid solution
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)

    # Create puzzle by removing cells while preserving uniqueness
    puzzle = remove_cells_with_uniqueness_check(board, target_clues)

    return puzzle, solution
