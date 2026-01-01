# Mixor - AI-Powered Instrumental Maker

> Clean, retro-styled Mac app for removing vocals from any YouTube video using state-of-the-art AI

![Mixor Interface](docs/screenshot.png)

## Features

🎵 **Instant Vocal Removal** - Remove vocals from any YouTube video with one click
🎸 **Dual Output** - Get both instrumental and acapella (vocals-only) tracks
⚡ **GPU Accelerated** - Blazing fast processing with CUDA/Metal support
🎨 **Retro Studio UI** - Beautiful vintage-inspired interface
💾 **Local Processing** - All processing happens on your machine, no data sent to cloud

## Tech Stack

**Backend**
- Python 3.12
- Demucs (Meta's state-of-the-art source separation)
- yt-dlp (YouTube audio extraction)
- Flask REST API
- PyTorch with GPU acceleration

**Frontend**
- React 18 + Vite
- Tailwind CSS
- Framer Motion (animations)
- Retro-styled UI components

## Project Structure

```
mixor/
├── backend/
│   ├── app.py                      # Flask REST API
│   ├── youtube_vocal_remover.py    # Demucs vocal separation
│   └── README.md                   # Backend docs
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Main app component
│   │   ├── components/
│   │   │   └── InstrumentalMaker.jsx
│   │   └── lib/
│   │       └── api.js              # API client
│   └── package.json
└── README.md                       # This file
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- FFmpeg installed
- CUDA-enabled GPU (recommended) or Apple Silicon Mac

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mixor.git
   cd mixor
   ```

2. **Install backend dependencies**
   ```bash
   cd backend
   pip install flask flask-cors demucs yt-dlp torch
   ```

3. **Install frontend dependencies**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the App

1. **Start the backend server**
   ```bash
   cd backend
   python app.py
   ```
   Server runs on `http://localhost:5000`

2. **Start the frontend dev server**
   ```bash
   cd frontend
   npm run dev
   ```
   App opens at `http://localhost:5181`

## Usage

1. Paste a YouTube URL into the input field
2. Click **CONVERT**
3. Wait for processing (uses GPU acceleration)
4. Play, download, or save your instrumental and acapella tracks

## API Endpoints

- `POST /api/process-instrumental` - Process YouTube URL
- `GET /api/status/<job_id>` - Get job status
- `POST /api/cancel/<job_id>` - Cancel a job
- `GET /output/<filename>` - Serve output files

## Building for Mac

### Electron App (Recommended)

Coming soon - native Mac app with:
- Native menu bar integration
- Drag-and-drop support
- System notifications
- Auto-updater

### PyInstaller (Alternative)

Package the backend as a standalone executable:
```bash
cd backend
pip install pyinstaller
pyinstaller --onefile --add-data "youtube_vocal_remover.py:." app.py
```

## Performance

- **Processing Speed**: ~30 seconds per 3-minute song (RTX 3060)
- **Quality**: Professional-grade separation using Demucs
- **GPU Memory**: ~4GB VRAM required

## Troubleshooting

**FFmpeg not found**
```bash
# Mac
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

**CUDA not detected**
- Ensure PyTorch is installed with CUDA support
- Check GPU drivers are up to date

## Roadmap

- [ ] Native Mac app with Electron
- [ ] Batch processing support
- [ ] Custom Demucs model training
- [ ] Real-time preview during processing
- [ ] Multiple stem separation (drums, bass, vocals, other)

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## License

MIT License - see [LICENSE](LICENSE) for details

## Acknowledgments

- [Demucs](https://github.com/facebookresearch/demucs) by Meta Research
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube downloading
- Retro UI inspired by vintage studio equipment

## Support

- 🐛 [Report a bug](https://github.com/yourusername/mixor/issues)
- 💡 [Request a feature](https://github.com/yourusername/mixor/issues)
- 📧 Email: support@mixor.app
