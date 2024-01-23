from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_ikb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Button1', callback_data='btn_1')]
    ])
    return ikb
