from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty')
    clues = request.args.get('clues')

    if clues is not None:
        try:
            puzzle, solution = sudoku_logic.generate_puzzle(int(clues))
            current_difficulty = 'custom'
        except ValueError:
            puzzle, solution = sudoku_logic.generate_puzzle(difficulty or 'medium')
            current_difficulty = difficulty or 'medium'
    else:
        puzzle, solution = sudoku_logic.generate_puzzle(difficulty or 'medium')
        current_difficulty = difficulty or 'medium'

    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle, 'solution': solution, 'difficulty': current_difficulty})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.get_json(silent=True) or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            value = board[i][j] if board and i < len(board) and j < len(board[i]) else 0
            if value == 0:
                continue
            if value != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)