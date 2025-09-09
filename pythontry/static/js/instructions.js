// Instructions content
const instructions = {
    welcome: `
        <h2>Welcome to the Exploration Experiment</h2>
        <p>In this experiment, you will navigate through a virtual environment to find targets. The experiment consists of three phases:</p>
        <ol>
            <li>Training Phase (3 trials)</li>
            <li>Dark Training Phase (2 trials)</li>
            <li>Test Phase (5 trials)</li>
        </ol>
        <p>Please read all instructions carefully before proceeding.</p>
    `,
    practice: `
        <h2>Practice Game</h2>
        <p>Before starting the main experiment, you will play a practice game to familiarize yourself with the controls:</p>
        <ul>
            <li>Use the arrow keys to move and rotate</li>
            <li>Up/Down arrows: Move forward/backward</li>
            <li>Left/Right arrows: Rotate left/right</li>
            <li>Try to collect 15 targets to proceed</li>
        </ul>
        <p>Press Enter to start the practice game.</p>
    `,
    training: `
        <h2>Training Phase</h2>
        <p>In the training phase:</p>
        <ul>
            <li>You will see all targets clearly</li>
            <li>Navigate to each target</li>
            <li>When you reach a target, it will be highlighted</li>
            <li>After finding all targets, press Enter to proceed to the annotation phase</li>
        </ul>
        <p>Press Enter to start the training phase.</p>
    `,
    darkTraining: `
        <h2>Dark Training Phase</h2>
        <p>In the dark training phase:</p>
        <ul>
            <li>Targets will be hidden</li>
            <li>You will only see the arena border when near it</li>
            <li>Use your memory and spatial awareness to find targets</li>
            <li>Press Enter to start the dark training phase</li>
        </ul>
    `,
    test: `
        <h2>Test Phase</h2>
        <p>In the test phase:</p>
        <ul>
            <li>Targets will be hidden</li>
            <li>You will not see the arena border</li>
            <li>Use your spatial memory to find targets</li>
            <li>Press Enter to start the test phase</li>
        </ul>
    `,
    final: `
        <h2>Thank You!</h2>
        <p>You have completed the experiment. Your responses have been recorded.</p>
        <p>You may now close this window.</p>
    `
};

// Current instruction phase
let currentPhase = 'welcome';

// Show instructions
function showInstructions(phase) {
    const content = document.getElementById('instruction-content');
    content.innerHTML = instructions[phase];
    currentPhase = phase;
}

// Handle Enter key for instructions
document.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        switch(currentPhase) {
            case 'welcome':
                showInstructions('practice');
                break;
            case 'practice':
                startPracticeGame();
                break;
            case 'training':
                showInstructions('darkTraining');
                break;
            case 'darkTraining':
                showInstructions('test');
                break;
            case 'test':
                showInstructions('final');
                break;
        }
    }
});

// Start session
async function startSession() {
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
        startGame(data.session_id);
    } catch (error) {
        console.error('Error starting session:', error);
        alert('Failed to start session. Please try again.');
    }
}

// Initialize instructions
showInstructions('welcome'); 