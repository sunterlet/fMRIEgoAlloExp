// Game configuration
const ARENA_DIAMETER = 3.3;
const ARENA_RADIUS = ARENA_DIAMETER / 2.0;
const BORDER_THRESHOLD = 0.1;
const TARGET_RADIUS = 0.1;
const MOVE_SPEED = 1.0;
const ROTATE_SPEED = 90.0;
const SCALE = 200;
const WIN_WIDTH = 1000;
const WIN_HEIGHT = 800;
const CENTER_SCREEN = [WIN_WIDTH / 2, WIN_HEIGHT / 2];

// Colors
const BACKGROUND_COLOR = '#030301';
const AVATAR_COLOR = '#ff4365';
const BORDER_COLOR = '#fffff3';
const TARGET_COLOR = '#00d9c0';
const CLOCK_COLOR = '#b7ad99';
const WHITE = '#ffffff';

// Game state
let gameState = {
    sessionId: null,
    playerPos: [0, 0],
    playerAngle: 0,
    currentPhase: 'start',
    currentTrial: 1,
    trainingTrial: 1,
    darkTrainingTrial: 1,
    testTrial: 1,
    targets: [],
    startTime: null,
    moveKeyPressed: null,
    moveStartPos: null,
    rotateKeyPressed: null,
    rotateStartAngle: null,
    targetWasInside: false,
    encounteredGoal: null,
    lastUpdate: null
};

// Canvas setup
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Event listeners
document.addEventListener('keydown', handleKeyDown);
document.addEventListener('keyup', handleKeyUp);

function handleKeyDown(event) {
    if (gameState.currentPhase !== 'exploration') return;
    
    switch(event.key) {
        case 'ArrowUp':
            if (!gameState.moveKeyPressed) {
                gameState.moveKeyPressed = 'up';
                gameState.moveStartPos = [...gameState.playerPos];
            }
            break;
        case 'ArrowDown':
            if (!gameState.moveKeyPressed) {
                gameState.moveKeyPressed = 'down';
                gameState.moveStartPos = [...gameState.playerPos];
            }
            break;
        case 'ArrowLeft':
            if (!gameState.rotateKeyPressed) {
                gameState.rotateKeyPressed = 'left';
                gameState.rotateStartAngle = gameState.playerAngle;
            }
            break;
        case 'ArrowRight':
            if (!gameState.rotateKeyPressed) {
                gameState.rotateKeyPressed = 'right';
                gameState.rotateStartAngle = gameState.playerAngle;
            }
            break;
        case 'Enter':
            if (gameState.currentPhase === 'exploration') {
                transitionToAnnotation();
            } else if (gameState.currentPhase === 'annotation') {
                transitionToFeedback();
            } else if (gameState.currentPhase === 'feedback') {
                startNextTrial();
            }
            break;
    }
}

function handleKeyUp(event) {
    switch(event.key) {
        case 'ArrowUp':
        case 'ArrowDown':
            gameState.moveKeyPressed = null;
            gameState.moveStartPos = null;
            break;
        case 'ArrowLeft':
        case 'ArrowRight':
            gameState.rotateKeyPressed = null;
            gameState.rotateStartAngle = null;
            break;
    }
}

// Game loop
function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

