"""
Configuration and constants for the hand detection application.
"""

# ==============================================================================
# MEDIAPIPE HAND DETECTION SETTINGS
# ==============================================================================

# Maximum number of hands to detect (1 or 2)
MAX_HANDS = 2

# Minimum detection confidence threshold (0.0 - 1.0)
# Higher values = more confident detections but fewer false positives
HAND_DETECTION_CONFIDENCE = 0.7

# Minimum tracking confidence threshold (0.0 - 1.0)
# Helps smooth detections across frames
HAND_TRACKING_CONFIDENCE = 0.5

# Model complexity: 0 (lite, fast) or 1 (full, accurate)
MODEL_COMPLEXITY = 0

# ==============================================================================
# HAND LANDMARKS AND TOPOLOGY
# ==============================================================================

# Total number of hand landmarks in MediaPipe
NUM_LANDMARKS = 21

# Hand landmark indices for easier reference
LANDMARKS = {
    # Wrist
    'WRIST': 0,
    # Thumb
    'THUMB_CMC': 1,
    'THUMB_MCP': 2,
    'THUMB_IP': 3,
    'THUMB_TIP': 4,
    # Index finger
    'INDEX_MCP': 5,
    'INDEX_PIP': 6,
    'INDEX_DIP': 7,
    'INDEX_TIP': 8,
    # Middle finger
    'MIDDLE_MCP': 9,
    'MIDDLE_PIP': 10,
    'MIDDLE_DIP': 11,
    'MIDDLE_TIP': 12,
    # Ring finger
    'RING_MCP': 13,
    'RING_PIP': 14,
    'RING_DIP': 15,
    'RING_TIP': 16,
    # Pinky
    'PINKY_MCP': 17,
    'PINKY_PIP': 18,
    'PINKY_DIP': 19,
    'PINKY_TIP': 20,
}

# Finger groupings (MCP, PIP, DIP, TIP indices)
FINGERS = {
    'THUMB': [1, 2, 3, 4],
    'INDEX': [5, 6, 7, 8],
    'MIDDLE': [9, 10, 11, 12],
    'RING': [13, 14, 15, 16],
    'PINKY': [17, 18, 19, 20],
}

# MediaPipe hand connections for drawing
HAND_CONNECTIONS = [
    # Thumb
    (0, 1), (1, 2), (2, 3), (3, 4),
    # Index
    (0, 5), (5, 6), (6, 7), (7, 8),
    # Middle
    (0, 9), (9, 10), (10, 11), (11, 12),
    # Ring
    (0, 13), (13, 14), (14, 15), (15, 16),
    # Pinky
    (0, 17), (17, 18), (18, 19), (19, 20),
    # Palms
    (5, 9), (9, 13), (13, 17),
]

# ==============================================================================
# FINGER EXTENSION DETECTION PARAMETERS
# ==============================================================================

# Angle-based finger extension detection thresholds (in degrees)
# A finger is considered "extended" if the angle is greater than this threshold

# Angle for detecting if a finger is extended (using DIP-PIP-TIP angles)
EXTENSION_ANGLE_THRESHOLD = 160

# Minimum distance ratio for finger tip to be considered raised
# (distance from PIP to TIP) / (distance from MCP to PIP)
FINGER_RAISE_RATIO = 0.5

# Use angle-based detection instead of coordinate comparison
USE_ANGLE_BASED_DETECTION = True

# ==============================================================================
# GESTURE CLASSIFICATION PARAMETERS
# ==============================================================================

# Fist detection: if fewer than this many fingers are extended, classify as fist
FIST_THRESHOLD = 2

# ==============================================================================
# TEMPORAL SMOOTHING
# ==============================================================================

# Number of frames to average for smoothing (moving average window size)
SMOOTHING_WINDOW_SIZE = 5

# If hand not detected for more than this many frames, remove output
HAND_TIMEOUT_FRAMES = 3

# ==============================================================================
# UI AND RENDERING
# ==============================================================================

# Display window title
WINDOW_TITLE = "Hand Finger Counter"

# Camera frame size (width, height)
# Smaller values = faster processing, larger = better quality
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Camera frame rate target (FPS)
CAMERA_FPS = 30

# Color definitions (BGR format for OpenCV)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_BLUE = (255, 0, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_CYAN = (255, 255, 0)
COLOR_MAGENTA = (255, 0, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (128, 128, 128)

# Landmark drawing properties
LANDMARK_RADIUS = 4
LANDMARK_COLOR = COLOR_CYAN
LANDMARK_THICKNESS = -1

# Connection drawing properties
CONNECTION_THICKNESS = 2
CONNECTION_COLOR = COLOR_BLUE

# Fingertip highlight
FINGERTIP_RADIUS = 6
FINGERTIP_COLOR = COLOR_YELLOW
FINGERTIP_THICKNESS = -1

# Bounding box properties
BOUNDING_BOX_THICKNESS = 2
BOUNDING_BOX_COLOR_LEFT = COLOR_GREEN
BOUNDING_BOX_COLOR_RIGHT = COLOR_RED

# Text properties
TEXT_FONT = 4  # cv2.FONT_HERSHEY_SIMPLEX
TEXT_FONT_SCALE = 1.2
TEXT_THICKNESS = 2
TEXT_COLOR = COLOR_WHITE
TEXT_BG_COLOR = COLOR_BLACK

# Status HUD properties
STATUS_HUD_Y_START = 30
STATUS_HUD_X_OFFSET = 15
STATUS_HUD_LINE_SPACING = 35

# Performance metrics HUD
PERF_HUD_Y_START = 30
PERF_HUD_X_OFFSET = FRAME_WIDTH - 200
PERF_HUD_LINE_SPACING = 30

# ==============================================================================
# DEBUG AND LOGGING
# ==============================================================================

# Enable debug visualizations
DEBUG_MODE = True

# Show landmarks and connections
DEBUG_SHOW_LANDMARKS = True

# Show bounding boxes
DEBUG_SHOW_BOUNDING_BOX = True

# Show finger angles (for debugging angle-based detection)
DEBUG_SHOW_ANGLES = False

# Log level: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
LOG_LEVEL = 'INFO'

# ==============================================================================
# PERFORMANCE OPTIMIZATION
# ==============================================================================

# Use multithreading for hand detection (experimental)
USE_THREADING = False

# Frame skip: process every Nth frame (higher = faster but less responsive)
# Set to 1 to process every frame
FRAME_SKIP = 1

# ==============================================================================
# CAMERA AND INPUT
# ==============================================================================

# Camera device index (0 = default webcam, 1 = second camera, etc.)
CAMERA_DEVICE = 0

# Use camera auto-focus (if supported)
USE_AUTO_FOCUS = True

# Flip the frame horizontally (mirror effect)
FLIP_FRAME_HORIZONTALLY = True
