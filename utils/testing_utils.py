import time
import tracemalloc
from functools import wraps
import inspect
import os
from api_utils import check_key

###
from dotenv import load_dotenv
load_dotenv()
###

def profile(include_time=True, include_memory=True):
    def decorator(func):
        is_async = inspect.iscoroutinefunction(func)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if include_memory:
                tracemalloc.start()
            if include_time:
                start = time.perf_counter()

            result = await func(*args, **kwargs)

            print()
            if include_time:
                duration = time.perf_counter() - start
                print(f"⏱ {func.__name__} took {duration:.2f}s")

            if include_memory:
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                print(f"🧠 Memory used: {current / 1024 / 1024:.2f} MB (Current), Peak: {peak / 1024 / 1024:.2f} MB")
            print()

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if include_memory:
                tracemalloc.start()
            if include_time:
                start = time.perf_counter()

            result = func(*args, **kwargs)

            print()
            if include_time:
                duration = time.perf_counter() - start
                print(f"⏱ {func.__name__} took {duration:.2f}s")

            if include_memory:
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                print(f"🧠 Memory used: {current / 1024 / 1024:.2f} MB (Current), Peak: {peak / 1024 / 1024:.2f} MB")
            print()

            return result

        return async_wrapper if is_async else sync_wrapper

    return decorator


def check_keys(user_key = None):
    if user_key:
        return {user_key: check_key(user_key)}

    keys_raw = os.getenv("GEMINI_API_KEYS", "")
    keys = [k.strip() for k in keys_raw.split(",") if k.strip()]
    
    return {key: check_key(key)['valid'] for key in keys}

if __name__ == "__main__":
    print(check_keys())