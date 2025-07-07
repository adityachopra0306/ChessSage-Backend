import httpx, types, asyncio
from services.chess_api import get_profile, get_games, get_stats

async def test_get_games(num_days=365):
    async with httpx.AsyncClient(headers={"User-Agent": "chess-sage-app"}) as client:

        fake_request = types.SimpleNamespace()
        fake_request.app = types.SimpleNamespace()
        fake_request.app.state = types.SimpleNamespace()
        fake_request.app.state.client = client

        games = await get_games('revamb', num_days, fake_request)
        assert isinstance(games, list)
        assert len(games) > 0
        assert "pgn" in games[0]
        
        return games
    
async def test_get_stats():
    async with httpx.AsyncClient(headers={"User-Agent": "chess-sage-app"}) as client:

        fake_request = types.SimpleNamespace()
        fake_request.app = types.SimpleNamespace()
        fake_request.app.state = types.SimpleNamespace()
        fake_request.app.state.client = client

        stats = await get_stats('revamb', fake_request)
        assert isinstance(stats, dict)
        assert "chess_blitz" in stats or "chess_rapid" in stats
        return stats
        
async def test_get_profile():
    async with httpx.AsyncClient(headers={"User-Agent": "chess-sage-app"}) as client:

        fake_request = types.SimpleNamespace()
        fake_request.app = types.SimpleNamespace()
        fake_request.app.state = types.SimpleNamespace()
        fake_request.app.state.client = client

        profile = await get_profile('revamb', fake_request)
        assert isinstance(profile, dict)
        assert len(profile) > 0
        return profile

async def main():
    profile = await test_get_profile()
    stats = await test_get_stats()
    games = await test_get_games()
    print('The Chess API integrations work correctly.')
    
if __name__ == "__main__":
    asyncio.run(main())