#!/usr/bin/env python3
"""
YouTube to Instrumental Converter
Downloads YouTube video, converts to MP3, and removes vocals
Optimized for M4 Mac - November 2025

DISCLAIMER AND LEGAL NOTICE:
============================
This tool is provided for EDUCATIONAL and PERSONAL USE ONLY.

By using this software, you acknowledge and agree that:

1. COPYRIGHT: You are responsible for respecting all copyright laws and the
   intellectual property rights of content creators.

2. PERSONAL USE: This tool should only be used for:
   - Processing content you own or have explicit rights to
   - Personal practice and education
   - Fair use purposes as defined by your local laws

3. PROHIBITED USE: Do NOT use this tool for:
   - Commercial purposes without proper licensing
   - Distributing copyrighted content without permission
   - Any activity that violates YouTube's Terms of Service
   - Any activity that infringes on artists' rights

4. PRIVACY: All processing happens locally on your device. No data is sent
   to external servers. The AI model does not learn from or store your content.

5. NO WARRANTY: This software is provided "as is" without any warranties.
   The creators are not liable for any misuse or copyright violations.

6. YOUTUBE TOS: Downloading content from YouTube may violate their Terms of
   Service. Use at your own discretion and risk.

7. ARTIST SUPPORT: Consider supporting artists by purchasing their music
   through official channels.

By proceeding, you confirm that you understand these terms and will use
this tool responsibly and legally.
"""

import os
import sys
import time
import shutil
import argparse
from pathlib import Path
import subprocess
import torch

