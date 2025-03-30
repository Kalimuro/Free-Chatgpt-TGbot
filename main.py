import asyncio
from aiogram import Bot, Dispatcher
import logging
from utils.handlers import router


# Вообще не трогать этот файл, это запуск бота

async def main():
    bot = Bot(token='')  # Сюда токен вашего бота
    dp = Dispatcher()
    dp.include_router(router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

