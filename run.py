from fastapi import FastAPI
from contextlib import asynccontextmanager
from bot_init import TOKEN, types, config
import uvicorn
from main import bot, dp


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    webhook_url = f"{config['tg_domain']}/bot/{TOKEN}"
    print(webhook_url)
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != webhook_url:
        await bot.set_webhook(
            url=webhook_url,
            # allowed_updates=["message", "callback_query"]
        )
    yield
    # Clean up the ML models and release the resources
    await bot.session.close()


app = FastAPI(lifespan=lifespan)


@app.post(f'/bot/{TOKEN}')
async def webhook(update: dict) -> None:
    await dp.feed_webhook_update(bot=bot, update=types.Update(**update))


if __name__ == '__main__':
    uvicorn.run('run:app', host='127.0.0.1', port=8000, reload=True)

