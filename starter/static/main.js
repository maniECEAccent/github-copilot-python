// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const DARK_MODE_STORAGE_KEY = 'sudokuDarkMode';
let puzzle = [];
let currentSolution = [];
let currentDifficulty = 'medium';
let timerSeconds = 0;
let timerIntervalId = null;
let hintCount = 0;
let puzzleCompleted = false;
let leaderboardSaved = false;

const LEADERBOARD_STORAGE_KEY = 'sudokuLeaderboard';

function applyDarkModePreference(isDarkMode) {
  document.body.classList.toggle('dark-mode', isDarkMode);
  const toggleButton = document.getElementById('dark-mode-toggle');
  if (toggleButton) {
    toggleButton.textContent = isDarkMode ? 'Light Mode' : 'Dark Mode';
    toggleButton.setAttribute('aria-pressed', String(isDarkMode));
  }
  try {
    localStorage.setItem(DARK_MODE_STORAGE_KEY, JSON.stringify(isDarkMode));
  } catch (error) {
    // The app remains usable if browser storage is unavailable.
  }
}

function loadDarkModePreference() {
  try {
    const savedPreference = JSON.parse(localStorage.getItem(DARK_MODE_STORAGE_KEY) || 'false');
    applyDarkModePreference(Boolean(savedPreference));
  } catch (error) {
    applyDarkModePreference(false);
  }
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const timerEl = document.getElementById('timer');
  timerEl.textContent = formatTime(timerSeconds);
}

function updateHintDisplay() {
  const hintCounterEl = document.getElementById('hint-count');
  hintCounterEl.textContent = String(hintCount);
}

function getLeaderboard() {
  try {
    const savedScores = JSON.parse(localStorage.getItem(LEADERBOARD_STORAGE_KEY) || '[]');
    return Array.isArray(savedScores) ? savedScores : [];
  } catch (error) {
    return [];
  }
}

function renderLeaderboard() {
  const body = document.getElementById('leaderboard-body');
  const scores = getLeaderboard()
    .filter((score) => Number.isFinite(score.time) && typeof score.name === 'string')
    .sort((first, second) => first.time - second.time)
    .slice(0, 10);

  body.innerHTML = '';
  if (scores.length === 0) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 5;
    cell.textContent = 'No scores yet. Complete a puzzle to join the leaderboard.';
    row.appendChild(cell);
    body.appendChild(row);
    return;
  }

  scores.forEach((score, index) => {
    const row = document.createElement('tr');
    [index + 1, score.name, formatTime(score.time), score.level, score.hints].forEach((value) => {
      const cell = document.createElement('td');
      cell.textContent = String(value);
      row.appendChild(cell);
    });
    body.appendChild(row);
  });
}

function saveCompletedGame() {
  if (leaderboardSaved) {
    return;
  }

  leaderboardSaved = true;

  const playerName = window.prompt('Enter your name for the leaderboard:');
  if (playerName === null || playerName.trim() === '') {
    return;
  }

  const scores = getLeaderboard();
  scores.push({
    name: playerName.trim(),
    time: timerSeconds,
    level: currentDifficulty,
    hints: hintCount,
  });
  scores.sort((first, second) => first.time - second.time);
  try {
    localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(scores.slice(0, 10)));
  } catch (error) {
    // The game remains usable when browser storage is unavailable.
  }
  renderLeaderboard();
}

function buildBoardFromInputs(inputs) {
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

function updateIncorrectHighlights(inputs, incorrect) {
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) {
      inp.classList.remove('incorrect');
      continue;
    }

    inp.classList.remove('incorrect');
    if (incorrect.has(idx) && inp.value !== '') {
      inp.classList.add('incorrect');
    }
  }
}

async function validateBoard({ showMessage = true } = {}) {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = Array.from(boardDiv.getElementsByTagName('input'));
  const board = buildBoardFromInputs(inputs);

  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return false;
  }

  const incorrect = new Set(data.incorrect.map(([row, col]) => row * SIZE + col));
  updateIncorrectHighlights(inputs, incorrect);

  const hasEmptyCell = inputs.some((inp) => inp.value === '');
  const isSolved = incorrect.size === 0 && !hasEmptyCell;

  if (isSolved) {
    if (puzzleCompleted) {
      return true;
    }
    puzzleCompleted = true;
    stopTimer();
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
    saveCompletedGame();
    return true;
  }

  if (showMessage) {
    if (incorrect.size === 0) {
      msg.style.color = '#1976d2';
      msg.innerText = 'No incorrect entries found so far.';
    } else {
      msg.style.color = '#d32f2f';
      msg.innerText = 'Some cells are incorrect.';
    }
  }

  return false;
}

