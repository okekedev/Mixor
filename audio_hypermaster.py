#!/usr/bin/env python3
"""
HyperMaster - Professional AI Audio Mastering
Enhances instrumental tracks with reverb, EQ, compression, and stereo widening
Uses Spotify's Pedalboard - Optimized for M4 Mac - November 2025
"""

from pathlib import Path
from pedalboard import (
    Pedalboard, Compressor, Gain, Reverb, 
    HighShelfFilter, LowShelfFilter, PeakFilter,
    Limiter, Chorus
)
from pedalboard.io import AudioFile
import numpy as np


class AudioHyperMaster:
    def __init__(self):
        """Initialize HyperMaster audio processor"""
        print("🎛️  HyperMaster initialized (Pedalboard - M4 optimized)")
        
    def create_mastering_chain(self, intensity="medium"):
        """
        Create professional mastering pedalboard chain
        
        Args:
            intensity: "light", "medium", "heavy"
        
        Returns:
            Pedalboard processing chain
        """
        # Intensity presets
        presets = {
            "light": {
                "reverb_room": 0.15,
                "reverb_wet": 0.08,
                "chorus_depth": 0.15,
                "low_shelf_gain": 1.5,
                "high_shelf_gain": 2.0,
                "compression_ratio": 2.0,
                "compression_threshold": -18
            },
            "medium": {
                "reverb_room": 0.25,
                "reverb_wet": 0.12,
                "chorus_depth": 0.25,
                "low_shelf_gain": 2.5,
                "high_shelf_gain": 3.0,
                "compression_ratio": 3.0,
                "compression_threshold": -20
            },
            "heavy": {
                "reverb_room": 0.35,
                "reverb_wet": 0.18,
                "chorus_depth": 0.35,
                "low_shelf_gain": 3.5,
                "high_shelf_gain": 4.0,
                "compression_ratio": 4.0,
                "compression_threshold": -22
            }
        }
        
        settings = presets.get(intensity, presets["medium"])
        
        # Build professional mastering chain
        board = Pedalboard([
            # 1. EQ - Enhance frequency spectrum
            LowShelfFilter(
                cutoff_frequency_hz=80, 
                gain_db=settings["low_shelf_gain"],  # Boost bass
                q=0.7
            ),
            PeakFilter(
                cutoff_frequency_hz=400,
                gain_db=-1.5,  # Slight mid scoop for clarity
                q=1.0
            ),
            PeakFilter(
                cutoff_frequency_hz=3000,
                gain_db=2.0,  # Boost presence
                q=1.5
            ),
            HighShelfFilter(
                cutoff_frequency_hz=8000,
                gain_db=settings["high_shelf_gain"],  # Boost highs for air
                q=0.7
            ),
            
            # 2. Stereo widening via subtle chorus
            Chorus(
                rate_hz=0.5,
                depth=settings["chorus_depth"],
                centre_delay_ms=7,
                feedback=0.0,
                mix=0.3  # Subtle stereo enhancement
            ),
            
            # 3. Reverb - Add space and depth
            Reverb(
                room_size=settings["reverb_room"],
                damping=0.5,
                wet_level=settings["reverb_wet"],
                dry_level=1.0 - settings["reverb_wet"],
                width=1.0,
                freeze_mode=0.0
            ),
            
            # 4. Compression - Glue everything together
            Compressor(
                threshold_db=settings["compression_threshold"],
                ratio=settings["compression_ratio"],
                attack_ms=10.0,
                release_ms=100.0
            ),
            
            # 5. Make-up gain
            Gain(gain_db=3.0),
            
            # 6. Final limiter - Prevent clipping
            Limiter(
                threshold_db=-1.0,
                release_ms=50.0
            )
        ])
        
        return board
    
    def hypermaster(self, input_file, output_file=None, intensity="medium"):
        """
        Apply full HyperMaster processing chain
        
        Args:
            input_file: Path to input audio
            output_file: Path to output (defaults to input_hypermastered.mp3)
            intensity: "light", "medium", "heavy"
        
        Returns:
            Path to mastered file
        """
        print("\n" + "="*70)
        print("🎛️  HyperMaster - Professional Audio Enhancement")
        print("="*70)
        
        input_path = Path(input_file)
        
        if output_file is None:
            output_file = input_path.parent / f"{input_path.stem}_hypermastered.mp3"
        else:
            output_file = Path(output_file)
        
        print(f"\n📁 Input: {input_path.name}")
        print(f"🎚️  Intensity: {intensity.upper()}")
        
        # Create mastering chain
        print("\n⚙️  Building mastering chain...")
        board = self.create_mastering_chain(intensity)
        
        print("   ✓ EQ (Low/Mid/High shelf filters)")
        print("   ✓ Stereo widening (Chorus)")
        print("   ✓ Reverb (Room ambience)")
        print("   ✓ Compression (Dynamic control)")
        print("   ✓ Limiter (Peak protection)")
        
        # Process audio
        print(f"\n🎵 Processing audio...")
        
        with AudioFile(str(input_file)) as f:
            sample_rate = f.samplerate
            audio = f.read(f.frames)
            
            print(f"   Sample rate: {sample_rate} Hz")
            print(f"   Channels: {audio.shape[0]}")
            print(f"   Duration: {audio.shape[1] / sample_rate:.1f}s")
        
        # Apply mastering
        print("\n✨ Applying HyperMaster processing...")
        mastered_audio = board(audio, sample_rate)
        
        # Save output
        print(f"\n💾 Saving HyperMastered audio...")
        
        with AudioFile(str(output_file), 'w', sample_rate, mastered_audio.shape[0]) as f:
            f.write(mastered_audio)
        
        file_size = output_file.stat().st_size / (1024 * 1024)
        
        print("\n" + "="*70)
        print(f"✅ HyperMaster Complete!")
        print(f"   📁 Output: {output_file.name}")
        print(f"   💾 Size: {file_size:.1f} MB")
        print(f"   🎚️  Processing: {intensity.upper()}")
        print("   🎧 Enhanced with: Reverb + EQ + Compression + Stereo Width")
        print("="*70)
        
        return str(output_file)


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="HyperMaster - Professional audio mastering with Pedalboard"
    )
    parser.add_argument("input", help="Input audio file")
    parser.add_argument(
        "--output", "-o",
        help="Output file (default: input_hypermastered.mp3)"
    )
    parser.add_argument(
        "--intensity", "-i",
        choices=["light", "medium", "heavy"],
        default="medium",
        help="Processing intensity (default: medium)"
    )
    
    args = parser.parse_args()
    
    master = AudioHyperMaster()
    master.hypermaster(args.input, args.output, args.intensity)


if __name__ == "__main__":
    main()
