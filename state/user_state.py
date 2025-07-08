from pydantic import BaseModel
from typing import Optional
from upstash_redis.asyncio import Redis
import os, json, zlib, base64
from datetime import datetime, date
### LOCAL
from dotenv import load_dotenv
load_dotenv()
###

REDIS_URL = os.getenv("REDIS_URL", "")
REDIS_TOKEN = os.getenv("REDIS_TOKEN", "")

DEFAULT_TTL = 3600
RESULTS_TTL = 1200

redis = Redis(url=REDIS_URL, token=REDIS_TOKEN)

def compress_json(data: dict) -> str:
    def default_serializer(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    return base64.b64encode(
        zlib.compress(json.dumps(data, default=default_serializer).encode())
    ).decode()

def decompress_json(data: str) -> str:
    '''
    Returns JSON string of the formed dict for UserInfo after decompression
    '''
    return zlib.decompress(base64.b64decode(data.encode())).decode()


class UserConfig(BaseModel):
    username: str
    tone: str 
    background: str
    response_length: int
    num_days: int
    gemini_key: Optional[str] = None

class UserInfo(BaseModel):
    profile: dict
    stats: dict
    games: dict[str, list[dict]]

async def set_user_config(user_id: str, config: UserConfig):
    await redis.set(f"user:{user_id}:config", config.model_dump_json(), ex=DEFAULT_TTL)

async def get_user_config(user_id: str) -> Optional[UserConfig]:
    raw = await redis.get(f"user:{user_id}:config")
    if not raw:
        return None
    return UserConfig.model_validate_json(raw)


async def set_user_info(user_id: str, info: UserInfo):
    compressed = compress_json(info.model_dump())
    await redis.set(f"user:{user_id}:info", compressed, ex=DEFAULT_TTL)

async def get_user_info(user_id: str) -> Optional[UserInfo]:
    raw = await redis.get(f'user:{user_id}:info')
    if not raw:
        return None
    data = decompress_json(raw)
    return UserInfo.model_validate_json(data)

async def set_user_results_field(user_id: str, field_name: str, value: dict):
    if field_name not in ['basic_stats', 'detailed_stats_rapid', 'detailed_stats_bullet', 'detailed_stats_blitz', 'detailed_stats_daily']:
        raise ValueError("Invalid field_name")
    compressed = compress_json(value)
    await redis.set(f"user:{user_id}:results:{field_name}", compressed, ex=RESULTS_TTL)

async def get_user_results_field(user_id: str, field_name: str) -> Optional[dict]:
    if field_name not in ['basic_stats', 'detailed_stats_rapid', 'detailed_stats_bullet', 'detailed_stats_blitz', 'detailed_stats_daily']:
        raise ValueError("Invalid field_name")
    raw = await redis.get(f"user:{user_id}:results:{field_name}")
    if not raw:
        return None
    return json.loads(decompress_json(raw))