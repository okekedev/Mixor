#!/usr/bin/env python3
"""
Test script for YouTube Vocal Remover
Automatically accepts disclaimer for testing
"""

import sys
import os

# Add auto-accept for testing
sys.argv = [
    'youtube_vocal_remover.py',
    'https://www.youtube.com/watch?v=Tz6OUIjtM6E'
    # htdemucs_ft is now the default, no need to specify
]

# Mock the input to auto-accept disclaimer
import builtins
real_input = builtins.input
def mock_input(prompt):
    print(prompt)
    if "Do you accept" in prompt:
        print("yes (auto-accepted for testing)")
        return "yes"
    return real_input(prompt)
builtins.input = mock_input

# Import and run the main script
from youtube_vocal_remover import main

if __name__ == "__main__":
    print("🧪 Testing YouTube Vocal Remover")
    print("=" * 60)
    print(f"URL: {sys.argv[1]}")
    print("Model: htdemucs_ft (best quality - default)")
    print("=" * 60)

    main()