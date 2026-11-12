import asyncio

import uvicorn

from app.api import app as app_fastapi


async def main():
    """Run API and task scheduler"""
    server = uvicorn.Server(
        config=uvicorn.Config(
            app_fastapi, workers=1, loop="asyncio", host="0.0.0.0", port=80
        )
    )
    api = asyncio.create_task(server.serve())
    await asyncio.wait([api])


if __name__ == "__main__":
    asyncio.run(main())
