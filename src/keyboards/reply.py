from aiogram import types


def get_back_reply_button() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="Назад")]], resize_keyboard=True)


def get_main_menu_reply_buttons() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Додати статтю витрат")],
            [types.KeyboardButton(text="Отримати звіт витрат за вказаний період")],
            [types.KeyboardButton(text="Видалити статтю у списку витрат")],
            [types.KeyboardButton(text="Відредагувати статтю у списку витрат")],
        ],
        resize_keyboard=True,
    )
