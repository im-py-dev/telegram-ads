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


def cancel_confirm_markup(__: STR):
    user_keyboard = [
        [__.cancel_t, __.confirm_t],
    ]
    user_btn = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def select_city_markup(__: STR, category_key):
    user_keyboard = [
        [InlineKeyboardButton(__.city_1, callback_data=f'{category_key} city city_1')],
        [InlineKeyboardButton(__.city_2, callback_data=f'{category_key} city city_2'),
         InlineKeyboardButton(__.city_3, callback_data=f'{category_key} city city_3')],
        [InlineKeyboardButton(__.city_4, callback_data=f'{category_key} city city_4'),
         InlineKeyboardButton(__.city_5, callback_data=f'{category_key} city city_5'),
         InlineKeyboardButton(__.city_6, callback_data=f'{category_key} city city_6')],
        [InlineKeyboardButton(__.city_other, callback_data=f'{category_key} city other')],
    ]

    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def select_2city_markup(__: STR, category_key):
    user_keyboard = [
        [InlineKeyboardButton(__.buying_cargo_ia_btn, callback_data=f'{category_key} from_to_city buying_cargo_ia'),
         InlineKeyboardButton(__.buying_cargo_ai_btn, callback_data=f'{category_key} from_to_city buying_cargo_ai')],
    ]

    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 2

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def buying_cargo_from_iran_markup(__: STR, category_key):
    # farisi_city_esfehan
    # farisi_city_mashhad
    # farisi_city_tehran
    # farisi_city_karaj
    # farisi_city_shiraz
    # farisi_city_tabriz
    # farisi_city_qom
    # farisi_city_ahvaz
    # farisi_city_kermanshah
    # farisi_city_oromie
    # farisi_city_rasht
    # farisi_city_zahedan
    # farisi_city_hamedan
    # farisi_city_kerman
    # farisi_city_ardabil
    # farisi_city_bandarabbas
    # farisi_city_arak
    # farisi_city_zanjan
    # farisi_city_sanandaj
    # farisi_city_qazvin
    # farisi_city_gorgan
    # farisi_city_sari
    user_keyboard = [
        [
            InlineKeyboardButton(__.farisi_city_esfehan, callback_data=f'{category_key} from_iran farisi_city_esfehan'),
            InlineKeyboardButton(__.farisi_city_mashhad, callback_data=f'{category_key} from_iran farisi_city_mashhad'),
            InlineKeyboardButton(__.farisi_city_tehran, callback_data=f'{category_key} from_iran farisi_city_tehran'),
            InlineKeyboardButton(__.farisi_city_karaj, callback_data=f'{category_key} from_iran farisi_city_karaj'),
         ],
        [
            InlineKeyboardButton(__.farisi_city_shiraz, callback_data=f'{category_key} from_iran farisi_city_shiraz'),
            InlineKeyboardButton(__.farisi_city_tabriz, callback_data=f'{category_key} from_iran farisi_city_tabriz'),
            InlineKeyboardButton(__.farisi_city_qom, callback_data=f'{category_key} from_iran farisi_city_qom'),
            InlineKeyboardButton(__.farisi_city_ahvaz, callback_data=f'{category_key} from_iran farisi_city_ahvaz'),
         ],
        [
            InlineKeyboardButton(__.farisi_city_kermanshah, callback_data=f'{category_key} from_iran farisi_city_kermanshah'),
            InlineKeyboardButton(__.farisi_city_oromie, callback_data=f'{category_key} from_iran farisi_city_oromie'),
            InlineKeyboardButton(__.farisi_city_rasht, callback_data=f'{category_key} from_iran farisi_city_rasht'),
            InlineKeyboardButton(__.farisi_city_zahedan, callback_data=f'{category_key} from_iran farisi_city_zahedan'),
         ],
        [
            InlineKeyboardButton(__.farisi_city_hamedan, callback_data=f'{category_key} from_iran farisi_city_hamedan'),
            InlineKeyboardButton(__.farisi_city_kerman, callback_data=f'{category_key} from_iran farisi_city_kerman'),
            InlineKeyboardButton(__.farisi_city_ardabil, callback_data=f'{category_key} from_iran farisi_city_ardabil'),
            InlineKeyboardButton(__.farisi_city_bandarabbas, callback_data=f'{category_key} from_iran farisi_city_bandarabbas'),
         ],
        [
            InlineKeyboardButton(__.farisi_city_arak, callback_data=f'{category_key} from_iran farisi_city_arak'),
            InlineKeyboardButton(__.farisi_city_zanjan, callback_data=f'{category_key} from_iran farisi_city_zanjan'),
            InlineKeyboardButton(__.farisi_city_sanandaj, callback_data=f'{category_key} from_iran farisi_city_sanandaj'),
            InlineKeyboardButton(__.farisi_city_qazvin, callback_data=f'{category_key} from_iran farisi_city_qazvin'),
         ],
        [
            InlineKeyboardButton(__.farisi_city_gorgan, callback_data=f'{category_key} from_iran farisi_city_gorgan'),
            InlineKeyboardButton(__.farisi_city_sari, callback_data=f'{category_key} from_iran farisi_city_sari'),
         ],

        [InlineKeyboardButton(__.city_other, callback_data=f'{category_key} from_iran other')],
    ]

    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 3

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def buying_cargo_to_austria_markup(__: STR, category_key):
    user_keyboard = [
        [
            InlineKeyboardButton(__.city_1, callback_data=f'{category_key} to_austria city_4'),
            InlineKeyboardButton(__.city_2, callback_data=f'{category_key} to_austria city_5'),
            InlineKeyboardButton(__.city_3, callback_data=f'{category_key} to_austria city_6'),
        ],
        [
            InlineKeyboardButton(__.city_4, callback_data=f'{category_key} to_austria city_4'),
            InlineKeyboardButton(__.city_5, callback_data=f'{category_key} to_austria city_5'),
            InlineKeyboardButton(__.city_6, callback_data=f'{category_key} to_austria city_6'),
        ],

        [InlineKeyboardButton(__.city_other, callback_data=f'{category_key} to_austria other')],
    ]

    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 3

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def buying_cargo_to_iran_markup(__: STR, category_key):
    user_keyboard = [
        [
            InlineKeyboardButton(__.farisi_city_esfehan, callback_data=f'{category_key} to_iran farisi_city_esfehan'),
            InlineKeyboardButton(__.farisi_city_mashhad, callback_data=f'{category_key} to_iran farisi_city_mashhad'),
            InlineKeyboardButton(__.farisi_city_tehran, callback_data=f'{category_key} to_iran farisi_city_tehran'),
            InlineKeyboardButton(__.farisi_city_karaj, callback_data=f'{category_key} to_iran farisi_city_karaj'),
            InlineKeyboardButton(__.farisi_city_shiraz, callback_data=f'{category_key} to_iran farisi_city_shiraz'),
            InlineKeyboardButton(__.farisi_city_tabriz, callback_data=f'{category_key} to_iran farisi_city_tabriz'),
            InlineKeyboardButton(__.farisi_city_qom, callback_data=f'{category_key} to_iran farisi_city_qom'),
            InlineKeyboardButton(__.farisi_city_ahvaz, callback_data=f'{category_key} to_iran farisi_city_ahvaz'),
            InlineKeyboardButton(__.farisi_city_kermanshah, callback_data=f'{category_key} to_iran farisi_city_kermanshah'),
            InlineKeyboardButton(__.farisi_city_oromie, callback_data=f'{category_key} to_iran farisi_city_oromie'),
            InlineKeyboardButton(__.farisi_city_rasht, callback_data=f'{category_key} to_iran farisi_city_rasht'),
            InlineKeyboardButton(__.farisi_city_zahedan, callback_data=f'{category_key} to_iran farisi_city_zahedan'),
            InlineKeyboardButton(__.farisi_city_hamedan, callback_data=f'{category_key} to_iran farisi_city_hamedan'),
            InlineKeyboardButton(__.farisi_city_kerman, callback_data=f'{category_key} to_iran farisi_city_kerman'),
            InlineKeyboardButton(__.farisi_city_ardabil, callback_data=f'{category_key} to_iran farisi_city_ardabil'),
            InlineKeyboardButton(__.farisi_city_bandarabbas, callback_data=f'{category_key} to_iran farisi_city_bandarabbas'),
            InlineKeyboardButton(__.farisi_city_arak, callback_data=f'{category_key} to_iran farisi_city_arak'),
            InlineKeyboardButton(__.farisi_city_zanjan, callback_data=f'{category_key} to_iran farisi_city_zanjan'),
            InlineKeyboardButton(__.farisi_city_sanandaj, callback_data=f'{category_key} to_iran farisi_city_sanandaj'),
            InlineKeyboardButton(__.farisi_city_qazvin, callback_data=f'{category_key} to_iran farisi_city_qazvin'),
            InlineKeyboardButton(__.farisi_city_gorgan, callback_data=f'{category_key} to_iran farisi_city_gorgan'),
            InlineKeyboardButton(__.farisi_city_sari, callback_data=f'{category_key} to_iran farisi_city_sari'),
        ],

        [InlineKeyboardButton(__.city_other, callback_data=f'{category_key} to_iran other')],
    ]

    user_btn = InlineKeyboardMarkup()
    user_btn.row_width = 3

    for _ in user_keyboard:
        user_btn.row(*_)
    return user_btn


def buying_cargo_from_austria_markup(__: STR, category_key):
    user_keyboard = [
        [
            InlineKeyboardButton(__.city_1, callback_data=f'{category_key} from_austria city_1'),
            InlineKeyboardButton(__.city_2, callback_data=f'{category_key} from_austria city_2'),
            InlineKeyboardButton(__.city_3, callback_data=f'{category_key} from_austria city_3'),
         ],
        [
            InlineKeyboardButton(__.city_4, callback_data=f'{category_key} from_austria city_4'),
            InlineKeyboardButton(__.city_5, callback_data=f'{category_key} from_austria city_5'),
            InlineKeyboardButton(__.city_6, callback_data=f'{category_key} from_austria city_6'),
         ],

        [InlineKeyboardButton(__.city_other, callback_data=f'{category_key} from_austria other')],
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
        [InlineKeyboardButton(__.rent_with_contract_btn,
                              callback_data=f'{category_key} contract_status with_contract')],
        [InlineKeyboardButton(__.rent_without_contract_btn,
                              callback_data=f'{category_key} contract_status without_contract')],
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
