import { messages, MessageCategories } from '/static/KidVenture/js/messages.js';

const urlParams = new URLSearchParams(window.location.search);
const activityId = urlParams.get('activity') || null;
const gameType = window.GAME_TYPE || 'memory';
const maxLevel = 13;
const allLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
const cardClickSound = document.getElementById("card-click-sound");
const levelUpSound = document.getElementById("level-up-sound");
const mismatchSound = document.getElementById("mismatch-sound");

let currentLevel = 1;
let totalMatches = currentLevel + 1;
let selectedPairs = [];
let firstCard = null;
let secondCard = null;
let timerStarted = false;
let timerInterval = null;
let elapsedSeconds = 0;
let matches = 0;
let mismatchCount = 0;
let mismatchedLetters = [];

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
}

function initializeGame() {
  shuffle(allLetters);
  selectedPairs = allLetters.slice(0, totalMatches);
  const cards = [
    ...selectedPairs.map(letter => letter.toUpperCase()),
    ...selectedPairs.map(letter => letter.toLowerCase())
  ].sort(() => 0.5 - Math.random());
  createBoard(cards);
  updateScore();
}

function createBoard(cards) {
  const gameBoard = document.getElementById("game-board");
  gameBoard.innerHTML = "";

  cards.forEach(card => {
    const cardElement = document.createElement("div");
    cardElement.classList.add("card");

    const cardInner = document.createElement("div");
    cardInner.classList.add("card-inner");
    cardInner.dataset.card = card;

    const frontFace = document.createElement("div");
    frontFace.classList.add("card-front");
    frontFace.textContent = card;

    const backFace = document.createElement("div");
    backFace.classList.add("card-back");

    cardInner.appendChild(frontFace);
    cardInner.appendChild(backFace);
    cardElement.appendChild(cardInner);

    cardElement.addEventListener("click", () => {
      onCardClick(cardElement);
    });

    gameBoard.appendChild(cardElement);
  });
}

