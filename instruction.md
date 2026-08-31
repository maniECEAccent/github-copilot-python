# Copilot Instructions

Act as a senior full-stack developer. We are refactoring a legacy Flask/Python Sudoku app.

## Development Guidelines

- Use Python and Flask for the backend.
- Use vanilla JavaScript for the frontend.
- Write modular, clean, readable, and maintainable Python code.
- Use clean HTML and CSS.
- Prioritize responsive and accessible UI design.
- Preserve existing functionality unless a requirement specifically changes it.
- Always consider the existing test suite before modifying code.
- Run tests after refactoring or adding major features.

## Sudoku Requirements

- Every generated Sudoku puzzle must have exactly one unique solvable solution.
- Support Easy, Medium, and Hard difficulty levels.
- Difficulty levels should change the number of pre-filled cells.
- Pre-filled cells must be locked so users cannot edit them.
- Invalid user inputs should receive immediate visual feedback.
- Provide a Hint button that reveals a correct empty cell and locks it.
- Provide a Check button that highlights incorrect entries.
- Display a completion/congratulations message when the puzzle is correctly solved.

## Game Features

- Include a stopwatch timer using MM:SS format.
- Include a Top 10 leaderboard.
- Store leaderboard data using browser localStorage.
- Store player name, time, difficulty, and hints used.
- Display leaderboard data using a structured HTML table.
- Include a dark mode toggle.
- Persist the dark mode preference using localStorage.

## UI Requirements

- Use a 9x9 Sudoku grid.
- Visually distinguish the nine 3x3 Sudoku blocks.
- Use alternating block backgrounds to create a checkerboard appearance.
- Make the layout responsive on different screen sizes.
- Keep text and controls readable in both light and dark modes.

## Copilot Behavior

Before making significant changes, inspect the existing implementation.
Do not blindly replace working code.
Explain important changes when requested.
If a proposed solution does not match the existing application, revise it.
Prefer small, testable changes over unnecessary rewrites.