# ⚡ Quick Start (2 Minutes)

## TL;DR - Get It Running

### Step 1: Setup (1 minute)
```bash
cd countFingers
python -m venv venv

# Windows:
.\venv\Scripts\Activate.ps1

# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Run (30 seconds)
```bash
python main.py
```

### Step 3: Test (30 seconds)
1. Show your hands to camera
2. Raise fingers to count them
3. Make a fist
4. Press **ESC** to exit

## Minimal Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Activate venv first |
| Camera not found | Try `CAMERA_DEVICE = 1` in settings |
| Low FPS | Set `MODEL_COMPLEXITY = 0` |
| Hands not detected | Improve lighting |

## What You're Running

```
Real-time hand detection
├─ 21 landmarks per hand
├─ Finger counting (0-5)
├─ Fist detection
├─ ~30 FPS on typical laptop
└─ Fully working, no additional setup needed
```

## Next Steps

- 📖 Read [README.md](README.md) for full documentation
- 🏗️ Check [ARCHITECTURE.md](ARCHITECTURE.md) to understand design
- 🛠️ Customize [app/config/settings.py](app/config/settings.py)
- 🧠 Explore code starting with [main.py](main.py)

---

**That's it! You now have a working hand detection app.** 🎉