function update() {
    if (gameState.currentPhase !== 'exploration') return;
    
    const now = Date.now();
    const dt = (now - gameState.lastUpdate) / 1000;
    gameState.lastUpdate = now;
    
    // Update player position
    if (gameState.moveKeyPressed) {
        const rad = gameState.playerAngle * Math.PI / 180;
        const dx = MOVE_SPEED * dt * Math.sin(rad);
        const dy = MOVE_SPEED * dt * Math.cos(rad);
        
        if (gameState.moveKeyPressed === 'up') {
            const newX = gameState.playerPos[0] + dx;
            const newY = gameState.playerPos[1] + dy;
            if (Math.hypot(newX, newY) <= ARENA_RADIUS) {
                gameState.playerPos[0] = newX;
                gameState.playerPos[1] = newY;
            }
        } else if (gameState.moveKeyPressed === 'down') {
            const newX = gameState.playerPos[0] - dx;
            const newY = gameState.playerPos[1] - dy;
            if (Math.hypot(newX, newY) <= ARENA_RADIUS) {
                gameState.playerPos[0] = newX;
                gameState.playerPos[1] = newY;
            }
        }
    }
    
    // Update player rotation
    if (gameState.rotateKeyPressed) {
        if (gameState.rotateKeyPressed === 'left') {
            gameState.playerAngle -= ROTATE_SPEED * dt;
        } else if (gameState.rotateKeyPressed === 'right') {
            gameState.playerAngle += ROTATE_SPEED * dt;
        }
        gameState.playerAngle = gameState.playerAngle % 360;
    }
    
    // Check for target collision
    checkTargetCollision();
    
    // Send update to server
    updatePosition();
}

async function updatePosition() {
    try {
        const response = await fetch('/update_position', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sessionId: gameState.sessionId,
                trial_info: getCurrentTrialInfo(),
                phase: gameState.currentPhase,
                time: (Date.now() - gameState.startTime) / 1000,
                x: gameState.playerPos[0],
                y: gameState.playerPos[1]
            })
        });
        
        if (!response.ok) {
            console.error('Failed to update position');
        }
    } catch (error) {
        console.error('Error updating position:', error);
    }
}

function draw() {
    // Clear canvas
    ctx.fillStyle = BACKGROUND_COLOR;
    ctx.fillRect(0, 0, WIN_WIDTH, WIN_HEIGHT);
    
    // Draw arena border
    ctx.strokeStyle = BORDER_COLOR;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(CENTER_SCREEN[0], CENTER_SCREEN[1], ARENA_RADIUS * SCALE, 0, 2 * Math.PI);
    ctx.stroke();
    
    // Draw targets
    if (gameState.currentPhase === 'exploration' || gameState.currentPhase === 'feedback') {
        ctx.fillStyle = TARGET_COLOR;
        gameState.targets.forEach(target => {
            const screenPos = toScreenCoords(target);
            ctx.beginPath();
            ctx.arc(screenPos[0], screenPos[1], TARGET_RADIUS * SCALE, 0, 2 * Math.PI);
            ctx.fill();
        });
    }
    
    // Draw player
    drawPlayer();
    
    // Draw trial counter
    updateTrialCounter();
}

function drawPlayer() {
    const screenPos = toScreenCoords(gameState.playerPos);
    const rad = gameState.playerAngle * Math.PI / 180;
    
    // Draw player triangle
    ctx.fillStyle = gameState.currentPhase === 'annotation' ? CLOCK_COLOR : AVATAR_COLOR;
    ctx.beginPath();
    ctx.moveTo(
        screenPos[0] + 30 * Math.sin(rad),
        screenPos[1] - 30 * Math.cos(rad)
    );
    ctx.lineTo(
        screenPos[0] - 20 * Math.sin(rad) + 17 * Math.cos(rad),
        screenPos[1] - 20 * Math.cos(rad) - 17 * Math.sin(rad)
    );
    ctx.lineTo(
        screenPos[0] - 20 * Math.sin(rad) - 17 * Math.cos(rad),
        screenPos[1] - 20 * Math.cos(rad) + 17 * Math.sin(rad)
    );
    ctx.closePath();
    ctx.fill();
}

function toScreenCoords(pos) {
    return [
        CENTER_SCREEN[0] + pos[0] * SCALE,
        CENTER_SCREEN[1] - pos[1] * SCALE
    ];
}

function checkTargetCollision() {
    let isInsideTarget = false;
    let encountered = null;
    
    gameState.targets.forEach(target => {
        const dist = Math.hypot(
            gameState.playerPos[0] - target[0],
            gameState.playerPos[1] - target[1]
        );
        if (dist <= TARGET_RADIUS) {
            isInsideTarget = true;
            encountered = target;
        }
    });
    
    if (!gameState.targetWasInside && isInsideTarget) {
        // Play target sound
        const audio = new Audio('/static/sounds/target.wav');
        audio.play();
        
        if (!gameState.encounteredGoal) {
            gameState.encounteredGoal = encountered;
        }
        gameState.targets = [encountered];
    }
    
    gameState.targetWasInside = isInsideTarget;
}

