# YouTube Transcript Scraper

This project contains a Python script (`fetch_transcripts.py`) that asynchronously downloads transcripts for a list of YouTube videos and saves them locally as readable text files.

## How it Works (Code Explanation)

The `fetch_transcripts.py` script works in the following steps:
1. **Configuration**: It has a hardcoded list of YouTube Video IDs (`VIDEO_IDS`) at the top of the file.
2. **API Request**: It uses the `aiohttp` library to make concurrent, asynchronous requests to an external API (`notegpt.io/api/v2/video-transcript`). It passes a generated UUID to bypass basic tracking/restrictions.
3. **Data Parsing**: It parses the JSON response to extract the video's title and its transcript segments (which contain text, start, and end times).
4. **Saving to File**: It formats these segments into a human-readable text file and saves it inside the `transcripts/` directory.

## Prerequisites

You need to have Python installed on your machine along with the `aiohttp` library.

Install the required library using pip:
```bash
pip install aiohttp
```

## How to Add a YouTube Link

You can now fetch transcripts for a single video or an entire playlist by simply passing the URL as an argument when running the script! The script uses `yt-dlp` to extract the video IDs automatically.

## How to Run

Run the script from your terminal and pass the YouTube URL (video or playlist) like this:

```bash
# For a playlist
python fetch_transcripts.py "https://youtube.com/playlist?list=YOUR_PLAYLIST_ID"

# For a single video
python fetch_transcripts.py "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
```

The script will fetch the transcripts concurrently and save them as `.txt` files in the `backend/` folder.
