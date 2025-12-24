# Mixor - YouTube Made Simple

> **Current Project Status**: Active development - Modern web interface with 1960s retro studio aesthetic

A full-stack application that creates instrumental versions of YouTube videos using AI-powered vocal separation. Features a beautiful retro-themed web interface inspired by vintage recording studios.

## Features

### Core Functionality
- **Vocal Separation** - Uses Demucs AI model to separate vocals from instrumentals
- **Audio Mastering** - Professional loudness normalization to -14 LUFS (streaming standard)
- **Dynamic Progress Tracking** - Smart progress estimation that learns from your hardware performance
- **Local Processing** - Save instrumentals directly to your computer

### Modern Web Interface (New!)
- **Retro Studio Design** - 1960s-inspired UI with wood panels, VU meters, and vintage aesthetics
- **React 19 + Vite** - Lightning-fast modern frontend with hot module replacement
- **Tailwind CSS v4** - Using latest CSS-first approach with @theme directive
- **Framer Motion** - Smooth animations and transitions
- **Real-time Updates** - Live progress tracking with WebSocket-like polling

### Interface Tabs
- **Instrumental Maker** - Convert YouTube videos to instrumentals and save locally
- **Video Studio** - Create videos with visualizations and effects
- **YouTube Uploader** - Upload videos with AI-generated metadata
- **Playlist Manager** - Organize your YouTube playlists
- **Settings** - Configure application preferences

## Tech Stack

### Backend
- Python 3.10+
- Flask web server
- Demucs AI (vocal separation)
- PyTorch (CUDA/MPS/CPU)
- FFmpeg (video/audio processing)
- Ollama + llama3.2:3b (AI metadata generation)

### Frontend
- React 19
- Vite 7.3
- Tailwind CSS v4
- Framer Motion
- Lucide React (icons)

## Requirements

- Python 3.10+
- Node.js 18+ (for frontend)
- FFmpeg
- [Ollama](https://ollama.ai) with `llama3.2:3b` model (optional, for AI features)
- YouTube API credentials (optional, for upload features)
- GPU recommended (CUDA or Apple Silicon)

## Installation

### Backend Setup

#### Quick Start (macOS/Linux)

```bash
# Clone the repo
git clone https://github.com/okekedev/Vocalless.git
cd Vocalless

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install PyTorch (choose based on your hardware)
# For Mac (Apple Silicon):
pip install torch torchaudio
# For NVIDIA GPU:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
# For CPU only:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install dependencies
pip install -r requirements.txt

# Pull the LLM model (optional, for AI metadata)
ollama pull llama3.2:3b
```

#### Windows Setup (NVIDIA GPU)

```powershell
# Clone the repo
git clone https://github.com/okekedev/Vocalless.git
cd Vocalless

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install PyTorch with CUDA 12.1 (for NVIDIA GPUs)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (required for video processing)
# Option 1: Using Chocolatey (recommended)
choco install ffmpeg

# Option 2: Using Winget
winget install Gyan.FFmpeg

# Pull the LLM model (optional, for AI metadata)
ollama pull llama3.2:3b
```

See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for detailed Windows-specific instructions.

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start on http://localhost:5181

## Usage

### Start the Application

```bash
# Terminal 1: Start Flask backend
python app.py

# Terminal 2: Start React frontend
cd frontend
npm run dev
```

Then open http://localhost:5181 in your browser.

### Quick Workflow

1. **Instrumental Maker Tab**:
   - Paste YouTube URL(s) or upload audio file
   - Click "CONVERT TO INSTRUMENTAL"
   - Watch the retro VU meter-style progress bar
   - Play and download your instrumental

2. **Video Studio Tab**:
   - Create visualized videos with your instrumentals
   - Choose from various background styles

3. **YouTube Uploader Tab**:
   - Upload videos with AI-generated metadata
   - Automatically optimized for SEO

## Configuration

### YouTube API Setup (Optional)

YouTube API setup is only needed for uploading videos. You can download and process videos without it.

1. **Create Google Cloud Project & Get Credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable **YouTube Data API v3**
   - Create **OAuth client ID** (Desktop app)
   - Download the JSON file as `client_secrets.json`

2. **Set Up OAuth**:
   ```bash
   python setup_youtube_oauth.py
   ```

See `.env.example` for configuration options.

## How It Works

```
YouTube URL → Download Audio → Vocal Separation (Demucs) →
Audio Mastering → Local Save / Video Generation → YouTube Upload (optional)
```

### Progress Estimation System

The app features an intelligent progress estimation system:
- Starts with a 3-minute default estimate
- Learns from each video processed
- Adapts to your hardware performance
- Shows real-time progress capped at 99% until completion

## Project Structure

```
├── app.py                          # Flask backend server
├── youtube_vocal_remover.py        # Demucs vocal separation
├── audio_hypermaster.py            # Audio mastering
├── youtube_uploader.py             # YouTube API integration
├── metadata_generator.py           # AI metadata via Ollama
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InstrumentalMaker.jsx   # Main conversion interface
│   │   │   ├── VideoStudio.jsx         # Video creation
│   │   │   ├── YouTubeUploader.jsx     # Upload interface
│   │   │   ├── PlaylistManager.jsx     # Playlist management
│   │   │   └── SettingsTab.jsx         # Configuration
│   │   ├── lib/
│   │   │   └── api.js                  # API client
│   │   ├── App.jsx                     # Main app component
│   │   └── index.css                   # Retro styles + Tailwind
│   ├── vite.config.js
│   └── package.json
└── output/
    ├── instrumentals/              # Separated audio files
    └── videos/                     # Generated videos
```

## Platform Support

| Platform | GPU | Status | Performance |
|----------|-----|--------|-------------|
| macOS | Apple Silicon (MPS) | ✅ Tested | Excellent |
| Windows | NVIDIA (CUDA 12.1) | ✅ Tested | Excellent |
| Linux | NVIDIA (CUDA) | ✅ Supported | Excellent |
| Any | CPU Only | ✅ Supported | Slow |

**Automatic GPU Detection**: The application automatically detects and uses the best available hardware.

## Development

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server with HMR
npm run dev

# Build for production
npm run build
```

### API Endpoints

- `POST /api/process` - Start video processing
- `GET /api/status/:jobId` - Get processing status
- `POST /api/process-audio` - Process uploaded audio file
- `POST /api/job/:jobId/cancel` - Cancel processing job
- `POST /api/open-file-location` - Open file in system explorer

## Screenshots

*Coming soon - showcasing the beautiful retro studio interface!*

## License

MIT

## Credits

- **Demucs** - AI vocal separation by Meta Research
- **Ollama** - Local LLM inference
- **Design Inspiration** - 1960s recording studio aesthetics
