#!/usr/bin/env python3
"""
AI-Powered Metadata Generator for YouTube Instrumental Videos
Generates natural, SEO-friendly titles, descriptions, and tags using local LLM
"""

import json
import re
from typing import Dict, List
import requests


class MetadataGenerator:
    def __init__(self, model="llama3.2:3b", ollama_url="http://localhost:11434"):
        """
        Initialize metadata generator

        Args:
            model: Ollama model to use
            ollama_url: URL for Ollama API
        """
        self.model = model
        self.ollama_url = ollama_url

    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Call Ollama LLM with a prompt"""
        url = f"{self.ollama_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            print(f"❌ Error calling LLM: {e}")
            return ""

    def extract_artist_and_title(self, filename: str) -> Dict[str, str]:
        """
        Extract artist and title from filename

        Args:
            filename: e.g., "Artist - Song Title (Official Music Video)"

        Returns:
            Dict with 'artist' and 'title' keys
        """
        # Remove common suffixes (more comprehensive list)
        clean_name = filename
        suffixes_to_remove = [
            " (Official Music Video)", " (Official Video)", " (Official Audio)",
            " (Lyric Video)", " (Lyrics)", " (Audio)", " (Music Video)",
            " [Official Video]", " [Official Music Video]", " [Official Audio]",
            " [Lyric Video]", " [Music Video]",
            "_instrumental", ".mp3", ".mp4", ".wav"
        ]

        for suffix in suffixes_to_remove:
            clean_name = clean_name.replace(suffix, "")

        # Remove any remaining parenthetical content that looks like video labels
        clean_name = re.sub(r'\s*[\(\[](?:official|lyric|music|audio|video).*?[\)\]]', '', clean_name, flags=re.IGNORECASE)

        # Try to split on " - "
        if " - " in clean_name:
            parts = clean_name.split(" - ", 1)
            return {
                "artist": parts[0].strip(),
                "title": parts[1].strip()
            }

        # If no dash, assume it's just a title
        return {
            "artist": "",
            "title": clean_name.strip()
        }

    def generate_youtube_title(self, artist: str, title: str) -> str:
        """
        Generate SEO-friendly YouTube title

        Args:
            artist: Artist name
            title: Song title

        Returns:
            Natural, engaging title
        """
        system_prompt = """You are a YouTube content specialist who creates engaging, natural video titles.
Your titles should be:
- SEO-friendly but not keyword-stuffed
- Natural and appealing to humans
- Include "Instrumental Remaster" clearly
- Maximum 100 characters
- Follow format: Artist - Title (Instrumental Remaster)
- Do NOT include video descriptors like "Official Video", "Music Video", etc."""

        prompt = f"""Create a YouTube video title for an instrumental remaster version of a song.

Artist: {artist}
Song Title: {title}

Generate ONLY the title, nothing else. Make it natural and appealing.
Format: Artist - Title (Instrumental Remaster)"""

        result = self._call_llm(prompt, system_prompt)

        # Fallback if LLM fails
        if not result:
            return f"{artist} - {title} (Instrumental Remaster)"

        # Clean up any extra formatting
        result = result.strip('"\'')
        return result

    def generate_description(self, artist: str, title: str) -> str:
        """
        Generate natural, SEO-friendly YouTube description

        Args:
            artist: Artist name
            title: Song title

        Returns:
            Engaging description with natural keyword integration
        """
        system_prompt = """You are a YouTube content writer who creates direct, practical video descriptions.
Your descriptions should be:
- Exactly 2 short, concise paragraphs
- Direct and factual (not flowery or poetic)
- Include relevant keywords naturally
- Professional but straightforward
- No promotional language, no poetic descriptions, no flowery phrases
- No mentions of: film scoring, advertising, commercial uses, yoga, meditation, serenity, ambiance"""

        prompt = f"""Write a direct, practical YouTube video description for an instrumental remaster of a song.

Artist: {artist}
Song Title: {title}

