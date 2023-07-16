from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
import uvicorn
from redis.asyncio import Redis

from src.database.redis_db import get_async_redis_client
from src.routes import contacts, auth, users


app = FastAPI()

app.include_router(contacts.router)
app.include_router(auth.router)
app.include_router(users.router)


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the server starts up.
    It's a good place to initialize things that are needed by your application,
    such as connecting to databases or doing expensive calculations.
    
    :return: A coroutine
    :doc-author: Trelent
    """
    redis_client = await get_async_redis_client()
    await FastAPILimiter.init(redis_client)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)