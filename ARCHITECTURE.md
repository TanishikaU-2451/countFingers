# Hand Detection Architecture & Design

## High-Level Overview

The application follows a **modular, pipeline-based architecture** where each component has a single responsibility:

```
┌─────────────┐
│   Input     │  Camera Frame (1280x720)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Frame Preprocessing                │  - Mirror flip
│  (FrameProcessor)                   │  - Resize
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Hand Detection                     │  - MediaPipe Hands
│  (HandDetector)                     │  - 21 landmarks per hand
│                                     │  - Confidence scores
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Landmark Extraction                │  - Normalize coordinates
│  (Landmark, Hand, HandsData)        │  - Store per-hand data
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Gesture Recognition                │  - Finger counting
│  (FingerCounter)                    │  - Angle-based detection
│                                     │  - Per-finger analysis
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Gesture Classification             │  - Fist vs Open
│  (GestureClassifier)                │  - Confidence scoring
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Temporal Smoothing                 │  - Moving average
│  (GestureStateTracker,              │  - Hand timeout logic
│   FingerCountSmoother)              │  - State persistence
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Rendering Pipeline                 │  - Landmarks visualization
│  (FrameRenderer)                    │  - Text overlays
│                                     │  - Performance metrics
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Display Output                     │  OpenCV window
│  (RenderingPipeline)                │
└─────────────────────────────────────┘
```

---

## Module Details

### 1. **Config Module** (`app/config/settings.py`)

**Responsibility**: Centralized configuration and constants

**Key Features**:
- Detection parameters (confidence, model complexity)
- UI/rendering settings (colors, sizes, positions)
- Feature flags (debug mode, threading)
- Gesture thresholds (FIST_THRESHOLD, EXTENSION_ANGLE_THRESHOLD)
- Smoothing parameters (SMOOTHING_WINDOW_SIZE)

**Design Pattern**: Configuration Object
```python
# Single source of truth for all settings
from app.config import settings
print(settings.MAX_HANDS)  # Access anywhere
```

---

### 2. **Detector Module** (`app/detector/`)

#### **detector/landmarks.py**
**Data Classes**:
- `Landmark`: Single point (x, y, z, visibility)
- `Hand`: Collection of 21 landmarks + handedness
- `HandsData`: Container for detected hands in a frame

**Key Responsibility**: Model the data structure, not the detection logic

```python
# Example usage
hand = Hand(
    handedness='Left',
    confidence=0.95,
    landmarks=[...],  # List of 21 Landmark objects
    frame_width=1280,
    frame_height=720
)
pixel_coords = hand.get_landmarks_pixel()  # Convert to screen coords
```

#### **detector/hand_detector.py**
**Classes**:
- `HandDetector`: Wraps MediaPipe, handles detection
- `FrameProcessor`: Preprocessing (flip, resize, frame skip)

**Key Responsibility**: Hand detection and landmark extraction

**Design Pattern**: Adapter Pattern
- Adapts MediaPipe's output to our `Hand` data structure
- Isolates MediaPipe dependency

```python
# Example usage
detector = HandDetector()
hands_data = detector.detect(frame)
for hand in hands_data.get_all_hands():
    print(f"Detected {hand.handedness} with {len(hand.landmarks)} landmarks")
```

**Mirror Correction Logic**:
```python
# MediaPipe gives "Right" for right hand in mirror view
# We correct it based on FLIP_FRAME_HORIZONTALLY setting
if FLIP_FRAME_HORIZONTALLY:
    handedness = "Left" if label == "Right" else "Right"
```

---

### 3. **Gesture Module** (`app/gesture/`)

#### **gesture/finger_counter.py**
**Core Algorithm**: Angle-based finger extension detection

**Key Concept**:
```
For each finger, calculate angle at PIP joint:
  MCP─────PIP─────DIP
        angle > 160° ? = Extended

Example:
  - Straight finger: angle ≈ 170° ✓ Extended
  - Bent finger: angle ≈ 90° ✗ Not extended
```

**Thumb Special Handling**:
```python
# Thumb extends horizontally, not vertically
# Check:
# 1. IP joint angle > 160°
# 2. Thumb tip distance from index MCP > 30 pixels
```

