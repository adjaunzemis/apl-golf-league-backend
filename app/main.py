import asyncio
import uvicorn

from .api import app as app_fastapi
from .scheduler import app as app_rocketry


class Server(uvicorn.Server):

    def handle_exit(self, sig: int, frame) -> None:
        """
        Shut down scheduler when server closes.
        """
        app_rocketry.session.shut_down()
        return super().handle_exit(sig, frame)


async def main():
    """Run API and task scheduler"""
    server = Server(config=uvicorn.Config(app_fastapi, workers=1, loop="asyncio", host="0.0.0.0", port=80))

    api = asyncio.create_task(server.serve())
    sched = asyncio.create_task(app_rocketry.serve())

    await asyncio.wait([sched, api])

if __name__ == "__main__":
    asyncio.run(main())
