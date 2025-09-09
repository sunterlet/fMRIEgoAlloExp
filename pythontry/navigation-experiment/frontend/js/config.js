const CONFIG = {
    // Arena parameters (in meters)
    ARENA_DIAMETER: 3.3,
    ARENA_RADIUS: 3.3 / 2.0,
    BORDER_THRESHOLD: 0.1,

    // Target parameters
    TARGET_RADIUS: 0.1,
    DEFAULT_TARGET_COUNT: 3,

    // Movement settings
    MOVE_SPEED: 1.0,  // meters per second
    ROTATE_SPEED: 90.0,  // degrees per second

    // Scale factor: pixels per meter
    SCALE: 200,

    // Window size
    WIN_WIDTH: 1000,
    WIN_HEIGHT: 800,

    // Colors (matching Python implementation)
    BACKGROUND_COLOR: '#030301',
    AVATAR_COLOR: '#ff4365',
    BORDER_COLOR: '#fffff3',
    TARGET_COLOR: '#00d9c0',
    CLOCK_COLOR: '#b7ad99',

    // Backend URL
    BACKEND_URL: 'http://localhost:5000',

    // Experiment parameters
    TRAINING_SESSIONS: 3,
    DARK_TRAINING_TRIALS: 2,
    TEST_TRIALS: 5
}; 