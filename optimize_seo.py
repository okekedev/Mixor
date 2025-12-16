#!/usr/bin/env python3
"""
Advanced SEO Optimizer for YouTube Instrumental Channels
Implements specific growth strategies: Karaoke, Type Beats, and Remixes.
"""

import json
import sys
import os
from metadata_generator import MetadataGenerator

class SEOOptimizer(MetadataGenerator):
    def __init__(self):
        super().__init__()
        self.strategies = {
            "1": "Karaoke / Sing-Along",
            "2": "Type Beat / Rapper Focus",
            "3": "Remix / Producer Focus",
            "4": "Relaxing / Mood / Lo-Fi"
        }

    def get_strategy_prompts(self, strategy_key, artist, title):
        """Return the specific prompts for the chosen strategy"""
        
        if strategy_key == "1": # Karaoke
            return {
                "title_prompt": f"""Create a viral YouTube title for a KARAOKE version of '{title}' by '{artist}'.
                - Format: Artist - Title (Karaoke Version) [Best Quality]
                - You MUST include catchy brackets like: [Original Key], [No Vocals], [Lower Key], or [Best Instrumental].
                - The goal is to make a singer click this over the 10 other versions.
                - NO quotes around the whole title.
                - Do NOT use "With Lyrics" unless specifically asked.
                - ONLY return the title string.""",
                
                "desc_prompt": f"""Write a YouTube description for a Karaoke version of '{title}' by '{artist}'.
                - Target Audience: Singers, Vocal Coaches, Choir members.
                - Paragraph 1: "Sing along to this high-quality instrumental of {title}..."
                - Paragraph 2: "Perfect for auditions, practice, or cover videos..."
                - Include: Key, BPM (if you can guess), and terms like "Backing Track", "No Vocals", "Clean Audio".
                - ONLY return the description body.""",
                
                "tags_prompt": f"""Generate 20 high-traffic YouTube tags for a Karaoke video of '{title}' by '{artist}'.
                - Include: karaoke, instrumental, backing track, cover, sing along, {artist} karaoke, {title} instrumental, lower key, higher key, vocal coach reaction, singing practice, clean audio, no vocals.
                - Comma separated.
                - ONLY return the list."""
            }
            
        elif strategy_key == "2": # Type Beat
            return {
                "title_prompt": f"""Create a viral YouTube title for a TYPE BEAT inspired by '{artist}' and the song '{title}'.
                - CRITICAL: You MUST invent/pick a similar trending artist to pair with {artist}. (e.g. if Drake, pick 21 Savage. If Taylor Swift, pick Olivia Rodrigo).
                - Format: [FREE] {artist} x [Similar Artist] Type Beat - "{title}"
                - Use tags like [HARD], [SOULFUL], [DARK] in the title.
                - NO quotes around the whole title.
                - ONLY return the title string.""",
                
                "desc_prompt": f"""Write a YouTube description for a Type Beat instrumental inspired by '{title}' by '{artist}'.
                - Target Audience: Rappers, Freestylers, Content Creators.
                - Paragraph 1: "Download this {artist} style beat for free..."
                - Paragraph 2: "Subscribe for more daily instrumentals! This is a remake/instrumental version of {title}."
                - Include keywords: type beat 2025, trap beat, hip hop instrumental.
                - DO NOT say "Free for profit" or claim ownership.
                - ONLY return the description body.""",
                
                "tags_prompt": f"""Generate 20 high-traffic YouTube tags for a Type Beat video style of '{title}' by '{artist}'.
                - Include: type beat, free type beat, {artist} type beat, rap instrumental, trap beat, free beat 2025, hip hop instrumental, freestyle beat, hard type beat.
                - Comma separated.
                - ONLY return the list."""
            }
            
        elif strategy_key == "3": # Remix
            return {
                "title_prompt": f"""Create a viral YouTube title for a REMIX / REPRODUCTION of '{title}' by '{artist}'.
                - Format: Artist - Title (Remix) [Reprod. Djokeke]
                - Use click-worthy terms in brackets: [Stems Available], [FL Studio Remake], [Acapella Included], [Bass Boosted].
                - Make it appeal to other producers or DJs.
                - NO quotes around the whole title.
                - ONLY return the title string.""",
                
                "desc_prompt": f"""Write a YouTube description for a Producer Remix/Reproduction of '{title}' by '{artist}'.
                - Target Audience: Music Producers, DJs, Sound Engineers.
                - Paragraph 1: "Deconstructed and remastered version of {title}..."
                - Paragraph 2: Mention the DAW used (FL Studio/Ableton) and sound design quality.
                - Include keywords: stems, acapella, flp, project file, instrumental, remake.
                - ONLY return the description body.""",
                
                "tags_prompt": f"""Generate 20 high-traffic YouTube tags for a Remix/Producer video of '{title}' by '{artist}'.
                - Include: remix, reproduction, remake, instrumental, music production, fl studio, ableton, {artist} remix, acapella, stems, diy acapella, vocal remover.
                - Comma separated.
                - ONLY return the list."""
            }
            
        elif strategy_key == "4": # Mood / Lo-Fi
            return {
                "title_prompt": f"""Create a viral YouTube title for a MOOD / VIBE version of '{title}' by '{artist}'.
                - Do NOT use the standard song title format.
                - Format: "feeling/activity to {title} (Slowed + Reverb)"
                - Examples: "driving at 3am to {title}", "studying in the rain to {title}", "pov: you're the main character listening to {title}".
                - NO quotes around the whole title.
                - ONLY return the title string.""",
                
                "desc_prompt": f"""Write a YouTube description for a Mood/Vibe version (Instrumental) of '{title}' by '{artist}'.
                - Target Audience: Students, Insomniacs, Drivers, Gamers.
                - Paragraph 1: Set the scene (rainy window, late night, nostalgia).
                - Paragraph 2: "Slowed and reverb remix perfect for studying, sleeping, or relaxing."
                - Include keywords: lo-fi, aesthetic, slowed + reverb, chill, ambience.
                - ONLY return the description body.""",
                
                "tags_prompt": f"""Generate 20 high-traffic YouTube tags for a Mood/Vibe video of '{title}' by '{artist}'.
                - Include: lo-fi, chill, relaxing, study music, sleep music, slowed and reverb, aesthetic, {title} instrumental, 3am vibes, sad songs, nostalgia.
                - Comma separated.
                - ONLY return the list."""
            }
        
        return None

    def generate_optimized_metadata(self, strategy_key, artist, title):
        prompts = self.get_strategy_prompts(strategy_key, artist, title)
        if not prompts:
            print("Invalid strategy.")
            return None

        print(f"\n🧠 Generating Optimized Metadata using Strategy: {self.strategies[strategy_key]}...")

        # Generate Title
        print("   ...thinking of a click-worthy title")
        seo_title_raw = self._call_llm(prompts["title_prompt"])
        
        # Clean title: take first non-empty line, remove quotes
        seo_title_lines = [line.strip() for line in seo_title_raw.split('\n') if line.strip()]
        if seo_title_lines:
            seo_title = seo_title_lines[0].strip('"\'')
        else:
            seo_title = f"{artist} - {title}" # Fallback
        
        # Generate Description
        print("   ...writing an SEO-rich description")
        seo_desc = self._call_llm(prompts["desc_prompt"])
        
        # Generate Tags
        print("   ...selecting viral tags")
        seo_tags_str = self._call_llm(prompts["tags_prompt"])
        
        # Clean tags
        tags = [t.strip() for t in seo_tags_str.split(',')]
        tags = [t for t in tags if t] # remove empty

        return {
            "title": seo_title,
            "description": seo_desc,
            "tags": tags,
            "artist": artist,
            "song_title": title,
            "strategy": self.strategies[strategy_key]
        }

    def recommend_strategy(self, artist, title):
        """
        Ask LLM to recommend the best growth strategy based on Artist/Title.
        Returns the strategy key ('1', '2', '3', or '4').
        """
        system_prompt = """You are a music marketing expert. 
        Analyze the Artist and Song Title and pick the BEST YouTube growth strategy.
        
        Strategies:
        1 = Karaoke/Sing-Along (Best for: Pop, Ballads, Disney, Musical Theatre, Famous Vocal Songs)
        2 = Type Beat/Rapper (Best for: Hip Hop, Trap, Rap, Drill, R&B)
        3 = Remix/Producer (Best for: EDM, House, Techno, Dubstep, Experimental)
        4 = Mood/Lo-Fi (Best for: Chill, Study, Ambient, Slowed+Reverb, Oldies)

        Reply ONLY with the number (1, 2, 3, or 4)."""

        prompt = f"Artist: {artist}\nTitle: {title}\n\nWhich strategy number fits best?"
        
        result = self._call_llm(prompt, system_prompt).strip()
        
        # Extract just the number if the LLM is chatty
        import re
        match = re.search(r'[1-4]', result)
        if match:
            return match.group(0)
        
        return '2' # Default to Type Beat if unsure