**Output Format**:
```python
{
    'thumb': True,
    'index': False,
    'middle': True,
    'ring': False,
    'pinky': False,
    'total': 2,  # Sum of extended fingers
    'angles': {...}  # For debugging
}
```

#### **gesture/gesture_classifier.py**
**Responsibility**: Classify gestures into categories

**Logic**:
```python
if finger_count <= FIST_THRESHOLD:  # <= 1
    gesture = 'fist'
elif finger_count >= 4:
    gesture = 'open'
else:
    gesture = 'partial'
```

**Output Format**:
```python
{
    'gesture': 'open',  # or 'fist', 'partial'
    'finger_count': 3,
    'confidence': 0.9,  # 0-1 based on finger consistency
    'details': {...}  # Raw finger analysis
}
```

#### **gesture/smoothing.py**
**Responsibility**: Temporal stabilization

**Classes**:
1. `MovingAverageSmoother`: Smooth any numeric value
2. `FingerCountSmoother`: Output integer finger counts
3. `GestureStateTracker`: Track state, remove stale hands
4. `GestureBuffer`: Buffer multiple frames for consensus

**Key Concept** - Moving Average Window:
```
Frames:  [3, 3, 4, 3, 3]     SMOOTHING_WINDOW_SIZE=5
Average: (3+3+4+3+3)/5 = 3.4 → rounds to 3
```

**Hand Timeout Logic**:
```
Detection:  YES → YES → NO → NO → NO → REMOVED
Missing:     0 →   0 →  1 →  2 →  3 → (> threshold)
```

---

### 4. **UI Module** (`app/ui/`)

#### **ui/overlays.py**
**Rendering Classes**:
1. `LandmarkRenderer`: Draw hand skeleton
2. `BoundingBoxRenderer`: Draw bounding boxes
3. `TextRenderer`: Draw text with backgrounds
4. `DebugRenderer`: Debug visualizations

**Example Usage**:
```python
# Draw landmarks
LandmarkRenderer.draw_landmarks(frame, hand)

# Draw text with background
TextRenderer.draw_text_with_background(
    frame,
    "Left Hand: 3",
    position=(50, 50),
    text_color=(255, 255, 255),
    bg_color=(0, 0, 0)
)
```

#### **ui/renderer.py**
**Classes**:
1. `FrameRenderer`: Main rendering orchestration
2. `RenderingPipeline`: Window display and input handling

**Rendering Order** (back to front):
1. Hand landmarks & connections (if debug mode)
2. Bounding boxes (if debug mode)
3. Gesture labels
4. Performance HUD (bottom right)
5. Status HUD (left side)

**Pipeline**:
```python
renderer = FrameRenderer()

# Each frame:
renderer.render_frame(
    frame,
    hands_data,      # Detected hands
    gesture_results, # Finger counts
    debug_mode=True  # Show landmarks?
)
```

---

### 5. **Utils Module** (`app/utils/`)

#### **utils/geometry.py**
**Functions**:
- `distance()`: 2D Euclidean distance
- `distance_3d()`: 3D Euclidean distance
- `angle_between_points()`: Angle at vertex (key function!)
- `get_bounding_box()`: Calculate bounding box
- `normalize_landmarks()`: Convert pixels to 0-1 range

**Key Function** - Angle Calculation:
```python
def angle_between_points(A, B, C):
    """
    Calculate angle at B formed by A-B-C
    
    Vector BA = A - B
    Vector BC = C - B
    
    cos(θ) = (BA · BC) / (|BA| × |BC|)
    θ = arccos(...)
    """
```

#### **utils/fps.py**
**Responsibility**: Performance monitoring

**Features**:
- Rolling average over window (default: 30 frames)
- FPS calculation
- Inference time tracking

**Usage**:
```python
counter = FPSCounter(window_size=30)

# Each frame:
counter.update()
fps = counter.get_fps()
time_ms = counter.get_inference_time()
```

#### **utils/logger.py**
**Responsibility**: Colored console logging

**Features**:
- Severity levels: DEBUG, INFO, WARNING, ERROR
- Colored output (requires ANSI support)
- Timestamps

