from datetime import datetime, timedelta

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from Database.models import Ad
from Modules.Base.languages import STR


def inline_markup(__: STR):
    user_keyboard = [
        InlineKeyboardButton("Button_Text", callback_data=f'')
    ]

    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2
    user_btn.add(*user_keyboard)
    return user_btn


def keyboard_markup(__: STR):
    user_btn = ReplyKeyboardMarkup()
    for _ in [['1', '2'], ['3']]:
        user_btn.row(*_)
    return user_btn


def user_main_menu_markup(__: STR):
    user_btn = ReplyKeyboardMarkup()
    for _ in __.keyboard_main_menu:
        user_btn.row(*_)
    return user_btn


def ads_catygories_markup(__: STR, user_id):
    user_keyboard = [
        [
            InlineKeyboardButton(__.rent_btn, callback_data=f'RENT start value'),
            InlineKeyboardButton(__.room_rent_btn, callback_data=f'ROOM_RENT start value'),
        ],

        [
            InlineKeyboardButton(__.room_applicant_btn, callback_data=f'ROOM_APPLICANT start value'),
            InlineKeyboardButton(__.home_applicant_btn, callback_data=f'HOME_APPLICANT start value'),
         ],

        [
            InlineKeyboardButton(__.meldezettel_btn, callback_data=f'MELDEZETTEL start value'),
            InlineKeyboardButton(__.meldezettel_applicant_btn, callback_data=f'MELDEZETTEL_APPLICANT start value'),
         ],

        [
            InlineKeyboardButton(__.selling_goods_btn, callback_data=f'SELLING_GOODS start value'),
            InlineKeyboardButton(__.buying_goods_btn, callback_data=f'BUYING_GOODS start value'),
         ],

        [
            InlineKeyboardButton(__.selling_cargo_btn, callback_data=f'SELLING_CARGO start value'),
            InlineKeyboardButton(__.buying_cargo_btn, callback_data=f'BUYING_CARGO start value'),
        ],
    ]

    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 3

    for _ in user_keyboard:
        user_btn.row(*_)

    # user_btn.add(*user_keyboard)
    return user_btn


def my_ads_3options_markup(__: STR, user_id):
    user_keyboard = [
        InlineKeyboardButton('PENDING ADS', callback_data=f'OPEN_ADS pending {user_id}'),
        InlineKeyboardButton('ACCEPTED ADS', callback_data=f'OPEN_ADS completed {user_id}'),
        InlineKeyboardButton('EXPIRED ADS', callback_data=f'OPEN_ADS expired {user_id}'),
        InlineKeyboardButton('DECLINED ADS', callback_data=f'OPEN_ADS canceled {user_id}'),
    ]

    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 1
    user_btn.add(*user_keyboard)
    return user_btn


def my_ads_markup(__: STR, user_id, user_ad: Ad, len_user_ads):
    user_keyboard = []

    if len_user_ads > 1:
        user_keyboard.append(InlineKeyboardButton('<<', callback_data=f'AD_BACK {user_id} {user_ad.ad_status.name} {user_ad.id}'))
        user_keyboard.append(InlineKeyboardButton('>>', callback_data=f'AD_FORWARD {user_id} {user_ad.ad_status.name} {user_ad.id}'))

    if user_ad.ad_status.name == 'pending':
        user_keyboard.append(InlineKeyboardButton('DELETE', callback_data=f'AD_DELETE {user_id} {user_ad.id}'))

    if user_ad.ad_status.name == 'completed':
        user_keyboard.append(InlineKeyboardButton('EXPIRE', callback_data=f'AD_EXPIRE {user_id} {user_ad.id}'))

    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2
    user_btn.add(*user_keyboard)
    return user_btn


def confirm_delete_ad_markup(__: STR):
    user_btn = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder=__.rent_hint_text_confirm_or_cancel)
    for _ in [
        [__.cancel_t, __.confirm_t],
    ]:
        user_btn.row(*_)
    return user_btn
