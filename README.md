# Vocalless

A full-stack application that creates instrumental versions of YouTube videos using AI-powered vocal separation, then uploads them back to YouTube with SEO-optimized metadata.

## Features

- **Vocal Separation** - Uses Demucs AI model to separate vocals from instrumentals
- **Audio Mastering** - Professional loudness normalization to -14 LUFS (streaming standard)
- **Video Generation** - Creates videos with gradient backgrounds and title overlays
- **AI Metadata** - Generates titles, descriptions, and tags using local LLM (Ollama)
- **YouTube Integration** - Upload videos and manage playlists via OAuth
- **Web Interface** - Three-tab UI for processing, uploading, and playlist management

## Requirements

- Python 3.10+
- FFmpeg
- [Ollama](https://ollama.ai) with `llama3.2:3b` model
- YouTube API credentials (OAuth 2.0)
- GPU recommended (CUDA or Apple Silicon)

## Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/Vocalless.git
cd Vocalless

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install PyTorch (choose one)
# For NVIDIA GPU:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
# For Mac (Apple Silicon):
pip install torch torchaudio
# For CPU only:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install dependencies
pip install -r requirements.txt

# Pull the LLM model
ollama pull llama3.2:3b
```

## Configuration

1. Create a `.env` file with your YouTube OAuth credentials:
   ```
   YOUTUBE_CLIENT_ID=your_client_id
   YOUTUBE_CLIENT_SECRET=your_client_secret
   YOUTUBE_REFRESH_TOKEN=your_refresh_token
   ```

2. Run `python setup_youtube_oauth.py` if you need to generate credentials

## Usage

```bash
# Start Ollama (if not running as service)
ollama serve

# Start the web app
python app.py
```

Open http://localhost:5000 in your browser.

### Web Interface

| Tab | Purpose |
|-----|---------|
| **Process Videos** | Convert YouTube videos/playlists to instrumentals |
| **Upload Video** | Upload local videos with AI-generated metadata |
| **Playlist Manager** | Organize videos into playlists with drag-and-drop |

## How It Works

```
YouTube URL → Download Audio → Vocal Separation (Demucs) →
Audio Mastering → Video Generation → AI Metadata → YouTube Upload
```

## Project Structure

```
├── app.py                    # Flask web server
├── youtube_uploader.py       # YouTube API integration
├── metadata_generator.py     # AI metadata via Ollama
├── youtube_vocal_remover.py  # Demucs vocal separation
├── audio_hypermaster.py      # Audio mastering
├── optimize_seo.py           # SEO optimization strategies
├── templates/
│   └── index.html            # Web UI
└── output/
    ├── videos/               # Generated MP4s
    ├── instrumentals/        # Separated instrumentals
    └── acapellas/            # Extracted vocals
```

## Platform Support

| Platform | GPU | Status |
|----------|-----|--------|
| macOS | Apple Silicon (MPS) | Tested |
| Windows | NVIDIA (CUDA) | Supported |
| Linux | NVIDIA (CUDA) | Supported |
| Any | CPU | Supported (slower) |

See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for Windows-specific instructions.

## License

MIT
