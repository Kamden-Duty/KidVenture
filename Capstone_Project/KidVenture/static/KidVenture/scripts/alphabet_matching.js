const maxLevel = 25;
const allLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
const cardClickSound = document.getElementById("card-click-sound");
let currentLevel = 1;
let totalMatches = 2;
let selectedPairs = [];
let firstCard = null;
let secondCard = null;
let timerStarted = false;
let timerInterval = null;
let elapsedSeconds = 0;
let matches = 0;
let mismatchCount = 0;

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
    cardElement.dataset.card = card;
    cardElement.textContent = card;
    cardElement.addEventListener("click", onCardClick);
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
).textContent = `Mismatched: ${mismatchCount}`;
}

function advanceToNextLevel() {
currentLevel++;
if (currentLevel > maxLevel) {
    alert(
    `Congratulations! You completed all levels in ${elapsedSeconds} seconds.`
    );
    return;
}

matches = 0;
totalMatches = currentLevel + 1;
elapsedSeconds = 0;
timerStarted = false;
firstCard = null;
secondCard = null;

document.getElementById("timer").textContent = "Time: 0 seconds";
initializeGame();
}

function triggerConfetti() {
confetti({
    particleCount: 300,
    spread: 200,
    origin: { y: 0.5 }
});
}

function playSound(soundId) {
const sound = document.getElementById(soundId);
sound.play();
}

function onCardClick(event) {
const clickedCard = event.target;

if (!timerStarted) {
    startTimer();
}

if (
    clickedCard.classList.contains("matched") ||
    clickedCard.classList.contains("selected")
)
    return;

clickedCard.classList.add("selected");

if (!firstCard) {
    firstCard = clickedCard;
    cardClickSound.play(); 
} else {
    secondCard = clickedCard;

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
    playSound("match-sound");

    if (matches === totalMatches) {
        stopTimer();
        playSound("level-up-sound");
        triggerConfetti(); 
        // The advanceToNextLevel function will be called once the level-up sound ends
    }
    } else {
    playSound("mismatch-sound");
    mismatchCount++; 
    firstCard.classList.add("mismatched");
    secondCard.classList.add("mismatched");
    updateScore();

    setTimeout(() => {
        firstCard.classList.remove("selected", "mismatched");
        secondCard.classList.remove("selected", "mismatched");
        firstCard = null;
        secondCard = null;
    }, 1000);
    }
}
}

// Add this event listener to call advanceToNextLevel once the sound has finished playing
document.getElementById("level-up-sound").addEventListener("ended", advanceToNextLevel);

initializeGame();
updateScore();