#!/usr/bin/env python3
"""
YouTube Video Uploader
Uploads videos to YouTube with metadata using OAuth credentials from .env
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class YouTubeUploader:
    def __init__(self):
        """Initialize YouTube uploader with credentials from .env"""
        load_dotenv()

        # Load credentials from .env
        self.client_id = os.getenv('YOUTUBE_CLIENT_ID')
        self.client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
        self.refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')

        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise ValueError("Missing YouTube credentials in .env file. Run setup_youtube_oauth.py first.")

        # Create credentials object
        self.credentials = Credentials(
            token=None,
            refresh_token=self.refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=['https://www.googleapis.com/auth/youtube.upload']
        )

        # Refresh the token
        self.credentials.refresh(Request())

        # Build YouTube API client
        self.youtube = build('youtube', 'v3', credentials=self.credentials)

        print("✅ YouTube API authenticated successfully")

    def upload_video(self, video_file, metadata, privacy_status='public'):
        """
        Upload video to YouTube with metadata

        Args:
            video_file: Path to video file
            metadata: Dict with title, description, tags
            privacy_status: 'public', 'unlisted', or 'private'

        Returns:
            Video ID if successful, None otherwise
        """
        video_file = Path(video_file)

        if not video_file.exists():
            print(f"❌ Video file not found: {video_file}")
            return None

        print(f"\n📤 Uploading video to YouTube...")
        print(f"   File: {video_file.name}")
        print(f"   Size: {video_file.stat().st_size / (1024*1024):.1f} MB")

        # Prepare request body
        body = {
            'snippet': {
                'title': metadata.get('title', 'Instrumental Video'),
                'description': metadata.get('description', ''),
                'tags': metadata.get('tags', []),
                'categoryId': '10',  # Music category
                'defaultLanguage': 'en'
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False,
                'embeddable': True,
                'publicStatsViewable': True,
                'license': 'youtube'
            }
        }

        # Create media upload
        media = MediaFileUpload(
            str(video_file),
            chunksize=1024*1024,  # 1MB chunks
            resumable=True,
            mimetype='video/mp4'
        )

        try:
            # Insert video
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )

            # Execute upload with progress
            response = None
            print("   Uploading...")

            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"   Progress: {progress}%")

            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            print("\n✅ Upload complete!")
            print(f"   Video ID: {video_id}")
            print(f"   URL: {video_url}")
            print(f"   Privacy: {privacy_status}")

            return video_id

        except Exception as e:
            print(f"\n❌ Upload failed: {e}")
            return None

    def upload_from_metadata_file(self, video_file, metadata_file, privacy_status='public'):
        """
        Upload video using metadata from JSON file

        Args:
            video_file: Path to video file
            metadata_file: Path to metadata JSON file
            privacy_status: 'public', 'unlisted', or 'private'

        Returns:
            Video ID if successful, None otherwise
        """
        metadata_file = Path(metadata_file)

        if not metadata_file.exists():
            print(f"❌ Metadata file not found: {metadata_file}")
            return None

        # Load metadata
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        print("\n📋 Loaded metadata:")
        print(f"   Title: {metadata.get('title', 'N/A')}")
        print(f"   Tags: {len(metadata.get('tags', []))} tags")
        print(f"   Description: {len(metadata.get('description', ''))} characters")

        # Upload video
        return self.upload_video(video_file, metadata, privacy_status)


def main():
    """Test uploader with example video"""
    import argparse

    parser = argparse.ArgumentParser(description="Upload video to YouTube")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--metadata", "-m", help="Path to metadata JSON file")
    parser.add_argument(
        "--privacy", "-p",
        choices=['public', 'unlisted', 'private'],
        default='public',
        help="Privacy status (default: public)"
    )

    args = parser.parse_args()

    # Create uploader
    uploader = YouTubeUploader()

    # Upload video
    if args.metadata:
        video_id = uploader.upload_from_metadata_file(
            args.video,
            args.metadata,
            args.privacy
        )
    else:
        # Use basic metadata if no file provided
        metadata = {
            'title': Path(args.video).stem,
            'description': 'Uploaded via YouTube Uploader',
            'tags': ['instrumental', 'music']
        }
        video_id = uploader.upload_video(args.video, metadata, args.privacy)

    if video_id:
        print(f"\n🎉 Success! Video ID: {video_id}")
    else:
        print("\n❌ Upload failed")


if __name__ == '__main__':
    main()
