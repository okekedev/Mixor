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

app = Flask(__name__)
CORS(app)

# Store job status
jobs = {}

class ProcessingJob:
    def __init__(self, job_id, urls, upload_to_youtube, save_locally, create_playlist, playlist_name, add_to_playlist):
        self.job_id = job_id
        self.urls = urls
        self.upload_to_youtube = upload_to_youtube
        self.save_locally = save_locally
        self.create_playlist = create_playlist
        self.playlist_name = playlist_name
        self.add_to_playlist = add_to_playlist
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

        # Create playlist if requested
        if job.create_playlist and job.playlist_name and uploader:
            job.message = 'Creating playlist...'
            playlist_id = uploader.create_playlist(
                title=job.playlist_name,
                description=f"Instrumental remasters created with AI vocal separation",
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
    data = request.json

    # Parse URLs (playlist or individual videos)
    urls = []
    if data.get('playlist_url'):
        urls.append(data['playlist_url'])

    if data.get('video_urls'):
        urls.extend([url.strip() for url in data['video_urls'] if url.strip()])

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
        add_to_playlist=data.get('add_to_playlist', False)
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


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    Path('templates').mkdir(exist_ok=True)

    print("\n" + "="*70)
    print("🎵 YouTube to Instrumental Video - Web Interface")
    print("="*70)
    print("\n📱 Starting server on http://localhost:5000")
    print("   Press Ctrl+C to stop\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
