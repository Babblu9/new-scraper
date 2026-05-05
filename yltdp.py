import subprocess
import json
import os
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).parent / "downloads"
OUT.mkdir(exist_ok=True)

URLS = [
    "https://www.youtube.com/watch?v=ERW9i1lwnBw"
]

def get_ffprobe_info(filepath):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", filepath],
            capture_output=True, text=True, timeout=30
        )
        info = json.loads(result.stdout)
        stream = info.get("streams", [{}])[0]
        fmt = info.get("format", {})
        return {
            "audio_sample_rate": int(stream.get("sample_rate", 0)),
            "audio_channels": int(stream.get("channels", 0)),
            "audio_duration_sec": round(float(fmt.get("duration", 0)), 2),
            "audio_size_bytes": int(fmt.get("size", 0)),
        }
    except Exception as e:
        return {"error": str(e)}

def download_one(idx, url):
    vid_id = url.split("v=")[1].split("&")[0]
    prefix = f"{idx:03d}_{vid_id}"
    audio_path = OUT / f"{prefix}.mp3"
    meta_path = OUT / f"{prefix}_metadata.json"

    if meta_path.exists():
        print(f"  [{idx}/{len(URLS)}] SKIP (already done): {vid_id}")
        return True

    # Get YouTube metadata
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download", url],
            capture_output=True, text=True, timeout=60
        )
        yt_info = json.loads(result.stdout)
    except Exception as e:
        print(f"  [{idx}/{len(URLS)}] FAIL metadata: {vid_id} - {e}")
        return False

    try:
        subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3",
             "--postprocessor-args", "ffmpeg:-b:a 48k",
             "-o", str(audio_path), url],
            capture_output=True, text=True, timeout=300
        )
    except Exception as e:
        print(f"  [{idx}/{len(URLS)}] FAIL download: {vid_id} - {e}")
        return False

    if not audio_path.exists():
        print(f"  [{idx}/{len(URLS)}] FAIL no file: {vid_id}")
        return False

    audio_info = get_ffprobe_info(str(audio_path))

    metadata = {
        "id": yt_info.get("id"),
        "url": url,
        "title": yt_info.get("title"),
        "channel": yt_info.get("channel"),
        "channel_id": yt_info.get("channel_id"),
        "upload_date": yt_info.get("upload_date"),
        "duration_sec": yt_info.get("duration"),
        "description": yt_info.get("description"),
        "view_count": yt_info.get("view_count"),
        "like_count": yt_info.get("like_count"),
        "tags": yt_info.get("tags", []),
        "categories": yt_info.get("categories", []),
        "language": yt_info.get("language"),
        "playlist_index": idx,
        "audio_file": f"{prefix}.mp3",
        "audio_format": "mp3",
        "audio_bitrate": "48k",
        "audio_sample_rate": audio_info.get("audio_sample_rate"),
        "audio_channels": audio_info.get("audio_channels"),
        "audio_duration_sec": audio_info.get("audio_duration_sec"),
        "audio_size_bytes": audio_info.get("audio_size_bytes"),
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    size_mb = audio_path.stat().st_size / 1024 / 1024
    print(f"  [{idx}/{len(URLS)}] OK: {yt_info.get('title', vid_id)[:60]} ({size_mb:.1f}MB, {yt_info.get('duration', '?')}s)")
    return True

from concurrent.futures import ThreadPoolExecutor, as_completed

WORKERS = 10

print(f"=== Downloading {len(URLS)} videos to {OUT} ({WORKERS} parallel) ===\n")

success = 0
fail = 0

with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    futures = {pool.submit(download_one, idx, url): idx for idx, url in enumerate(URLS, 1)}
    for future in as_completed(futures):
        if future.result():
            success += 1
        else:
            fail += 1

print(f"\n=== DONE: {success} ok, {fail} failed out of {len(URLS)} ===")
