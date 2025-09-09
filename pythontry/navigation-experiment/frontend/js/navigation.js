class NavigationGame {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.playerPos = { x: 0, y: 0 };
        this.playerAngle = 0;
        this.targets = [];
        this.isTraining = true;
        this.moveStartPos = null;
        this.rotateStartAngle = null;
        this.lastTime = null;
        this.keysPressed = new Set();
        this.beepPlaying = false;

        // Set canvas size
        this.canvas.width = CONFIG.WIN_WIDTH;
        this.canvas.height = CONFIG.WIN_HEIGHT;

        // Bind event handlers
        this.handleKeyDown = this.handleKeyDown.bind(this);
        this.handleKeyUp = this.handleKeyUp.bind(this);
        this.gameLoop = this.gameLoop.bind(this);

        // Add event listeners
        window.addEventListener('keydown', this.handleKeyDown);
        window.addEventListener('keyup', this.handleKeyUp);
    }

    start() {
        this.lastTime = performance.now();
        requestAnimationFrame(this.gameLoop);
    }

    stop() {
        window.removeEventListener('keydown', this.handleKeyDown);
        window.removeEventListener('keyup', this.handleKeyUp);
    }

    handleKeyDown(event) {
        if (event.key === 'k') {
            this.showDebug = true;
        }
        this.keysPressed.add(event.key);
        
        if (event.key === 'Enter') {
            this.onEnterPress && this.onEnterPress();
        }
    }

    handleKeyUp(event) {
        if (event.key === 'k') {
            this.showDebug = false;
        }
        this.keysPressed.delete(event.key);
    }

    setTargets(targets) {
        this.targets = targets;
    }

    gameLoop(currentTime) {
        const deltaTime = (currentTime - this.lastTime) / 1000;
        this.lastTime = currentTime;

        this.update(deltaTime);
        this.draw();

        requestAnimationFrame(this.gameLoop);
    }

    update(deltaTime) {
        // Handle movement
        const moveSpeed = CONFIG.MOVE_SPEED * deltaTime;
        const rotateSpeed = CONFIG.ROTATE_SPEED * deltaTime;

        if (this.keysPressed.has('ArrowUp')) {
            const rad = toRadians(this.playerAngle);
            const dx = moveSpeed * Math.sin(rad);
            const dy = moveSpeed * Math.cos(rad);
            const newX = this.playerPos.x + dx;
            const newY = this.playerPos.y + dy;
            
            if (isWithinArena(newX, newY)) {
                this.playerPos.x = newX;
                this.playerPos.y = newY;
            }
        }
        if (this.keysPressed.has('ArrowDown')) {
            const rad = toRadians(this.playerAngle);
            const dx = moveSpeed * Math.sin(rad);
            const dy = moveSpeed * Math.cos(rad);
            const newX = this.playerPos.x - dx;
            const newY = this.playerPos.y - dy;
            
            if (isWithinArena(newX, newY)) {
                this.playerPos.x = newX;
                this.playerPos.y = newY;
            }
        }
        if (this.keysPressed.has('ArrowLeft')) {
            this.playerAngle = (this.playerAngle - rotateSpeed + 360) % 360;
        }
        if (this.keysPressed.has('ArrowRight')) {
            this.playerAngle = (this.playerAngle + rotateSpeed) % 360;
        }

        // Check if near border
        const distFromCenter = distance(this.playerPos.x, this.playerPos.y, 0, 0);
        if (distFromCenter >= (CONFIG.ARENA_RADIUS - CONFIG.BORDER_THRESHOLD)) {
            if (!this.beepPlaying) {
                playBeep();
                this.beepPlaying = true;
            }
        } else {
            this.beepPlaying = false;
        }

        // Update debug info
        updateDebugInfo(this.playerPos.x, this.playerPos.y, this.playerAngle);

        // Check target collection
        for (let i = 0; i < this.targets.length; i++) {
            const target = this.targets[i];
            if (distance(this.playerPos.x, this.playerPos.y, target.x, target.y) <= CONFIG.TARGET_RADIUS) {
                this.onTargetCollected && this.onTargetCollected(target);
                this.targets = [target]; // Keep only the collected target
                break;
            }
        }
    }

    draw() {
        // Clear canvas
        this.ctx.fillStyle = CONFIG.BACKGROUND_COLOR;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw arena border
        this.ctx.strokeStyle = CONFIG.BORDER_COLOR;
        this.ctx.lineWidth = 2;
        const center = toScreenCoords(0, 0);
        this.ctx.beginPath();
        this.ctx.arc(center.x, center.y, CONFIG.ARENA_RADIUS * CONFIG.SCALE, 0, Math.PI * 2);
        this.ctx.stroke();

        // Draw targets if in training mode or debug mode
        if (this.isTraining || this.showDebug) {
            this.targets.forEach(target => {
                const screenPos = toScreenCoords(target.x, target.y);
                this.ctx.fillStyle = CONFIG.TARGET_COLOR;
                this.ctx.beginPath();
                this.ctx.arc(screenPos.x, screenPos.y, CONFIG.TARGET_RADIUS * CONFIG.SCALE, 0, Math.PI * 2);
                this.ctx.fill();
            });
        }

        // Draw player
        const playerScreen = toScreenCoords(this.playerPos.x, this.playerPos.y);
        const tipLength = 30;
        const baseLength = 20;
        const halfWidth = 17;
        const rad = toRadians(this.playerAngle);

        this.ctx.fillStyle = CONFIG.AVATAR_COLOR;
        this.ctx.beginPath();
        
        // Calculate triangle points
        const tip = {
            x: playerScreen.x + tipLength * Math.sin(rad),
            y: playerScreen.y - tipLength * Math.cos(rad)
        };
        const baseCenter = {
            x: playerScreen.x - baseLength * Math.sin(rad),
            y: playerScreen.y + baseLength * Math.cos(rad)
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
        this.ctx.moveTo(tip.x, tip.y);
        this.ctx.lineTo(left.x, left.y);
        this.ctx.lineTo(right.x, right.y);
        this.ctx.closePath();
        this.ctx.fill();
    }
} 