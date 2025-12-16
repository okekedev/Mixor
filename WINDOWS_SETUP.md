# Windows Setup (RTX 3060)

## Prerequisites

1. **Python 3.10+** - Download from python.org
2. **FFmpeg** - Install via `winget install ffmpeg` or download from ffmpeg.org and add to PATH
3. **Ollama** - Download from ollama.ai, then run `ollama pull llama3.2:3b`
4. **Git** - For cloning/syncing

## Setup Steps

```bash
# Clone/sync the repo
git clone <your-repo-url>
cd youtube

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install PyTorch with CUDA (RTX 3060)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install remaining dependencies
pip install -r requirements.txt
```

## Required Code Change

In `youtube_vocal_remover.py`, find lines 78-79 and replace:

```python
# OLD (Mac-only):
self.device = "mps" if torch.backends.mps.is_available() else "cpu"

# NEW (cross-platform):
if torch.cuda.is_available():
    self.device = "cuda"
elif torch.backends.mps.is_available():
    self.device = "mps"
else:
    self.device = "cpu"
```

## YouTube OAuth Setup

1. Copy `.env.example` to `.env` (or create `.env`)
2. Add your Google OAuth credentials:
   ```
   YOUTUBE_CLIENT_ID=your_client_id
   YOUTUBE_CLIENT_SECRET=your_client_secret
   YOUTUBE_REFRESH_TOKEN=your_refresh_token
   ```
3. Run `python setup_youtube_oauth.py` if you need to generate a refresh token

## Running

```bash
# Make sure Ollama is running first
ollama serve

# Start the web app
python app.py
```

Then open http://localhost:5000 in your browser.

## Verify CUDA is Working

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

Should output:
```
CUDA available: True
GPU: NVIDIA GeForce RTX 3060
```
