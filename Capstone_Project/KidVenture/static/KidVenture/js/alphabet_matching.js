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
        data.activity_id = activityId;  // Attach activity ID if available
    }

    console.log('Sending game progress data:', data);

    return fetch('/save_game_progress/', {  // <-- Return the fetch Promise
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())  // Parse JSON response
    .then(data => {
        console.log('Server response:', data);
        return data;  // Return the response data for further chaining
    })
    .catch(error => {
        console.error('Error saving game progress:', error);
        throw error;  // Rethrow to be caught in calling function
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
    return cookieValue;
}
function advanceToNextLevel() {
    if (matches === totalMatches) {  // Ensure user completed the level
        if (activityId) {
            // Wait for saveGameProgress to complete before checking progress
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
                        // If not complete, move to the next level
                        return saveGameProgress(currentLevel, elapsedSeconds, mismatchCount, mismatchedLetters, activityId)
                            .then(() => {
                                matches = 0;  
                                totalMatches = currentLevel + 1;
                                initializeGame();
                            });
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
                            window.location.href = "/"; // Redirect home after clicking OK
                        });
                    }
                })
                .catch(error => console.error("Error checking activity progress:", error));

        } else {
            // Free Play: Move to the next level normally
            currentLevel++;
            saveGameProgress(currentLevel, elapsedSeconds, mismatchCount, mismatchedLetters, activityId)
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
            
                // Ensure the next level only advances when the user got all matches
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

    // Replace placeholders with actual values
    message = message.replace('{time}', elapsedSeconds).replace('{mistakes}', mismatchCount);

    // Display the message in the overlay
    const overlay = document.getElementById("end-level-overlay");
    const messageElement = document.getElementById("end-level-message");
    messageElement.textContent = message;
    overlay.style.visibility = "visible";

    // Hide the overlay after a few seconds
    setTimeout(() => {
        overlay.style.visibility = "hidden";
    }, 3500);
}

// Add this event listener to call advanceToNextLevel once the sound has finished playing
document.getElementById("level-up-sound").addEventListener("ended", advanceToNextLevel);


document.addEventListener("DOMContentLoaded", () => {
    const urlParams = new URLSearchParams(window.location.search);
    const activityId = urlParams.get('activity'); // Check if it's an assigned activity

    const sessionModal = document.getElementById("session-modal");
    const gameModeText = document.getElementById("game-mode-text");
    const gameTypeText = document.getElementById("game-type");

    if (activityId) {
        console.log("Game started for assigned activity. Checking last progress...");

        // Fetch last saved progress for this activity
        fetch(`/get_activity_progress/${activityId}/`)
            .then(response => response.json())
            .then(data => {
                console.log("Activity progress response:", data);

                if (data.last_level && data.last_level > 1) {
                    currentLevel = data.last_level; // Restore last completed level
                    totalMatches = currentLevel + 1;
                    console.log(`Resuming activity from level ${currentLevel}`);
                }

                if (gameModeText) gameModeText.textContent = "Complete the assigned activity!";
                if (gameTypeText) gameTypeText.textContent = "Mode: Activity";

                initializeGame(); // Start game at last saved level
            })
            .catch(error => {
                console.error("Error fetching activity progress:", error);
                alert("There was an issue loading your progress. Starting from Level 1.");
                initializeGame();
            });

    } else {
        console.log("Standard game mode - Checking last session progress.");
        if (gameTypeText) gameTypeText.textContent = "Mode: Free Play";

        fetch('/get_last_session/')
            .then(response => response.json())
            .then(data => {
                console.log('Free play session response:', data);

                if (data.last_level && data.last_level > 1) {
                    console.log('Last level found:', data.last_level);
                    if (sessionModal) {
                        sessionModal.classList.remove("hidden"); 
                        sessionModal.style.display = "block";  
                    }

                    document.getElementById("continue-btn").addEventListener("click", () => {
                        currentLevel = data.last_level;
                        totalMatches = currentLevel + 1;
                        sessionModal.style.display = "none"; // Hide modal
                        initializeGame();
                        showGameElements();
                    });

                    document.getElementById("start-over-btn").addEventListener("click", () => {
                        sessionModal.style.display = "none"; // Hide modal
                        initializeGame();
                        showGameElements();
                    });

                } else {
                    console.log("No previous session found. Starting new game.");
                    initializeGame();
                    showGameElements();
                }
            })
            .catch(error => {
                console.error('Error fetching last session:', error);
                initializeGame();
                showGameElements();
            });
    }
});




function showSessionModal(lastLevel) {
    if (activityId) {
        return; // Skip modal for activity mode
    }

    const modal = document.getElementById("session-modal");
    if (!modal) return;  // Prevent errors if modal is missing

    modal.style.display = "block";

    document.getElementById("continue-btn").addEventListener("click", () => {
        currentLevel = lastLevel;
        totalMatches = currentLevel + 1;
        modal.style.display = "none";
        initializeGame();
        showGameElements();
    });

    document.getElementById("start-over-btn").addEventListener("click", () => {
        sessionModal.style.display = "none"; // Hide modal
    
        if (!activityId) {  // Only reset if NOT in activity mode
            console.log("Resetting free play progress...");
    
            // Reset all variables
            currentLevel = 1;
            totalMatches = 2;
            elapsedSeconds = 0;
            matches = 0;
            mismatchCount = 0;
            mismatchedLetters = [];
            timerStarted = false;
    
            // Clear backend progress in free play mode
            fetch('/reset_free_play_progress/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
            })
            .then(response => response.json())
            .then(data => {
                console.log("Free play progress reset:", data);
                initializeGame(); // Start fresh after reset
            })
            .catch(error => {
                console.error("Error resetting free play progress:", error);
                alert("There was an issue resetting progress. Please try again.");
            });
    
        } else {
            console.log("Start Over clicked in activity mode - Progress remains saved.");
            initializeGame(); // Just restart the game without resetting progress
        }
    
        showGameElements();
    });
    
}



function showGameElements() {
    document.getElementById("timer").classList.remove("hidden");
    document.querySelector(".score-container").classList.remove("hidden");
    document.getElementById("game-board").classList.remove("hidden");
}

updateScore();