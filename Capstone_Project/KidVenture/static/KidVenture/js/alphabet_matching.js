import { messages, MessageCategories } from '/static/KidVenture/js/messages.js';

const urlParams = new URLSearchParams(window.location.search);
const activityId = urlParams.get('activity') || null;

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
    if (timerStarted) return; // Prevent multiple timers
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

function saveGameProgress(level, timeTaken, mistakes, mismatchedLetters, activityId = null) {
    const data = {
        level: level,
        time_taken: timeTaken,
        mistakes: mistakes,
        mismatched_letters: mismatchedLetters
    };

    if (activityId) {
        data.activity_id = activityId; // Attach activity ID if available
    }

    console.log('Sending game progress data:', data);

    return fetch('/save_game_progress/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Server response:', data);
        return data;
    })
    .catch(error => {
        console.error('Error saving game progress:', error);
        throw error;
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    if (!cookieValue) {
        console.error(`CSRF token "${name}" not found.`);
    }
    return cookieValue;
}

function advanceToNextLevel() {
    if (matches === totalMatches) {
        if (activityId) {
            currentLevel++;
            saveGameProgress(currentLevel, elapsedSeconds, mismatchCount, mismatchedLetters, activityId)
                .then(() => fetch(`/check_activity_progress/${activityId}/`))
                .then(response => response.json())
                .then(data => {
                    if (data && data.completed) {
                        return fetch(`/complete_activity/${activityId}/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                        }).then(response => response.json());
                    } else {
                        matches = 0;
                        totalMatches = currentLevel + 1;
                        initializeGame();
                    }
                })
                .then(data => {
                    if (data && data.status === "success") {
                        Swal.fire({
                            title: "Congratulations!",
                            text: "You have successfully completed the activity!",
                            icon: "success",
                            confirmButtonText: "OK",
                            allowOutsideClick: false
                        }).then(() => {
                            window.location.href = "/";
                        });
                    }
                })
                .catch(error => console.error("Error checking activity progress:", error));
        } else {
            currentLevel++;
            saveGameProgress(currentLevel, elapsedSeconds, mismatchCount, mismatchedLetters)
                .then(() => {
                    matches = 0;
                    totalMatches = currentLevel + 1;

                    if (currentLevel > maxLevel) {
                        Swal.fire({
                            title: "Well Done!",
                            text: `Congratulations! You completed all levels in ${elapsedSeconds} seconds.`,
                            icon: "success",
                            confirmButtonText: "OK",
                            allowOutsideClick: false
                        }).then(() => {
                            window.location.href = "/";
                        });
                        return;
                    }
                    initializeGame();
                })
                .catch(error => console.error("Error saving game progress:", error));
        }
    }
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
                displayEndLevelMessages(elapsedSeconds, mismatchCount);

                const levelUpSound = document.getElementById("level-up-sound");
                levelUpSound.removeEventListener("ended", advanceToNextLevel);
                levelUpSound.addEventListener("ended", advanceToNextLevel);
            }
        } else {
            playSound("mismatch-sound");
            mismatchCount++;
            mismatchedLetters.push({ first: firstCard.dataset.card, second: secondCard.dataset.card });
            firstCard.classList.add("mismatched");
            secondCard.classList.add("mismatched");
            updateScore();

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

    const allCardValues = allCards.map(card => ({
        value: card.dataset.card,
        isMatched: card.classList.contains("matched")
    }));

    shuffle(allCardValues);

    gameBoard.innerHTML = "";

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

document.getElementById("level-up-sound").addEventListener("ended", advanceToNextLevel);

document.addEventListener("DOMContentLoaded", () => {
    const urlParams = new URLSearchParams(window.location.search);
    const activityId = urlParams.get('activity');

    const sessionModal = document.getElementById("session-modal");
    const modalText = document.getElementById("modal-text");
    const gameModeText = document.getElementById("game-mode-text");
    const gameTypeText = document.getElementById("game-type");
    const continueBtn = document.getElementById("continue-btn");
    const startOverBtn = document.getElementById("start-over-btn");

    const activityModal = document.getElementById("activity-modal");
    const modalContent = document.querySelector(".modal-content");
    const levelContainer = document.getElementById("level-container");
    const openModalBtn = document.querySelector(".open-level-select-btn");
    const closeModalBtn = document.getElementById("close-level-select-btn");

    function hideModal() {
        sessionModal.style.display = "none"; // Hide modal
    }

    function hideModalContent() {
        modalContent.style.display = "none"; // Hide modal content
    }

    function generateLevels(numLevels) {
        levelContainer.innerHTML = ''; // Clear any existing levels

        for (let i = 1; i <= numLevels; i++) {
            const button = document.createElement('button');
            button.textContent = `Level ${i}`;
            button.className = 'level-button';
            button.onclick = () => selectLevel(i); // Add an event listener for level selection
            levelContainer.appendChild(button);
        }
    }

    function selectLevel(level) {
        currentLevel = level;
        totalMatches = level + 1;
        hideModal();
        initializeGame();
        showGameElements();
    }

    function showActivityModal() {
        activityModal.classList.remove('hidden');
        activityModal.style.display = 'block'; // Explicitly set display to block
    }

    function hideActivityModal() {
        activityModal.classList.add('hidden');
        activityModal.style.display = 'none'; // Explicitly set display to none
    }

    if (activityId) {
        console.log("Game started for assigned activity. Checking last progress...");

        fetch(`/get_activity_progress/${activityId}/`)
            .then(response => response.json())
            .then(data => {
                console.log("Activity progress response:", data);

                console.log("data.last_level: " + data.last_level);
                if (data.last_level && data.last_level >= 1) {
                    currentLevel = data.last_level;
                    totalMatches = currentLevel + 1;
                    console.log(`Resuming activity from level ${currentLevel}`);
                    if (sessionModal) {
                        modalText.textContent = "Do you want to continue from your last activity or start from the first level?";
                        sessionModal.classList.remove("hidden");
                    }

                    continueBtn.addEventListener("click", () => {
                        currentLevel = data.last_level;
                        totalMatches = currentLevel + 1;
                        hideModal();
                        initializeGame();
                        showGameElements();
                    });

                    startOverBtn.addEventListener("click", () => {
                        hideModal();
                        initializeGame();
                        showGameElements();
                    });

                } else {
                    console.log("No previous activity progress found. Starting new game.");
                    initializeGame();
                    showGameElements();
                }

                if (gameModeText) gameModeText.textContent = "Complete the assigned activity!";
                if (gameTypeText) gameTypeText.textContent = "Mode: Activity";

            })
            .catch(error => {
                console.error("Error fetching activity progress:", error);
                alert("There was an issue loading your progress. Starting from Level 1.");
                initializeGame();
            });

    } else {
        if (gameTypeText) gameTypeText.textContent = "Mode: Free Play";

        // Ensure the session modal is hidden
        hideModal();
        hideActivityModal();

        openModalBtn.addEventListener("click", () => {
            console.log("openModalBtn clicked");
            showActivityModal();
        });

        closeModalBtn.addEventListener("click", () => {
            console.log("closeModalBtn clicked");
            hideActivityModal();
            hideModalContent();
            initializeGame();
            showGameElements();
        });

        generateLevels(maxLevel);
        initializeGame();
        showGameElements();
    }
});

// Get the modal
var modal = document.getElementById("modal");

// Get the button that opens the modal
var btn = document.getElementById("menuButton");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close-button")[0];

// When the user clicks the button, open the modal 
btn.onclick = function() {
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Add event listener for level select button
document.getElementById("levelSelectButton").onclick = function() {
    // Add your level select logic here
    alert("Level Select button clicked!");
}


function showGameElements() {
    document.getElementById("timer").classList.remove("hidden");
    document.querySelector(".score-container").classList.remove("hidden");
    document.getElementById("game-board").classList.remove("hidden");
}

updateScore();