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
                displayEndLevelMessages(timerInterval, mismatchCount);
                // The advanceToNextLevel function will be called once the level-up sound ends
            }
        } else {
            playSound("mismatch-sound");
            mismatchCount++; 
            firstCard.classList.add("mismatched");
            secondCard.classList.add("mismatched");
            updateScore();

            // Highlight the correct match
            const correctMatch = Array.from(document.querySelectorAll(".card")).find(
                card => card.dataset.card.toLowerCase() === firstCard.dataset.card.toLowerCase() && card !== firstCard
            );
            correctMatch.classList.add("correct-match");

            setTimeout(() => {
                firstCard.classList.remove("selected", "mismatched");
                secondCard.classList.remove("selected", "mismatched");
                correctMatch.classList.remove("correct-match");
                firstCard = null;
                secondCard = null;
                reshuffleCards();
            }, 2000);
        }
    }
}

function reshuffleCards() {
    const gameBoard = document.getElementById("game-board");
    const allCards = Array.from(gameBoard.querySelectorAll(".card"));

    // Get the values and matched status of all cards
    const allCardValues = allCards.map(card => ({
        value: card.dataset.card,
        isMatched: card.classList.contains("matched")
    }));

    // Shuffle all cards
    shuffle(allCardValues);

    // Clear the board
    gameBoard.innerHTML = "";

    // Re-add all cards in shuffled order
    allCardValues.forEach(cardInfo => {
        const cardElement = document.createElement("div");
        cardElement.classList.add("card");
        cardElement.dataset.card = cardInfo.value;
        cardElement.textContent = cardInfo.value;
        if (cardInfo.isMatched) {
            cardElement.classList.add("matched");
        }
        cardElement.addEventListener("click", onCardClick);
        gameBoard.appendChild(cardElement);
    });
}

function displayEndLevelMessages(elapsedSeconds, mismatchCount) {
    const generalPraise = [
        `Fantastic work! You completed the level in just ${elapsedSeconds} seconds with only ${mismatchCount} mistakes. Keep it up!`,
        `Great job! It took you ${elapsedSeconds} seconds to finish, and you’re improving every step of the way!`,
        `Well done! With only ${mismatchCount} mistakes and a time of ${elapsedSeconds} seconds, you’re mastering these letters quickly!`,
        `Awesome effort! Just ${elapsedSeconds} seconds to finish this level. Let’s aim for even fewer mistakes next time!`,
        `You did it! ${elapsedSeconds} seconds and ${mismatchCount} mistakes—your hard work is paying off!`
    ];

    const lowMistakes = [
        `Wow! Only ${mismatchCount} mistakes this level! Your focus is fantastic!`,
        `Amazing! ${mismatchCount} mistakes in ${elapsedSeconds} seconds? That’s incredible progress!`,
        `So close to perfection! ${elapsedSeconds} seconds and just ${mismatchCount} mistakes. You’re on fire!`
    ];

    const fastCompletion = [
        `Speedy and sharp! You finished the level in just ${elapsedSeconds} seconds. Can you go even faster next time?`,
        `Lightning quick! ${elapsedSeconds} seconds flat. Keep pushing, and you’ll be unstoppable!`
    ];

    const motivationForImprovement = [
        `Good effort! You completed the level in ${elapsedSeconds} seconds. Let’s focus on cutting down those ${mismatchCount} mistakes!`,
        `Well done! ${mismatchCount} mistakes this time. Try for even fewer in the next level!`,
        `Every mistake is a learning opportunity! You finished in ${elapsedSeconds} seconds, and you’ll get even better.`,
        `Keep going! ${elapsedSeconds} seconds and ${mismatchCount} mistakes mean you’re making solid progress.`
    ];

    const friendlyEncouragement = [
        `Great job! Remember, practice makes perfect. On to the next level!`,
        `Fantastic effort! No matter the time or mistakes, you’re doing great!`,
        `Keep up the amazing work! Your brain is getting stronger every level!`,
        `Another level mastered! You’re building skills step by step. Awesome!`
    ];

    const reallyWell = [
        `Perfect score! No mistakes and ${elapsedSeconds} seconds—this level didn’t stand a chance against you!`,
        `Wow, you’re a pro! You conquered this level with ${elapsedSeconds} seconds and no mistakes!`
    ];

    const creativeAndFun = [
        `You’re climbing to the top like a spelling wizard! ${elapsedSeconds} seconds and ${mismatchCount} mistakes this time.`,
        `That level didn’t know what hit it! ${elapsedSeconds} seconds and ${mismatchCount} mistakes—great stuff!`,
        `Alphabet champ! You’re making those letters look easy in ${elapsedSeconds} seconds.`,
        `You aced that level faster than a cheetah! ${elapsedSeconds} seconds and just ${mismatchCount} mistakes!`,
        `Your brainpower is unstoppable! ${elapsedSeconds} seconds and only ${mismatchCount} mistakes. Let’s keep the momentum!`
    ];

    let message = "";

    if (mismatchCount === 0) {
        message = reallyWell[Math.floor(Math.random() * reallyWell.length)];
    } else if (mismatchCount < 3) {
        message = lowMistakes[Math.floor(Math.random() * lowMistakes.length)];
    } else if (elapsedSeconds < 30) {
        message = fastCompletion[Math.floor(Math.random() * fastCompletion.length)];
    } else if (elapsedSeconds < 60) {
        message = generalPraise[Math.floor(Math.random() * generalPraise.length)];
    } else {
        message = motivationForImprovement[Math.floor(Math.random() * motivationForImprovement.length)];
    }

    // Display the message in the overlay
    const overlay = document.getElementById("end-level-overlay");
    const messageElement = document.getElementById("end-level-message");
    messageElement.textContent = message;
    overlay.style.visibility = "visible";

    // Hide the overlay after a few seconds
    setTimeout(() => {
        overlay.style.visibility = "hidden";
        advanceToNextLevel();
    }, 3500);
}

// Add this event listener to call advanceToNextLevel once the sound has finished playing
document.getElementById("level-up-sound").addEventListener("ended", advanceToNextLevel);

initializeGame();
updateScore();