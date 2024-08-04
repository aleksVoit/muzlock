from crud import create_user
from info_handler import send_weather
import asyncio


if __name__ == "__main__":
    asyncio.run(send_weather())