function startTimer() {
  if (timerStarted) return;
  timerStarted = true;
  timerInterval = setInterval(() => {
    elapsedSeconds++;
    document.getElementById("timer").textContent = `Time: ${elapsedSeconds} seconds`;
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
  document.getElementById("timer").textContent = `Time: ${elapsedSeconds} seconds - Level Complete!`;
}

function updateScore() {
  document.getElementById("score").textContent = `Score: ${matches} / ${totalMatches}`;
  document.getElementById("mismatched").textContent = `Mismatched: ${mismatchCount}`;
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function displayEndLevelMessages(elapsedSeconds, mismatchCount) {
    let message = "";
  
    if (mismatchCount === 0) {
      message = messages[MessageCategories.REALLY_WELL][Math.floor(Math.random() * messages[MessageCategories.REALLY_WELL].length)];
    } else if (mismatchCount < 3) {
      message = messages[MessageCategories.LOW_MISTAKES][Math.floor(Math.random() * messages[MessageCategories.LOW_MISTAKES].length)];
    } else if (elapsedSeconds < 30) {
      message = messages[MessageCategories.FAST_COMPLETION][Math.floor(Math.random() * messages[MessageCategories.FAST_COMPLETION].length)];
    } else if (elapsedSeconds < 60) {
      const options = [
        ...messages[MessageCategories.GENERAL_PRAISE],
        ...messages[MessageCategories.FRIENDLY_ENCOURAGEMENT],
        ...messages[MessageCategories.CREATIVE_AND_FUN]
      ];
      message = options[Math.floor(Math.random() * options.length)];
    } else {
      const options = [
        ...messages[MessageCategories.MOTIVATION_FOR_IMPROVEMENT],
        ...messages[MessageCategories.FRIENDLY_ENCOURAGEMENT],
        ...messages[MessageCategories.CREATIVE_AND_FUN]
      ];
      message = options[Math.floor(Math.random() * options.length)];
    }
  
    message = message.replace('{time}', elapsedSeconds).replace('{mistakes}', mismatchCount);
  
    const overlay = document.getElementById("end-level-overlay");
    const messageElement = document.getElementById("end-level-message");
    messageElement.textContent = message;
    overlay.style.visibility = "visible";
  
    setTimeout(() => {
      overlay.style.visibility = "hidden";
    }, 3500);
  }
  
function triggerConfetti() {
  confetti({
    particleCount: 250,
    spread: 200,
    origin: { y: 0.5 }
  });
}

function saveGameProgress(level, timeTaken, mistakes, mismatchedLetters, activityId = null) {
  const data = {
    level,
    time_taken: timeTaken,
    mistakes,
    mismatched_letters: mismatchedLetters,
    game_type: gameType,
  };

  if (activityId) {
    data.activity_id = activityId;
  }

  return fetch('/save_game_progress/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify(data),
  }).then(res => res.json());
}

function advanceToNextLevel() {
  currentLevel++;
  totalMatches = currentLevel + 1;

  if (activityId) {
    saveGameProgress(currentLevel, elapsedSeconds, mismatchCount, mismatchedLetters, activityId)
      .then(() => fetch(`/check_activity_progress/${activityId}/`))
      .then(res => res.json())
      .then(data => {
        if (data.completed) {
          return fetch(`/complete_activity/${activityId}/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken'),
            }
          }).then(res => res.json());
        } else {
          startNextRound();
        }
      })
      .then(data => {
        if (data?.status === 'success') {
          Swal.fire({
            title: 'Activity Complete!',
            text: 'Great job!',
            icon: 'success',
            confirmButtonText: 'OK',
            allowOutsideClick: false,
          }).then(() => window.location.href = '/');
        }
      });
  } else {
    saveGameProgress(currentLevel, elapsedSeconds, mismatchCount, mismatchedLetters)
      .then(() => {
        if (currentLevel > maxLevel) {
          Swal.fire({
            title: 'Well Done!',
            text: `You completed all levels in ${elapsedSeconds} seconds.`,
            icon: 'success',
            confirmButtonText: 'OK'
          }).then(() => window.location.href = '/');
          return;
        }

        localStorage.removeItem('skipSessionModal');
        startNextRound();
      });
  }
}

function startNextRound() {
  matches = 0;
  mismatchCount = 0;
  elapsedSeconds = 0;
  timerStarted = false;
  firstCard = null;
  secondCard = null;
  document.getElementById("timer").textContent = "Time: 0 seconds";
  initializeGame();
}

function onCardClick(cardElement) {
  const cardInner = cardElement.querySelector(".card-inner");
  if (cardInner.classList.contains("matched") || cardElement.classList.contains("flip")) return;

  if (!timerStarted) startTimer();

  cardElement.classList.add("flip");

  if (!firstCard) {
    firstCard = cardInner;
    cardClickSound.play();
  } else {
    secondCard = cardInner;

    if (firstCard.dataset.card.toLowerCase() === secondCard.dataset.card.toLowerCase()) {
      firstCard.classList.add("matched");
      secondCard.classList.add("matched");
      matches++;
      firstCard = null;
      secondCard = null;
      updateScore();
      if (matches === totalMatches) {
        stopTimer();
        triggerConfetti();
        displayEndLevelMessages(elapsedSeconds, mismatchCount);
        levelUpSound.removeEventListener("ended", advanceToNextLevel);
        levelUpSound.addEventListener("ended", advanceToNextLevel);
        levelUpSound.play();
      }
    } else {
      mismatchCount++;
      mismatchedLetters.push({ first: firstCard.dataset.card, second: secondCard.dataset.card });
      updateScore();
      mismatchSound.play();

      setTimeout(() => {
        firstCard.parentElement.classList.remove("flip");
        secondCard.parentElement.classList.remove("flip");
        firstCard = null;
        secondCard = null;
      }, 1000);
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (activityId) {
    fetch(`/get_activity_progress/${activityId}/`)
      .then(res => res.json())
      .then(data => {
        currentLevel = data.last_level || 1;
        totalMatches = currentLevel + 1;
        initializeGame();
      });
  } else {
    fetch(`/get_last_session/?game_type=${gameType}`)
      .then(res => res.json())
      .then(data => {
        if (data.last_level && data.last_level > 1) {
          const skipModal = localStorage.getItem("skipSessionModal") === "true";
          if (!skipModal) {
            document.getElementById("continue-btn").setAttribute("data-last-level", data.last_level);
            document.getElementById("session-modal").classList.remove("hidden");
            document.getElementById("continue-btn").addEventListener("click", () => {
              currentLevel = data.last_level;
              totalMatches = currentLevel + 1;
              document.getElementById("session-modal").classList.add("hidden");
              initializeGame();
            });
            document.getElementById("start-over-btn").addEventListener("click", () => {
                localStorage.setItem("skipSessionModal", "true");
                fetch('/reset_free_play_progress/', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                  },
                  body: JSON.stringify({ game_type: gameType })
                }).then(() => {
                  currentLevel = 1;
                  totalMatches = currentLevel + 1;
                  initializeGame();
                  document.getElementById("session-modal").classList.add("hidden");
                });
              });
              
          } else {
            localStorage.removeItem("skipSessionModal");
            initializeGame();
          }
        } else {
          initializeGame();
        }
      })
      .catch(() => initializeGame());
  }

  updateScore();
});
