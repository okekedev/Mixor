#!/usr/bin/env python3
"""
Flask Web App for YouTube to Instrumental Video Pipeline
Simple, modern interface for processing videos
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import threading
import uuid
import json
from youtube_to_instrumental_video import InstrumentalVideoGenerator
from youtube_uploader import YouTubeUploader
from metadata_generator import MetadataGenerator
from optimize_seo import SEOOptimizer

app = Flask(__name__)
CORS(app)

# Store job status
jobs = {}

class ProcessingJob:
    def __init__(self, job_id, urls, upload_to_youtube, save_locally, create_playlist, playlist_name, add_to_playlist, existing_playlist_id=None):
        self.job_id = job_id
        self.urls = urls
        self.upload_to_youtube = upload_to_youtube
        self.save_locally = save_locally
        self.create_playlist = create_playlist
        self.playlist_name = playlist_name
        self.add_to_playlist = add_to_playlist
        self.existing_playlist_id = existing_playlist_id
        self.status = 'queued'
        self.progress = 0
        self.current_video = 0
        self.total_videos = len(urls)
        self.message = 'Queued'
        self.results = []
        self.error = None
        self.playlist_id = None
        self.playlist_url = None

def process_videos(job):
    """Process videos in background thread"""
    try:
        job.status = 'processing'
        generator = InstrumentalVideoGenerator()

        # Initialize uploader if needed
        uploader = None
        if job.upload_to_youtube or job.create_playlist:
            try:
                uploader = YouTubeUploader()
            except Exception as e:
                job.error = f"YouTube auth failed: {str(e)}"
                job.status = 'failed'
                return

        # Create playlist if requested, or use existing
        if job.existing_playlist_id:
            # Use existing playlist from dropdown
            job.playlist_id = job.existing_playlist_id
        elif job.create_playlist and job.playlist_name and uploader:
            # Create new playlist with AI-generated description
            job.message = 'Generating playlist description...'
            metadata_gen = MetadataGenerator()
            playlist_description = metadata_gen.generate_playlist_description(job.playlist_name)

            job.message = 'Creating playlist...'
            playlist_id = uploader.create_playlist(
                title=job.playlist_name,
                description=playlist_description,
                privacy_status='public'
            )
            if playlist_id:
                job.playlist_id = playlist_id
                job.playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            else:
                job.error = "Failed to create playlist"
                job.status = 'failed'
                return

        # Process each video
        for i, url in enumerate(job.urls):
            job.current_video = i + 1
            job.message = f'Processing video {i+1}/{job.total_videos}'
            job.progress = int((i / job.total_videos) * 80)  # 0-80% for processing

            try:
                # Run the pipeline
                job.message = f'Downloading and separating vocals ({i+1}/{job.total_videos})'
                video_file_str = generator.process_youtube_url(url)

                if not video_file_str:
                    job.results.append({
                        'url': url,
                        'status': 'failed',
                        'error': 'Processing failed'
                    })
                    continue

                # Convert to Path object for easier manipulation
                video_file = Path(video_file_str)

                result = {
                    'url': url,
                    'status': 'completed',
                    'video_file': str(video_file)
                }

                # Upload to YouTube if requested
                if job.upload_to_youtube and uploader:
                    job.message = f'Uploading to YouTube ({i+1}/{job.total_videos})'

                    # Find metadata file
                    video_name = video_file.stem.replace('_video', '')
                    metadata_file = video_file.parent / f"{video_name}_metadata.json"

                    if metadata_file.exists():
                        video_id = uploader.upload_from_metadata_file(
                            video_file,
                            metadata_file,
                            privacy_status='public'
                        )

                        if video_id:
                            result['youtube_url'] = f"https://www.youtube.com/watch?v={video_id}"
                            result['youtube_id'] = video_id

                            # Add to playlist if requested
                            if job.add_to_playlist and job.playlist_id:
                                if uploader.add_video_to_playlist(job.playlist_id, video_id):
                                    result['added_to_playlist'] = True
                                else:
                                    result['playlist_add_error'] = 'Failed to add to playlist'
                        else:
                            result['upload_error'] = 'Upload failed'

                # Clean up files if save_locally is False
                if not job.save_locally:
                    try:
                        # Delete video file
                        video_file.unlink(missing_ok=True)

                        # Delete metadata file
                        video_name = video_file.stem.replace('_video', '')
                        metadata_file = video_file.parent / f"{video_name}_metadata.json"
                        metadata_file.unlink(missing_ok=True)

                        # Delete instrumental and acapella files
                        instrumental_file = video_file.parent.parent / "instrumentals" / f"{video_name}.mp3"
                        acapella_file = video_file.parent.parent / "acapellas" / f"{video_name}.mp3"
                        instrumental_file.unlink(missing_ok=True)
                        acapella_file.unlink(missing_ok=True)

                        result['files_deleted'] = True
                    except Exception as e:
                        print(f"Warning: Could not delete files: {e}")

                job.results.append(result)

            except Exception as e:
                job.results.append({
                    'url': url,
                    'status': 'failed',
                    'error': str(e)
                })

        # Final progress
        job.progress = 100
        job.status = 'completed'
        job.message = f'Completed {len([r for r in job.results if r["status"] == "completed"])}/{job.total_videos} videos'

    except Exception as e:
        job.status = 'failed'
        job.error = str(e)
        job.message = f'Failed: {str(e)}'


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/process', methods=['POST'])
def process():
    """Start processing videos"""
    import re
    import yt_dlp

    data = request.json

    # Parse URLs (playlist or individual videos)
    urls = []

    # If playlist URL is provided, extract all video URLs from it
    if data.get('playlist_url'):
        playlist_url = data['playlist_url'].strip()
        print(f"\n📋 Processing playlist URL: {playlist_url}")

        # Extract playlist ID if present in URL
        playlist_id_match = re.search(r'[?&]list=([^&]+)', playlist_url)

        if playlist_id_match:
            # Convert to pure playlist URL for proper extraction
            playlist_id = playlist_id_match.group(1)
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            print(f"   Detected playlist ID: {playlist_id}")

        try:
            # Extract all video URLs from playlist
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,  # Don't download, just extract info
                'no_warnings': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                if 'entries' in info:
                    # It's a playlist
                    print(f"   Found {len(info['entries'])} videos in playlist")
                    for entry in info['entries']:
                        if entry:
                            video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                            urls.append(video_url)
                            print(f"   Added: {video_url}")
                else:
                    # It's a single video
                    print(f"   Single video detected")
                    urls.append(playlist_url)
            print(f"✅ Total URLs extracted: {len(urls)}")
        except Exception as e:
            print(f"❌ Error extracting playlist: {e}")
            # Fallback to treating it as a single URL
            urls.append(data.get('playlist_url').strip())

    # Individual video URLs - strip playlist parameters to get only the specific video
    if data.get('video_urls'):
        print(f"\n📺 Processing individual video URLs")
        for video_url in data['video_urls']:
            video_url = video_url.strip()
            if not video_url:
                continue

            # If URL contains a playlist parameter, remove it to get only the specific video
            if '&list=' in video_url or '?list=' in video_url:
                # Extract just the video ID
                video_id_match = re.search(r'[?&]v=([^&]+)', video_url)
                if video_id_match:
                    video_id = video_id_match.group(1)
                    clean_url = f"https://www.youtube.com/watch?v={video_id}"
                    print(f"   Stripped playlist from URL: {clean_url}")
                    urls.append(clean_url)
                else:
                    urls.append(video_url)
            else:
                urls.append(video_url)
        print(f"✅ Added {len(urls)} individual video(s)")

    if not urls:
        return jsonify({'error': 'No URLs provided'}), 400

    # Create job
    job_id = str(uuid.uuid4())
    job = ProcessingJob(
        job_id=job_id,
        urls=urls,
        upload_to_youtube=data.get('upload_to_youtube', False),
        save_locally=data.get('save_locally', True),
        create_playlist=data.get('create_playlist', False),
        playlist_name=data.get('playlist_name', ''),
        add_to_playlist=data.get('add_to_playlist', False),
        existing_playlist_id=data.get('existing_playlist_id', None)
    )

    jobs[job_id] = job

    # Start processing in background
    thread = threading.Thread(target=process_videos, args=(job,))
    thread.daemon = True
    thread.start()

    return jsonify({
        'job_id': job_id,
        'message': 'Processing started'
    })


@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get job status"""
    job = jobs.get(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify({
        'status': job.status,
        'progress': job.progress,
        'message': job.message,
        'current_video': job.current_video,
        'total_videos': job.total_videos,
        'results': job.results,
        'error': job.error,
        'playlist_id': job.playlist_id,
        'playlist_url': job.playlist_url
    })


@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    return jsonify([{
        'job_id': job_id,
        'status': job.status,
        'progress': job.progress,
        'total_videos': job.total_videos
    } for job_id, job in jobs.items()])


@app.route('/api/playlists', methods=['GET'])
def get_playlists():
    """Get user's YouTube playlists"""
    try:
        uploader = YouTubeUploader()
        playlists = uploader.get_user_playlists()
        return jsonify({'playlists': playlists})
    except Exception as e:
        print(f"\n❌ Error fetching playlists: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/playlist/<playlist_id>/videos', methods=['GET'])
def get_playlist_videos(playlist_id):
    """Get videos in a specific playlist"""
    try:
        uploader = YouTubeUploader()
        videos = uploader.get_playlist_videos(playlist_id)
        return jsonify({'videos': videos})
    except Exception as e:
        print(f"\n❌ Error fetching playlist videos: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/channel/videos', methods=['GET'])
def get_channel_videos():
    """Get user's uploaded videos"""
    try:
        uploader = YouTubeUploader()
        videos = uploader.get_channel_videos()
        return jsonify({'videos': videos})
    except Exception as e:
        print(f"\n❌ Error fetching channel videos: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/playlist/create', methods=['POST'])
def create_new_playlist():
    """Create a new playlist"""
    data = request.json
    try:
        uploader = YouTubeUploader()
        playlist_id = uploader.create_playlist(
            title=data.get('title'),
            description=data.get('description', ''),
            privacy_status=data.get('privacy_status', 'public')
        )
        if playlist_id:
            return jsonify({
                'success': True,
                'playlist_id': playlist_id,
                'playlist_url': f"https://www.youtube.com/playlist?list={playlist_id}"
            })
        else:
            return jsonify({'error': 'Failed to create playlist'}), 500
    except Exception as e:
        print(f"\n❌ Error creating playlist: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/playlist/<playlist_id>/add', methods=['POST'])
def add_to_existing_playlist(playlist_id):
    """Add a video to an existing playlist"""
    data = request.json
    try:
        uploader = YouTubeUploader()
        success = uploader.add_video_to_playlist(playlist_id, data.get('video_id'))
        return jsonify({'success': success})
    except Exception as e:
        print(f"\n❌ Error adding video to playlist: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/playlist/<playlist_id>/remove/<video_id>', methods=['DELETE'])
def remove_from_playlist(playlist_id, video_id):
    """Remove a video from a playlist"""
    try:
        uploader = YouTubeUploader()
        success = uploader.remove_video_from_playlist(playlist_id, video_id)
        return jsonify({'success': success})
    except Exception as e:
        print(f"\n❌ Error removing video from playlist: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/<video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Delete a video from YouTube"""
    try:
        uploader = YouTubeUploader()
        success = uploader.delete_video(video_id)
        return jsonify({'success': success})
    except Exception as e:
        print(f"\n❌ Error deleting video: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload a video directly to YouTube with AI-generated metadata"""
    from werkzeug.utils import secure_filename
    from metadata_generator import MetadataGenerator
    import tempfile
    import shutil

    try:
        # Get uploaded file
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400

        video_file = request.files['video']
        title = request.form.get('title', '').strip()
        brief_description = request.form.get('brief_description', '').strip()
        playlist_id = request.form.get('playlist_id', '').strip()

        if not video_file or video_file.filename == '':
            return jsonify({'error': 'No video file selected'}), 400

        if not title or not brief_description:
            return jsonify({'error': 'Title and description are required'}), 400

        # Save uploaded file temporarily
        filename = secure_filename(video_file.filename)
        temp_dir = Path(tempfile.mkdtemp())
        video_path = temp_dir / filename
        video_file.save(str(video_path))

        print(f"\n📁 Received video upload: {filename}")
        print(f"   Title: {title}")
        print(f"   Brief description: {brief_description[:50]}...")

        # Generate metadata using AI
        print("\n🤖 Generating AI metadata...")
        generator = MetadataGenerator()
        metadata = generator.generate_metadata_from_custom(title, brief_description)

        # Upload to YouTube
        print("\n📤 Uploading to YouTube...")
        uploader = YouTubeUploader()
        video_id = uploader.upload_video(
            video_path,
            metadata,
            privacy_status='public'
        )

        # Clean up temp file
        shutil.rmtree(temp_dir)

        if video_id:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"\n✅ Upload successful!")
            print(f"   Video ID: {video_id}")
            print(f"   URL: {youtube_url}")

            # Add to playlist if requested
            added_to_playlist = False
            if playlist_id:
                print(f"\n📋 Adding to playlist {playlist_id}...")
                added_to_playlist = uploader.add_video_to_playlist(playlist_id, video_id)

            return jsonify({
                'success': True,
                'video_id': video_id,
                'youtube_url': youtube_url,
                'metadata': metadata,
                'added_to_playlist': added_to_playlist
            })
        else:
            return jsonify({'error': 'Upload to YouTube failed'}), 500

    except Exception as e:
        print(f"\n❌ Upload error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/local-videos', methods=['GET'])
def list_local_videos():
    """List processed videos in output directory"""
    try:
        video_dir = Path(__file__).parent / "output" / "videos"
        if not video_dir.exists():
            print(f"Video dir not found: {video_dir}")
            return jsonify({'videos': []})
            
        videos = [f.name for f in video_dir.glob("*.mp4")]
        return jsonify({'videos': sorted(videos)})
    except Exception as e:
        print(f"Error listing local videos: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/optimize-seo', methods=['POST'])
def optimize_seo():
    """Generate optimized SEO metadata"""
    data = request.json
    
    # Handle filename input (auto-extraction)
    filename = data.get('filename')
    artist = data.get('artist')
    title = data.get('title')
    strategy = data.get('strategy')
    auto_strategy = data.get('auto_strategy', False)

    try:
        optimizer = SEOOptimizer()

        # If filename provided, extract artist/title
        if filename:
            info = optimizer.extract_artist_and_title(filename)
            artist = info['artist']
            title = info['title']

        if not artist or not title:
            return jsonify({'error': 'Could not determine Artist and Title'}), 400

        # If auto-strategy requested (or none provided), ask LLM
        if auto_strategy or not strategy:
            print(f"🧠 Auto-detecting strategy for {artist} - {title}...")
            strategy = optimizer.recommend_strategy(artist, title)
            print(f"   Selected Strategy: {strategy}")

        metadata = optimizer.generate_optimized_metadata(strategy, artist, title)
        
        if metadata:
            return jsonify({
                'success': True,
                'metadata': metadata,
                'detected_info': {
                    'artist': artist,
                    'title': title,
                    'strategy': strategy
                }
            })
        else:
            return jsonify({'error': 'Failed to generate metadata'}), 500
            
    except Exception as e:
        print(f"SEO Optimization error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    Path('templates').mkdir(exist_ok=True)

    print("\n" + "="*70)
    print("🎵 YouTube to Instrumental Video - Web Interface")
    print("="*70)
    print("\n📱 Starting server on http://localhost:5000")
    print("   Press Ctrl+C to stop\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