**Usage**:
```python
from app.utils.logger import logger

logger.info("Starting application")
logger.debug("Detected 2 hands")
logger.warning("Low hand visibility")
logger.error("Camera not found")
```

---

## Key Design Patterns

### 1. **Single Responsibility Principle**
Each module handles ONE thing:
- Detector: Detection only (not classification)
- Gesture: Recognition only (not rendering)
- UI: Rendering only (not detection)

### 2. **Data Class Pattern**
Use dataclasses for clean data representation:
```python
@dataclass
class Hand:
    handedness: str
    confidence: float
    landmarks: List[Landmark]
    frame_width: int
    frame_height: int
```

### 3. **Pipeline Pattern**
Functions are organized as a pipeline that transforms data:
```
Input → Process → Transform → Process → Output
```

### 4. **Adapter Pattern**
`HandDetector` adapts MediaPipe's output to our format

### 5. **Strategy Pattern**
`FingerCounter` implements angle-based strategy for extension detection

### 6. **Configuration Object Pattern**
All settings centralized in `settings.py` - easy to change behavior without code modification

---

## Data Flow Example

Here's how a frame flows through the system:

```python
# 1. CAPTURE
frame = camera.read()  # 1280x720 BGR image

# 2. PREPROCESS
frame_flipped = cv2.flip(frame, 1)  # Mirror

# 3. DETECT HANDS
results = mediapipe.process(frame_flipped)
# → List[Hand objects] with 21 landmarks each

# 4. COUNT FINGERS
for hand in hands:
    angles = calculate_angles(hand.landmarks)
    # angles = [172°, 85°, 165°, ...]
    extended = [a > 160 for a in angles]
    # extended = [True, False, True, ...]
    count = sum(extended) = 2

# 5. CLASSIFY
gesture = 'open' if count >= 4 else 'fist'

# 6. SMOOTH
smoothed_count = moving_avg([3, 2, 2, 3, 2])
# → 2.4 → rounds to 2

# 7. TRACK STATE
gesture_tracker.update_left(
    {'count': 2, 'gesture': 'partial', 'display': 'Left Hand: 2'}
)

# 8. RENDER
render_landmarks(frame, hand)
render_text(frame, "Left Hand: 2", (50, 50))
render_fps(frame)

# 9. DISPLAY
cv2.imshow('Hand Detection', frame)
```

---

## Performance Considerations

### Frame Processing Time Breakdown (typical)
```
Camera capture:        2 ms
MediaPipe detection:  15 ms ← Largest
Finger counting:       3 ms
Smoothing:             1 ms
Rendering:             5 ms
Display:               1 ms
──────────────────────────
Total:                27 ms ≈ 37 FPS
```

### Optimization Opportunities
1. **Detection**: Use lite model (`MODEL_COMPLEXITY = 0`)
2. **Rendering**: Skip rendering in headless mode
3. **Threading**: Detect on thread, render on main
4. **Resolution**: Lower resolution = faster processing

---

## Extension Points

### Adding New Gestures
1. Modify `gesture_classifier.py`:
   ```python
   elif hand_state == 'peace_sign':
       return 'peace'
   ```

2. Add recognition logic in `finger_counter.py`

### Custom Rendering
1. Create new `Renderer` class in `ui/overlays.py`
2. Call it from `FrameRenderer.render_frame()`

### Custom Smoothing
1. Extend `MovingAverageSmoother` class
2. Implement custom averaging logic

### Custom Detection
1. Replace `HandDetector` with new detector
2. Ensure it outputs `HandsData` format

---

## Testing Strategy

### Unit Testing
```python
# Test angle calculation
from app.utils.geometry import angle_between_points

angle = angle_between_points((0, 0), (0, 10), (10, 10))
assert 80 < angle < 100  # Should be ~90°
```

### Integration Testing
```python
# Test detector → gesture pipeline
detector = HandDetector()
hands_data = detector.detect(frame)

for hand in hands_data.get_all_hands():
    result = recognizer.recognize(hand)
    assert 0 <= result['finger_count'] <= 5
```

### Visual Testing
1. Enable `DEBUG_MODE = True`
2. Check visualizations match hand poses
3. Verify smoothing removes jitter

---

**Architecture Design Complete** ✅
