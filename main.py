from fastapi import FastAPI
import httpx
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient(headers={"User-Agent": "chess-sage-app"})
    yield
    await app.state.client.aclose()

app = FastAPI(lifespan = lifespan)

'''
app.include_router(game_review.router)
app.include_router(profile_stats.router)
'''