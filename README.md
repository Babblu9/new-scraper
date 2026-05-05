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

To download transcripts for new videos, you don't add the full link; instead, you extract the **Video ID** and add it to the script.

For example, if your YouTube link is:
`https://www.youtube.com/watch?v=VAEWEHIoTFo`

The Video ID is the part after `v=`, which is `VAEWEHIoTFo`.

1. Open `fetch_transcripts.py`.
2. Locate the `VIDEO_IDS` list at the beginning of the script.
3. Add your Video ID as a string to the list:

```python
VIDEO_IDS = [
    "VAEWEHIoTFo",
    "YOUR_NEW_VIDEO_ID_HERE"
]
```

## How to Run

Once you have added your desired Video IDs, simply run the script from your terminal:

```bash
python fetch_transcripts.py
```

The script will fetch the transcripts concurrently and save them as `.txt` files in the `transcripts/` folder.
