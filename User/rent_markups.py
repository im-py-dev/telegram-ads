import json
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from Database.models import Ad
from Modules.Base.languages import STR


def cancel_markup(__: STR):
    user_keyboard = [
        [__.cancel_t],
    ]
    user_btn = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def select_city_markup(__: STR, category_key):
    user_keyboard = [
        [InlineKeyboardButton(__.city_1, callback_data=f'{category_key} city city_1')],
        [InlineKeyboardButton(__.city_2, callback_data=f'{category_key} city city_2'), InlineKeyboardButton(__.city_3, callback_data=f'{category_key} city city_3')],
        [InlineKeyboardButton(__.city_4, callback_data=f'{category_key} city city_4'), InlineKeyboardButton(__.city_5, callback_data=f'{category_key} city city_5'), InlineKeyboardButton(__.city_6, callback_data=f'{category_key} city city_6')],
        [InlineKeyboardButton(__.city_other, callback_data=f'{category_key} city other')],
    ]

    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def select_sub_city_markup(__: STR):
    user_keyboard = [
        [__.cancel_t],
        # [__.city_other]
    ]

    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def end_date_markup(__: STR, category_key):
    user_keyboard = [
        [InlineKeyboardButton(__.rent_agreemental, callback_data=f'{category_key} end_date agreemental')],
    ]
    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def contract_status_markup(__: STR, category_key):
    user_keyboard = [
        [InlineKeyboardButton(__.rent_with_contract_btn, callback_data=f'{category_key} contract_status with_contract')],
        [InlineKeyboardButton(__.rent_without_contract_btn, callback_data=f'{category_key} contract_status without_contract')],
    ]
    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def pricing_type_markup(__: STR, category_key):
    user_keyboard = [
        [InlineKeyboardButton(__.rent_daily, callback_data=f'{category_key} pricing_type daily')],
        [InlineKeyboardButton(__.rent_monthly, callback_data=f'{category_key} pricing_type monthly')],
    ]
    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def pricing_markup(__: STR, category_key):
    user_keyboard = [
        [InlineKeyboardButton(__.rent_agreemental, callback_data=f'{category_key} pricing agreemental')],
    ]
    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def description_markup(__: STR, category_key):
    user_keyboard = [
        [InlineKeyboardButton(__.skip_btn, callback_data=f'{category_key} description skip')],
    ]
    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def photos_markup(__: STR, category_key):
    user_keyboard = [
        [InlineKeyboardButton(__.rent_without_photo, callback_data=f'{category_key} photos skip')],
    ]
    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def photo_markup(__: STR, category_key):
    user_keyboard = [
        [InlineKeyboardButton(__.rent_next_step, callback_data=f'{category_key} photo skip')],
    ]
    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def ad_preview_markup(__: STR, category_key):
    user_keyboard = [
        [
            InlineKeyboardButton(__.confirm_t, callback_data=f'{category_key} ad_preview confirm'),
            InlineKeyboardButton(__.cancel_t, callback_data=f'{category_key} ad_preview cancel')
        ],
    ]
    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn
