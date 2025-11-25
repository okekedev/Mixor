#!/usr/bin/env python3
"""
Complete YouTube to Instrumental Video Pipeline
Downloads YouTube video, removes vocals, creates video with gradient + EQ + title
Optimized for M4 Mac - November 2025
"""

import sys
import subprocess
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import hashlib
from youtube_vocal_remover import YouTubeVocalRemover
from metadata_generator import MetadataGenerator
from audio_hypermaster import AudioHyperMaster


class InstrumentalVideoGenerator:
    def __init__(self, output_dir="output", enable_hypermaster=True):
        """Initialize generator

        Args:
            output_dir: Output directory
            enable_hypermaster: Enable HyperMaster audio enhancement (default: True)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Use organized folder structure
        self.videos_dir = self.output_dir / "videos"
        self.videos_dir.mkdir(exist_ok=True)

        # HyperMaster settings
        self.enable_hypermaster = enable_hypermaster
        if self.enable_hypermaster:
            self.hypermaster = AudioHyperMaster()

    def create_gradient_background(self, artist_title, size=(1920, 1080)):
        """
        Create gradient background with artist name and "- Instrumental"

        Args:
            artist_title: Artist name (e.g., "PARTYNEXTDOOR, Drake")
            size: Output dimensions

        Returns:
            Path to saved background image
        """
        print("🎨 Creating gradient background...")

        # Create gradient
        img = Image.new('RGB', size)
        draw = ImageDraw.Draw(img)

        # Professional color schemes (darker backgrounds) - 30 total
        schemes = [
            # Purples & Violets
            [(15, 0, 30), (45, 0, 90), (90, 0, 150)],      # 1. Deep Purple
            [(20, 0, 40), (40, 0, 80), (60, 0, 120)],      # 2. Royal Purple
            [(30, 0, 50), (60, 20, 80), (90, 40, 110)],    # 3. Violet Dreams
            [(40, 10, 60), (70, 30, 90), (100, 50, 120)],  # 4. Lavender Night

            # Blues
            [(0, 10, 25), (0, 30, 60), (0, 60, 120)],      # 5. Ocean Blue
            [(0, 0, 20), (0, 20, 60), (20, 40, 100)],      # 6. Midnight
            [(0, 20, 40), (10, 40, 70), (20, 60, 100)],    # 7. Deep Sea
            [(0, 30, 50), (20, 50, 80), (40, 70, 110)],    # 8. Navy Night
            [(10, 40, 60), (30, 60, 90), (50, 80, 120)],   # 9. Teal Depths

            # Greens
            [(0, 15, 0), (0, 40, 15), (0, 70, 30)],        # 10. Forest
            [(0, 30, 20), (10, 50, 40), (20, 70, 60)],     # 11. Emerald
            [(10, 40, 30), (30, 60, 50), (50, 80, 70)],    # 12. Mint Shadow
            [(20, 30, 10), (40, 50, 30), (60, 70, 50)],    # 13. Olive Dusk

            # Reds & Pinks
            [(30, 0, 10), (60, 0, 20), (90, 10, 40)],      # 14. Crimson
            [(40, 10, 20), (70, 20, 40), (100, 40, 60)],   # 15. Ruby
            [(50, 0, 30), (80, 20, 50), (110, 40, 70)],    # 16. Magenta Night
            [(40, 15, 30), (80, 30, 50), (120, 45, 70)],   # 17. Sunset
            [(35, 10, 25), (65, 25, 45), (95, 45, 65)],    # 18. Rose Twilight

            # Oranges & Ambers
            [(30, 15, 10), (60, 30, 20), (90, 45, 30)],    # 19. Warm Earth
            [(40, 20, 0), (70, 40, 10), (100, 60, 30)],    # 20. Amber Glow
            [(35, 25, 5), (65, 45, 20), (95, 65, 40)],     # 21. Bronze

            # Teals & Cyans
            [(0, 25, 30), (10, 45, 60), (30, 65, 90)],     # 22. Cyan Deep
            [(10, 30, 40), (30, 50, 70), (50, 70, 100)],   # 23. Aqua Night
            [(5, 35, 35), (25, 55, 65), (45, 75, 95)],     # 24. Turquoise

            # Greys & Neutrals
            [(20, 20, 30), (40, 40, 60), (60, 60, 90)],    # 25. Cool Grey
            [(25, 25, 25), (50, 50, 50), (75, 75, 75)],    # 26. Charcoal
            [(15, 20, 25), (35, 45, 55), (55, 70, 85)],    # 27. Steel Blue

            # Mixed/Gradient Blends
            [(30, 10, 40), (50, 40, 70), (70, 70, 100)],   # 28. Purple-Blue Blend
            [(10, 30, 50), (40, 50, 70), (70, 70, 90)],    # 29. Blue-Grey Fusion
            [(25, 15, 35), (55, 35, 65), (85, 55, 95)]     # 30. Plum Twilight
        ]

        # Pick a truly random color scheme each time
        import random
        colors = random.choice(schemes)

        # Three-point smooth gradient
        for y in range(size[1]):
            if y < size[1] * 0.3:
                ratio = y / (size[1] * 0.3)
                r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
                g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
                b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            elif y < size[1] * 0.7:
                ratio = (y - size[1] * 0.3) / (size[1] * 0.4)
                r = int(colors[1][0] * (1 - ratio) + colors[2][0] * ratio)
                g = int(colors[1][1] * (1 - ratio) + colors[2][1] * ratio)
                b = int(colors[1][2] * (1 - ratio) + colors[2][2] * ratio)
            else:
                # Darker at bottom for spectrum contrast
                ratio = (y - size[1] * 0.7) / (size[1] * 0.3)
                r = int(colors[2][0] * (1 - ratio * 0.5))
                g = int(colors[2][1] * (1 - ratio * 0.5))
                b = int(colors[2][2] * (1 - ratio * 0.5))

            draw.rectangle([(0, y), (size[0], y+1)], fill=(r, g, b))

        # Add subtle vignette
        overlay = Image.new('RGBA', size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        for corner in [(0, 0), (size[0], 0), (0, size[1]), (size[0], size[1])]:
            for radius in range(300, 0, -10):
                opacity = int(20 * (1 - radius / 300))
                overlay_draw.ellipse(
                    [corner[0] - radius, corner[1] - radius,
                     corner[0] + radius, corner[1] + radius],
                    fill=(0, 0, 0, opacity)
                )

        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

        # Add modern 3-line text label: Title / Artist / Instrumental
        if artist_title:
            try:
                # Modern fonts with different sizes
                title_font = ImageFont.truetype("/System/Library/Fonts/SF-Pro-Display-Bold.otf", 64)
                artist_font = ImageFont.truetype("/System/Library/Fonts/SF-Pro-Display-Medium.otf", 48)
                label_font = ImageFont.truetype("/System/Library/Fonts/SF-Pro-Display-Light.otf", 36)
            except:
                try:
                    title_font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 64)
                    artist_font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 48)
                    label_font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 36)
                except:
                    title_font = ImageFont.load_default()
                    artist_font = ImageFont.load_default()
                    label_font = ImageFont.load_default()

            # Parse artist and title (assuming format: "Artist - Title")
            if " - " in artist_title:
                parts = artist_title.rsplit(" - ", 1)
                artist = parts[0].strip()
                title = parts[1].replace(" (Official Music Video)", "").strip()
            else:
                artist = artist_title
                title = ""

            # Create text lines
            lines = []
            temp_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))

            if title:
                title_bbox = temp_draw.textbbox((0, 0), title, font=title_font)
                lines.append((title, title_font, title_bbox[2] - title_bbox[0], title_bbox[3] - title_bbox[1], (255, 255, 255)))

            if artist:
                artist_bbox = temp_draw.textbbox((0, 0), artist, font=artist_font)
                lines.append((artist, artist_font, artist_bbox[2] - artist_bbox[0], artist_bbox[3] - artist_bbox[1], (200, 200, 200)))

            label_bbox = temp_draw.textbbox((0, 0), "INSTRUMENTAL REMASTER", font=label_font)
            lines.append(("INSTRUMENTAL REMASTER", label_font, label_bbox[2] - label_bbox[0], label_bbox[3] - label_bbox[1], (160, 160, 160)))

            # Calculate box dimensions
            max_width = max(line[2] for line in lines)
            total_height = sum(line[3] for line in lines) + (len(lines) - 1) * 20  # 20px spacing

            padding_h = 60
            padding_v = 50
            box_width = max_width + padding_h * 2
            box_height = total_height + padding_v * 2

            # Center the box
            box_x = (size[0] - box_width) // 2
            box_y = (size[1] - box_height) // 2

            # Draw more opaque rounded rectangle
            box_overlay = Image.new('RGBA', size, (0, 0, 0, 0))
            box_draw = ImageDraw.Draw(box_overlay)

            # More opaque background
            box_draw.rounded_rectangle(
                [box_x, box_y, box_x + box_width, box_y + box_height],
                radius=20,
                fill=(0, 0, 0, 200)  # More opaque (78% opacity)
            )

            # Subtle white border
            box_draw.rounded_rectangle(
                [box_x, box_y, box_x + box_width, box_y + box_height],
                radius=20,
                outline=(255, 255, 255, 60),
                width=2
            )

            # Apply box
            img = Image.alpha_composite(img.convert('RGBA'), box_overlay).convert('RGB')
            draw = ImageDraw.Draw(img)

            # Draw centered text lines
            current_y = box_y + padding_v
            for text, font, width, height, color in lines:
                text_x = box_x + (box_width - width) // 2
                draw.text((text_x, current_y), text, font=font, fill=color)
                current_y += height + 20  # Move to next line with spacing

        # Apply slight blur for smoothness
        img = img.filter(ImageFilter.GaussianBlur(radius=0.3))

        # Save
        output_path = self.videos_dir / "background.png"
        img.save(output_path, quality=95)
        print(f"   ✅ Background saved: {output_path.name}")

        return str(output_path)

    def create_video_with_spectrum(self, audio_file, background_image, output_name):
        """
        Create video with EQ spectrum visualization

        Args:
            audio_file: Path to instrumental audio
            background_image: Path to background image
            output_name: Output filename (without extension)

        Returns:
            Path to output video
        """
        print("\n🎬 Creating video with spectrum...")

        output_path = self.videos_dir / f"{output_name}.mp4"

        # FFmpeg filter: gradient background + highly visible EQ spectrum
        filter_complex = (
            # Scale background
            '[0:v]scale=1920:1080[bg];'

            # Create MUCH MORE VISIBLE frequency spectrum - 3-4x bigger
            '[1:a]showfreqs='
            's=1920x1200:'       # Much taller (3x from original 400px)
            'mode=line:'         # Single line mode
            'colors=white:'      # White bar
            'fscale=log:'        # Logarithmic frequency
            'ascale=sqrt:'       # Square root for better visibility
            'win_size=4096[spectrum];'  # Higher resolution

            # Scale spectrum to fit and enhance visibility
            '[spectrum]scale=1920:900[spectrum_scaled];'

            # Much stronger glow effect for maximum visibility
            '[spectrum_scaled]colorkey=0x000000:0.01:0.1[transparent];'
            '[transparent]gblur=sigma=8:steps=4[glow];'

            # Composite: background + large spectrum at bottom
            '[bg][glow]overlay=0:H-h-100:format=auto[outv]'
        )

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', background_image,
            '-i', audio_file,
            '-filter_complex', filter_complex,
            '-map', '[outv]',
            '-map', '1:a',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '20',  # Good quality
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            str(output_path)
        ]

        print("   Processing (this may take 1-2 minutes)...")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Get file size
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"   ✅ Video created: {output_path.name}")
            print(f"   💾 Size: {size_mb:.1f} MB")

            return str(output_path)

        except subprocess.CalledProcessError as e:
            print(f"   ❌ FFmpeg error: {e.stderr}")
            return None

    def process_youtube_url(self, youtube_url, artist_title=None):
        """
        Complete pipeline: YouTube → Audio → Remove Vocals → Create Video

        Args:
            youtube_url: YouTube video URL
            artist_title: Artist name (auto-detected from YouTube if not provided)

        Returns:
            Path to output video
        """
        print("\n" + "="*70)
        print("🎵 YouTube to Instrumental Video Pipeline")
        print("="*70)

        # Step 1: Download and remove vocals
        remover = YouTubeVocalRemover(output_dir=str(self.output_dir))
        instrumental_file = remover.process_youtube_url(youtube_url, model="htdemucs_ft")

        if not instrumental_file:
            print("❌ Failed to create instrumental")
            return None

        # Extract artist name from filename if not provided
        if not artist_title:
            # instrumental_file is like: "PARTYNEXTDOOR, Drake - SOMEBODY LOVES ME_instrumental.mp3"
            filename = Path(instrumental_file).stem
            # Remove "_instrumental" suffix
            if filename.endswith("_instrumental"):
                artist_title = filename[:-13]  # Remove "_instrumental"
            else:
                artist_title = filename

        print(f"\n🎨 Creating video for: {artist_title}")

        # Step 2: Apply AI audio mastering (intelligent loudness normalization)
        if self.enable_hypermaster:
            try:
                hypermastered_file = self.hypermaster.hypermaster(
                    instrumental_file,
                    target_lufs=-14.0  # Streaming platform standard
                )
                # Replace original instrumental with hypermastered version
                Path(instrumental_file).unlink(missing_ok=True)
                Path(hypermastered_file).rename(instrumental_file)
                print(f"   ✅ AI mastering applied")
            except Exception as e:
                print(f"   ⚠️  AI mastering failed, using original: {e}")

        # Step 3: Create gradient background with title
        background = self.create_gradient_background(artist_title)

        # Step 4: Create video with spectrum
        output_name = f"{artist_title.replace('/', '-')}_video"
        video_file = self.create_video_with_spectrum(
            instrumental_file,
            background,
            output_name
        )

        if video_file:
            # Clean up background PNG
            try:
                Path(background).unlink(missing_ok=True)
                print(f"   🗑️  Cleaned up background image")
            except Exception as e:
                print(f"   ⚠️  Could not delete background: {e}")

            # Step 4: Generate AI metadata
            print("\n🤖 Generating AI metadata...")
            metadata_generator = MetadataGenerator()
            metadata = metadata_generator.generate_all_metadata(artist_title)

            # Save metadata alongside video
            metadata_file = self.videos_dir / f"{artist_title.replace('/', '-')}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            print(f"   💾 Metadata saved: {metadata_file.name}")

            print("\n" + "="*70)
            print("✅ COMPLETE! Your instrumental video is ready:")
            print(f"   📁 Video: {video_file}")
            print(f"   📋 Metadata: {metadata_file}")
            print("="*70)

        return video_file


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download YouTube video, remove vocals, and create instrumental video"
    )
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument(
        "--artist",
        help="Artist name (auto-detected if not provided)"
    )
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="Output directory (default: output)"
    )

    args = parser.parse_args()

    # Create generator
    generator = InstrumentalVideoGenerator(output_dir=args.output)

    # Process
    generator.process_youtube_url(
        args.url,
        artist_title=args.artist
    )


if __name__ == "__main__":
    main()
