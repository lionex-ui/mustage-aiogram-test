from datetime import datetime
from decimal import Decimal, InvalidOperation

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.keyboards import get_back_reply_button, get_main_menu_reply_buttons
from src.utils import logging
from src.utils.requests import add_expense

router = Router(name=__name__)


class AddExpenseStates(StatesGroup):
    title = State()
    date = State()
    uah = State()


@router.message(F.text == "Додати статтю витрат")
async def handle_add_expense_and_request_title(message: types.Message, state: FSMContext):
    await state.clear()

    logging.logger.info(
        f"Користувач [@{message.from_user.username} | {message.from_user.id}] запустив додавання статті."
    )

    await message.answer(text="Введіть назву:", reply_markup=get_back_reply_button())

    await state.set_state(AddExpenseStates.title)


@router.message(AddExpenseStates.title)
async def handle_title_and_request_date(message: types.Message, state: FSMContext):
    if len(message.text) > 64:
        return await message.answer(text="Введіть назву:", reply_markup=get_back_reply_button())

    logging.logger.info(f"Користувач [@{message.from_user.username} | {message.from_user.id}] ввів назву.")

    await state.update_data(title=message.text)

    await message.answer(text="Введіть дату (дд.мм.рррр):", reply_markup=get_back_reply_button())

    await state.set_state(AddExpenseStates.date)


@router.message(AddExpenseStates.date)
async def handle_date_and_request_uah(message: types.Message, state: FSMContext):
    try:
        raw_date = datetime.strptime(message.text, "%d.%m.%Y")
        date = raw_date.strftime("%Y-%m-%d")
    except ValueError:
        return await message.answer(text="Введіть дату (дд.мм.рррр):", reply_markup=get_back_reply_button())

    logging.logger.info(f"Користувач [@{message.from_user.username} | {message.from_user.id}] ввів дату.")

    await state.update_data(date=date)

    await message.answer(text="Введіть кіл-ть UAH (наприклад, 10.5):", reply_markup=get_back_reply_button())

    await state.set_state(AddExpenseStates.uah)


@router.message(AddExpenseStates.uah)
async def handle_uah_and_send_request_add_expense(message: types.Message, state: FSMContext):
    if len(message.text.replace(".", "")) > 9 or ("." in message.text and len(message.text.split(".")[1]) > 2):
        return await message.answer(text="Введіть кіл-ть UAH (наприклад, 10.5):", reply_markup=get_back_reply_button())

    try:
        Decimal(message.text)
    except InvalidOperation:
        return await message.answer(text="Введіть кіл-ть UAH (наприклад, 10.5):", reply_markup=get_back_reply_button())

    logging.logger.info(f"Користувач [@{message.from_user.username} | {message.from_user.id}] ввів гроші.")

    data = await state.get_data()
    title = data.get("title")
    date = data.get("date")
    uah = message.text
    await state.clear()

    status_code = await add_expense({"telegramId": message.from_user.id, "title": title, "date": date, "uah": uah})
    await message.answer(
        text="Запис додано!" if status_code == 200 else "Щось пішло не так...",
        reply_markup=get_main_menu_reply_buttons(),
    )
