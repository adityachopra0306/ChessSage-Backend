from fastapi import FastAPI
import httpx
from contextlib import asynccontextmanager

from routers import set_user, get_profile_data, get_stats

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient(headers={"User-Agent": "chess-sage-app"}, timeout = 15.0)
    yield
    await app.state.client.aclose()

app = FastAPI(lifespan = lifespan)

app.include_router(set_user.router, prefix = '')
app.include_router(get_profile_data.router, prefix = '')
app.include_router(get_stats.router, prefix = '/stats')

@app.get('/health')
def health_check():
    return {'status': 'healthy'}