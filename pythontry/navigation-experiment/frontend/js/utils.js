// Convert arena coordinates (in meters) to screen coordinates (in pixels)
function toScreenCoords(x, y) {
    const screenX = CONFIG.WIN_WIDTH / 2 + x * CONFIG.SCALE;
    const screenY = CONFIG.WIN_HEIGHT / 2 - y * CONFIG.SCALE;
    return { x: screenX, y: screenY };
}

// Convert screen coordinates (in pixels) to arena coordinates (in meters)
function toArenaCoords(screenX, screenY) {
    const x = (screenX - CONFIG.WIN_WIDTH / 2) / CONFIG.SCALE;
    const y = (CONFIG.WIN_HEIGHT / 2 - screenY) / CONFIG.SCALE;
    return { x, y };
}

// Calculate Euclidean distance between two points
function distance(x1, y1, x2, y2) {
    return Math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
}

// Convert degrees to radians
function toRadians(degrees) {
    return degrees * Math.PI / 180;
}

// Convert radians to degrees
function toDegrees(radians) {
    return radians * 180 / Math.PI;
}

// Check if a point is within the arena bounds
function isWithinArena(x, y) {
    return distance(x, y, 0, 0) <= CONFIG.ARENA_RADIUS;
}

// Play a beep sound
function playBeep() {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.type = 'sine';
    oscillator.frequency.value = 440;
    gainNode.gain.value = 0.1;

    oscillator.start();
    setTimeout(() => {
        oscillator.stop();
    }, 200);
}

// Update debug information display
function updateDebugInfo(x, y, angle) {
    const positionElement = document.getElementById('position');
    const angleElement = document.getElementById('angle');
    
    if (positionElement && angleElement) {
        positionElement.textContent = `(${x.toFixed(2)}, ${y.toFixed(2)})`;
        angleElement.textContent = `${angle.toFixed(1)}°`;
    }
} 