Write exactly 2 short paragraphs:
1. First paragraph (1-2 sentences): State what this is - an instrumental remaster of the song with AI-powered audio enhancement
2. Second paragraph (1-2 sentences): List practical uses - background music for work/study, or karaoke practice

Keep it simple and factual. No flowery language about feelings, moods, or atmosphere.

Write ONLY the description, nothing else."""

        result = self._call_llm(prompt, system_prompt)

        # Fallback if LLM fails
        if not result:
            return f"""Instrumental remaster of "{title}" by {artist}.

This high-quality instrumental remaster removes the vocals while preserving the original music with AI-powered audio enhancement, making it perfect for karaoke, music production, or simply enjoying the instrumental arrangement.

Perfect as background music for studying, working, or creative projects."""

        return result

    def generate_tags(self, artist: str, title: str) -> List[str]:
        """
        Generate relevant YouTube tags

        Args:
            artist: Artist name
            title: Song title

        Returns:
            List of 10-15 relevant tags
        """
        system_prompt = """You are a YouTube SEO specialist who generates relevant tags.
Your tags should be:
- 10-15 tags total
- Mix of specific and general terms
- Include: artist name, song title, "instrumental", genre terms
- Natural and relevant (not spam)
- Comma-separated list"""

        prompt = f"""Generate YouTube tags for an instrumental version of a song.

Artist: {artist}
Song Title: {title}

Generate 10-15 relevant tags. Output ONLY a comma-separated list, nothing else."""

        result = self._call_llm(prompt, system_prompt)

        # Parse tags
        if result:
            tags = [tag.strip() for tag in result.split(",")]
            # Clean up tags
            tags = [re.sub(r'[^a-zA-Z0-9\s-]', '', tag) for tag in tags]
            tags = [tag for tag in tags if tag]  # Remove empty
            return tags[:15]  # Limit to 15

        # Fallback tags
        return [
            f"{artist}",
            f"{title}",
            "instrumental",
            "karaoke",
            "no vocals",
            "background music",
            "instrumental version",
            "music without vocals",
            "instrumental track",
            "backing track"
        ]

    def generate_all_metadata(self, filename: str) -> Dict[str, any]:
        """
        Generate all metadata for a video

        Args:
            filename: Video filename (e.g., "Artist - Title (Official Music Video)")

        Returns:
            Dict containing title, description, and tags
        """
        print(f"\n🤖 Generating metadata for: {filename}")

        # Extract artist and title
        info = self.extract_artist_and_title(filename)
        artist = info["artist"]
        title = info["title"]

        print(f"   Artist: {artist}")
        print(f"   Title: {title}")

        # Generate metadata
        print("\n   🏷️  Generating title...")
        youtube_title = self.generate_youtube_title(artist, title)

        print("   📝 Generating description...")
        description = self.generate_description(artist, title)

        print("   🔖 Generating tags...")
        tags = self.generate_tags(artist, title)

        metadata = {
            "title": youtube_title,
            "description": description,
            "tags": tags,
            "artist": artist,
            "song_title": title
        }

        print("\n✅ Metadata generated:")
        print(f"   Title: {metadata['title']}")
        print(f"   Tags: {len(metadata['tags'])} tags")
        print(f"   Description: {len(metadata['description'])} characters")

        return metadata


def main():
    """Test metadata generation"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python metadata_generator.py <filename>")
        print("Example: python metadata_generator.py 'Elderbrook - Inner Light with Bob Moses (Official Music Video)'")
        sys.exit(1)

    filename = sys.argv[1]

    generator = MetadataGenerator()
    metadata = generator.generate_all_metadata(filename)

    # Pretty print
    print("\n" + "="*70)
    print("GENERATED METADATA")
    print("="*70)
    print(f"\nTitle:\n{metadata['title']}\n")
    print(f"Description:\n{metadata['description']}\n")
    print(f"Tags:\n{', '.join(metadata['tags'])}\n")
    print("="*70)

    # Save to JSON
    output_file = "metadata.json"
    with open(output_file, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"\n💾 Saved to {output_file}")


if __name__ == "__main__":
    main()
