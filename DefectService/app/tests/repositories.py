

import asyncio
from functools import wraps


def run_async_func(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

async def test_uow():
    from app.domain.repositories.uow import BaseUnitOfWork
    uow = BaseUnitOfWork()
    