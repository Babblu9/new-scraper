import asyncio
import aiohttp
import uuid
import time

VIDEO_IDS = [
    "JzKTnvF0OgU",
    "qHaQA8CG1VM",
    "VlOvr8tp5ao",
    "2ADSAW_D_P8",
    "3yKkOTBjyj0",
    "ShwnlRlUKA4",
    "L_SXd5hd4rM",
]

API_URL = "https://notegpt.io/api/v2/video-transcript"
TOTAL_REQUESTS = 100
CONCURRENCY = 20

async def make_request(session, request_num, video_id):
    anon_id = str(uuid.uuid4())
    params = {"platform": "youtube", "video_id": video_id}
    headers = {
        "Accept": "application/json",
        "Cookie": f"anonymous_user_id={anon_id}",
    }
    start = time.monotonic()
    try:
        async with session.get(API_URL, params=params, headers=headers) as resp:
            body = await resp.json()
            elapsed = (time.monotonic() - start) * 1000
            code = body.get("code")
            msg = body.get("message", "")
            status = resp.status
            print(f"[{request_num:3d}] HTTP {status} | API code={code} | msg={msg:20s} | {elapsed:6.0f}ms | vid={video_id}")
            return {"req": request_num, "http": status, "code": code, "msg": msg, "ms": elapsed}
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        print(f"[{request_num:3d}] ERROR: {e} | {elapsed:.0f}ms")
        return {"req": request_num, "http": 0, "code": -1, "msg": str(e), "ms": elapsed}

async def main():
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i in range(TOTAL_REQUESTS):
            vid = VIDEO_IDS[i % len(VIDEO_IDS)]
            tasks.append(make_request(session, i + 1, vid))

        print(f"Firing {TOTAL_REQUESTS} requests (concurrency={CONCURRENCY})...\n")
        wall_start = time.monotonic()
        results = await asyncio.gather(*tasks)
        wall_elapsed = time.monotonic() - wall_start

        success = sum(1 for r in results if r["code"] == 100000)
        failed = sum(1 for r in results if r["code"] != 100000)
        avg_ms = sum(r["ms"] for r in results) / len(results)
        http_codes = {}
        api_codes = {}
        for r in results:
            http_codes[r["http"]] = http_codes.get(r["http"], 0) + 1
            api_codes[r["code"]] = api_codes.get(r["code"], 0) + 1

        print(f"\n{'='*60}")
        print(f"RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"Total requests:   {TOTAL_REQUESTS}")
        print(f"Wall clock time:  {wall_elapsed:.2f}s")
        print(f"Req/sec:          {TOTAL_REQUESTS / wall_elapsed:.1f}")
        print(f"Avg latency:      {avg_ms:.0f}ms")
        print(f"Success (100000): {success}")
        print(f"Failed:           {failed}")
        print(f"HTTP status dist: {http_codes}")
        print(f"API code dist:    {api_codes}")

if __name__ == "__main__":
    asyncio.run(main())
