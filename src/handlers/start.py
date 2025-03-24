from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from src.keyboards import get_main_menu_reply_buttons
from src.utils import logging

router = Router(name=__name__)


@router.message(CommandStart())
@router.message(F.text == "Назад")
async def handle_command_start(message: types.Message, state: FSMContext):
    await state.clear()

    logging.logger.info(f"Користувач [@{message.from_user.username} | {message.from_user.id}] запустив бота.")
    await message.answer(text="Вітаю!", reply_markup=get_main_menu_reply_buttons())
