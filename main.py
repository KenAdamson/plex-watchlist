import requests
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import time
from typing import Optional, List, Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('plex_monitor.log'),
        logging.StreamHandler()
    ]
)


class PlexMonitor:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Initialize configuration
        self.server = os.getenv('PLEX_SERVER', 'http://localhost:32400')
        self.username = os.getenv('PLEX_USERNAME')
        self.password = os.getenv('PLEX_PASSWORD')
        self.token = os.getenv('PLEX_TOKEN')

        # Headers for API requests
        self.headers = {
            'X-Plex-Client-Identifier': 'PlexMonitorTool',
            'X-Plex-Product': 'PlexMonitor',
            'X-Plex-Version': '1.0',
            'X-Plex-Platform': 'Python',
            'Content-Type': 'application/json'
        }

        # Authenticate if token not provided
        if not self.token:
            self.token = self.authenticate()

    def authenticate(self) -> Optional[str]:
        """Authenticates with Plex and returns the auth token."""
        try:
            auth_headers = {
                'X-Plex-Client-Identifier': 'PlexMonitorTool',
                'X-Plex-Product': 'PlexMonitor',
                'X-Plex-Version': '1.0',
                'X-Plex-Platform': 'Python',
                'X-Plex-Device': 'PlexMonitorScript',
                'X-Plex-Device-Name': 'PlexMonitor',
                'Accept': 'application/json'
            }

            response = requests.post(
                'https://plex.tv/users/sign_in',
                headers=auth_headers,
                auth=(self.username, self.password)
            )
            response.raise_for_status()
            token = response.json()['user']['authToken']
            logging.info("Successfully authenticated with Plex")
            return token
        except requests.RequestException as e:
            logging.error(f"Authentication failed: {str(e)}")
            return None

    def make_request(self, endpoint: str) -> Optional[str]:
        """Makes a request to the Plex server with error handling."""
        if not self.token:
            logging.error("No valid token available")
            return None

        url = f'{self.server}{endpoint}?X-Plex-Token={self.token}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"Request failed for {endpoint}: {str(e)}")
            return None

    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Gets all active viewing sessions with enhanced details."""
        xml_data = self.make_request('/status/sessions')
        if not xml_data:
            return []

        sessions = []
        try:
            root = ET.fromstring(xml_data)
            for video in root.findall(".//Video"):
                user = video.find("./User")
                player = video.find("./Player")

                session_info = {
                    'username': user.get("title") if user is not None else "Unknown User",
                    'title': video.get("title"),
                    'year': video.get("year"),
                    'type': video.get("type"),
                    'duration': video.get("duration"),
                    'view_offset': video.get("viewOffset"),
                    'player': player.get("platform") if player is not None else "Unknown Platform",
                    'state': player.get("state") if player is not None else "Unknown State",
                    'progress': f"{(int(video.get('viewOffset', 0)) / int(video.get('duration', 1)) * 100):.1f}%"
                }
                sessions.append(session_info)
        except (ET.ParseError, AttributeError) as e:
            logging.error(f"Error parsing sessions XML: {str(e)}")

        return sessions

    def get_playlists(self) -> List[Dict[str, Any]]:
        """Gets all playlists with enhanced metadata."""
        xml_data = self.make_request('/playlists/all')
        if not xml_data:
            return []

        playlists = []
        try:
            root = ET.fromstring(xml_data)
            for playlist in root.findall(".//Playlist"):
                playlist_info = {
                    'title': playlist.get("title"),
                    'summary': playlist.get("summary", "No description"),
                    'duration': int(playlist.get("duration", 0)) // 1000,  # Convert to seconds
                    'item_count': playlist.get("leafCount", "0"),
                    'last_viewed_at': datetime.fromtimestamp(
                        int(playlist.get("lastViewedAt", 0))
                    ).strftime('%Y-%m-%d %H:%M:%S') if playlist.get("lastViewedAt") else "Never"
                }
                playlists.append(playlist_info)
        except ET.ParseError as e:
            logging.error(f"Error parsing playlists XML: {str(e)}")

        return playlists

    def get_item_metadata(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Gets detailed metadata for a specific media item."""
        xml_data = self.make_request(f'/library/metadata/{item_id}')
        if not xml_data:
            return None

        try:
            root = ET.fromstring(xml_data)
            video = root.find(".//Video")
            if video is None:
                return None

            metadata = {
                'title': video.get("title"),
                'year': video.get("year"),
                'rating': video.get("rating"),
                'summary': video.get("summary"),
                'duration': f"{int(video.get('duration', 0)) // 60000} minutes",
                'viewed_by': [account.get("title") for account in root.findall(".//Account")],
                'genres': [genre.get("tag") for genre in root.findall(".//Genre")],
                'directors': [director.get("tag") for director in root.findall(".//Director")],
                'writers': [writer.get("tag") for writer in root.findall(".//Writer")]
            }
            return metadata
        except ET.ParseError as e:
            logging.error(f"Error parsing metadata XML: {str(e)}")
            return None

    def monitor_activity(self, interval: int = 60):
        """Continuously monitors server activity with specified interval."""
        try:
            while True:
                print("\n=== Current Plex Activity ===")
                sessions = self.get_active_sessions()

                if not sessions:
                    print("No active sessions")
                else:
                    for session in sessions:
                        print(f"\nUser: {session['username']}")
                        print(f"Watching: {session['title']} ({session['year']})")
                        print(f"Progress: {session['progress']}")
                        print(f"Player: {session['player']} ({session['state']})")

                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped")


def main():
    monitor = PlexMonitor()

    while True:
        print("\nPlex Monitor Menu:")
        print("1. Show active sessions")
        print("2. Show playlists")
        print("3. Get item metadata")
        print("4. Start continuous monitoring")
        print("5. Exit")

        choice = input("\nSelect an option (1-5): ")

        if choice == '1':
            sessions = monitor.get_active_sessions()
            if sessions:
                for session in sessions:
                    print(f"\nUser: {session['username']}")
                    print(f"Watching: {session['title']} ({session['year']})")
                    print(f"Progress: {session['progress']}")
            else:
                print("No active sessions")

        elif choice == '2':
            playlists = monitor.get_playlists()
            if playlists:
                for playlist in playlists:
                    print(f"\nTitle: {playlist['title']}")
                    print(f"Items: {playlist['item_count']}")
                    print(f"Duration: {playlist['duration']} seconds")
                    print(f"Last Viewed: {playlist['last_viewed_at']}")
            else:
                print("No playlists found")

        elif choice == '3':
            item_id = input("Enter media item ID: ")
            if item_id.isdigit():
                metadata = monitor.get_item_metadata(item_id)
                if metadata:
                    print(f"\nTitle: {metadata['title']} ({metadata['year']})")
                    print(f"Duration: {metadata['duration']}")
                    print(f"Rating: {metadata['rating']}")
                    print(f"Genres: {', '.join(metadata['genres'])}")
                    print(f"Directors: {', '.join(metadata['directors'])}")
                    print(f"Writers: {', '.join(metadata['writers'])}")
                    print(f"Viewed by: {', '.join(metadata['viewed_by'])}")
                    print(f"\nSummary: {metadata['summary']}")
                else:
                    print("Item not found or error occurred")
            else:
                print("Invalid item ID")

        elif choice == '4':
            interval = input("Enter monitoring interval in seconds (default 60): ")
            try:
                interval = int(interval) if interval else 60
                monitor.monitor_activity(interval)
            except ValueError:
                print("Invalid interval, using default 60 seconds")
                monitor.monitor_activity()

        elif choice == '5':
            print("Exiting...")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()