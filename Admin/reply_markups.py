import json
import os

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from Database.models import Ad
from Modules.Base.languages import STR
from dotenv import load_dotenv

load_dotenv()

BOT_USERNAME = os.getenv('BOT_USERNAME')


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


def admin_change_lang_file(__: STR):
    user_btn = ReplyKeyboardMarkup(resize_keyboard=True)
    for _ in [
        [__.cancel_t],
    ]:
        user_btn.row(*_)
    return user_btn


def admin_confirm_action_markup(__: STR):
    user_btn = ReplyKeyboardMarkup(resize_keyboard=True)
    for _ in [
        [__.cancel_t, __.confirm_t],
    ]:
        user_btn.row(*_)
    return user_btn


def admin_decline_action_markup(__: STR):
    user_btn = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder=__.write_reason)
    for _ in [
        [__.cancel_t, __.confirm_t],
    ]:
        user_btn.row(*_)
    return user_btn


def admin_main_menu_markup(__: STR):
    user_btn = ReplyKeyboardMarkup(resize_keyboard=True)
    user_btn.row_width = 1
    for _ in __.admin_keyboard:
        user_btn.row(*_)
    return user_btn


def admin_ad_preview_markup(__: STR, user_id, new_ad_id):
    user_keyboard = [
        InlineKeyboardButton("✅", callback_data=f'ADMIN_AD_REVIEW ACCEPT  {user_id} {new_ad_id}'),
        InlineKeyboardButton("❌", callback_data=f'ADMIN_AD_REVIEW DECLINE {user_id} {new_ad_id}')
    ]

    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2
    user_btn.add(*user_keyboard)
    return user_btn


def rent_channel_markup(__: STR, ad_id):
    user_keyboard = [
        InlineKeyboardButton(__.rent_channel_view_photos, url=f'https://t.me/{BOT_USERNAME}?start=ViewImgs{ad_id}'),
    ]

    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2
    user_btn.add(*user_keyboard)
    return user_btn
