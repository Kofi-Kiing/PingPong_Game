# AGENTS.md

## Cursor Cloud specific instructions

### Project overview
Single-file Python game (`PingPong_Game.py`) — a hand-gesture-controlled Ping Pong game using OpenCV + MediaPipe. No build system, no test suite, no package manager config.

### Dependencies
- `opencv-python` (or `opencv-contrib-python`) and `mediapipe<0.10.21` (the legacy `mp.solutions.hands` API was removed in 0.10.21+).
- `flake8` for linting.
- Install via: `pip install opencv-python 'mediapipe<0.10.21' flake8`

### Running the application
- Requires a physical webcam (`/dev/video0`) and a display (X11). The game uses `cv2.VideoCapture(0, cv2.CAP_DSHOW)` — the `CAP_DSHOW` flag is Windows-specific but is silently ignored on Linux.
- In Cloud Agent VMs (headless, no webcam): the game will start but crash at `cv2.resize()` because `cam.read()` returns `None` when no camera is present. This is a hardware limitation, not a code bug.
- To run with a virtual display: `Xvfb :99 -screen 0 1280x720x24 &` then `DISPLAY=:99 python3 PingPong_Game.py`.

### Linting
```
flake8 PingPong_Game.py --max-line-length=200
```
Note: the codebase has many pre-existing style warnings; this is expected.

### Testing
No automated test suite exists. Verify the environment by checking that `import cv2` and `import mediapipe` succeed, and that `mp.solutions.hands.Hands()` initializes without error.

### Key gotcha
The `mediapipe` version must be pinned below `0.10.21`. Version 0.10.21+ removed `mp.solutions` in favor of a new `mp.tasks` API, which breaks the game code.