class YouTubeVocalRemover:
    def __init__(self, output_dir="output", keep_original=False):
        """
        Initialize YouTube Vocal Remover

        Args:
            output_dir: Directory for output files
            keep_original: If True, keeps the original MP3 with vocals
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.keep_original = keep_original

        # Create organized output directories
        self.temp_dir = self.output_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)

        self.instrumentals_dir = self.output_dir / "instrumentals"
        self.instrumentals_dir.mkdir(exist_ok=True)

        self.acapellas_dir = self.output_dir / "acapellas"
        self.acapellas_dir.mkdir(exist_ok=True)

        self.videos_dir = self.output_dir / "videos"
        self.videos_dir.mkdir(exist_ok=True)

        # Create stems directory for 4-stem separation (Creator feature)
        self.stems_dir = self.output_dir / "stems"
        self.stems_dir.mkdir(exist_ok=True)

        # Check for GPU acceleration (CUDA > MPS > CPU)
        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"
        print(f"Using device: {self.device}")

    def download_from_youtube(self, url):
        """
        Download audio from YouTube and convert to MP3

        Args:
            url: YouTube URL

        Returns:
            Path to downloaded MP3 file
        """
        print(f"\nDownloading from YouTube...")
        print(f"   URL: {url}")

        try:
            import yt_dlp

            # Configure yt-dlp options
            # Auto-detect ffmpeg location based on platform
            ffmpeg_location = None
            if sys.platform == 'darwin':  # macOS
                # Check common macOS paths
                mac_paths = ['/opt/homebrew/bin', '/usr/local/bin']
                for path in mac_paths:
                    if os.path.exists(os.path.join(path, 'ffmpeg')):
                        ffmpeg_location = path
                        break
            # For Windows/Linux, rely on system PATH (no need to specify location)

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',  # Use WAV for lossless processing
                    'preferredquality': '0',  # Best quality
                }],
                'outtmpl': str(self.temp_dir / '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': True,  # Suppress warnings
                'extractaudio': True,
                'noplaylist': True,  # Only download single video, not playlist
            }

            # Only set ffmpeg_location if explicitly found (macOS)
            if ffmpeg_location:
                ydl_opts['ffmpeg_location'] = ffmpeg_location

            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info['title']
                # Clean filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                audio_file = self.temp_dir / f"{safe_title}.wav"

                # Find the actual downloaded file (yt-dlp might change the name)
                for file in self.temp_dir.glob("*.wav"):
                    if file.exists():
                        audio_file = file
                        break

                if audio_file.exists():
                    print(f"Success: Downloaded: {audio_file.name}")
                    print(f"   Duration: {info.get('duration', 'unknown')} seconds")
                    print(f"   Format: WAV (lossless)")
                    return audio_file
                else:
                    print("Error: Download failed - audio file not found")
                    return None

        except ImportError:
            print("Error: yt-dlp not installed!")
            print("   Run: pip install yt-dlp")
            return None
        except Exception as e:
            print(f"Error: Download error: {e}")
            return None

    def remove_vocals(self, audio_file, model="htdemucs_ft"):
        """
        Remove vocals from audio file using Demucs

        Args:
            audio_file: Path to input audio file
            model: Demucs model to use

        Returns:
            Path to instrumental file
        """
        print(f"\nRemoving vocals...")
        print(f"   Model: {model}")

        try:
            # Run Demucs using command line (more reliable than API for single files)
            output_name = audio_file.stem

            # Build command - use MP3 output to avoid torchcodec issues
            cmd = [
                sys.executable, "-m", "demucs",
                "--two-stems=vocals",  # Only separate vocals and instrumental
                "-n", model,
                "-o", str(self.output_dir),
                "--device", self.device,
                "--mp3",  # Output as MP3 to avoid torchcodec dependency
                str(audio_file)
            ]

            # Run Demucs
            print("Processing (this may take 30-60 seconds)...")
            print(f"   Using device: {self.device}")
            start_time = time.time()

            # Set environment to use UTF-8 encoding for subprocess
            import os
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'

            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)

            # Show Demucs output for debugging
            if result.stdout:
                print(f"   Demucs output: {result.stdout[:200]}")

            if result.returncode != 0:
                print(f"Error: Demucs error: {result.stderr}")
                return None

            elapsed = time.time() - start_time
            print(f"Processing time: {elapsed:.1f} seconds")

            # Find output files
            # Demucs creates a folder structure: output/htdemucs/song_name/
            model_dir = self.output_dir / model / output_name
            instrumental_file = model_dir / "no_vocals.mp3"
            vocals_file = model_dir / "vocals.mp3"

            if instrumental_file.exists():
                # Move instrumental to instrumentals folder
                final_instrumental = self.instrumentals_dir / f"{output_name}.mp3"
                shutil.move(str(instrumental_file), str(final_instrumental))
                print(f"Success: Instrumental saved: instrumentals/{final_instrumental.name}")
                print(f"   Size: {final_instrumental.stat().st_size / (1024*1024):.1f} MB")

                # Move vocals to acapellas folder
                if vocals_file.exists():
                    final_vocals = self.acapellas_dir / f"{output_name}.mp3"
                    shutil.move(str(vocals_file), str(final_vocals))
                    print(f"Success: Acapella saved: acapellas/{final_vocals.name}")
                    print(f"   Size: {final_vocals.stat().st_size / (1024*1024):.1f} MB")

                # Clean up temp model directories
                shutil.rmtree(model_dir.parent, ignore_errors=True)

                return final_instrumental
            else:
                print("Error: Vocal removal failed - output file not found")
                return None

        except Exception as e:
            print(f"Error: Error during vocal removal: {e}")
            return None

    def separate_to_4stems(self, audio_file, model="htdemucs_ft"):
        """
        Separate audio into 4 stems: drums, bass, vocals, other

        Args:
            audio_file: Path to input audio file
            model: Demucs model to use (htdemucs or htdemucs_ft)

        Returns:
            dict with paths to all stems: {"drums": path, "bass": path, "vocals": path, "other": path}
        """
        print(f"\nSeparating into 4 stems (drums, bass, vocals, other)...")
        print(f"   Model: {model}")

        try:
            output_name = audio_file.stem

            # Build command for 4-stem separation
            cmd = [
                sys.executable, "-m", "demucs",
                "-n", model,  # Use full separation (not --two-stems)
                "-o", str(self.output_dir),
                "--device", self.device,
                "--mp3",  # Output as MP3
                str(audio_file)
            ]

            # Run Demucs
            print("Processing (this may take 60-90 seconds)...")
            print(f"   Using device: {self.device}")
            start_time = time.time()

            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'

            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)

            if result.returncode != 0:
                print(f"Error: Demucs error: {result.stderr}")
                return None

            elapsed = time.time() - start_time
            print(f"Processing time: {elapsed:.1f} seconds")

            # Find output files
            model_dir = self.output_dir / model / output_name

            # Create organized directory for this separation
            stem_output_dir = self.stems_dir / output_name
            stem_output_dir.mkdir(exist_ok=True, parents=True)

            # Collect all stems
            stems = {}
            for stem_name in ["drums", "bass", "vocals", "other"]:
                stem_file = model_dir / f"{stem_name}.mp3"

                if stem_file.exists():
                    # Move to organized stems directory
                    final_stem = stem_output_dir / f"{stem_name}.mp3"
                    shutil.move(str(stem_file), str(final_stem))
                    stems[stem_name] = final_stem
                    print(f"Success: {stem_name.capitalize()} stem saved: {final_stem.relative_to(self.output_dir)}")
                    print(f"   Size: {final_stem.stat().st_size / (1024*1024):.1f} MB")
                else:
                    print(f"Warning: {stem_name} stem not found")
                    stems[stem_name] = None

            # Clean up temp model directories
            shutil.rmtree(model_dir.parent, ignore_errors=True)

            return stems

        except Exception as e:
            print(f"Error: Error during stem separation: {e}")
            return None

    def convert_to_mp3(self, wav_file):
        """Convert WAV to MP3 for smaller file size"""
        print("\nConverting to MP3...")

        mp3_file = wav_file.with_suffix('.mp3')

        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_wav(str(wav_file))
            audio.export(str(mp3_file), format="mp3", bitrate="192k")

            # Remove WAV file
            wav_file.unlink()

            print(f"Success: Converted to MP3: {mp3_file.name}")
            print(f"   Size: {mp3_file.stat().st_size / (1024*1024):.1f} MB")
            return mp3_file

        except Exception as e:
            print(f"Warning: Could not convert to MP3: {e}")
            return wav_file

    def process_youtube_url(self, url, model="htdemucs_ft"):
        """
        Complete pipeline: Download from YouTube → Remove Vocals → Save

        Args:
            url: YouTube URL
            model: Demucs model to use

        Returns:
            Path to final instrumental file
        """
        print("\n" + "="*60)
        print("YouTube to Instrumental Converter")
        print("="*60)

        # Step 1: Download from YouTube
        mp3_file = self.download_from_youtube(url)
        if not mp3_file:
            return None

        # Step 2: Remove vocals (outputs MP3 directly)
        instrumental_file = self.remove_vocals(mp3_file, model)
        if not instrumental_file:
            return None

        # Step 3: Clean up
        if not self.keep_original:
            mp3_file.unlink(missing_ok=True)
        else:
            # Move original to output
            final_original = self.output_dir / mp3_file.name
            shutil.move(str(mp3_file), str(final_original))
            print(f"Original saved: {final_original.name}")

        # Clean temp directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

        print("\n" + "="*60)
        print("Success: Complete! Your instrumental is ready:")
        print(f"   {instrumental_file}")
        print("="*60)

        return instrumental_file

    def process_youtube_url_4stems(self, url, model="htdemucs_ft"):
        """
        Complete pipeline for Creator feature: Download from YouTube → Separate into 4 stems

        Args:
            url: YouTube URL
            model: Demucs model to use

        Returns:
            dict with paths to all stems: {"drums": path, "bass": path, "vocals": path, "other": path, "title": str}
        """
        print("\n" + "="*60)
        print("YouTube to 4-Stem Separator (Creator Feature)")
        print("="*60)

        # Step 1: Download from YouTube
        audio_file = self.download_from_youtube(url)
        if not audio_file:
            return None

        # Step 2: Separate into 4 stems
        stems = self.separate_to_4stems(audio_file, model)
        if not stems:
            return None

        # Step 3: Clean up
        if not self.keep_original:
            audio_file.unlink(missing_ok=True)

        # Clean temp directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

        # Add title to stems dict
        stems["title"] = audio_file.stem

        print("\n" + "="*60)
        print("Success: Complete! Your 4 stems are ready:")
        for stem_name, stem_path in stems.items():
            if stem_name != "title" and stem_path:
                print(f"   {stem_name}: {stem_path.relative_to(self.output_dir)}")
        print("="*60)

        return stems

def show_disclaimer():
    """Show legal disclaimer and get user confirmation"""
    print("\n" + "="*70)
    print("LEGAL DISCLAIMER & TERMS OF USE")
    print("="*70)
    print("""
