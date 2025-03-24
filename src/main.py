import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import bot_config
from src.handlers import add_expense, delete_expense, edit_expense, get_expenses, start
from src.utils import logging


async def main():
    bot = Bot(
        token=bot_config.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )
    dp = Dispatcher(bot=bot, storage=MemoryStorage())

    dp.include_routers(
        start.router, add_expense.router, get_expenses.router, edit_expense.router, delete_expense.router
    )

    logging.logger.info("Бота запущено.")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logging.logger.error(f"Помилка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
