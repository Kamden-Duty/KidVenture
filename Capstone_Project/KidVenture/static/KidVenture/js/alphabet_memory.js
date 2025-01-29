const maxLevel = 13;
const allLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
const cardClickSound = document.getElementById("card-click-sound");
const levelUpSound = document.getElementById("level-up-sound");
const mismatchSound = document.getElementById("mismatch-sound");
let currentLevel = 1;
let totalMatches = 2;
let selectedPairs = [];
let firstCard = null;
let secondCard = null;
let timerStarted = false;
let timerInterval = null;
let elapsedSeconds = 0;
let matches = 0;
let mismatches = 0;

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
    ...selectedPairs.map((letter) => letter.toUpperCase()),
    ...selectedPairs.map((letter) => letter.toLowerCase()),
].sort(() => 0.5 - Math.random());
createBoard(cards);
updateScore();
}

function createBoard(cards) {
const gameBoard = document.getElementById("game-board");
gameBoard.innerHTML = "";

cards.forEach((card) => {
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
timerStarted = true;
timerInterval = setInterval(() => {
    elapsedSeconds++;
    document.getElementById(
    "timer"
    ).textContent = `Time: ${elapsedSeconds} seconds`;
}, 1000);
}

function stopTimer() {
clearInterval(timerInterval);
document.getElementById(
    "timer"
).textContent = `Time: ${elapsedSeconds} seconds - Level Complete!`;
}

function updateScore() {
document.getElementById(
    "score"
).textContent = `Score: ${matches} / ${totalMatches}`;
document.getElementById(
    "mismatched"
).textContent = `Mismatched: ${mismatches}`;
}

function advanceToNextLevel() {
currentLevel++;
if (currentLevel > maxLevel) {
    alert(
    "Congratulations! You completed all levels in ${elapsedSeconds} seconds."
    );
    return;
}

matches = 0;
mismatches = 0;
totalMatches = currentLevel;
elapsedSeconds = 0;
timerStarted = false;
firstCard = null;
secondCard = null;

document.getElementById("timer").textContent = "Time: 0 seconds";
initializeGame();
levelUpSound.play();
}

function playSound(soundId) {
const sound = document.getElementById(soundId);
sound.play().catch((error) => {
    console.error("Error playing sound:", error);
});
}

function flipCard(cardElement) {
cardElement.classList.toggle("flip");
}

function onCardClick(cardElement) {
const cardInner = cardElement.querySelector(".card-inner");

if (
    cardInner.classList.contains("matched") ||
    cardElement.classList.contains("flip")
)
    return;

cardElement.classList.add("flip");

if (!firstCard) {
    firstCard = cardInner; // Mark the first card
} else {
    secondCard = cardInner; // Mark the second card

    // Check for a match
    if (
    firstCard.dataset.card.toLowerCase() ===
    secondCard.dataset.card.toLowerCase()
    ) {
    firstCard.classList.add("matched");
    secondCard.classList.add("matched");
    firstCard = null;
    secondCard = null;
    matches++;

    updateScore();
    if (matches === totalMatches) {
        stopTimer();
        setTimeout(advanceToNextLevel, 2000);
    }
    } else {
    mismatches++;
    updateScore();
    playSound("mismatch-sound");
    setTimeout(() => {
        firstCard.parentElement.classList.remove("flip");
        secondCard.parentElement.classList.remove("flip");
        firstCard = null;
        secondCard = null;
    }, 1000);    
    }
}
}

initializeGame();
updateScore();