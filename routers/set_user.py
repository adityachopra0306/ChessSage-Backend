from fastapi import APIRouter
from utils.api_utils import select_key, check_key
from state.user_state import UserConfig, set_user_config, get_user_config


router = APIRouter()

@router.post('/config/{user_id}')
async def set_user(user_id: str, config: UserConfig):
    user_key_used = False

    if config.gemini_key:
        if not (await check_key(config.gemini_key)).get('valid', False):
            return {'status': 'error', 'user_key': False}
        user_key_used = True
    else:
        config.gemini_key = select_key()

    await set_user_config(user_id, config)
    return {'status': 'stored', 'user_key': user_key_used}