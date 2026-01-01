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
import logging
import os
from youtube_vocal_remover import YouTubeVocalRemover

app = Flask(__name__)

# Enable Flask logging for debugging - suppress HTTP request logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Only show errors, not every request

# Configure CORS - must be after app creation
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Store job status
jobs = {}

# Removed ProcessingJob and process_videos - only Instrumental Maker is available


@app.route('/')
def index():
    """API root - redirect to frontend or return API info"""
    return jsonify({
        'message': 'Vocalless API Server',
        'frontend': 'http://localhost:5181',
        'endpoints': {
            'process': '/api/process-instrumental',
            'status': '/api/status/<job_id>',
            'output': '/output/<path:filename>'
        }
    })


# Simple job class for instrumental-only processing
class InstrumentalJob:
    def __init__(self, job_id, urls):
        self.job_id = job_id
        self.urls = urls
        self.status = 'queued'
        self.progress = 0
        self.current_video = 0
        self.total_videos = len(urls)
        self.message = 'Queued'
        self.results = []
        self.error = None

def process_instrumentals(job):
    """Process YouTube URLs to create instrumental MP3s only (no video)"""
    try:
        job.status = 'processing'
        remover = YouTubeVocalRemover(output_dir="output", keep_original=False)

        for i, url in enumerate(job.urls):
            job.current_video = i + 1
            job.message = f'Processing audio {i+1}/{job.total_videos}'
            job.progress = int((i / job.total_videos) * 80)  # 0-80% for processing

            try:
                # Download and remove vocals (no video creation)
                instrumental_path = remover.process_youtube_url(url, model="htdemucs_ft")

                if instrumental_path:
                    # Construct acapella path from instrumental path
                    instrumental_path_obj = Path(instrumental_path)
                    acapella_path = instrumental_path_obj.parent.parent / "acapellas" / instrumental_path_obj.name

                    # Convert absolute paths to relative URLs for serving via Flask
                    # Path format: output/instrumentals/filename.mp3 -> instrumentals/filename.mp3
                    instrumental_url = f"/output/instrumentals/{instrumental_path_obj.name}"
                    acapella_url = f"/output/acapellas/{acapella_path.name}" if acapella_path.exists() else None

                    job.results.append({
                        'url': url,
                        'title': instrumental_path_obj.stem,  # Filename without extension
                        'instrumental': instrumental_url,
                        'acapella': acapella_url,
                        'success': True
                    })
                else:
                    job.results.append({
                        'url': url,
                        'error': 'Failed to create instrumental',
                        'success': False
                    })
            except Exception as e:
                job.results.append({
                    'url': url,
                    'error': str(e),
                    'success': False
                })

            # Update progress after each video
            job.progress = int(((i + 1) / job.total_videos) * 100)

        job.status = 'complete'
        job.message = 'All instrumentals created!'
        job.progress = 100

    except Exception as e:
        job.status = 'failed'
        job.error = str(e)


