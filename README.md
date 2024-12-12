# Plex Monitor

A Python-based monitoring tool for Plex Media Server that provides real-time session tracking, playlist management, and metadata retrieval.

## Features

- Real-time monitoring of active Plex sessions
- View detailed information about current viewers and their progress
- List and manage Plex playlists
- Retrieve comprehensive metadata about media items
- Continuous monitoring with customizable intervals
- Detailed logging of all activities
- Interactive menu-driven interface

## Prerequisites

- Python 3.6 or higher
- A Plex Media Server instance
- Plex authentication token
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/plex-monitor.git
cd plex-monitor
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root directory with your Plex configuration:
```env
PLEX_SERVER=http://your-plex-server:32400
PLEX_TOKEN=your-plex-token
```

### Getting Your Plex Token

You can find your Plex token by:
1. Log into Plex web interface (app.plex.tv)
2. Play any media file
3. Click the three dots menu (...)
4. Select "Get Info"
5. Click "View XML"
6. Look for `X-Plex-Token=` in the URL

## Usage

Run the script:
```bash
python plex_monitor.py
```

The interactive menu provides the following options:
1. Show active sessions
2. Show playlists
3. Get item metadata
4. Start continuous monitoring
5. Exit

### Example Output

```
=== Current Plex Activity ===
User: JohnDoe
Watching: Gremlins (1984)
Progress: 45.2%
Player: Roku (playing)

User: JaneSmith
Watching: The Matrix (1999)
Progress: 78.9%
Player: Chrome (paused)
```

## Configuration

The script can be configured through the following environment variables in your `.env` file:
- `PLEX_SERVER`: URL of your Plex server (default: http://localhost:32400)
- `PLEX_TOKEN`: Your Plex authentication token

## Logging

The script creates a log file (`plex_monitor.log`) that includes:
- Authentication attempts
- API request status
- Error messages
- Session information

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built using the Plex Media Server API
- Inspired by the need for better Plex server monitoring tools
- Thanks to the Plex community for their support and feedback

## Security Considerations

- Keep your Plex token secure and never share it publicly
- The token provides access to your Plex server
- Consider using a dedicated Plex account with limited permissions for monitoring

## Error Handling

The script includes comprehensive error handling for:
- Failed authentication
- Network connectivity issues
- XML parsing errors
- Invalid media IDs
- Missing permissions

## Support

For issues, questions, or contributions, please:
1. Check existing GitHub issues
2. Create a new issue with detailed information
3. Include relevant log entries and configuration details

---
Created and maintained by [Your Name]