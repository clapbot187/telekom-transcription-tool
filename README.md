# Telekom Transcription Tool

A GUI application for recording audio and transcribing it using the Telekom Whisper API, with optional GPT enhancement.

## Features

- Record audio from your microphone
- Transcribe recordings using Whisper API (whisper-large-v3)
- Enhance transcriptions with GPT for grammar and clarity
- Simple Tkinter-based GUI interface
- Configurable via environment variables

## Requirements

- Python 3.11+
- API key for Telekom LLM services
- Microphone access

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd transcription-tool
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API key

Copy the template environment file and add your API key:

```bash
cp .env.template .env
```

Edit `.env` and replace `your-api-key-here` with your actual API key:

```env
TELEKOM_API_KEY=your-actual-api-key
WHISPER_ENDPOINT=https://llm-server.llmhub.t-systems.net/v2/audio/transcriptions
GPT_ENDPOINT=https://llm-server.llmhub.t-systems.net/v2/chat/completions
SAMPLE_RATE=16000
CHANNELS=1
```

Alternatively, you can set the API key via environment variable:

```bash
export TELEKOM_API_KEY="your-actual-api-key"
```

## Usage

### Run the application

```bash
python -m src.main
```

### Command-line options

```bash
python -m src.main --help

# Pass API key directly
python -m src.main --api-key your-api-key
```

### Using the GUI

1. Click **Start Recording** to begin capturing audio
2. Speak into your microphone
3. Click **Stop Recording** when finished
4. Click **Transcribe** to convert audio to text using Whisper API
5. (Optional) Click **Enhance with GPT** to improve the transcription
6. Use **Copy to Clipboard** to copy the result

Recordings are automatically saved to the `recordings/` directory.

## Docker Usage

### Build the image

```bash
docker build -t transcription-tool .
```

### Run with environment file

```bash
docker run -it \
  --env-file .env \
  -v $(pwd)/recordings:/app/recordings \
  transcription-tool
```

Or pass environment variables directly:

```bash
docker run -it \
  -e TELEKOM_API_KEY=your-api-key \
  -e SAMPLE_RATE=16000 \
  -e CHANNELS=1 \
  -v $(pwd)/recordings:/app/recordings \
  transcription-tool
```

Note: Running GUI applications in Docker requires additional setup for display forwarding (X11 on Linux, XQuartz on macOS).

## API Endpoints

The application uses the following Telekom LLM endpoints:

- **Whisper Transcription**: `https://llm-server.llmhub.t-systems.net/v2/audio/transcriptions`
  - Model: `whisper-large-v3`
- **GPT Enhancement**: `https://llm-server.llmhub.t-systems.net/v2/chat/completions`
  - Model: `gpt-4`

## Configuration Options

| Environment Variable | Description | Default |
|--------|-------------|---------|
| `TELEKOM_API_KEY` | Your Telekom LLM API key | Required |
| `WHISPER_ENDPOINT` | Whisper API endpoint URL | `https://llm-server.llmhub.t-systems.net/v2/audio/transcriptions` |
| `GPT_ENDPOINT` | GPT API endpoint URL | `https://llm-server.llmhub.t-systems.net/v2/chat/completions` |
| `SAMPLE_RATE` | Audio sample rate in Hz | 16000 |
| `CHANNELS` | Number of audio channels | 1 (mono) |

## Project Structure

```
transcription-tool/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── audio_capture.py     # Audio recording functionality
│   ├── api_client.py        # Whisper and GPT API clients
│   ├── gui.py               # Tkinter GUI implementation
│   └── main.py              # Application entry point
├── recordings/              # Saved audio recordings (created at runtime)
├── .env.template            # Environment configuration template
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
└── README.md                # This file
```

## Troubleshooting

### No audio detected

- Check that your microphone is properly connected
- Verify microphone permissions in your system settings
- Try adjusting the SAMPLE_RATE in your .env file

### API errors

- Verify your API key is correct
- Check network connectivity to the LLM endpoints
- Ensure you have sufficient API quota

### PortAudio errors

On Linux, you may need to install PortAudio development libraries:

```bash
# Ubuntu/Debian
sudo apt-get install portaudio19-dev

# Fedora/RHEL
sudo dnf install portaudio-devel

# macOS
brew install portaudio
```

## License

© Telekom
