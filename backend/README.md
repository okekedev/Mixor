# Mixor Backend

AI-Powered Instrumental Maker

## Features

**Instrumental Maker** - Remove vocals from any YouTube video using Demucs AI

## Core Modules

### `youtube_vocal_remover.py`
- Downloads YouTube audio via yt-dlp
- Runs Demucs 2-stem separation (vocals + instrumental)
- GPU-accelerated (CUDA/MPS support)
- Outputs clean instrumentals and isolated vocals

### `app.py`
- Flask API server
- `/api/remove-vocals` - Instrumental Maker endpoint
  - Accepts YouTube URL
  - Returns instrumental and acapella tracks

## Usage

### Start Backend Server
```bash
cd backend
python app.py
```

Server runs on `http://localhost:5000`

### API Endpoint
```
POST /api/remove-vocals
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=..."
}
```

## Requirements

- Python 3.12
- CUDA-enabled GPU (RTX 3060 or better) recommended
- FFmpeg installed
- See `requirements.txt` for Python packages

## Output Structure

```
output/
├── instrumentals/        # Vocal-removed tracks
├── acapellas/           # Isolated vocals
└── temp/                # Temporary files
```

## Tech Stack

- **Demucs** - State-of-the-art source separation
- **yt-dlp** - YouTube audio download
- **Flask** - REST API server
- **PyTorch** - GPU acceleration
