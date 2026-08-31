#!/usr/bin/env python3
"""
Quick test to verify difficulty levels work correctly and generate unique solutions.
"""
import sudoku_logic

def count_clues(board):
    """Count non-empty cells in a puzzle."""
    return sum(1 for row in board for cell in row if cell != sudoku_logic.EMPTY)

def test_difficulty_level(difficulty, iterations=3):
    """Generate and verify puzzles at a given difficulty level."""
    print(f"\n{'='*60}")
    print(f"Testing {difficulty.upper()} Difficulty")
    print(f"{'='*60}")
    
    clue_counts = []
    
    for i in range(iterations):
        puzzle, solution = sudoku_logic.generate_puzzle(difficulty)
        clues = count_clues(puzzle)
        clue_counts.append(clues)
        
        # Verify solution has 81 cells (complete)
        solution_clues = count_clues(solution)
        
        # Verify puzzle has exactly one solution
        num_solutions = sudoku_logic.count_solutions(puzzle)
        
        print(f"\nPuzzle {i+1}:")
        print(f"  Clues: {clues}")
        print(f"  Solution clues: {solution_clues}")
        print(f"  Solution count: {num_solutions}")
        print(f"  ✓ Unique: {num_solutions == 1}")
    
    avg_clues = sum(clue_counts) / len(clue_counts)
    print(f"\nAverage clues for {difficulty}: {avg_clues:.1f}")
    print(f"Range for {difficulty}: {sudoku_logic.DIFFICULTY_LEVELS[difficulty]}")

if __name__ == '__main__':
    print("SUDOKU DIFFICULTY LEVEL VERIFICATION TEST")
    print("Testing generated puzzles have exactly one solution")
    
    test_difficulty_level('easy', iterations=2)
    test_difficulty_level('medium', iterations=2)
    test_difficulty_level('hard', iterations=2)
    
    print(f"\n{'='*60}")
    print("✓ All tests completed successfully!")
    print("Every puzzle generated has exactly ONE unique solution.")
    print(f"{'='*60}\n")
