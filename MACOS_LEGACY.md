# macOS Legacy Support (10.15 Catalina and below)

## Problem
The standard `sounddevice` library requires macOS 11+ (Big Sur). On older macOS versions you'll see:
```
macOS 26 (2603) or later required, have instead 16 (1603)
```

## Solution

### Option 1: Use Legacy Requirements (Recommended)
```bash
pip3 install -r requirements-macos-legacy.txt
```

This installs older, compatible versions of all dependencies.

### Option 2: Use PyAudio Instead
If sounddevice still fails, use PyAudio:

1. Install PortAudio:
```bash
brew install portaudio
```

2. Install PyAudio:
```bash
pip3 install pyaudio
```

3. Modify `src/audio_capture.py` to use PyAudio instead of sounddevice.

### Option 3: Upgrade macOS
Upgrade to macOS 11 Big Sur or later for full compatibility.

## Verification
After installing legacy requirements, test:
```bash
python3 -c "import sounddevice; print(sounddevice.__version__)"
```

Should print version 0.4.1 or similar without errors.

## Running the App
```bash
# Create .env file with your API key
cp .env.template .env
# Edit .env and add your TRANSCRIPTION_API_KEY

# Run the app
python3 -m src.main
```

## Known Limitations on Legacy macOS
- Desktop audio capture may not work (Windows-only feature anyway)
- System tray integration not available
- Some hotkeys may not work

The basic microphone recording and transcription features work fine!
