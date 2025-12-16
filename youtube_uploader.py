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
            scopes=[
                'https://www.googleapis.com/auth/youtube.upload',
                'https://www.googleapis.com/auth/youtube'
            ]
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

    def create_playlist(self, title, description="", privacy_status='public'):
        """
        Create a new YouTube playlist

        Args:
            title: Playlist title
            description: Playlist description (optional)
            privacy_status: 'public', 'unlisted', or 'private'

        Returns:
            Playlist ID if successful, None otherwise
        """
        print(f"\n📋 Creating playlist: {title}")

        body = {
            'snippet': {
                'title': title,
                'description': description
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }

        try:
            response = self.youtube.playlists().insert(
                part='snippet,status',
                body=body
            ).execute()

            playlist_id = response['id']
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"

            print(f"✅ Playlist created!")
            print(f"   Playlist ID: {playlist_id}")
            print(f"   URL: {playlist_url}")

            return playlist_id

        except Exception as e:
            print(f"❌ Failed to create playlist: {e}")
            return None

    def add_video_to_playlist(self, playlist_id, video_id):
        """
        Add a video to an existing playlist

        Args:
            playlist_id: YouTube playlist ID
            video_id: YouTube video ID to add

        Returns:
            True if successful, False otherwise
        """
        print(f"   Adding video {video_id} to playlist...")

        body = {
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }

        try:
            self.youtube.playlistItems().insert(
                part='snippet',
                body=body
            ).execute()

            print(f"   ✅ Video added to playlist")
            return True

        except Exception as e:
            print(f"   ❌ Failed to add video to playlist: {e}")
            return False

    def get_user_playlists(self):
        """
        Get list of user's playlists

        Returns:
            List of dicts with 'id' and 'title' keys, or empty list on error
        """
        try:
            playlists = []
            request = self.youtube.playlists().list(
                part='snippet',
                mine=True,
                maxResults=50
            )

            while request:
                response = request.execute()

                for item in response.get('items', []):
                    playlists.append({
                        'id': item['id'],
                        'title': item['snippet']['title']
                    })

                request = self.youtube.playlists().list_next(request, response)

            return playlists

        except Exception as e:
            print(f"❌ Failed to fetch playlists: {e}")
            return []

    def get_playlist_videos(self, playlist_id):
        """
        Get videos in a specific playlist

        Args:
            playlist_id: YouTube playlist ID

        Returns:
            List of dicts with video information
        """
        try:
            videos = []
            request = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50
            )

            while request:
                response = request.execute()

                for item in response.get('items', []):
                    videos.append({
                        'id': item['snippet']['resourceId']['videoId'],
                        'title': item['snippet']['title'],
                        'thumbnail': item['snippet']['thumbnails']['default']['url'],
                        'published_at': item['snippet']['publishedAt'],
                        'playlist_item_id': item['id']
                    })

                request = self.youtube.playlistItems().list_next(request, response)

            return videos

        except Exception as e:
            print(f"❌ Failed to fetch playlist videos: {e}")
            return []

    def get_channel_videos(self):
        """
        Get user's uploaded videos

        Returns:
            List of dicts with video information
        """
        try:
            # First, get the user's upload playlist ID
            channels_response = self.youtube.channels().list(
                part='contentDetails',
                mine=True
            ).execute()

            if not channels_response.get('items'):
                return []

            upload_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            # Then get videos from that playlist
            return self.get_playlist_videos(upload_playlist_id)

        except Exception as e:
            print(f"❌ Failed to fetch channel videos: {e}")
            return []

    def remove_video_from_playlist(self, playlist_id, video_id):
        """
        Remove a video from a playlist

        Args:
            playlist_id: YouTube playlist ID
            video_id: YouTube video ID to remove

        Returns:
            True if successful, False otherwise
        """
        try:
            # First, get the playlist item ID for this video
            request = self.youtube.playlistItems().list(
                part='id',
                playlistId=playlist_id,
                videoId=video_id
            )
            response = request.execute()

            if not response.get('items'):
                print(f"❌ Video not found in playlist")
                return False

            playlist_item_id = response['items'][0]['id']

            # Delete the playlist item
            self.youtube.playlistItems().delete(
                id=playlist_item_id
            ).execute()

            print(f"✅ Removed video from playlist")
            return True

        except Exception as e:
            print(f"❌ Failed to remove video from playlist: {e}")
            return False

    def delete_video(self, video_id):
        """
        Delete a video from YouTube

        Args:
            video_id: YouTube video ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.youtube.videos().delete(
                id=video_id
            ).execute()

            print(f"✅ Deleted video {video_id}")
            return True

        except Exception as e:
            print(f"❌ Failed to delete video: {e}")
            return False

    def get_video_details(self, video_id):
        """
        Get detailed metadata for a video

        Args:
            video_id: YouTube video ID

        Returns:
            Dict with title, description, tags, stats, etc., or None if not found
        """
        try:
            request = self.youtube.videos().list(
                part="snippet,status,statistics",
                id=video_id
            )
            response = request.execute()

            if not response.get('items'):
                return None

            item = response['items'][0]
            snippet = item['snippet']
            stats = item.get('statistics', {})
            
            return {
                'id': video_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'tags': snippet.get('tags', []),
                'categoryId': snippet.get('categoryId'),
                'privacy_status': item['status']['privacyStatus'],
                'view_count': stats.get('viewCount', 0),
                'like_count': stats.get('likeCount', 0)
            }

        except Exception as e:
            print(f"❌ Failed to get video details: {e}")
            return None

    def update_video_metadata(self, video_id, metadata):
        """
        Update a video's metadata (title, description, tags)

        Args:
            video_id: YouTube video ID
            metadata: Dict with 'title', 'description', 'tags' keys

        Returns:
            True if successful, False otherwise
        """
        print(f"\n🔄 Updating metadata for video {video_id}...")
        
        try:
            # First get current details to preserve categoryId and other fields
            current_details = self.get_video_details(video_id)
            if not current_details:
                print("❌ Could not fetch current video details. Aborting update.")
                return False

            body = {
                'id': video_id,
                'snippet': {
                    'title': metadata.get('title', current_details['title']),
                    'description': metadata.get('description', current_details['description']),
                    'tags': metadata.get('tags', current_details['tags']),
                    'categoryId': current_details.get('categoryId', '10'), # Default to Music if missing
                    'defaultLanguage': 'en'
                }
            }

            self.youtube.videos().update(
                part='snippet',
                body=body
            ).execute()

            print(f"✅ Metadata updated successfully!")
            return True

        except Exception as e:
            print(f"❌ Failed to update metadata: {e}")
            return False


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
