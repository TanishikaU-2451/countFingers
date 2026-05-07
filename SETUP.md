# Setup and Installation Guide

## Complete Step-by-Step Installation

This guide walks you through setting up and running the Hand Detection application on your system.

## Prerequisites

Before starting, make sure you have:
- ✅ A working webcam (built-in or USB)
- ✅ Python 3.8 or higher installed
- ✅ pip (Python package manager)
- ✅ Good lighting for hand detection to work well

## Step 1: Verify Python Installation

### Windows (PowerShell)
```powershell
python --version
python -m pip --version
```

### macOS/Linux
```bash
python3 --version
python3 -m pip --version
```

**Expected output**: Python 3.8+ and pip with version numbers

If you don't have Python installed:
- Download from https://www.python.org/downloads/
- During installation, **CHECK** "Add Python to PATH"

## Step 2: Navigate to Project Directory

### Windows (PowerShell)
```powershell
cd C:\Users\YourUsername\OneDrive\Desktop\countFingers
```

### macOS/Linux
```bash
cd ~/Desktop/countFingers
```

## Step 3: Create Virtual Environment

A virtual environment keeps project dependencies isolated.

### Windows (PowerShell)
```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# You should see (venv) in your prompt now
```

### macOS/Linux
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your prompt now
```

**Troubleshooting**: If activation fails on Windows, try:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Step 4: Install Dependencies

With virtual environment activated:

```bash
pip install -r requirements.txt
```

This installs:
- `opencv-python` - Computer vision library
- `mediapipe` - Hand detection model
- `numpy` - Numerical computing

**Installation takes 2-5 minutes** depending on internet speed.

Verify installation:
```bash
pip list
```

Should show:
- opencv-python 4.8.1.78
- mediapipe 0.10.7
- numpy 1.24.3

## Step 5: Test Camera Access (Optional)

Before running the full app, test camera access:

### Windows/macOS/Linux
```python
python -c "
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
print(f'Camera accessible: {ret}')
cap.release()
cv2.destroyAllWindows()
"
```

Expected output: `Camera accessible: True`

If False, check:
1. Webcam is connected
2. No other application has exclusive camera access
3. Camera permissions are granted (macOS/Linux)

## Step 6: Run the Application

With virtual environment still activated:

```bash
python main.py
```

Expected output:
```
============================================================
Hand Detection and Finger Counting Application
============================================================
[INFO] 14:32:45 | Initializing Hand Detection Application...
[INFO] 14:32:45 | HandDetector initialized with max_hands=2
[INFO] 14:32:46 | Camera initialized: 1280x720
[INFO] 14:32:47 | Starting main loop. Press ESC to exit
```

A window should open showing your webcam feed.

## Step 7: Test the Application

1. **Position your hands** in front of the camera
2. **Raise fingers** to see them counted
3. **Make a fist** to see "Fist (0)" displayed
4. **Move hands** to track both left and right
5. **Remove hands** to see output clear

Expected output on screen:
```
=== Gesture Status ===
Left Hand: 3
Right Hand: Fist (0)

FPS: 28.5
Time: 35.2ms
```

## Step 8: Exit the Application

Press `ESC` key or `Ctrl+C` in terminal.

Expected output:
```
[INFO] 14:32:50 | Keyboard interrupt received
[INFO] 14:32:50 | Cleaning up resources...
[INFO] 14:32:50 | Application closed
```

---

## Troubleshooting Common Issues

### Issue: Python command not found

**Solution:**
```powershell
# Windows: Use full path
C:\Python310\python.exe main.py

# Or reinstall Python with "Add to PATH" checked
```

### Issue: Virtual environment won't activate

**Solution (Windows):**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try activation again
```

### Issue: pip install fails

**Solutions:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try installing with specific Python version
python -m pip install -r requirements.txt

# Or install packages one by one
pip install opencv-python
pip install mediapipe
pip install numpy
```

### Issue: "ModuleNotFoundError" when running app

**Solution:**
```bash
# Ensure virtual environment is activated (you should see (venv) in prompt)
# On Windows:
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
source venv/bin/activate

# Then run again
python main.py
```

### Issue: Camera not detected

**Solution:**
1. Check camera is connected/enabled
2. Test in another app first (e.g., Zoom, Skype)
3. Try changing camera device in `settings.py`:
   ```python
   CAMERA_DEVICE = 0  # Try 0, 1, 2, etc.
   ```

### Issue: Very low FPS or laggy output

**Solution:** Edit `settings.py`:
```python
# Use lite model (faster)
MODEL_COMPLEXITY = 0

# Reduce resolution
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Process fewer frames
FRAME_SKIP = 2
```

### Issue: Hands not detected despite being visible

**Solutions:**
1. Improve lighting (especially around hands)
2. Move hands closer to camera (1-2 feet away)
3. Lower confidence threshold in `settings.py`:
   ```python
   HAND_DETECTION_CONFIDENCE = 0.5  # From 0.7
   ```

---

## Deactivating Virtual Environment

When done working, deactivate:

```bash
deactivate
```

Prompt returns to normal (no "(venv)" prefix).

## Running Again Later

Next time you want to run the app:

1. Open terminal/PowerShell
2. Navigate to project: `cd countFingers`
3. Activate virtual environment:
   - Windows: `.\venv\Scripts\Activate.ps1`
   - macOS/Linux: `source venv/bin/activate`
4. Run app: `python main.py`

## System Requirements Recap

| Aspect | Minimum | Recommended |
|--------|---------|-------------|
| Python | 3.8 | 3.10+ |
| RAM | 4 GB | 8 GB+ |
| CPU | i5 | i7+ |
| FPS | 15 | 25+ |
| Resolution | 640x480 | 1280x720 |

## Next Steps

After successful installation:

1. **Read about Configuration**: See `settings.py` for customization options
2. **Explore Code**: Start with `main.py`, then check `app/` modules
3. **Try Debug Mode**: Set `DEBUG_MODE = True` in settings
4. **Customize**: Modify colors, thresholds, detection parameters

## Getting Help

If stuck:
1. Check error message carefully
2. See **Troubleshooting** section above
3. Review README.md for more details
4. Check logs with `DEBUG_MODE = True`

---

**Congratulations!** You're ready to detect hands and count fingers! 🎉
