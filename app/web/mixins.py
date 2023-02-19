from functools import wraps
from aiohttp.web_exceptions import HTTPForbidden, HTTPUnauthorized
from aiohttp_session import get_session


def login_required(func):
    @wraps(func)
    async def inner(cls):
        if not cls.request.cookies:
            raise HTTPUnauthorized
        session = await get_session(cls.request)
        if not session.get("admin_id"):
            raise HTTPForbidden
        return await func(cls)
    return inner
