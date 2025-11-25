#!/bin/bash

# Setup script for YouTube Vocal Remover
# Compatible with M4 Mac (Apple Silicon)
# Date: November 22, 2025

echo "🎵 Setting up YouTube Vocal Remover..."

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip to latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install PyTorch with MPS (Metal Performance Shaders) support for M4 Mac
echo "Installing PyTorch with Apple Silicon support..."
pip install torch torchvision torchaudio

# Install YouTube downloader
echo "Installing yt-dlp (YouTube downloader)..."
pip install yt-dlp

# Install Demucs and dependencies
echo "Installing Demucs for vocal removal..."
pip install demucs

# Install additional dependencies
pip install pydub numpy scipy

# Install ffmpeg if not present (required for audio conversion)
if ! command -v ffmpeg &> /dev/null; then
    echo "Installing ffmpeg..."
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "⚠️  Please install ffmpeg manually (required for audio processing)"
    fi
else
    echo "✅ ffmpeg already installed"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Quick Start:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Run: python youtube_vocal_remover.py 'YOUTUBE_URL'"
echo ""
echo "Example:"
echo "  python youtube_vocal_remover.py 'https://www.youtube.com/watch?v=VIDEO_ID'"