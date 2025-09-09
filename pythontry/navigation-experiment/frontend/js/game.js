class NavigationGame {
    constructor(participantId) {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.participantId = participantId;
        
        // Game state
        this.state = {
            playerPos: [0, 0],
            playerAngle: 0,
            targets: [],
            phase: 'welcome',  // welcome, practice, training, dark_training, test, complete
            currentTrial: 1,
            moveKeyPressed: null,
            rotateKeyPressed: null,
            moveStartPos: null,
            rotateStartAngle: null
        };

        // Constants from original
        this.ARENA_DIAMETER = 3.3;
        this.ARENA_RADIUS = this.ARENA_DIAMETER / 2.0;
        this.BORDER_THRESHOLD = 0.1;
        this.TARGET_RADIUS = 0.1;
        this.MOVE_SPEED = 1.0;
        this.ROTATE_SPEED = 90.0;
        this.SCALE = 200;
        this.WIN_WIDTH = 1000;
        this.WIN_HEIGHT = 800;
        this.CENTER_SCREEN = [this.WIN_WIDTH / 2, this.WIN_HEIGHT / 2];

        // Colors
        this.COLORS = {
            BACKGROUND: [3, 3, 1],
            AVATAR: [255, 67, 101],
            BORDER: [255, 255, 243],
            TARGET: [0, 217, 192],
            CLOCK: [183, 173, 153]
        };

        // Predefined target positions
        this.PREDEFINED_TARGETS = {
            "training 1": [[-0.5, -1.0], [0.3, 0.8], [-1.0, 0.2]],
            "training 2": [[0.7, -0.8], [-0.4, 0.9], [0.3, -1.2]],
            "training 3": [[-0.8, -0.5], [0.5, 0.5], [0.2, -1.0]],
            "dark_training 1": [[-0.6, -0.9], [0.4, 0.7], [-0.9, 0.1]],
            "dark_training 2": [[0.2, -1.0], [-0.3, 0.8], [0.7, -0.6]],
            "test 1": [[0.5, 1.0], [-0.8, -0.2], [0.7, -0.7]],
            "test 2": [[-0.3, 0.7], [0.8, 0.2], [-0.9, -0.9]],
            "test 3": [[0.4, -0.4], [-0.6, 0.8], [0.2, 1.0]],
            "test 4": [[0.9, -0.3], [-0.4, -1.0], [1.0, 0.8]],
            "test 5": [[-0.2, -0.8], [0.5, 0.6], [-0.7, 1.2]]
        };

        // Initialize keyboard state
        this.keys = {};
        this.setupEventListeners();
    }

    setupEventListeners() {
        window.addEventListener('keydown', (e) => this.handleKeyDown(e));
        window.addEventListener('keyup', (e) => this.handleKeyUp(e));
    }

    handleKeyDown(e) {
        if (e.key === 'Enter') {
            this.handleEnterKey();
            return;
        }

        this.keys[e.key] = true;
        
        if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
            if (!this.state.moveKeyPressed) {
                this.state.moveKeyPressed = e.key;
                this.state.moveStartPos = [...this.state.playerPos];
            }
        }
        if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
            if (!this.state.rotateKeyPressed) {
                this.state.rotateKeyPressed = e.key;
                this.state.rotateStartAngle = this.state.playerAngle;
            }
        }
    }

    handleKeyUp(e) {
        this.keys[e.key] = false;
        
        if (e.key === this.state.moveKeyPressed) {
            this.state.moveKeyPressed = null;
            this.state.moveStartPos = null;
        }
        if (e.key === this.state.rotateKeyPressed) {
            this.state.rotateKeyPressed = null;
            this.state.rotateStartAngle = null;
        }
    }

    handleEnterKey() {
        switch (this.state.phase) {
            case 'welcome':
                this.showInstructions(1);
                break;
            case 'instructions':
                if (this.currentInstruction === 1) {
                    this.showInstructions(2);
                } else if (this.currentInstruction === 2) {
                    this.startPractice();
                } else if (this.currentInstruction === 3) {
                    this.startTraining();
                } else if (this.currentInstruction === 4) {
                    this.startDarkTraining();
                } else if (this.currentInstruction === 5) {
                    this.startTest();
                } else if (this.currentInstruction === 6) {
                    this.completeExperiment();
                }
                break;
            case 'practice':
                if (this.practiceScore >= 5) {
                    this.showInstructions(3);
                }
                break;
            case 'training':
            case 'dark_training':
            case 'test':
                this.endTrial();
                break;
        }
    }

    showInstructions(num) {
        this.state.phase = 'instructions';
        this.currentInstruction = num;
        
        // Load and display instruction image
        const img = new Image();
        img.onload = () => {
            this.ctx.drawImage(img, 0, 0, this.WIN_WIDTH, this.WIN_HEIGHT);
        };
        img.src = `images/instructions/${num}.png`;
    }

    startPractice() {
        this.state.phase = 'practice';
        this.practiceScore = 0;
        this.resetPlayer();
        this.generateRandomTarget();
    }

    startTraining() {
        this.state.phase = 'training';
        this.state.currentTrial = 1;
        this.resetPlayer();
        this.loadTrialTargets();
    }

    startDarkTraining() {
        this.state.phase = 'dark_training';
        this.state.currentTrial = 1;
        this.resetPlayer();
        this.loadTrialTargets();
    }

    startTest() {
        this.state.phase = 'test';
        this.state.currentTrial = 1;
        this.resetPlayer();
        this.loadTrialTargets();
    }

    completeExperiment() {
        this.state.phase = 'complete';
        // Send final data to server and redirect to completion URL
        this.saveData().then(() => {
            // Redirect to Prolific completion URL
            window.location.href = 'https://app.prolific.co/submissions/complete?cc=XXXXXX';
        });
    }

    resetPlayer() {
        this.state.playerPos = [0, 0];
        this.state.playerAngle = 0;
    }

    loadTrialTargets() {
        const trialKey = `${this.state.phase} ${this.state.currentTrial}`;
        this.state.targets = this.PREDEFINED_TARGETS[trialKey] || [];
    }

    generateRandomTarget() {
        const angle = Math.random() * 2 * Math.PI;
        const r = this.ARENA_RADIUS * Math.sqrt(Math.random());
        this.state.targets = [[r * Math.cos(angle), r * Math.sin(angle)]];
    }

    endTrial() {
        // Save trial data
        this.saveData();

        // Move to next trial or phase
        if (this.state.phase === 'training' && this.state.currentTrial >= 3) {
            this.showInstructions(4);
        } else if (this.state.phase === 'dark_training' && this.state.currentTrial >= 2) {
            this.showInstructions(5);
        } else if (this.state.phase === 'test' && this.state.currentTrial >= 5) {
            this.showInstructions(6);
        } else {
            this.state.currentTrial++;
            this.resetPlayer();
            this.loadTrialTargets();
        }
    }

    async saveData() {
        const data = {
            participant_id: this.participantId,
            phase: this.state.phase,
            trial: this.state.currentTrial,
            final_position: this.state.playerPos,
            final_angle: this.state.playerAngle,
            timestamp: new Date().toISOString()
        };

        try {
            const response = await fetch('/api/save_trial', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Error saving data:', error);
        }
    }

    update(dt) {
        if (this.state.phase === 'instructions') return;

        // Update movement
        if (this.keys['ArrowUp']) {
            const rad = this.state.playerAngle * Math.PI / 180;
            const dx = this.MOVE_SPEED * dt * Math.sin(rad);
            const dy = this.MOVE_SPEED * dt * Math.cos(rad);
            const newX = this.state.playerPos[0] + dx;
            const newY = this.state.playerPos[1] + dy;
            if (Math.hypot(newX, newY) <= this.ARENA_RADIUS) {
                this.state.playerPos[0] = newX;
                this.state.playerPos[1] = newY;
            }
        }
        if (this.keys['ArrowDown']) {
            const rad = this.state.playerAngle * Math.PI / 180;
            const dx = this.MOVE_SPEED * dt * Math.sin(rad);
            const dy = this.MOVE_SPEED * dt * Math.cos(rad);
            const newX = this.state.playerPos[0] - dx;
            const newY = this.state.playerPos[1] - dy;
            if (Math.hypot(newX, newY) <= this.ARENA_RADIUS) {
                this.state.playerPos[0] = newX;
                this.state.playerPos[1] = newY;
            }
        }

        // Update rotation
        if (this.keys['ArrowLeft']) {
            this.state.playerAngle -= this.ROTATE_SPEED * dt;
        }
        if (this.keys['ArrowRight']) {
            this.state.playerAngle += this.ROTATE_SPEED * dt;
        }
        this.state.playerAngle = this.state.playerAngle % 360;

        // Check target collisions
        if (this.state.phase === 'practice') {
            const target = this.state.targets[0];
            if (Math.hypot(this.state.playerPos[0] - target[0], this.state.playerPos[1] - target[1]) <= this.TARGET_RADIUS) {
                this.practiceScore++;
                this.generateRandomTarget();
            }
        }
    }

    draw() {
        if (this.state.phase === 'instructions') return;

        // Clear canvas
        this.ctx.fillStyle = `rgb(${this.COLORS.BACKGROUND.join(',')})`;
        this.ctx.fillRect(0, 0, this.WIN_WIDTH, this.WIN_HEIGHT);

        // Draw arena border
        this.ctx.strokeStyle = `rgb(${this.COLORS.BORDER.join(',')})`;
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.arc(
            this.CENTER_SCREEN[0],
            this.CENTER_SCREEN[1],
            this.ARENA_RADIUS * this.SCALE,
            0,
            2 * Math.PI
        );
        this.ctx.stroke();

        // Draw player
        this.drawPlayer();

        // Draw targets based on phase
        if (this.state.phase === 'practice' || this.state.phase === 'training' ||
            (this.state.phase === 'dark_training' && this.isNearBorder()) ||
            this.state.phase === 'feedback') {
            this.state.targets.forEach(target => {
                const screenPos = this.toScreenCoords(target);
                this.ctx.fillStyle = `rgb(${this.COLORS.TARGET.join(',')})`;
                this.ctx.beginPath();
                this.ctx.arc(
                    screenPos[0],
                    screenPos[1],
                    this.TARGET_RADIUS * this.SCALE,
                    0,
                    2 * Math.PI
                );
                this.ctx.fill();
            });
        }

        // Draw score in practice mode
        if (this.state.phase === 'practice') {
            this.ctx.fillStyle = `rgb(${this.COLORS.CLOCK.join(',')})`;
            this.ctx.font = '24px Arial';
            this.ctx.fillText(`Score: ${this.practiceScore}/5`, 10, 30);
        }
    }

    isNearBorder() {
        return Math.hypot(this.state.playerPos[0], this.state.playerPos[1]) >= 
               (this.ARENA_RADIUS - this.BORDER_THRESHOLD);
    }

    drawPlayer() {
        const screenPos = this.toScreenCoords(this.state.playerPos);
        const rad = this.state.playerAngle * Math.PI / 180;
        const tipLength = 30;
        const baseLength = 20;
        const halfWidth = 17;

        // Calculate triangle points
        const tip = {
            x: screenPos[0] + tipLength * Math.sin(rad),
            y: screenPos[1] - tipLength * Math.cos(rad)
        };
        const baseCenter = {
            x: screenPos[0] - baseLength * Math.sin(rad),
            y: screenPos[1] + baseLength * Math.cos(rad)
        };
        const left = {
            x: baseCenter.x + halfWidth * Math.sin(rad + Math.PI/2),
            y: baseCenter.y - halfWidth * Math.cos(rad + Math.PI/2)
        };
        const right = {
            x: baseCenter.x + halfWidth * Math.sin(rad - Math.PI/2),
            y: baseCenter.y - halfWidth * Math.cos(rad - Math.PI/2)
        };

        // Draw triangle
        this.ctx.fillStyle = `rgb(${this.COLORS.AVATAR.join(',')})`;
        this.ctx.beginPath();
        this.ctx.moveTo(tip.x, tip.y);
        this.ctx.lineTo(left.x, left.y);
        this.ctx.lineTo(right.x, right.y);
        this.ctx.closePath();
        this.ctx.fill();
    }

    toScreenCoords(pos) {
        return [
            this.CENTER_SCREEN[0] + pos[0] * this.SCALE,
            this.CENTER_SCREEN[1] - pos[1] * this.SCALE
        ];
    }

    start() {
        this.showInstructions(1);
        
        let lastTime = performance.now();
        const gameLoop = (currentTime) => {
            const dt = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            this.update(dt);
            this.draw();

            requestAnimationFrame(gameLoop);
        };

        requestAnimationFrame(gameLoop);
    }
} 