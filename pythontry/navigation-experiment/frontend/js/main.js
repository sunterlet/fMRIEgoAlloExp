document.addEventListener('DOMContentLoaded', () => {
    const prolificContainer = document.getElementById('prolific-id-container');
    const instructionContainer = document.getElementById('instruction-container');
    const gameCanvas = document.getElementById('game-canvas');
    const startButton = document.getElementById('start-button');
    const instructionImage = document.getElementById('instruction-image');
    
    let game = null;
    let currentPhase = 'initials';  // phases: initials, practice_instructions, practice, training_instructions, training, dark_training_instructions, dark_training, test_instructions, test
    let trainingSession = 1;
    let darkTrainingTrial = 1;
    let testTrial = 1;
    let playerInitials = '';
    let practiceTargetsCollected = 0;

    // Predefined target positions (matching Python implementation)
    const PREDEFINED_TARGETS = {
        'training 1': [[-0.5, -1.0], [0.3, 0.8], [-1.0, 0.2]],
        'training 2': [[0.7, -0.8], [-0.4, 0.9], [0.3, -1.2]],
        'training 3': [[-0.8, -0.5], [0.5, 0.5], [0.2, -1.0]],
        'dark_training 1': [[-0.6, -0.9], [0.4, 0.7], [-0.9, 0.1]],
        'dark_training 2': [[0.2, -1.0], [-0.3, 0.8], [0.7, -0.6]],
        'test 1': [[0.5, 1.0], [-0.8, -0.2], [0.7, -0.7]],
        'test 2': [[-0.3, 0.7], [0.8, 0.2], [-0.9, -0.9]],
        'test 3': [[0.4, -0.4], [-0.6, 0.8], [0.2, 1.0]],
        'test 4': [[0.9, -0.3], [-0.4, -1.0], [1.0, 0.8]],
        'test 5': [[-0.2, -0.8], [0.5, 0.6], [-0.7, 1.2]]
    };

    function showElement(element, show = true) {
        element.style.display = show ? 'block' : 'none';
    }

    function startExperiment() {
        playerInitials = document.getElementById('prolific-id').value.trim();
        if (!playerInitials) {
            alert('Please enter your initials');
            return;
        }

        // Show practice game instructions (image 2)
        currentPhase = 'practice_instructions';
        showElement(prolificContainer, false);
        showElement(instructionContainer, true);
        instructionImage.src = 'images/instructions/2.png';
    }

    function startGame() {
        showElement(instructionContainer, false);
        showElement(gameCanvas, true);
        
        game = new NavigationGame(gameCanvas);
        game.onTargetCollected = handleTargetCollected;
        game.onEnterPress = handleEnterPress;

        // Set up initial game state based on current phase
        if (currentPhase === 'practice') {
            game.isTraining = true;
            const practiceTargets = PREDEFINED_TARGETS['training 1'].map(([x, y]) => ({x, y}));
            game.setTargets(practiceTargets);
        } else if (currentPhase === 'training') {
            game.isTraining = true;
            const targets = PREDEFINED_TARGETS[`training ${trainingSession}`].map(([x, y]) => ({x, y}));
            game.setTargets(targets);
        } else if (currentPhase === 'dark_training') {
            game.isTraining = false;
            const targets = PREDEFINED_TARGETS[`dark_training ${darkTrainingTrial}`].map(([x, y]) => ({x, y}));
            game.setTargets(targets);
        } else if (currentPhase === 'test') {
            game.isTraining = false;
            const targets = PREDEFINED_TARGETS[`test ${testTrial}`].map(([x, y]) => ({x, y}));
            game.setTargets(targets);
        }

        game.start();
    }

    function handleTargetCollected(target) {
        if (currentPhase === 'practice') {
            practiceTargetsCollected++;
            if (practiceTargetsCollected >= 5) {
                // Practice complete, show training instructions
                game.stop();
                showElement(gameCanvas, false);
                currentPhase = 'training_instructions';
                showElement(instructionContainer, true);
                instructionImage.src = 'images/instructions/3.png';
                return;
            }
            // Reset targets for practice
            const practiceTargets = PREDEFINED_TARGETS['training 1'].map(([x, y]) => ({x, y}));
            game.setTargets(practiceTargets);
        }

        // Send data to backend
        const data = {
            player_initials: playerInitials,
            phase: currentPhase,
            trial: currentPhase === 'training' ? trainingSession :
                   currentPhase === 'dark_training' ? darkTrainingTrial :
                   currentPhase === 'test' ? testTrial : 0,
            target_position: [target.x, target.y],
            player_position: [game.playerPos.x, game.playerPos.y],
            player_angle: game.playerAngle,
            timestamp: Date.now()
        };

        fetch(`${CONFIG.BACKEND_URL}/data`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        }).catch(console.error);
    }

    function handleEnterPress() {
        if (currentPhase.endsWith('_instructions')) {
            if (currentPhase === 'practice_instructions') {
                currentPhase = 'practice';
                startGame();
            } else if (currentPhase === 'training_instructions') {
                currentPhase = 'training';
                startGame();
            } else if (currentPhase === 'dark_training_instructions') {
                currentPhase = 'dark_training';
                startGame();
            } else if (currentPhase === 'test_instructions') {
                currentPhase = 'test';
                startGame();
            }
        } else if (game && game.targets.length === 1) {
            // A target was collected, move to next phase
            game.stop();
            showElement(gameCanvas, false);
            
            if (currentPhase === 'training') {
                if (trainingSession < CONFIG.TRAINING_SESSIONS) {
                    trainingSession++;
                    startGame();
                } else {
                    // Show dark training instructions
                    currentPhase = 'dark_training_instructions';
                    showElement(instructionContainer, true);
                    instructionImage.src = 'images/instructions/4.png';
                }
            } else if (currentPhase === 'dark_training') {
                if (darkTrainingTrial < CONFIG.DARK_TRAINING_TRIALS) {
                    darkTrainingTrial++;
                    startGame();
                } else {
                    // Show test instructions
                    currentPhase = 'test_instructions';
                    showElement(instructionContainer, true);
                    instructionImage.src = 'images/instructions/5.png';
                }
            } else if (currentPhase === 'test') {
                if (testTrial < CONFIG.TEST_TRIALS) {
                    testTrial++;
                    startGame();
                } else {
                    // Show completion message
                    showElement(instructionContainer, true);
                    instructionImage.src = 'images/instructions/6.png';
                }
            }
        }
    }

    // Update UI text to match the original implementation
    document.querySelector('label[for="prolific-id"]').textContent = 'Enter player initials:';
    document.getElementById('prolific-id').placeholder = 'Enter initials';

    // Event listeners
    startButton.addEventListener('click', startExperiment);
    window.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            handleEnterPress();
        }
    });
}); 