function updateTrialCounter() {
    const counter = document.getElementById('trial-counter');
    let totalTrials;
    let currentTrial;
    
    if (gameState.currentTrial <= 3) {
        totalTrials = 3;
        currentTrial = gameState.trainingTrial;
    } else if (gameState.currentTrial <= 5) {
        totalTrials = 2;
        currentTrial = gameState.darkTrainingTrial;
    } else {
        totalTrials = 5;
        currentTrial = gameState.testTrial;
    }
    
    counter.textContent = `${currentTrial}/${totalTrials}`;
}

function getCurrentTrialInfo() {
    if (gameState.currentTrial <= 3) {
        return `training ${gameState.trainingTrial}`;
    } else if (gameState.currentTrial <= 5) {
        return `dark_training ${gameState.darkTrainingTrial}`;
    } else {
        return `test ${gameState.testTrial}`;
    }
}

// Game state transitions
function transitionToAnnotation() {
    gameState.currentPhase = 'annotation';
    gameState.annotationStartTime = Date.now();
}

async function transitionToFeedback() {
    gameState.currentPhase = 'feedback';
    gameState.annotationTime = (Date.now() - gameState.annotationStartTime) / 1000;
    
    // Calculate error distance
    const errorDistance = gameState.encounteredGoal ? 
        Math.hypot(
            gameState.encounteredGoal[0] - gameState.playerPos[0],
            gameState.encounteredGoal[1] - gameState.playerPos[1]
        ) : null;
    
    try {
        const response = await fetch('/complete_trial', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sessionId: gameState.sessionId,
                discrete_log: {
                    trial_type: gameState.currentTrial <= 3 ? 'training' : 'test',
                    exploration_time: (gameState.annotationStartTime - gameState.startTime) / 1000,
                    annotation_time: gameState.annotationTime,
                    encountered_goal: gameState.encounteredGoal,
                    annotation: [...gameState.playerPos],
                    error_distance: errorDistance
                }
            })
        });
        
        if (!response.ok) {
            console.error('Failed to complete trial');
            return;
        }
        
        const data = await response.json();
        if (data.status === 'success') {
            gameState.currentTrial++;
            if (gameState.currentTrial <= 3) {
                gameState.trainingTrial++;
            } else if (gameState.currentTrial <= 5) {
                gameState.darkTrainingTrial++;
            } else {
                gameState.testTrial++;
            }
            gameState.targets = data.targets;
        }
    } catch (error) {
        console.error('Error completing trial:', error);
    }
}

async function startNextTrial() {
    // Reset trial state
    gameState.currentPhase = 'exploration';
    gameState.playerPos = [0, 0];
    gameState.playerAngle = 0;
    gameState.startTime = Date.now();
    gameState.lastUpdate = gameState.startTime;
    gameState.targetWasInside = false;
    gameState.encounteredGoal = null;
}

// Start game
async function startGame() {
    const initials = document.getElementById('initials').value.trim();
    if (!initials) {
        alert('Please enter your initials');
        return;
    }
    
    try {
        const response = await fetch('/start_session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ initials })
        });
        
        if (!response.ok) {
            throw new Error('Failed to start session');
        }
        
        const data = await response.json();
        gameState.sessionId = data.session_id;
        gameState.targets = data.targets;
        gameState.startTime = Date.now();
        gameState.lastUpdate = gameState.startTime;
        gameState.currentPhase = 'exploration';
        
        // Hide start screen
        document.getElementById('start-screen').classList.remove('visible');
        
        // Start game loop
        gameLoop();
    } catch (error) {
        console.error('Error starting session:', error);
        alert('Failed to start session. Please try again.');
    }
} 