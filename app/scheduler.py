"""
Task Scheduler
"""

from rocketry import Rocketry

app = Rocketry(execution="async")


# @app.task("every 10 seconds")
# async def test_task():
#     print("Hello from Scheduler!")


if __name__ == "__main__":
    app.run()
