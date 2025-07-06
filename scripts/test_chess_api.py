import httpx, types, asyncio
from services.chess_api import get_profile, get_games, get_stats

async def test_get_games(num_days=365):
    async with httpx.AsyncClient(headers={"User-Agent": "chess-sage-app"}) as client:

        fake_request = types.SimpleNamespace()
        fake_request.app = types.SimpleNamespace()
        fake_request.app.state = types.SimpleNamespace()
        fake_request.app.state.client = client

        games = await get_games('revamb', num_days, fake_request)
        print(f"Fetched {len(games)} recent games.")
        return games
    
async def test_get_stats():
    async with httpx.AsyncClient(headers={"User-Agent": "chess-sage-app"}) as client:

        fake_request = types.SimpleNamespace()
        fake_request.app = types.SimpleNamespace()
        fake_request.app.state = types.SimpleNamespace()
        fake_request.app.state.client = client

        stats = await get_stats('revamb', fake_request)
        print(f"Fetched.")
        return stats

async def test_get_profile():
    async with httpx.AsyncClient(headers={"User-Agent": "chess-sage-app"}) as client:

        fake_request = types.SimpleNamespace()
        fake_request.app = types.SimpleNamespace()
        fake_request.app.state = types.SimpleNamespace()
        fake_request.app.state.client = client

        profile = await get_profile('revamb', fake_request)
        print(f"Fetched.")
        return profile

async def main():
    profile = await test_get_games()
    print(profile)
    
if __name__ == "__main__":
    asyncio.run(main())