import httpx, asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict
from fastapi import Request

async def make_request(url: str, request: Request) -> Dict:
    client: httpx.AsyncClient = request.app.state.client
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
    
async def get_profile(username: str, request: Request) -> Dict:
    url = f"https://api.chess.com/pub/player/{username}"
    return await make_request(url, request)

async def get_stats(username: str, request: Request) -> Dict:
    url = f"https://api.chess.com/pub/player/{username}/stats"
    return await make_request(url, request)

async def get_games(username: str, num_days: int, request: Request) -> List[Dict]:
    archive_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    archive_list = (await make_request(archive_url, request))["archives"]

    cutoff = datetime.now(timezone.utc) - timedelta(days=num_days)
    cutoff_ts = int(cutoff.timestamp())

    filtered_archives = []
    for url in reversed(archive_list):  #latest to oldest
        try:
            _, year, month = url.rsplit('/', 2)
            archive_start = datetime(int(year), int(month), 1)
            archive_end = (archive_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)

            if archive_end.timestamp() >= cutoff_ts:
                filtered_archives.append(url)
            else:
                break
        except:
            continue

    client: httpx.AsyncClient = request.app.state.client
    tasks = [client.get(url) for url in filtered_archives]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
   
    recent_games = []
    for res in responses:
        if isinstance(res, Exception):
            print(f"Error fetching games: {res}")
            continue
        if res.status_code == 200:
            data = res.json()
            for game in data.get("games", []):
                if game.get("end_time", 0) >= cutoff_ts:
                    recent_games.append(game)

    return sorted(recent_games, key=lambda g: g["end_time"], reverse=True)