function stopTimer() {
  if (timerIntervalId !== null) {
    clearInterval(timerIntervalId);
    timerIntervalId = null;
  }
}

function startTimer() {
  stopTimer();
  timerSeconds = 0;
  updateTimerDisplay();

  timerIntervalId = setInterval(() => {
    timerSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;

      if ((Math.floor(i / 3) + Math.floor(j / 3)) % 2 === 0) {
        input.classList.add('shaded-block');
      }

      input.addEventListener('input', async (e) => {
        if (e.target.disabled) {
          e.target.value = e.target.dataset.original || '';
          return;
        }
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;

        if (!puzzleCompleted) {
          await validateBoard({ showMessage: false });
        }
      });

      input.addEventListener('paste', (e) => {
        if (e.target.disabled) {
          e.preventDefault();
        }
      });

      input.addEventListener('cut', (e) => {
        if (e.target.disabled) {
          e.preventDefault();
        }
      });

      input.addEventListener('keydown', (e) => {
        if (e.target.disabled) {
          e.preventDefault();
        }
      });

      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz, solution = []) {
  puzzle = puz;
  currentSolution = solution;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.dataset.original = String(val);
        inp.disabled = true;
        inp.readOnly = true;
        inp.classList.add('prefilled');
        inp.classList.remove('hinted');
        inp.setAttribute('aria-label', `Pre-filled cell with value ${val}, row ${i+1}, column ${j+1}`);
      } else {
        inp.value = '';
        inp.dataset.original = '';
        inp.disabled = false;
        inp.readOnly = false;
        inp.classList.remove('prefilled', 'hinted');
        inp.setAttribute('aria-label', `Empty cell, row ${i+1}, column ${j+1}`);
      }
    }
  }
}

function giveHint() {
  const inputs = Array.from(document.querySelectorAll('.sudoku-cell'));
  const targetInput = inputs.find((inp) => {
    const isEditable = !inp.disabled && inp.value === '' && !inp.classList.contains('hinted');
    return isEditable;
  });

  const msg = document.getElementById('message');
  if (!targetInput) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'No empty cells remain for a hint.';
    return;
  }

  const row = Number(targetInput.dataset.row);
  const col = Number(targetInput.dataset.col);
  const value = currentSolution[row][col];

  if (value === undefined || value === null || value === 0) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'No hint available for this cell.';
    return;
  }

  targetInput.value = String(value);
  targetInput.dataset.original = String(value);
  targetInput.disabled = true;
  targetInput.readOnly = true;
  targetInput.classList.remove('prefilled');
  targetInput.classList.add('hinted');
  targetInput.setAttribute('aria-label', `Hinted cell with value ${value}, row ${row+1}, column ${col+1}`);

  hintCount += 1;
  updateHintDisplay();
  msg.style.color = '#1976d2';
  msg.innerText = `Hint used (${hintCount}).`;
}

async function newGame() {
  const res = await fetch(`/new?difficulty=${currentDifficulty}`);
  const data = await res.json();
  currentSolution = Array.isArray(data.solution) ? data.solution : [];
  hintCount = 0;
  puzzleCompleted = false;
  leaderboardSaved = false;
  updateHintDisplay();
  renderPuzzle(data.puzzle, currentSolution);
  document.getElementById('message').innerText = '';
  startTimer();
}

async function checkSolution() {
  await validateBoard({ showMessage: true });
}

function setDifficulty(difficulty) {
  currentDifficulty = difficulty;

  const buttons = document.querySelectorAll('.difficulty-btn');
  buttons.forEach(btn => {
    if (btn.dataset.difficulty === difficulty) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  newGame();
}

function initializeApp() {
  loadDarkModePreference();
  updateTimerDisplay();
  updateHintDisplay();
  renderLeaderboard();

  const newGameButton = document.getElementById('new-game');
  const hintButton = document.getElementById('hint-button');
  const checkSolutionButton = document.getElementById('check-solution');

  if (newGameButton) {
    newGameButton.addEventListener('click', newGame);
  }
  if (hintButton) {
    hintButton.addEventListener('click', giveHint);
  }
  if (checkSolutionButton) {
    checkSolutionButton.addEventListener('click', checkSolution);
  }

  const darkModeToggle = document.getElementById('dark-mode-toggle');
  if (darkModeToggle) {
    darkModeToggle.addEventListener('click', () => {
      const isDarkMode = !document.body.classList.contains('dark-mode');
      applyDarkModePreference(isDarkMode);
    });
  }

  const difficultyButtons = document.querySelectorAll('.difficulty-btn');
  difficultyButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      setDifficulty(e.target.dataset.difficulty);
    });
  });

  newGame();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeApp, { once: true });
} else {
  initializeApp();
} 