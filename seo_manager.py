
import re
import sys
from youtube_uploader import YouTubeUploader
from optimize_seo import SEOOptimizer

def parse_title(video_title):
    # Expected format: Artist - Title (Instrumental Remaster)
    # Or just: Artist - Title
    
    # Remove (Instrumental Remaster) suffix if present
    clean_title = re.sub(r'\s*\(Instrumental Remaster\).*$', '', video_title, flags=re.IGNORECASE)
    
    # Split by " - "
    parts = clean_title.split(' - ')
    if len(parts) >= 2:
        artist = parts[0].strip()
        title = ' - '.join(parts[1:]).strip() # Join rest in case title has dashes
        return artist, title
    
    return None, None

def main():
    uploader = YouTubeUploader()
    optimizer = SEOOptimizer()

    print("\nFetching videos...")
    videos = uploader.get_channel_videos()
    
    if not videos:
        print("No videos found.")
        return

    print(f"\nFound {len(videos)} videos. Showing top 10:")
    for i, video in enumerate(videos[:10]):
        print(f"{i+1}. {video['title']}")

    print("\nEnter the numbers of the videos you want to optimize (comma separated, e.g. '1, 3'):")
    selection = input("> ").strip()
    
    if not selection:
        print("No selection made. Exiting.")
        return

    try:
        indices = [int(x.strip()) - 1 for x in selection.split(',')]
    except ValueError:
        print("Invalid input. Please enter numbers only.")
        return

    for idx in indices:
        if idx < 0 or idx >= len(videos):
            print(f"Skipping invalid index {idx+1}")
            continue
            
        video = videos[idx]
        print(f"\n" + "="*50)
        print(f"Processing: {video['title']}")
        print("="*50)

        # Parse Artist/Title
        artist, song_title = parse_title(video['title'])
        
        if not artist:
            print(f"Could not parse Artist - Title from '{video['title']}'")
            artist = input("Enter Artist: ").strip()
            song_title = input("Enter Song Title: ").strip()
        else:
            print(f"Detected Artist: {artist}")
            print(f"Detected Title:  {song_title}")
            confirm = input("Is this correct? (y/n): ").lower()
            if confirm != 'y':
                artist = input("Enter Artist: ").strip()
                song_title = input("Enter Song Title: ").strip()

        # Strategy selection
        print("\nSelect Growth Strategy:")
        print("1. Karaoke / Sing-Along")
        print("2. Type Beat / Rapper")
        print("3. Remix / Producer")
        print("4. Mood / Lo-Fi")
        print("A. Auto-detect (Recommended)")
        
        strat = input("Choice (1-4, A): ").strip().upper()
        
        if strat == 'A' or strat == '':
            print("🧠 Auto-detecting best strategy...")
            strat = optimizer.recommend_strategy(artist, song_title)
            print(f"   Selected Strategy: {strat}")
        
        if strat not in ['1', '2', '3', '4']:
            strat = '2' # Default

        # Generate Metadata
        metadata = optimizer.generate_optimized_metadata(strat, artist, song_title)
        
        if not metadata:
            print("Failed to generate metadata.")
            continue

        print("\n" + "-"*30)
        print("GENERATED METADATA PREVIEW")
        print("-"*30)
        print(f"TITLE: {metadata['title']}")
        print(f"TAGS: {', '.join(metadata['tags'][:5])}...")
        print("-"*30)

        apply = input("Apply this update to YouTube? (y/n): ").lower()
        if apply == 'y':
            success = uploader.update_video_metadata(video['id'], metadata)
            if success:
                print("✅ Update successful!")
            else:
                print("❌ Update failed.")
        else:
            print("Skipped update.")

if __name__ == "__main__":
    main()
