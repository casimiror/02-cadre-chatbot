from slowapi import Limiter
from slowapi.util import get_remote_address

# Per-IP limits protect the shared LLM API key. Behind a proxy, run uvicorn with
# --proxy-headers so the client IP comes from X-Forwarded-For.
limiter = Limiter(key_func=get_remote_address)
