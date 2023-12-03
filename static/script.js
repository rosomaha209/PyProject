document.addEventListener("DOMContentLoaded", function () {
  const gameContainer = document.querySelector(".game-container");
  const canvas = document.getElementById("gameCanvas");
  const ctx = canvas.getContext("2d");

  const cellSize = 20;
  let currentLevel = 1;

  let maze = generateMaze(9, 9);
  const player = {
    x: 1,
    y: 1,
    size: cellSize, // Розмір гравця відповідає розміру клітинки
  };
  function resizeCanvas() {
  const { width, height } = gameContainer.getBoundingClientRect();

  // Очистити канвас перед зміною розміру
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Задати розміри канвасу з врахуванням розмірів блоку gameContainer
  canvas.width = width;
  canvas.height = height;

  // Перераховуємо лабіринт з новими розмірами канвасу
  const newWidth = Math.floor(width / cellSize);
  const newHeight = Math.floor(height / cellSize);

  maze = generateMaze(newWidth, newHeight);

  // Оновлюємо відображення лабіринту при зміні розмірів
  drawMaze();
  drawPlayer();
}


  window.addEventListener("resize", resizeCanvas);

// Функція для малювання відвіданих клітинок сірим кольором
function drawVisitedCells() {
  for (const cell of visitedCells) {
    ctx.fillStyle = '#888'; // Темно-сірий колір для пройдених клітинок
    ctx.fillRect(
      cell.x * cellWidth,
      cell.y * cellHeight,
      cellWidth,
      cellHeight
    );
  }
}
 // Функція для відображення рівня на сторінці
  function displayLevel() {
    const levelElement = document.getElementById('level');
    levelElement.innerText = `Level: ${currentLevel}`;
  }

 // Функція для відстеження часу проходження
  let seconds = 0;
  let timerInterval;

  function startTimer() {
    timerInterval = setInterval(function () {
      seconds++;
      displayTime();
    }, 1000);
  }

  function displayTime() {
    const timerElement = document.getElementById('timer');
    timerElement.innerText = `Time: ${seconds} sec`;
  }

const visitedCells = []; // Додайте це поза функцією generateMaze()


// Функція, яка відправляє рівень на сервер
function sendLevelToServer(level) {
  fetch('/save_level', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ level: level }),
  })
  .then(response => {
    if (response.ok) {
      console.log('Level sent successfully');
    } else {
      console.error('Failed to send level');
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

// Перевіряти, чи клітина була відвідана перед рухом гравця
function isCellVisited(x, y) {
  return visitedCells.some(cell => cell.x === x && cell.y === y);
}


function generateMaze(width, height) {
// Перевірка на парність розмірів
  if (width % 2 === 0) {
    width--; // Якщо ширина непарна, зменшуємо на одиницю
  }
  if (height % 2 === 0) {
    height--; // Якщо висота непарна, зменшуємо на одиницю
  }


  const maze = [];
  for (let i = 0; i < height; i++) {
    maze.push([]);
    for (let j = 0; j < width; j++) {
      maze[i].push(1); // Заповнення лабіринту стінами
    }
  }

  function recursiveBacktracking(x, y) {
  maze[y][x] = 0; // Позначення поточної клітини як прохід

  const directions = [
    [-2, 0],
    [2, 0],
    [0, -2],
    [0, 2],
  ]; // Всі можливі напрямки руху

  directions.sort(() => Math.random() - 0.5); // Випадковий порядок напрямків

  for (const direction of directions) {
    const dx = x + direction[0];
    const dy = y + direction[1];

    if (dx > 0 && dx < width - 1 && dy > 0 && dy < height - 1 && maze[dy][dx] === 1) {
      // Перевірка, щоб не виходити за межі лабіринту та не ламати прохідність
      const midX = x + direction[0] / 2;
      const midY = y + direction[1] / 2;

      maze[dy][dx] = 0;
      maze[midY][midX] = 0;

      recursiveBacktracking(dx, dy); // Рекурсивний виклик для наступної клітини
    }
  }
}


  recursiveBacktracking(1, 1); // Початок алгоритму з певної клітини

  // Точка входу
  maze[1][0] = 0;

  // Точка виходу
  maze[height - 2][width - 1] = 0;

  return maze;
}

function drawMaze() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const cellWidth = canvas.width / maze[0].length;
  const cellHeight = canvas.height / maze.length;

  for (let i = 0; i < maze.length; i++) {
    for (let j = 0; j < maze[i].length; j++) {
      if (maze[i][j] === 1) {
        ctx.fillStyle = '#000'; // Колір стін
      } else if (i === 1 && j === 0) {
        ctx.fillStyle = '#00FF00'; // Колір точки входу (зелений)
      } else if (i === maze.length - 2 && j === maze[i].length - 1) {
        ctx.fillStyle = '#FF0000'; // Колір точки виходу (червоний)
      } else {
        ctx.fillStyle = '#fff'; // Колір порожньої клітинки
      }
      ctx.fillRect(j * cellWidth, i * cellHeight, cellWidth, cellHeight);
      // Перевіряємо, чи клітинка вже відвідана, і малюємо її сірим, якщо так
      if (visitedCells.some(cell => cell.x === j && cell.y === i)) {
        ctx.fillStyle = '#888'; // Темно-сірий колір для пройдених клітинок
        ctx.fillRect(j * cellWidth, i * cellHeight, cellWidth, cellHeight);
      }
    }
  }

}

function drawPlayer() {
  ctx.fillStyle = "#0000FF"; // Змінити колір гравця
  const playerSize = Math.min(canvas.width / maze[0].length, canvas.height / maze.length);
  ctx.fillRect(player.x * (canvas.width / maze[0].length), player.y * (canvas.height / maze.length), playerSize, playerSize);
}

// Функція, яка блокує прокрутку сторінки при натисканні стрілок
function preventDefaultForScrollKeys(e) {
  const keys = { 37: 1, 38: 1, 39: 1, 40: 1 };
  if (keys[e.keyCode]) {
    e.preventDefault();
    return false;
  }
}

// Включення обробника подій для блокування прокрутки сторінки
function disableScroll() {
  window.addEventListener("keydown", preventDefaultForScrollKeys, false);
}
// Функція для переходу на наступний рівень
  function moveToNextLevel() {
  sendLevelToServer(currentLevel);
    currentLevel++;
     visitedCells.splice(0); // Очистка масиву відвіданих клітинок
    clearInterval(timerInterval); // Зупинка таймера перед переходом на новий рівень
    seconds = 0; // Скидання лічильника часу
    startTimer(); // Запуск таймера для нового рівня
    displayLevel();
    // Отримання нових розмірів лабіринту
  const newWidth = maze[0].length + 2;
  const newHeight = maze.length + 2;

  // Збільшення розміру лабіринту на 1
  maze = generateMaze(newWidth, newHeight);
  }

  function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }

 function movePlayer(event) {
  switch (event.key) {
    case "ArrowUp":
      if (maze[player.y - 1][player.x] !== 1) {
        player.y -= 1;
      }
      break;
    case "ArrowDown":
      if (maze[player.y + 1][player.x] !== 1) {
        player.y += 1;
      }
      break;
    case "ArrowLeft":
      if (maze[player.y][player.x - 1] !== 1) {
        player.x -= 1;
      }
      break;
    case "ArrowRight":
      if (maze[player.y][player.x + 1] !== 1) {
        player.x += 1;
      }
      break;
    default:
      return;
  }
if (isCellVisited(player.x, player.y)) {
    // Якщо так, зупинити рух гравця на цю клітинку
    return;
  } else {
    // Якщо клітинка ще не була відвідана, додати її в масив відвіданих
    visitedCells.push({ x: player.x, y: player.y });
  }
  // Перевірка, чи гравець досяг точки виходу
  if (player.y === maze.length - 2 && player.x === maze[0].length - 1) {
     moveToNextLevel(); // Виклик функції для переходу на наступний рівень


   // maze = generateMaze(19, 19); // Генеруємо новий лабіринт для наступного рівня
    player.x = 0; // Розміщуємо гравця на початку нового рівня
    player.y = 1;

    // Малюємо новий лабіринт та гравця
    clearCanvas();
    drawMaze();
    drawPlayer();
  } else {
    // Якщо гравець не досяг точки виходу, просто перемальовуємо гравця
    clearCanvas();
    drawMaze();
    drawPlayer();
     visitedCells.push({ x: player.x, y: player.y });
  }
}


  document.addEventListener("keydown", movePlayer);

  function startGame() {
    drawMaze();
    drawPlayer();
  }

  window.onload = function () {
    resizeCanvas(); // Задати розмір канвасу при запуску гри
    disableScroll();
    startGame();
    displayLevel();
    startTimer();
  };

  console.log("Сайт завантажився!");
});