def main():
    print("\n🚀 YOUTUBE SEO OPTIMIZER 2025 🚀")
    print("===================================")
    
    artist = input("Enter Artist Name: ").strip()
    title = input("Enter Song Title: ").strip()
    
    print("\nChoose your Growth Strategy:")
    print("1. 🎤 Karaoke / Sing-Along (Target: Singers)")
    print("2. 🎹 Type Beat / Rapper (Target: Rappers/Freestyle)")
    print("3. 🎧 Remix / Producer (Target: Music Heads)")
    print("4. 🌌 Mood / Lo-Fi (Target: Study/Sleep/Drive)")
    
    strategy = input("\nSelect Strategy (1-4): ").strip()
    
    if strategy not in ['1', '2', '3', '4']:
        print("Invalid selection. Defaulting to Type Beat (2).")
        strategy = '2'

    optimizer = SEOOptimizer()
    metadata = optimizer.generate_optimized_metadata(strategy, artist, title)
    
    if metadata:
        print("\n" + "="*60)
        print("✨ FINAL OPTIMIZED METADATA ✨")
        print("="*60)
        print(f"\n📺 TITLE:\n{metadata['title']}")
        print(f"\n📝 DESCRIPTION:\n{metadata['description']}")
        print(f"\n🏷️  TAGS:\n{', '.join(metadata['tags'])}")
        print("="*60)
        
        save = input("\n💾 Save to metadata.json for upload? (y/n): ").lower()
        if save == 'y':
            with open('metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            print("✅ Saved! You can now run youtube_uploader.py")

if __name__ == "__main__":
    main()