@app.route('/api/process-instrumental', methods=['POST'])
def process_instrumental():
    """Process YouTube URLs to create instrumental MP3s only (no video)"""
    import re

    data = request.json
    urls = []

    # Get YouTube URLs from request
    if data.get('video_urls'):
        print(f"\nProcessing YouTube URLs for instrumental-only")
        for video_url in data['video_urls']:
            video_url = video_url.strip()
            if not video_url:
                continue

            # Clean URL (remove playlist parameters)
            if '&list=' in video_url or '?list=' in video_url:
                video_id_match = re.search(r'[?&]v=([^&]+)', video_url)
                if video_id_match:
                    video_id = video_id_match.group(1)
                    clean_url = f"https://www.youtube.com/watch?v={video_id}"
                    urls.append(clean_url)
                else:
                    urls.append(video_url)
            else:
                urls.append(video_url)
        print(f"Added {len(urls)} URL(s) for instrumental processing")

    if not urls:
        return jsonify({'error': 'No URLs provided'}), 400

    # Create job
    job_id = str(uuid.uuid4())
    job = InstrumentalJob(job_id=job_id, urls=urls)
    jobs[job_id] = job

    # Start processing in background
    thread = threading.Thread(target=process_instrumentals, args=(job,))
    thread.daemon = True
    thread.start()

    return jsonify({
        'job_id': job_id,
        'message': 'Instrumental processing started'
    })

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get job status"""
    try:
        job = jobs.get(job_id)

        if not job:
            return jsonify({'error': 'Job not found'}), 404

        response_data = {
            'status': job.status,
            'progress': job.progress,
            'message': job.message,
            'current_video': job.current_video,
            'total_videos': job.total_videos,
            'results': job.results,
            'error': job.error
        }

        # Log status for debugging
        if job.status == 'complete':
            print(f"\n[SUCCESS] Job {job_id} is COMPLETE with {len(job.results)} results")
            print(f"  Status response: {response_data}")

        return jsonify(response_data)
    except Exception as e:
        print(f"Error in get_status: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    return jsonify([{
        'job_id': job_id,
        'status': job.status,
        'progress': job.progress,
        'total_videos': job.total_videos
    } for job_id, job in jobs.items()])


@app.route('/api/cancel/<job_id>', methods=['POST'])
def cancel_job(job_id):
    """Cancel a job"""
    job = jobs.get(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    # Mark as cancelled
    job.status = 'cancelled'
    job.message = 'Job cancelled by user'

    return jsonify({'status': 'cancelled'})


# Removed YouTube playlist/video/upload endpoints - only Instrumental Maker is available


@app.route('/output/<path:filename>')
def serve_output_file(filename):
    """Serve audio files from the output directory"""
    try:
        output_dir = Path('output').resolve()
        # Check if this is a download request (has 'download' query param)
        download = request.args.get('download', 'false').lower() == 'true'
        return send_from_directory(output_dir, filename, as_attachment=download)
    except Exception as e:
        print(f"Error serving file: {e}")
        return jsonify({'error': str(e)}), 404


# Creator feature job class
class CreatorJob:
    """Job for Creator feature (resample audio with AI)"""
    def __init__(self, job_id, url, target_genre, selected_stems):
        self.id = job_id
        self.url = url
        self.target_genre = target_genre
        self.selected_stems = selected_stems
        self.status = 'pending'  # pending, processing, complete, failed
        self.progress = 0  # 0-100
        self.message = ''
        self.output_file = None
        self.error = None


creator_jobs = {}  # Store Creator jobs


@app.route('/api/creator/process', methods=['POST'])
def process_creator():
    """Process YouTube URL with Creator feature (AI resampling)"""
    data = request.json

    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400

    url = data['url'].strip()
    target_genre = data.get('target_genre', 'lofi')
    selected_stems = data.get('selected_stems', ['drums', 'bass', 'other'])

    # Validate URL
    if not url.startswith('http'):
        return jsonify({'error': 'Invalid URL'}), 400

    # Create job
    job_id = str(uuid.uuid4())
    job = CreatorJob(job_id, url, target_genre, selected_stems)
    creator_jobs[job_id] = job

    # Start processing in background thread
    thread = threading.Thread(target=process_creator_job, args=(job,))
    thread.daemon = True
    thread.start()

    return jsonify({
        'job_id': job_id,
        'status': 'started'
    })


def process_creator_job(job):
    """Background thread to process Creator job"""
    # Creator pipeline has been removed
    job.status = 'failed'
    job.error = 'Creator feature has been removed - only Instrumental Maker is available'
    job.progress = 0


@app.route('/api/creator/status/<job_id>', methods=['GET'])
def get_creator_status(job_id):
    """Get Creator job status"""
    job = creator_jobs.get(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify({
        'id': job.id,
        'status': job.status,
        'progress': job.progress,
        'message': job.message,
        'output_file': job.output_file,
        'error': job.error,
        'target_genre': job.target_genre,
        'selected_stems': job.selected_stems
    })


@app.route('/api/creator/cancel/<job_id>', methods=['POST'])
def cancel_creator_job(job_id):
    """Cancel a Creator job"""
    job = creator_jobs.get(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    # Mark as cancelled (thread will check this)
    job.status = 'cancelled'
    job.message = 'Job cancelled by user'

    return jsonify({'status': 'cancelled'})


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    Path('templates').mkdir(exist_ok=True)

    print("\n" + "="*70)
    print("YouTube to Instrumental Video - Web Interface")
    print("="*70)
    print("\nStarting server on http://localhost:5000")
    print("Press Ctrl+C to stop\n")

    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
