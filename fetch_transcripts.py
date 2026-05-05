import asyncio
import aiohttp
import uuid
import json
import os
import sys
import subprocess

API_URL = "https://notegpt.io/api/v2/video-transcript"
OUTPUT_DIR = "backend"

def get_video_ids(url):
    print(f"Fetching video IDs from: {url}")
    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--get-id", url],
            capture_output=True, text=True, check=True
        )
        ids = [vid.strip() for vid in result.stdout.split('\n') if vid.strip()]
        print(f"Found {len(ids)} videos.")
        return ids
    except subprocess.CalledProcessError as e:
        print(f"Error fetching video IDs: {e}")
        return []


def sanitize_filename(name):
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip()[:100]


async def fetch_transcript(session, video_id):
    params = {"platform": "youtube", "video_id": video_id}
    headers = {
        "Accept": "application/json",
        "Cookie": f"anonymous_user_id={uuid.uuid4()}",
    }
    async with session.get(API_URL, params=params, headers=headers) as resp:
        body = await resp.json()

    if body.get("code") != 100000:
        print(f"[FAIL] {video_id} — {body.get('message')}")
        return None

    data = body["data"]
    title = data.get("videoInfo", {}).get("name", video_id)
    transcripts = data.get("transcripts", {})

    segments = []
    for lang, sources in transcripts.items():
        for source_type, entries in sources.items():
            if isinstance(entries, list) and entries:
                segments = entries
                break
        if segments:
            break

    if not segments:
        print(f"[SKIP] {video_id} — \"{title}\" has no transcript")
        return None

    return {"video_id": video_id, "title": title, "segments": segments}


def save_as_text(result):
    safe_name = sanitize_filename(result["title"])
    filepath = os.path.join(OUTPUT_DIR, f"{safe_name}.txt")

    with open(filepath, "w") as f:
        f.write(f"Title: {result['title']}\n")
        f.write(f"Video: https://www.youtube.com/watch?v={result['video_id']}\n")
        f.write(f"{'=' * 60}\n\n")
        for seg in result["segments"]:
            f.write(f"[{seg['start']} → {seg['end']}]\n{seg['text']}\n\n")

    return filepath


async def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
        video_ids = get_video_ids(url)
    else:
        video_ids = [
            "VAEWEHIoTFo",
        ]
        print("No URL provided, using default video IDs.")

    if not video_ids:
        print("No video IDs to process. Exiting.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_transcript(session, vid) for vid in video_ids]
        results = await asyncio.gather(*tasks)

    saved = 0
    for result in results:
        if result:
            path = save_as_text(result)
            print(f"[SAVED] {result['video_id']} — \"{result['title']}\" → {path}")
            saved += 1

    print(f"\nDone. {saved}/{len(video_ids)} transcripts saved to ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
