import os
from datetime import datetime
from uuid import uuid4

import pandas as pd
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.keyboards import get_back_reply_button, get_main_menu_reply_buttons
from src.utils import logging
from src.utils.requests import get_expenses

router = Router(name=__name__)


class GetExpensesStates(StatesGroup):
    from_date = State()
    to_date = State()


@router.message(F.text == "Отримати звіт витрат за вказаний період")
async def handle_get_expenses_and_request_from_date(message: types.Message, state: FSMContext):
    await state.clear()

    logging.logger.info(
        f"Користувач [@{message.from_user.username} | {message.from_user.id}] запустив отримання статей."
    )

    await message.answer(text='Введіть початкову дату (дд.мм.рррр) або "-":', reply_markup=get_back_reply_button())

    await state.set_state(GetExpensesStates.from_date)


@router.message(GetExpensesStates.from_date)
async def handle_from_date_and_request_to_date(message: types.Message, state: FSMContext):
    if message.text == "-":
        from_date = None
    else:
        try:
            raw_date = datetime.strptime(message.text, "%d.%m.%Y")
            from_date = raw_date.strftime("%Y-%m-%d")
        except ValueError:
            return await message.answer(
                text='Введіть початкову дату (дд.мм.рррр) або "-":', reply_markup=get_back_reply_button()
            )

    logging.logger.info("Користувач [@{message.from_user.username} | {message.from_user.id}] ввів початкову дату.")

    await state.update_data(from_date=from_date)

    await message.answer(text='Введіть кінцеву дату (дд.мм.рррр) або "-":', reply_markup=get_back_reply_button())

    await state.set_state(GetExpensesStates.to_date)


@router.message(GetExpensesStates.to_date)
async def handle_to_date_and_request_get_expenses(message: types.Message, state: FSMContext):
    if message.text == "-":
        to_date = None
    else:
        try:
            raw_date = datetime.strptime(message.text, "%d.%m.%Y")
            to_date = raw_date.strftime("%Y-%m-%d")
        except ValueError:
            return await message.answer(
                text='Введіть кінцеву дату (дд.мм.рррр) або "-":', reply_markup=get_back_reply_button()
            )

    logging.logger.info("Користувач [@{message.from_user.username} | {message.from_user.id}] ввів кінцеву дату.")

    data = await state.get_data()
    from_date = data.get("from_date")
    await state.clear()

    params = {"telegramId": message.from_user.id}
    if from_date is not None:
        params["fromDate"] = from_date
    if to_date is not None:
        params["toDate"] = to_date

    expenses = await get_expenses(params)

    df = pd.DataFrame(expenses)
    file_path = os.path.join(os.getcwd(), "src", "files", f"{str(uuid4())}.xlsx")
    df.to_excel(file_path, index=False)

    file = types.FSInputFile(file_path)
    await message.answer_document(document=file, reply_markup=get_main_menu_reply_buttons())

    os.remove(file_path)