This tool is for EDUCATIONAL and PERSONAL USE ONLY.

By continuing, you confirm that:
✓ You will only process content you own or have rights to
✓ You understand this may violate YouTube's Terms of Service
✓ You will not use this for commercial purposes without proper licensing
✓ You respect artists' intellectual property rights
✓ All processing happens locally - no data is sent to external servers

For learning purposes, consider using royalty-free music or content
you have created yourself.
    """)
    print("="*70)

    response = input("\nWarning: Do you accept these terms and wish to continue? (yes/no): ")
    return response.lower() in ['yes', 'y']

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Download YouTube video and remove vocals"
    )

    parser.add_argument(
        "url",
        help="YouTube URL"
    )
    parser.add_argument(
        "--model", "-m",
        default="htdemucs_ft",
        choices=["htdemucs", "htdemucs_ft", "mdx", "mdx_extra"],
        help="Demucs model to use (default: htdemucs_ft - best quality)"
    )
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="Output directory (default: output)"
    )
    parser.add_argument(
        "--keep-original", "-k",
        action="store_true",
        help="Keep the original audio with vocals"
    )

    args = parser.parse_args()

    # Check dependencies
    try:
        import yt_dlp
        import demucs
        print(f"\nyt-dlp version: {yt_dlp.version.__version__}")
        print(f"Demucs version: {demucs.__version__}")
    except ImportError as e:
        print(f"Error: Missing dependency: {e}")
        print("\nInstallation:")
        print("   pip install yt-dlp demucs")
        return

    # Process the YouTube URL
    remover = YouTubeVocalRemover(
        output_dir=args.output,
        keep_original=args.keep_original
    )

    result = remover.process_youtube_url(
        args.url,
        model=args.model
    )

    if not result:
        sys.exit(1)

if __name__ == "__main__":
    main()