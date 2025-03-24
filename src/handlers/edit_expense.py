import os
from decimal import Decimal, InvalidOperation
from uuid import uuid4

import pandas as pd
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.keyboards import get_back_reply_button, get_main_menu_reply_buttons
from src.utils import logging
from src.utils.requests import edit_expense, get_expenses

router = Router(name=__name__)


class EditExpenseStates(StatesGroup):
    expenses = State()
    expense_id = State()
    title = State()
    uah = State()


@router.message(F.text == "Відредагувати статтю у списку витрат")
async def handle_edit_expense_and_request_expense_id(message: types.Message, state: FSMContext):
    await state.clear()

    expenses = await get_expenses({"telegramId": message.from_user.id})

    df = pd.DataFrame(expenses)
    file_path = os.path.join(os.getcwd(), "src", "files", f"{str(uuid4())}.xlsx")
    df.to_excel(file_path, index=False)

    file = types.FSInputFile(file_path)
    await message.answer_document(document=file, reply_markup=get_main_menu_reply_buttons())

    os.remove(file_path)

    logging.logger.info(
        f"Користувач [@{message.from_user.username} | {message.from_user.id}] запустив редагування статті."
    )

    await message.answer(text="Введіть ID:", reply_markup=get_back_reply_button())

    await state.set_state(EditExpenseStates.expense_id)
    await state.update_data(expenses=expenses)


@router.message(EditExpenseStates.expense_id)
async def handle_expense_id_and_request_title(message: types.Message, state: FSMContext):
    try:
        expense_id = int(message.text)
    except ValueError:
        return await message.answer(text="Введіть ID:", reply_markup=get_back_reply_button())

    data = await state.get_data()
    expenses = data.get("expenses")

    is_expense_id_in_expenses = False
    for expense in expenses:
        if expense_id == expense.get("id"):
            is_expense_id_in_expenses = True
            break

    if not is_expense_id_in_expenses:
        return await message.answer(text="Введіть ID:", reply_markup=get_back_reply_button())

    logging.logger.info(f"Користувач [@{message.from_user.username} | {message.from_user.id}] ввів id.")

    await state.update_data(expense_id=expense_id)

    await message.answer(text="Введіть назву:", reply_markup=get_back_reply_button())

    await state.set_state(EditExpenseStates.title)


@router.message(EditExpenseStates.title)
async def handle_title_and_request_uah(message: types.Message, state: FSMContext):
    if len(message.text) > 64:
        return await message.answer(text="Введіть назву:", reply_markup=get_back_reply_button())

    logging.logger.info(f"Користувач [@{message.from_user.username} | {message.from_user.id}] ввів назву.")

    await state.update_data(title=message.text)

    await message.answer(text="Введіть кіл-ть UAH (наприклад, 10.5):", reply_markup=get_back_reply_button())

    await state.set_state(EditExpenseStates.uah)


@router.message(EditExpenseStates.uah)
async def handle_uah_and_send_request_add_expense(message: types.Message, state: FSMContext):
    if len(message.text.replace(".", "")) > 9 or ("." in message.text and len(message.text.split(".")[1]) > 2):
        return await message.answer(text="Введіть кіл-ть UAH (наприклад, 10.5):", reply_markup=get_back_reply_button())

    try:
        Decimal(message.text)
    except InvalidOperation:
        return await message.answer(text="Введіть кіл-ть UAH (наприклад, 10.5):", reply_markup=get_back_reply_button())

    logging.logger.info(f"Користувач [@{message.from_user.username} | {message.from_user.id}] ввів гроші.")

    data = await state.get_data()
    expense_id = data.get("expense_id")
    title = data.get("title")
    uah = message.text
    await state.clear()

    status_code = await edit_expense({"id": expense_id, "telegramId": message.from_user.id, "title": title, "uah": uah})
    await message.answer(
        text="Запис відредаговано!" if status_code == 200 else "Щось пішло не так...",
        reply_markup=get_main_menu_reply_buttons(),
    )
