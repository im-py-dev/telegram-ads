import time

# from User.reply_markups2 import select_city_markup2, end_date_markup2, contract_status_markup2, pricing_type_markup2, \
#     pricing_markup2, description_markup2, photos_markup2, photo_markup2, ad_preview_markup2, rent_cancel_markup
from config import ADMINS_IDS, force_subscribe_channels, posting_channels

from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import Message, InputFile, CallbackQuery
from telebot.types import User as TUser

from Admin.reply_markups import admin_ad_preview_markup
from User.reply_markups import *
from User.rent_markups import *
# from User.rent2 import start_rent2

from Modules.Base.User import users, TelegramUser
from Modules.Base.languages import set_lang, STR
from Modules.Extra.telethon_checker import check_user_in_channels

from Database.db import Session
from Database.models import User, Ad

_N = '\n'
user_data = {}


def format_number(price):
    if type(price) is str:
        return price

    if price.is_integer():
        return str(int(price))
    else:
        return "{:.2f}".format(price)


def formatted(text: str, data: dict) -> str:
    tmp = text
    for k, v in data.items():
        tmp = tmp.replace(k, str(v))
    return tmp


def bot_answer_or_send(bot: TeleBot, call, text, show_alert=False, url=None, cache_time=3):
    try:
        bot.answer_callback_query(call.id, text=text, show_alert=show_alert, url=url, cache_time=cache_time)
    except ApiTelegramException as _:
        bot.send_message(call.from_user.id, text)
    except Exception as _:
        bot.send_message(call.from_user.id, text)


def get_user(user_id) -> TelegramUser:
    user = users.get(user_id)
    if user:
        return user

    with Session() as session:
        db_user = session.query(User).filter_by(id=user_id).first()
        if db_user:
            return db_user


def update_user(user: TUser, database_user: User):
    with Session() as session:
        # Update all fields if they have changed
        for variable in ['first_name', 'last_name', 'username']:
            if getattr(database_user, variable) != getattr(user, variable):
                setattr(database_user, variable, getattr(user, variable))
        session.commit()


def create_user(message: Message):
    with Session() as session:
        new_user = User(
            id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            language_code=message.from_user.language_code,
        )
        session.add(new_user)
        session.commit()

    # Add to temp
    TelegramUser(new_user)


def user_start(message, bot: TeleBot):
    # logger.warning(message)
    user_id = message.from_user.id

    if len(message.text.split()) > 1:
        command = message.text.split()[1]
        if command.startswith('ViewImgs'):
            _, ad_id = command.split('ViewImgs')
            with Session() as session:
                ad: Ad = session.query(Ad).filter_by(id=ad_id).first()
                ad_photos: list[str] = json.loads(ad.data)['photos']
                for ad_photo in ad_photos:
                    bot.send_photo(chat_id=message.from_user.id, photo=ad_photo)
                return

    # found_user = get_user(user_id)
    # t1 = time.time()
    with Session() as session:
        # Check if the user already exists
        user = session.query(User).filter_by(id=user_id).first()

        if user:
            # update_user(message.from_user, user)
            # Update all fields if they have changed
            for variable in ['first_name', 'last_name', 'username']:
                if getattr(user, variable) != getattr(message.from_user, variable):
                    setattr(user, variable, getattr(message.from_user, variable))
            session.commit()
        else:
            # create_user(message)
            new_user = User(
                id=message.from_user.id,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                username=message.from_user.username,
                language_code=message.from_user.language_code,
            )
            session.add(new_user)
            session.commit()

    __: STR = set_lang(message.from_user.language_code)

    if not check_user_in_channels(user_id):
        return bot.send_message(message.from_user.id, f"{__.subscribe_first_m}\n {_N.join(force_subscribe_channels)}")

    bot.send_message(user_id, __.mm_m, reply_markup=user_main_menu_markup(__))


def user_message(message: Message, bot: TeleBot):
    # logger.warning(message)
    command: str = message.text
    user_id = message.from_user.id
    # user = users.get(user_id)

    with Session() as session:
        # Check if the user already exists
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return bot.send_message(text='/start', chat_id=user_id)

    __ = set_lang(user.language_code)

    if not check_user_in_channels(user_id):
        return bot.send_message(message.from_user.id, f"{__.subscribe_first_m}\n {_N.join(force_subscribe_channels)}")

    if message.text and message.text == __.cancel_t:
        return bot.send_message(message.from_user.id, __.canceled_t, reply_markup=user_main_menu_markup(__))

    # insert Ad
    def command_1():
        bot.send_message(
            user_id,
            __.mm_btn_1a,
            reply_markup=ads_catygories_markup(__, user_id)
        )

    # insert Rules
    def command_2():
        bot.send_message(
            user_id,
            __.mm_btn_2a,
            # reply_markup=ads_catygories_markup(__, user_id)
        )

    # insert Support
    def command_3():
        bot.send_message(
            user_id,
            __.mm_btn_3a,
            # reply_markup=ads_catygories_markup(__, user_id)
        )

    # insert Channels
    def command_4():
        bot.send_message(
            user_id,
            __.mm_btn_4a,
            # reply_markup=ads_catygories_markup(__, user_id)
        )

    # insert Ad
    def command_5():
        bot.send_message(
            user_id,
            __.mm_btn_5a,
            reply_markup=my_ads_3options_markup(__, user_id)
        )

    # not_known_command
    def not_known_command():
        bot.send_message(user_id, 'Unknown Command.')

    __ = set_lang(user.language_code)

    commands = {
        __.mm_btn_1: command_1,
        __.mm_btn_2: command_2,
        __.mm_btn_3: command_3,
        __.mm_btn_4: command_4,
        __.mm_btn_5: command_5,
    }
    func = commands.setdefault(command, not_known_command)
    func()


def user_callback_query(call: CallbackQuery, bot: TeleBot):
    # logger.warning(call)
    global user_data
    user_id = call.from_user.id
    call_str = call.data

    # user_data.setdefault(user_id, {
    #         'id': f'{user_id}_{call.message.id}',
    #         'uid': user_id,
    #         'category': 'buying_cargo',
    #         'user_full_name': call.from_user.full_name,
    #         'product_name': '',
    #         'from_to_city': '',
    #         'city': '',
    #         'city2': '',
    #         'load': '',
    #         'sub_city': '',
    #         'start_date': '',
    #         'end_date': '',
    #         'contract_status': '',
    #         'pricing_type': '',
    #         'price': '',
    #         'description': '',
    #         'photos': [],
    #     })

    def cancel_option(func):
        def wrapper(message: Message, *args, **kwargs):
            if message.text and message.text == __.cancel_t:
                return bot.send_message(message.from_user.id, __.canceled_t, reply_markup=user_main_menu_markup(__))
            return func(message, *args, **kwargs)

        return wrapper

    @cancel_option
    def get_city_name(message, message_to_edit):
        user_data[user_id]['city'] = message.text
        bot.edit_message_text(text=f'{__.city_label}{message.text}', chat_id=user_id, message_id=message_to_edit.id,
                              reply_markup=None)

        msg = bot.send_message(user_id, __.rent_sub_city, reply_markup=None)
        bot.register_next_step_handler(msg, get_sub_city)

    @cancel_option
    def get_city_from_other(message, message_to_edit):
        user_data[user_id]['city'] = message.text
        bot.edit_message_text(text=f'{__.city_label}{message.text}', chat_id=user_id, message_id=message_to_edit.id,
                              reply_markup=None)
        msg = bot.send_message(user_id, __.rent_sub_city, reply_markup=None)
        bot.register_next_step_handler(msg, get_sub_city)

    @cancel_option
    def get_sub_city(message):
        user_data[user_id]['sub_city'] = message.text

        # Get the date of tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        # Format the date in dd/mm/yyyy
        formatted_date = tomorrow.strftime("%d/%m/%Y")
        message_text = formatted(__.rent_start_date, {'[automatic_tomorrow_date]': formatted_date})

        bot.send_message(user_id, message_text, reply_markup=None)
        bot.register_next_step_handler(message, get_start_date)

    @cancel_option
    def get_start_date(message):
        user_data[user_id]['start_date'] = message.text

        # Get the date of tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        # Format the date in dd/mm/yyyy
        formatted_date = tomorrow.strftime("%d/%m/%Y")
        message_text = formatted(__.rent_end_date, {'[automatic_tomorrow_date]': formatted_date})

        msg = bot.send_message(message.from_user.id, message_text, reply_markup=end_date_markup(__, category_key))
        bot.register_next_step_handler(message, get_end_date, msg)

    @cancel_option
    def get_end_date(message, msg):
        user_data[user_id]['end_date'] = message.text
        bot.edit_message_text(text=f'{__.end_date_label}{message.text}', chat_id=user_id, message_id=msg.id,
                              reply_markup=None)

        bot.send_message(message.from_user.id, __.rent_contract_status,
                         reply_markup=contract_status_markup(__, category_key))
        # bot.register_next_step_handler(message, get_contract_status)

    @cancel_option
    def get_contract_status(message):
        # todo from call
        # user_data['contract_status'] = True if message.text == 'With contract' else False
        user_data[user_id]['contract_status'] = message.text
        bot.send_message(message.from_user.id, __.rent_pricing_type, reply_markup=pricing_type_markup(__, category_key))

    @cancel_option
    def get_pricing_type(message):
        # todo add call
        user_data[user_id]['pricing_type'] = message.text

        bot.send_message(message.from_user.id, __.rent_price, reply_markup=pricing_markup(__, category_key))
        bot.register_next_step_handler(message, get_price)
        # bot.clear_step_handler(message)

    @cancel_option
    def get_price(message, msg):
        # if message.text == __.rent_agreemental:
        #     user_data[user_id]['price'] = __.rent_agreemental
        #     bot.send_message(message.from_user.id, __.rent_description, reply_markup=description_markup2(__, ))
        #     return bot.register_next_step_handler(message, get_description)
        try:
            if message.text and float(message.text):
                price = float(message.text)
                user_data[user_id]['price'] = price
                bot.edit_message_text(text=f'{__.price_label}{price}', chat_id=user_id, message_id=msg.id,
                                      reply_markup=None)
                msg = bot.send_message(message.from_user.id, __.rent_description,
                                       reply_markup=description_markup(__, category_key))
                bot.register_next_step_handler(message, get_description, msg)
        except Exception as r:
            bot.send_message(message.from_user.id, __.rent_price)
            bot.register_next_step_handler(message, get_price)

    @cancel_option
    def get_description(message, msg):
        user_data[user_id]['description'] = ''
        if message.text != __.skip_btn:
            user_data[user_id]['description'] = message.text

        bot.edit_message_text(text=f'{__.description_label}{message.text}', chat_id=user_id, message_id=msg.id,
                              reply_markup=None)

        bot.send_message(message.from_user.id, __.rent_photos, reply_markup=photos_markup(__, category_key))
        user_data[user_id]['photos'] = []

        bot.register_next_step_handler(message, get_photos)

    @cancel_option
    def get_photos(message):
        if message.text == __.rent_without_photo:
            user_data[user_id]['photos'] = []
            ad_preview(message)

        elif message.photo:
            user_data[user_id]['photos'].append(message.photo[0].file_id)
            bot.send_message(message.from_user.id, __.rent_photos_done, reply_markup=photo_markup(__, category_key))
            bot.register_next_step_handler(message, get_photo)
        else:
            bot.send_message(message.from_user.id, __.rent_photo_error)
            bot.register_next_step_handler(message, get_photos)

    @cancel_option
    def get_photo(message):
        if message.text == __.rent_next_step:
            ad_preview(message)

        elif message.photo:
            if len(user_data[user_id]['photos']) >= 10:
                # todo handle 10 max
                return ad_preview(message)

            user_data[user_id]['photos'].append(message.photo[0].file_id)
            bot.send_message(message.from_user.id, __.rent_photos_done, reply_markup=photo_markup(__, category_key))
            bot.register_next_step_handler(message, get_photo)

        else:
            bot.send_message(message.from_user.id, __.rent_photo_error2)
            bot.register_next_step_handler(message, get_photos)

    @cancel_option
    def ad_preview(message):
        msg = bot.send_message(user_id, __.rent_creating_ad)

        price_line = f"{__.price_eye}{__.rent_agreemental}" if user_data[user_id]['price'] == __.rent_agreemental else f"{__.price_eye} {format_number(user_data[user_id]['price'])} {__.euros_per} #{user_data[user_id]['pricing_type']}"
        price_line2 = f"{__.price_eye}{__.rent_agreemental}" if user_data[user_id]['price'] == __.rent_agreemental else f"{__.price_eye} {format_number(user_data[user_id]['price'])}"
        print(price_line)
        print(price_line2)
        user_templates_preview = {
            'rent': {
                'template': __.rent_user_preview,
                'template_replacer': {
                    '[city]': user_data[user_id]['city'],
                    '[sub_city]': user_data[user_id]['sub_city'],
                    '[start_date]': user_data[user_id]['start_date'],
                    '[end_date]': user_data[user_id]['end_date'],
                    '[contract_status]': user_data[user_id]['contract_status'],
                    '[price_line]': price_line,
                    '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                    user_data[user_id]['description'] else '',
                }
            },
            'room_rent': {
                'template': __.room_rent_user_preview,
                'template_replacer': {
                    '[city]': user_data[user_id]['city'],
                    '[sub_city]': user_data[user_id]['sub_city'],
                    '[start_date]': user_data[user_id]['start_date'],
                    '[end_date]': user_data[user_id]['end_date'],
                    '[contract_status]': user_data[user_id]['contract_status'],
                    '[price_line]': price_line,
                    '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                    user_data[user_id]['description'] else '',
                }
            },

            'room_applicant': {
                'template': __.room_applicant_user_preview,
                'template_replacer': {
                    '[city]': user_data[user_id]['city'],
                    '[sub_city]': user_data[user_id]['sub_city'],
                    '[start_date]': user_data[user_id]['start_date'],
                    '[end_date]': user_data[user_id]['end_date'],
                    '[contract_status]': user_data[user_id]['contract_status'],
                    '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                    user_data[user_id]['description'] else '',
                }
            },
            'home_applicant': {
                'template': __.home_applicant_user_preview,
                'template_replacer': {
                    '[city]': user_data[user_id]['city'],
                    '[sub_city]': user_data[user_id]['sub_city'],
                    '[start_date]': user_data[user_id]['start_date'],
                    '[end_date]': user_data[user_id]['end_date'],
                    '[contract_status]': user_data[user_id]['contract_status'],
                    '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                    user_data[user_id]['description'] else '',
                }
            },

            'meldezettel_applicant': {
                'template': __.meldezettel_applicant_user_preview,
                'template_replacer': {
                    '[city]': user_data[user_id]['city'],
                    '[sub_city]': user_data[user_id]['sub_city'],
                    '[start_date]': user_data[user_id]['start_date'],
                    '[end_date]': user_data[user_id]['end_date'],
                    # '[contract_status]': user_data[user_id]['contract_status'],
                    # '[price_line]': price_line,
                    '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                    user_data[user_id]['description'] else '',
                }
            },
            'meldezettel': {
                'template': __.meldezettel_user_preview,
                'template_replacer': {
                    '[city]': user_data[user_id]['city'],
                    '[sub_city]': user_data[user_id]['sub_city'],
                    '[start_date]': user_data[user_id]['start_date'],
                    '[end_date]': user_data[user_id]['end_date'],
                    '[contract_status]': user_data[user_id]['contract_status'],
                    '[price_line]': price_line,
                    '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                    user_data[user_id]['description'] else '',
                }
            },

            'selling_goods': {
                'template': __.selling_goods_user_preview,
                'template_replacer': {
                    '[product_name]': user_data[user_id]['product_name'],
                    '[city]': user_data[user_id]['city'],
                    '[sub_city]': user_data[user_id]['sub_city'],
                    # '[start_date]': user_data[user_id]['start_date'],
                    # '[end_date]': user_data[user_id]['end_date'],
                    # '[contract_status]': user_data[user_id]['contract_status'],
                    '[price_line2]': price_line2,
                    '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                    user_data[user_id]['description'] else '',
                }
            },
            'buying_goods': {
                'template': __.buying_goods_user_preview,
                'template_replacer': {
                    '[product_name]': user_data[user_id]['product_name'],
                    '[city]': user_data[user_id]['city'],
                    '[sub_city]': user_data[user_id]['sub_city'],
                    # '[start_date]': user_data[user_id]['start_date'],
                    # '[end_date]': user_data[user_id]['end_date'],
                    # '[contract_status]': user_data[user_id]['contract_status'],
                    '[price_line2]': price_line2,
                    '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                    user_data[user_id]['description'] else '',
                }
            },

            'buying_cargo': {
                'template': __.buying_cargo_user_preview,
                'template_replacer': {
                    '[from_to_city]': user_data[user_id]['from_to_city'],
                    '[start_date]': user_data[user_id]['start_date'],
                    '[city]': user_data[user_id]['city'],
                    '[city2]': user_data[user_id]['city2'],
                    '[load]': user_data[user_id]['load'],
                    '[price]': __.rent_agreemental if user_data[user_id]['price'] == __.rent_agreemental else format_number(
                        user_data[user_id]['price']),
                    '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                    user_data[user_id]['description'] else '',
                }
            },
            'selling_cargo': {
                'template': __.selling_cargo_user_preview,
                'template_replacer': {
                    '[from_to_city]': user_data[user_id]['from_to_city'],
                    '[start_date]': user_data[user_id]['start_date'],
                    '[city]': user_data[user_id]['city'],
                    '[city2]': user_data[user_id]['city2'],
                    '[load]': user_data[user_id]['load'],
                    '[price]': __.rent_agreemental if user_data[user_id]['price'] == __.rent_agreemental else format_number(
                        user_data[user_id]['price']),
                    '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                    user_data[user_id]['description'] else '',
                }
            },

            'buying_euro': {
                'template': __.buying_euro_user_preview,
                'template_replacer': {
                    '[euros]': user_data[user_id]['euros'],
                    '[toman_per_euro]': __.rent_agreemental if user_data[user_id]['toman_per_euro'] == __.rent_agreemental else format_number(
                        user_data[user_id]['toman_per_euro']),
                    '[payment_methods]': ' '.join(map(
                        lambda i: f'#{getattr(__, i)}',
                        user_data[user_id]['payment_methods'])) + f" {user_data[user_id].get('payment_methods_other')}" if user_data[user_id].get('payment_methods_other') else "",
                    '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                    user_data[user_id]['description'] else '',
                }
            },
            'selling_euro': {
                'template': __.selling_euro_user_preview,
                'template_replacer': {
                    '[euros]': user_data[user_id]['euros'],
                    '[toman_per_euro]': __.rent_agreemental if user_data[user_id]['toman_per_euro'] == __.rent_agreemental else format_number(
                        user_data[user_id]['toman_per_euro']),
                    '[payment_methods]': ' '.join(map(
                        lambda i: f'#{getattr(__, i)}',
                        user_data[user_id]['payment_methods'])) + f" {user_data[user_id].get('payment_methods_other')}" if user_data[user_id].get('payment_methods_other') else "",
                    '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                    user_data[user_id]['description'] else '',
                }
            },
        }
        message_template_dict = user_templates_preview.get(user_data[user_id]['category'])
        # message_template_dict = categories_templates_preview.get(pending_ad.category)
        message_template_str = message_template_dict['template']
        message_template_replacer = message_template_dict['template_replacer']
        ad_preview_template = formatted(message_template_str, message_template_replacer)

        if user_data[user_id]['photos']:
            bot.send_photo(photo=user_data[user_id]['photos'][0], caption=ad_preview_template, chat_id=user_id,
                           reply_markup=ad_preview_markup(__, category_key))
        else:
            bot.send_message(text=ad_preview_template, chat_id=user_id,
                             reply_markup=ad_preview_markup(__, category_key))

        if category_key in ['rent', 'room_rent']:
            bot.delete_message(chat_id=user_id, message_id=message.id)

        bot.delete_message(chat_id=user_id, message_id=msg.message_id)
        # bot.register_next_step_handler(message, ad_confirm)

    def ad_confirm(message):
        print(message)
        print(message.text)
        try:
            with session:
                new_ad = Ad(
                    user_id=user.id,
                    category=user_data[user_id]['category'],
                    data=json.dumps(user_data[user_id]),
                )
                session.add(new_ad)
                session.commit()
                ad_id = new_ad.id
        except Exception as r:
            print(r)
            bot.send_message(user_id, text=__.error_t, reply_markup=user_main_menu_markup(__))

        else:
            ad_data = user_data[user_id]

            price_line = f"{__.price_eye}{__.rent_agreemental}" if user_data[user_id][
                                                                       'price'] == __.rent_agreemental else f"{__.price_eye} {format_number(user_data[user_id]['price'])} {__.euros_per} #{user_data[user_id]['pricing_type']}"
            price_line2 = f"{__.price_eye}{__.rent_agreemental}" if user_data[user_id][
                                                                        'price'] == __.rent_agreemental else f"{__.price_eye} {format_number(user_data[user_id]['price'])}"
            admin_templates_preview = {
                'rent': {
                    'template': __.rent_admin_preview,
                    'template_replacer': {
                        '[city]': ad_data['city'],
                        '[sub_city]': ad_data['sub_city'],
                        '[start_date]': ad_data['start_date'],
                        '[end_date]': ad_data['end_date'],
                        '[contract_status]': ad_data['contract_status'],
                        '[price_line]': price_line,
                        '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data[
                            'description'] else '',
                        '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                    }
                },
                'room_rent': {
                    'template': __.room_rent_admin_preview,
                    'template_replacer': {
                        '[city]': ad_data['city'],
                        '[sub_city]': ad_data['sub_city'],
                        '[start_date]': ad_data['start_date'],
                        '[end_date]': ad_data['end_date'],
                        '[contract_status]': ad_data['contract_status'],
                        '[price_line]': price_line,
                        '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data[
                            'description'] else '',
                        '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                    }
                },

                'room_applicant': {
                    'template': __.room_applicant_admin_preview,
                    'template_replacer': {
                        '[city]': ad_data['city'],
                        '[sub_city]': ad_data['sub_city'],
                        '[start_date]': ad_data['start_date'],
                        '[end_date]': ad_data['end_date'],
                        '[contract_status]': ad_data['contract_status'],
                        '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data[
                            'description'] else '',
                        '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                    }
                },
                'home_applicant': {
                    'template': __.home_applicant_admin_preview,
                    'template_replacer': {
                        '[city]': ad_data['city'],
                        '[sub_city]': ad_data['sub_city'],
                        '[start_date]': ad_data['start_date'],
                        '[end_date]': ad_data['end_date'],
                        '[contract_status]': ad_data['contract_status'],
                        '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data[
                            'description'] else '',
                        '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                    }
                },

                'meldezettel_applicant': {
                    'template': __.meldezettel_applicant_admin_preview,
                    'template_replacer': {
                        '[city]': user_data[user_id]['city'],
                        '[sub_city]': user_data[user_id]['sub_city'],
                        '[start_date]': user_data[user_id]['start_date'],
                        '[end_date]': user_data[user_id]['end_date'],
                        # '[contract_status]': user_data[user_id]['contract_status'],
                        # '[price_line]': price_line,
                        '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                        user_data[user_id]['description'] else '',
                        '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                    }
                },
                'meldezettel': {
                    'template': __.meldezettel_admin_preview,
                    'template_replacer': {
                        '[city]': user_data[user_id]['city'],
                        '[sub_city]': user_data[user_id]['sub_city'],
                        '[start_date]': user_data[user_id]['start_date'],
                        '[end_date]': user_data[user_id]['end_date'],
                        '[contract_status]': user_data[user_id]['contract_status'],
                        '[price_line]': price_line,
                        '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                        user_data[user_id]['description'] else '',
                        '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                    }
                },

                'selling_goods': {
                    'template': __.selling_goods_admin_preview,
                    'template_replacer': {
                        '[product_name]': user_data[user_id]['product_name'],
                        '[city]': user_data[user_id]['city'],
                        '[sub_city]': user_data[user_id]['sub_city'],
                        # '[start_date]': user_data[user_id]['start_date'],
                        # '[end_date]': user_data[user_id]['end_date'],
                        # '[contract_status]': user_data[user_id]['contract_status'],
                        '[price_line2]': price_line2,
                        '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                        user_data[user_id]['description'] else '',
                        '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                    }
                },
                'buying_goods': {
                    'template': __.buying_goods_admin_preview,
                    'template_replacer': {
                        '[product_name]': user_data[user_id]['product_name'],
                        '[city]': user_data[user_id]['city'],
                        '[sub_city]': user_data[user_id]['sub_city'],
                        # '[start_date]': user_data[user_id]['start_date'],
                        # '[end_date]': user_data[user_id]['end_date'],
                        # '[contract_status]': user_data[user_id]['contract_status'],
                        '[price_line2]': price_line2,
                        '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if
                        user_data[user_id]['description'] else '',
                        '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                    }
                },

                'buying_cargo': {
                    'template': __.buying_cargo_admin_preview,
                    'template_replacer': {
                        '[from_to_city]': ad_data['from_to_city'],
                        '[start_date]': ad_data['start_date'],
                        '[city]': ad_data['city'],
                        '[city2]': ad_data['city2'],
                        '[load]': ad_data['load'],
                        '[price]': __.rent_agreemental if ad_data['price'] == __.rent_agreemental else format_number(
                            ad_data['price']),
                        '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if
                        ad_data['description'] else '',
                        '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                    }
                },
                'selling_cargo': {
                    'template': __.selling_cargo_admin_preview,
                    'template_replacer': {
                        '[from_to_city]': ad_data['from_to_city'],
                        '[start_date]': ad_data['start_date'],
                        '[city]': ad_data['city'],
                        '[city2]': ad_data['city2'],
                        '[load]': ad_data['load'],
                        '[price]': __.rent_agreemental if ad_data['price'] == __.rent_agreemental else format_number(
                            ad_data['price']),
                        '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if
                        ad_data['description'] else '',
                        '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                    }
                },

                'buying_euro': {
                    'template': __.buying_euro_admin_preview,
                    'template_replacer': {
                        '[euros]': ad_data['euros'],
                        '[toman_per_euro]': __.rent_agreemental if ad_data['toman_per_euro'] == __.rent_agreemental else format_number(ad_data['toman_per_euro']),
                        '[payment_methods]': ' '.join(map(lambda i: f'#{getattr(__, i)}',ad_data['payment_methods'])) + f" {ad_data.get('payment_methods_other')}" if ad_data.get('payment_methods_other') else "",
                        '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if ad_data['description'] else '',
                        '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                    }
                },
                'selling_euro': {
                    'template': __.selling_euro_admin_preview,
                    'template_replacer': {
                        '[euros]': ad_data['euros'],
                        '[toman_per_euro]': __.rent_agreemental if ad_data['toman_per_euro'] == __.rent_agreemental else format_number(ad_data['toman_per_euro']),
                        '[payment_methods]': ' '.join(map(lambda i: f'#{getattr(__, i)}',ad_data['payment_methods'])) + f" {ad_data.get('payment_methods_other')}" if ad_data.get('payment_methods_other') else "",
                        '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if ad_data['description'] else '',
                        '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                    }
                },
            }
            message_template_dict = admin_templates_preview.get(user_data[user_id]['category'])
            # message_template_dict = categories_templates_preview.get(pending_ad.category)
            message_template_str = message_template_dict['template']
            message_template_replacer = message_template_dict['template_replacer']
            admin_preview_template = formatted(message_template_str, message_template_replacer)

            for admin_id in ADMINS_IDS:
                # bot.send_message(admin, f"New AD!, {user_data}", reply_markup=manage_ad_markup(message.from_user.id, "AD", user_data))
                if user_data[user_id]['photos']:
                    bot.send_photo(
                        photo=user_data[user_id]['photos'][0],
                        caption=admin_preview_template,
                        chat_id=admin_id,
                        reply_markup=admin_ad_preview_markup(__, user_id, ad_id)
                    )
                else:
                    bot.send_message(
                        text=admin_preview_template,
                        chat_id=admin_id,
                        reply_markup=admin_ad_preview_markup(__, user_id, ad_id)
                    )

            # Last step: tel user
            if message.text:
                bot.edit_message_text(text=__.rent_thank_you_msg, chat_id=user_id, message_id=message.id,
                                      reply_markup=None)
            elif message.caption:
                bot.edit_message_caption(caption=__.rent_thank_you_msg, chat_id=user_id, message_id=message.id,
                                         reply_markup=None)

            bot.send_message(user_id, text=__.mm_m, reply_markup=user_main_menu_markup(__))

    with Session() as session:
        # Check if the user already exists
        user = session.query(User).filter_by(id=user_id).first()

    __ = set_lang(user.language_code)

    if not check_user_in_channels(user_id):
        return bot.send_message(call.message.from_user.id,
                                f"{__.subscribe_first_m}\n {_N.join(force_subscribe_channels)}")

    if call_str.startswith('TEST FOR SEPRATE FILES'):
        _, step_name, value = call_str.split()
        # start_rent2(step_name, value)

    elif call_str.startswith('RENT'):
        category_key, step_name, value = call_str.split()
        print(call_str)
        print(category_key, step_name, value)

        if step_name == 'start':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            city_markup = select_city_markup(__, category_key)
            bot.delete_message(chat_id=user_id, message_id=call.message.id)
            # bot.edit_message_text(text=__.rent_t1, chat_id=user_id, message_id=call.message.id, reply_markup=None)
            # bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.id, reply_markup=cancel_markup(__))
            bot.send_message(user_id, __.rent_t1, reply_markup=cancel_markup(__))
            time.sleep(0.2)
            msg = bot.send_message(user_id, __.rent_t2, reply_markup=city_markup)
            # bot.add_data(user_id)
            user_data[user_id] = {
                'id': f'{user_id}_{call.message.id}',
                'uid': user_id,
                'category': 'rent',
                'user_full_name': call.from_user.full_name,
                'product_name': '',
                'from_to_city': '',
                'city': '',
                'city2': '',
                'load': '',
                'sub_city': '',
                'start_date': '',
                'end_date': '',
                'contract_status': '',
                'pricing_type': '',
                'price': '',
                'euros': '',
                'toman_per_euro': '',
                'payment_methods': [],
                'description': '',
                'photos': [],
            }
            bot.register_next_step_handler(msg, get_city_name, msg)

        if step_name == 'city':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                bot.register_next_step_handler(call.message, get_city_from_other, call.message)
            else:
                city = getattr(__, value)
                user_data[user_id]['city'] = city
                bot.edit_message_text(text=f'{__.city_label}{city}', chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)

                msg = bot.send_message(user_id, __.rent_sub_city, reply_markup=None)
                bot.register_next_step_handler(msg, get_sub_city)

        if step_name == 'end_date':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['end_date'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.end_date_label}{__.rent_agreemental}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_contract_status, reply_markup=contract_status_markup(__, category_key))

        if step_name == 'contract_status':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            contract_state = __.rent_with_contract if value == "with_contract" else __.rent_without_contract
            user_data[user_id]['contract_status'] = contract_state
            bot.edit_message_text(text=f'{__.contract_state_label}{contract_state}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_pricing_type, reply_markup=pricing_type_markup(__, category_key))

        if step_name == 'pricing_type':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            pricing_type = __.rent_daily if value == "daily" else __.rent_monthly
            user_data[user_id]['pricing_type'] = pricing_type
            msg = bot.edit_message_text(text=f'{__.pricing_type_label}{pricing_type}', chat_id=user_id,
                                        message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_price, reply_markup=pricing_markup(__, category_key))
            return bot.register_next_step_handler(call.message, get_price, msg)

        if step_name == 'pricing':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['price'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.price_label}{__.rent_agreemental}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            msg = bot.send_message(user_id, __.rent_description, reply_markup=description_markup(__, category_key))
            return bot.register_next_step_handler(call.message, get_description, msg)

        if step_name == 'description':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['description'] = ''
            user_data[user_id]['photos'] = []
            bot.edit_message_text(text=f'{__.description_label}{__.skip_btn}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_photos, reply_markup=photos_markup(__, category_key))
            return bot.register_next_step_handler(call.message, get_photos)

        if step_name == 'photos':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)
            user_data[user_id]['photos'] = []

            return ad_preview(call.message)

        if step_name == 'photo':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)
            return ad_preview(call.message)

        if step_name == 'ad_preview':
            if value == 'confirm':
                bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
                return ad_confirm(call.message)
            elif value == 'cancel':
                bot.clear_step_handler(call.message)

                if call.message.text:
                    bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id,
                                          reply_markup=None)
                elif call.message.caption:
                    bot.edit_message_caption(caption=__.rent_order_canceled, chat_id=user_id,
                                             message_id=call.message.id, reply_markup=None)

                # bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id, reply_markup=None)
                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))

    elif call_str.startswith('ROOM_RENT'):
        category_key, step_name, value = call_str.split()
        print(call_str)
        print(category_key, step_name, value)

        if step_name == 'start':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            city_markup = select_city_markup(__, category_key)
            bot.delete_message(chat_id=user_id, message_id=call.message.id)
            bot.send_message(user_id, __.room_rent_t1, reply_markup=cancel_markup(__))
            time.sleep(0.2)
            msg = bot.send_message(user_id, __.room_rent_t2, reply_markup=city_markup)
            user_data[user_id] = {
                'id': f'{user_id}_{call.message.id}',
                'uid': user_id,
                'category': 'room_rent',
                'user_full_name': call.from_user.full_name,
                'product_name': '',
                'from_to_city': '',
                'city': '',
                'city2': '',
                'load': '',
                'sub_city': '',
                'start_date': '',
                'end_date': '',
                'contract_status': '',
                'pricing_type': '',
                'price': '',
                'euros': '',
                'toman_per_euro': '',
                'payment_methods': [],
                'description': '',
                'photos': [],
            }
            bot.register_next_step_handler(msg, get_city_name, msg)

        if step_name == 'city':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                bot.register_next_step_handler(call.message, get_city_from_other, call.message)
            else:
                city = getattr(__, value)
                user_data[user_id]['city'] = city
                bot.edit_message_text(text=f'{__.city_label}{city}', chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)

                msg = bot.send_message(user_id, __.rent_sub_city, reply_markup=None)
                bot.register_next_step_handler(msg, get_sub_city)

        if step_name == 'end_date':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['end_date'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.end_date_label}{__.rent_agreemental}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_contract_status, reply_markup=contract_status_markup(__, category_key))

        if step_name == 'contract_status':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            contract_state = __.rent_with_contract if value == "with_contract" else __.rent_without_contract
            user_data[user_id]['contract_status'] = contract_state
            bot.edit_message_text(text=f'{__.contract_state_label}{contract_state}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_pricing_type, reply_markup=pricing_type_markup(__, category_key))

        if step_name == 'pricing_type':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            pricing_type = __.rent_daily if value == "daily" else __.rent_monthly
            user_data[user_id]['pricing_type'] = pricing_type
            msg = bot.edit_message_text(text=f'{__.pricing_type_label}{pricing_type}', chat_id=user_id,
                                        message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_price, reply_markup=pricing_markup(__, category_key))
            return bot.register_next_step_handler(call.message, get_price, msg)

        if step_name == 'pricing':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['price'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.price_label}{__.rent_agreemental}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            msg = bot.send_message(user_id, __.rent_description, reply_markup=description_markup(__, category_key))
            return bot.register_next_step_handler(call.message, get_description, msg)

        if step_name == 'description':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['description'] = ''
            user_data[user_id]['photos'] = []
            bot.edit_message_text(text=f'{__.description_label}{__.skip_btn}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_photos, reply_markup=photos_markup(__, category_key))
            return bot.register_next_step_handler(call.message, get_photos)

        if step_name == 'photos':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)
            user_data[user_id]['photos'] = []

            return ad_preview(call.message)

        if step_name == 'photo':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)
            return ad_preview(call.message)

        if step_name == 'ad_preview':
            if value == 'confirm':
                bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
                return ad_confirm(call.message)
            elif value == 'cancel':
                bot.clear_step_handler(call.message)

                if call.message.text:
                    bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id,
                                          reply_markup=None)
                elif call.message.caption:
                    bot.edit_message_caption(caption=__.rent_order_canceled, chat_id=user_id,
                                             message_id=call.message.id, reply_markup=None)

                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))

    elif call_str.startswith('ROOM_APPLICANT'):
        category_key, step_name, value = call_str.split()
        print(call_str)
        print(category_key, step_name, value)

        @cancel_option
        def get_description(message, msg):
            user_data[user_id]['description'] = ''
            if message.text != __.skip_btn:
                user_data[user_id]['description'] = message.text

            bot.edit_message_text(text=f'{__.description_label}{message.text}', chat_id=user_id, message_id=msg.id,
                                  reply_markup=None)
            return ad_preview(call.message)
            # bot.send_message(message.from_user.id, __.rent_photos, reply_markup=photos_markup(__, category_key))
            # user_data[user_id]['photos'] = []
            # bot.register_next_step_handler(message, get_photos)

        if step_name == 'start':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            city_markup = select_city_markup(__, category_key)
            bot.delete_message(chat_id=user_id, message_id=call.message.id)
            bot.send_message(user_id, __.room_applicant_t1, reply_markup=cancel_markup(__))
            time.sleep(0.2)
            msg = bot.send_message(user_id, __.room_applicant_t2, reply_markup=city_markup)
            user_data[user_id] = {
                'id': f'{user_id}_{call.message.id}',
                'uid': user_id,
                'category': 'room_applicant',
                'user_full_name': call.from_user.full_name,
                'product_name': '',
                'from_to_city': '',
                'city': '',
                'city2': '',
                'load': '',
                'sub_city': '',
                'start_date': '',
                'end_date': '',
                'contract_status': '',
                'pricing_type': '',
                'price': '',
                'euros': '',
                'toman_per_euro': '',
                'payment_methods': [],
                'description': '',
                'photos': [],
            }
            bot.register_next_step_handler(msg, get_city_name, msg)

        if step_name == 'city':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                bot.register_next_step_handler(call.message, get_city_from_other, call.message)
            else:
                city = getattr(__, value)
                user_data[user_id]['city'] = city
                bot.edit_message_text(text=f'{__.city_label}{city}', chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)

                msg = bot.send_message(user_id, __.rent_sub_city, reply_markup=None)
                bot.register_next_step_handler(msg, get_sub_city)

        if step_name == 'end_date':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['end_date'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.end_date_label}{__.rent_agreemental}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_contract_status, reply_markup=contract_status_markup(__, category_key))

        if step_name == 'contract_status':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            contract_state = __.rent_with_contract if value == "with_contract" else __.rent_without_contract
            user_data[user_id]['contract_status'] = contract_state
            bot.edit_message_text(text=f'{__.contract_state_label}{contract_state}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)
            msg = bot.send_message(user_id, __.rent_description, reply_markup=description_markup(__, category_key))
            return bot.register_next_step_handler(call.message, get_description, msg)
            # bot.send_message(user_id, __.rent_pricing_type, reply_markup=pricing_type_markup(__, category_key))

        if step_name == 'description':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['description'] = ''
            # user_data[user_id]['photos'] = []
            bot.edit_message_text(text=f'{__.description_label}{__.skip_btn}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            return ad_preview(call.message)
            # bot.send_message(user_id, __.rent_photos, reply_markup=photos_markup(__, category_key))
            # return bot.register_next_step_handler(call.message, get_photos)

        if step_name == 'ad_preview':
            if value == 'confirm':
                bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
                return ad_confirm(call.message)
            elif value == 'cancel':
                bot.clear_step_handler(call.message)
                bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))

    elif call_str.startswith('HOME_APPLICANT'):
        category_key, step_name, value = call_str.split()
        print(call_str)
        print(category_key, step_name, value)

        @cancel_option
        def get_description(message, msg):
            user_data[user_id]['description'] = ''
            if message.text != __.skip_btn:
                user_data[user_id]['description'] = message.text

            bot.edit_message_text(text=f'{__.description_label}{message.text}', chat_id=user_id, message_id=msg.id,
                                  reply_markup=None)
            return ad_preview(call.message)
            # bot.send_message(message.from_user.id, __.rent_photos, reply_markup=photos_markup(__, category_key))
            # user_data[user_id]['photos'] = []
            # bot.register_next_step_handler(message, get_photos)

        if step_name == 'start':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            city_markup = select_city_markup(__, category_key)
            bot.delete_message(chat_id=user_id, message_id=call.message.id)
            bot.send_message(user_id, __.home_applicant_t1, reply_markup=cancel_markup(__))
            time.sleep(0.2)
            msg = bot.send_message(user_id, __.home_applicant_t2, reply_markup=city_markup)
            user_data[user_id] = {
                'id': f'{user_id}_{call.message.id}',
                'uid': user_id,
                'category': 'home_applicant',
                'user_full_name': call.from_user.full_name,
                'product_name': '',
                'from_to_city': '',
                'city': '',
                'city2': '',
                'load': '',
                'sub_city': '',
                'start_date': '',
                'end_date': '',
                'contract_status': '',
                'pricing_type': '',
                'price': '',
                'euros': '',
                'toman_per_euro': '',
                'payment_methods': [],
                'description': '',
                'photos': [],
            }
            bot.register_next_step_handler(msg, get_city_name, msg)

        if step_name == 'city':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                bot.register_next_step_handler(call.message, get_city_from_other, call.message)
            else:
                city = getattr(__, value)
                user_data[user_id]['city'] = city
                bot.edit_message_text(text=f'{__.city_label}{city}', chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)

                msg = bot.send_message(user_id, __.rent_sub_city, reply_markup=None)
                bot.register_next_step_handler(msg, get_sub_city)

        if step_name == 'end_date':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['end_date'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.end_date_label}{__.rent_agreemental}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_contract_status, reply_markup=contract_status_markup(__, category_key))

        if step_name == 'contract_status':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            contract_state = __.rent_with_contract if value == "with_contract" else __.rent_without_contract
            user_data[user_id]['contract_status'] = contract_state
            bot.edit_message_text(text=f'{__.contract_state_label}{contract_state}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)
            msg = bot.send_message(user_id, __.rent_description, reply_markup=description_markup(__, category_key))
            return bot.register_next_step_handler(call.message, get_description, msg)
            # bot.send_message(user_id, __.rent_pricing_type, reply_markup=pricing_type_markup(__, category_key))

        if step_name == 'description':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['description'] = ''
            # user_data[user_id]['photos'] = []
            bot.edit_message_text(text=f'{__.description_label}{__.skip_btn}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            return ad_preview(call.message)
            # bot.send_message(user_id, __.rent_photos, reply_markup=photos_markup(__, category_key))
            # return bot.register_next_step_handler(call.message, get_photos)

        if step_name == 'ad_preview':
            if value == 'confirm':
                bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
                return ad_confirm(call.message)
            elif value == 'cancel':
                bot.clear_step_handler(call.message)
                bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))

    elif call_str.startswith('MELDEZETTEL_APPLICANT'):
        category_key, step_name, value = call_str.split()
        print(call_str)
        print(category_key, step_name, value)

        @cancel_option
        def get_description(message, msg):
            user_data[user_id]['description'] = ''
            if message.text != __.skip_btn:
                user_data[user_id]['description'] = message.text

            bot.edit_message_text(text=f'{__.description_label}{message.text}', chat_id=user_id, message_id=msg.id,
                                  reply_markup=None)
            return ad_preview(call.message)
            # bot.send_message(message.from_user.id, __.rent_photos, reply_markup=photos_markup(__, category_key))
            # user_data[user_id]['photos'] = []
            # bot.register_next_step_handler(message, get_photos)

        @cancel_option
        def get_end_date(message, msg):
            print("get_end_date inside")
            user_data[user_id]['end_date'] = message.text
            bot.edit_message_text(text=f'{__.end_date_label}{message.text}', chat_id=user_id, message_id=msg.id,
                                  reply_markup=None)

            msg = bot.send_message(user_id, __.rent_description, reply_markup=description_markup(__, category_key))
            return bot.register_next_step_handler(call.message, get_description, msg)

        if step_name == 'start':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            city_markup = select_city_markup(__, category_key)
            bot.delete_message(chat_id=user_id, message_id=call.message.id)
            bot.send_message(user_id, __.meldezettel_applicant_t1, reply_markup=cancel_markup(__))
            time.sleep(0.2)
            msg = bot.send_message(user_id, __.meldezettel_applicant_t2, reply_markup=city_markup)
            user_data[user_id] = {
                'id': f'{user_id}_{call.message.id}',
                'uid': user_id,
                'category': 'meldezettel_applicant',
                'user_full_name': call.from_user.full_name,
                'product_name': '',
                'from_to_city': '',
                'city': '',
                'city2': '',
                'load': '',
                'sub_city': '',
                'start_date': '',
                'end_date': '',
                'contract_status': '',
                'pricing_type': '',
                'price': '',
                'euros': '',
                'toman_per_euro': '',
                'payment_methods': [],
                'description': '',
                'photos': [],
            }
            bot.register_next_step_handler(msg, get_city_name, msg)

        if step_name == 'city':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                bot.register_next_step_handler(call.message, get_city_from_other, call.message)
            else:
                city = getattr(__, value)
                user_data[user_id]['city'] = city
                bot.edit_message_text(text=f'{__.city_label}{city}', chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)

                msg = bot.send_message(user_id, __.rent_sub_city, reply_markup=None)
                bot.register_next_step_handler(msg, get_sub_city)

        if step_name == 'end_date':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['end_date'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.end_date_label}{__.rent_agreemental}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            # bot.send_message(user_id, __.rent_contract_status, reply_markup=contract_status_markup(__, category_key))
            msg = bot.send_message(user_id, __.rent_description, reply_markup=description_markup(__, category_key))
            return bot.register_next_step_handler(call.message, get_description, msg)

        if step_name == 'description':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['description'] = ''
            # user_data[user_id]['photos'] = []
            bot.edit_message_text(text=f'{__.description_label}{__.skip_btn}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            return ad_preview(call.message)
            # bot.send_message(user_id, __.rent_photos, reply_markup=photos_markup(__, category_key))
            # return bot.register_next_step_handler(call.message, get_photos)

        if step_name == 'ad_preview':
            if value == 'confirm':
                bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
                return ad_confirm(call.message)
            elif value == 'cancel':
                bot.clear_step_handler(call.message)
                bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))

    elif call_str.startswith('MELDEZETTEL'):
        category_key, step_name, value = call_str.split()
        print(call_str)
        print(category_key, step_name, value)

        @cancel_option
        def get_description(message, msg):
            user_data[user_id]['description'] = message.text
            bot.edit_message_text(text=f'{__.description_label}{message.text}', chat_id=user_id, message_id=msg.id,
                                  reply_markup=None)

            ad_preview(message)

        if step_name == 'start':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            city_markup = select_city_markup(__, category_key)
            bot.delete_message(chat_id=user_id, message_id=call.message.id)
            # bot.edit_message_text(text=__.rent_t1, chat_id=user_id, message_id=call.message.id, reply_markup=None)
            # bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.id, reply_markup=cancel_markup(__))
            bot.send_message(user_id, __.meldezettel_t1, reply_markup=cancel_markup(__))
            time.sleep(0.2)
            msg = bot.send_message(user_id, __.meldezettel_t2, reply_markup=city_markup)
            # bot.add_data(user_id)
            user_data[user_id] = {
                'id': f'{user_id}_{call.message.id}',
                'uid': user_id,
                'category': 'meldezettel',
                'user_full_name': call.from_user.full_name,
                'product_name': '',
                'from_to_city': '',
                'city': '',
                'city2': '',
                'load': '',
                'sub_city': '',
                'start_date': '',
                'end_date': '',
                'contract_status': '',
                'pricing_type': '',
                'price': '',
                'euros': '',
                'toman_per_euro': '',
                'payment_methods': [],
                'description': '',
                'photos': [],
            }
            bot.register_next_step_handler(msg, get_city_name, msg)

        if step_name == 'city':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                bot.register_next_step_handler(call.message, get_city_from_other, call.message)
            else:
                city = getattr(__, value)
                user_data[user_id]['city'] = city
                bot.edit_message_text(text=f'{__.city_label}{city}', chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)

                msg = bot.send_message(user_id, __.rent_sub_city, reply_markup=None)
                bot.register_next_step_handler(msg, get_sub_city)

        if step_name == 'end_date':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['end_date'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.end_date_label}{__.rent_agreemental}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_contract_status, reply_markup=contract_status_markup(__, category_key))

        if step_name == 'contract_status':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            contract_state = __.rent_with_contract if value == "with_contract" else __.rent_without_contract
            user_data[user_id]['contract_status'] = contract_state
            bot.edit_message_text(text=f'{__.contract_state_label}{contract_state}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_pricing_type, reply_markup=pricing_type_markup(__, category_key))

        if step_name == 'pricing_type':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            pricing_type = __.rent_daily if value == "daily" else __.rent_monthly
            user_data[user_id]['pricing_type'] = pricing_type
            msg = bot.edit_message_text(text=f'{__.pricing_type_label}{pricing_type}', chat_id=user_id,
                                        message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_price, reply_markup=pricing_markup(__, category_key))
            return bot.register_next_step_handler(call.message, get_price, msg)

        if step_name == 'pricing':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['price'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.price_label}{__.rent_agreemental}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            msg = bot.send_message(user_id, __.rent_description, reply_markup=description_markup(__, category_key))
            return bot.register_next_step_handler(call.message, get_description, msg)

        if step_name == 'description':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['description'] = ''
            user_data[user_id]['photos'] = []
            bot.edit_message_text(text=f'{__.description_label}{__.skip_btn}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            return ad_preview(call.message)

        if step_name == 'ad_preview':
            if value == 'confirm':
                bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
                return ad_confirm(call.message)
            elif value == 'cancel':
                bot.clear_step_handler(call.message)

                if call.message.text:
                    bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id,
                                          reply_markup=None)
                elif call.message.caption:
                    bot.edit_message_caption(caption=__.rent_order_canceled, chat_id=user_id,
                                             message_id=call.message.id, reply_markup=None)

                # bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id, reply_markup=None)
                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))

    elif call_str.startswith('SELLING_GOODS'):
        @cancel_option
        def get_sub_city(message):
            user_data[user_id]['sub_city'] = message.text

            bot.send_message(user_id, __.ask_product_name, reply_markup=None)
            bot.register_next_step_handler(message, get_product_name)

        @cancel_option
        def get_product_name(message):
            user_data[user_id]['product_name'] = message.text

            msg = bot.send_message(message.from_user.id, __.rent_price)
            bot.register_next_step_handler(message, get_price, msg)

        @cancel_option
        def get_price(message, msg):
            try:
                if message.text and float(message.text):
                    price = float(message.text)
                    user_data[user_id]['price'] = price
                    bot.edit_message_text(text=f'{__.price_label}{price}', chat_id=user_id, message_id=msg.id,
                                          reply_markup=None)

                    msg = bot.send_message(message.from_user.id, __.rent_description,
                                           reply_markup=description_markup(__, category_key))
                    bot.register_next_step_handler(message, get_description, msg)
            except Exception as r:
                msg = bot.send_message(message.from_user.id, __.rent_price)
                bot.register_next_step_handler(message, get_price, msg)

        category_key, step_name, value = call_str.split()
        print(call_str)
        print(category_key, step_name, value)

        @cancel_option
        def get_description(message, msg):
            user_data[user_id]['description'] = message.text

            bot.edit_message_text(text=f'{__.description_label}{message.text}', chat_id=user_id, message_id=msg.id,
                                  reply_markup=None)
            return ad_preview(call.message)

        if step_name == 'start':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            city_markup = select_city_markup(__, category_key)
            bot.delete_message(chat_id=user_id, message_id=call.message.id)
            bot.send_message(user_id, __.selling_goods_t1, reply_markup=cancel_markup(__))
            time.sleep(0.2)
            msg = bot.send_message(user_id, __.selling_goods_t2, reply_markup=city_markup)
            user_data[user_id] = {
                'id': f'{user_id}_{call.message.id}',
                'uid': user_id,
                'category': 'selling_goods',
                'product_name': '',
                'user_full_name': call.from_user.full_name,
                'from_to_city': '',
                'city': '',
                'city2': '',
                'load': '',
                'sub_city': '',
                'start_date': '',
                'end_date': '',
                'contract_status': '',
                'pricing_type': '',
                'price': '',
                'euros': '',
                'toman_per_euro': '',
                'payment_methods': [],
                'description': '',
                'photos': [],
            }
            bot.register_next_step_handler(msg, get_city_name, msg)

        if step_name == 'city':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                bot.register_next_step_handler(call.message, get_city_from_other, call.message)
            else:
                city = getattr(__, value)
                user_data[user_id]['city'] = city
                bot.edit_message_text(text=f'{__.city_label}{city}', chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)

                msg = bot.send_message(user_id, __.rent_sub_city, reply_markup=None)
                bot.register_next_step_handler(msg, get_sub_city)

        if step_name == 'description':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['description'] = ''
            bot.edit_message_text(text=f'{__.description_label}{__.skip_btn}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            return ad_preview(call.message)
            # bot.send_message(user_id, __.rent_photos, reply_markup=photos_markup(__, category_key))
            # return bot.register_next_step_handler(call.message, get_photos)

        if step_name == 'ad_preview':
            if value == 'confirm':
                bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
                return ad_confirm(call.message)
            elif value == 'cancel':
                bot.clear_step_handler(call.message)
                bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))

    elif call_str.startswith('BUYING_GOODS'):
        @cancel_option
        def get_sub_city(message):
            user_data[user_id]['sub_city'] = message.text

            bot.send_message(user_id, __.ask_product_name, reply_markup=None)
            bot.register_next_step_handler(message, get_product_name)

        @cancel_option
        def get_product_name(message):
            user_data[user_id]['product_name'] = message.text

            msg = bot.send_message(message.from_user.id, __.rent_price)
            bot.register_next_step_handler(message, get_price, msg)

        @cancel_option
        def get_price(message, msg):
            try:
                if message.text and float(message.text):
                    price = float(message.text)
                    user_data[user_id]['price'] = price
                    bot.edit_message_text(text=f'{__.price_label}{price}', chat_id=user_id, message_id=msg.id,
                                          reply_markup=None)

                    msg = bot.send_message(message.from_user.id, __.rent_description,
                                           reply_markup=description_markup(__, category_key))
                    bot.register_next_step_handler(message, get_description, msg)
            except Exception as r:
                msg = bot.send_message(message.from_user.id, __.rent_price)
                bot.register_next_step_handler(message, get_price, msg)

        category_key, step_name, value = call_str.split()
        print(call_str)
        print(category_key, step_name, value)

        @cancel_option
        def get_description(message, msg):
            user_data[user_id]['description'] = message.text

            bot.edit_message_text(text=f'{__.description_label}{message.text}', chat_id=user_id, message_id=msg.id,
                                  reply_markup=None)
            return ad_preview(call.message)

        if step_name == 'start':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            city_markup = select_city_markup(__, category_key)
            bot.delete_message(chat_id=user_id, message_id=call.message.id)
            bot.send_message(user_id, __.buying_goods_t1, reply_markup=cancel_markup(__))
            time.sleep(0.2)
            msg = bot.send_message(user_id, __.buying_goods_t2, reply_markup=city_markup)
            user_data[user_id] = {
                'id': f'{user_id}_{call.message.id}',
                'uid': user_id,
                'category': 'buying_goods',
                'user_full_name': call.from_user.full_name,
                'product_name': '',
                'from_to_city': '',
                'city': '',
                'city2': '',
                'load': '',
                'sub_city': '',
                'start_date': '',
                'end_date': '',
                'contract_status': '',
                'pricing_type': '',
                'price': '',
                'euros': '',
                'toman_per_euro': '',
                'payment_methods': [],
                'description': '',
                'photos': [],
            }
            bot.register_next_step_handler(msg, get_city_name, msg)

        if step_name == 'city':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                bot.register_next_step_handler(call.message, get_city_from_other, call.message)
            else:
                city = getattr(__, value)
                user_data[user_id]['city'] = city
                bot.edit_message_text(text=f'{__.city_label}{city}', chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)

                msg = bot.send_message(user_id, __.rent_sub_city, reply_markup=None)
                bot.register_next_step_handler(msg, get_sub_city)

        if step_name == 'description':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['description'] = ''
            bot.edit_message_text(text=f'{__.description_label}{__.skip_btn}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            return ad_preview(call.message)
            # bot.send_message(user_id, __.rent_photos, reply_markup=photos_markup(__, category_key))
            # return bot.register_next_step_handler(call.message, get_photos)

        if step_name == 'ad_preview':
            if value == 'confirm':
                bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
                return ad_confirm(call.message)
            elif value == 'cancel':
                bot.clear_step_handler(call.message)
                bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))

    elif call_str.startswith('BUYING_CARGO'):
        category_key, step_name, value = call_str.split()
        print(call_str)
        print(category_key, step_name, value)

        @cancel_option
        def get_flight_date(message):
            user_data[user_id]['start_date'] = message.text

            msg = bot.send_message(message.from_user.id, __.buying_cargo_price, reply_markup=pricing_markup(__, category_key))
            bot.register_next_step_handler(message, get_price, msg)

        @cancel_option
        def get_cargo_load(message, msg):
            try:
                if message.text and int(message.text):
                    load = float(message.text)
                    user_data[user_id]['load'] = load
                    bot.edit_message_text(text=f'{__.buying_cargo_load_label} {load}', chat_id=user_id, message_id=msg.id, reply_markup=None)

                    msg = bot.send_message(user_id, __.rent_description, reply_markup=description_markup(__, category_key))
                    return bot.register_next_step_handler(call.message, get_description, msg)

            except Exception as r:
                msg = bot.send_message(message.from_user.id, __.buying_cargo_load)
                bot.register_next_step_handler(message, get_cargo_load, msg)

        @cancel_option
        def get_description(message, msg):
            user_data[user_id]['description'] = ''
            if message.text != __.skip_btn:
                user_data[user_id]['description'] = message.text

            bot.edit_message_text(text=f'{__.description_label}{message.text}', chat_id=user_id, message_id=msg.id,
                                  reply_markup=None)
            return ad_preview(call.message)

        @cancel_option
        def get_from_city_other(message, message_to_edit):
            user_data[user_id]['city'] = message.text
            bot.edit_message_text(text=f'{__.buying_cargo_origin_label}{message.text}', chat_id=user_id, message_id=message_to_edit.id, reply_markup=None)

            bot.send_message(user_id, __.buying_cargo_destination, reply_markup=buying_cargo_to_austria_markup(__, category_key))

        @cancel_option
        def get_to_city_other(message, message_to_edit):
            user_data[user_id]['city2'] = message.text
            bot.edit_message_text(text=f'{__.buying_cargo_destination_label}{message.text}', chat_id=user_id, message_id=message_to_edit.id, reply_markup=None)

            msg = bot.send_message(user_id, __.buying_cargo_flight_date, reply_markup=None)
            bot.register_next_step_handler(call.message, get_flight_date)

        @cancel_option
        def get_price(message, msg):
            try:
                if message.text and float(message.text):
                    price = float(message.text)
                    user_data[user_id]['price'] = price
                    bot.edit_message_text(text=f'{__.price_label}{price}', chat_id=user_id, message_id=msg.id, reply_markup=None)

                    msg = bot.send_message(message.from_user.id, __.buying_cargo_load)
                    bot.register_next_step_handler(message, get_cargo_load, msg)
            except Exception as r:
                msg = bot.send_message(message.from_user.id, __.buying_cargo_price, reply_markup=pricing_markup(__, category_key))
                bot.register_next_step_handler(message, get_price)

        if step_name == 'start':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            city_markup = select_2city_markup(__, category_key)
            bot.delete_message(chat_id=user_id, message_id=call.message.id)
            # bot.edit_message_text(text=__.rent_t1, chat_id=user_id, message_id=call.message.id, reply_markup=None)
            # bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.id, reply_markup=cancel_markup(__))
            bot.send_message(user_id, __.buying_cargo_t1, reply_markup=cancel_markup(__))
            time.sleep(0.2)
            msg = bot.send_message(user_id, __.buying_cargo_t2, reply_markup=city_markup)
            # bot.add_data(user_id)
            user_data[user_id] = {
                'id': f'{user_id}_{call.message.id}',
                'uid': user_id,
                'category': 'buying_cargo',
                'user_full_name': call.from_user.full_name,
                'product_name': '',
                'from_to_city': '',
                'city': '',
                'city2': '',
                'load': '',
                'sub_city': '',
                'start_date': '',
                'end_date': '',
                'contract_status': '',
                'pricing_type': '',
                'price': '',
                'euros': '',
                'toman_per_euro': '',
                'payment_methods': [],
                'description': '',
                'photos': [],
            }

        elif step_name == 'from_to_city':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'buying_cargo_ia':
                user_data[user_id]['city'] = __.buying_cargo_iran
                user_data[user_id]['city2'] = __.buying_cargo_austria
                user_data[user_id]['from_to_city'] = __.buying_cargo_ia
                bot.edit_message_text(text=f'{__.buying_cargo_od_label} {__.buying_cargo_ia_btn}', chat_id=user_id,
                                      message_id=call.message.id, reply_markup=None)

                msg = bot.send_message(user_id, __.buying_cargo_origin,
                                       reply_markup=buying_cargo_from_iran_markup(__, category_key))

            elif value == 'buying_cargo_ai':
                user_data[user_id]['city'] = __.buying_cargo_austria
                user_data[user_id]['city2'] = __.buying_cargo_iran
                user_data[user_id]['from_to_city'] = __.buying_cargo_ai
                bot.edit_message_text(text=f'{__.buying_cargo_od_label} {__.buying_cargo_ai_btn}', chat_id=user_id,
                                      message_id=call.message.id, reply_markup=None)

                msg = bot.send_message(user_id, __.buying_cargo_origin,
                                       reply_markup=buying_cargo_from_austria_markup(__, category_key))

        elif step_name == 'from_iran':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id, reply_markup=None)
                bot.register_next_step_handler(call.message, get_from_city_other, call.message)

            else:
                city = getattr(__, value)
                user_data[user_id]['city'] = city
                bot.edit_message_text(text=f'{__.buying_cargo_origin_label} {city}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

                msg = bot.send_message(user_id, __.buying_cargo_destination, reply_markup=buying_cargo_to_austria_markup(__, category_key))

        elif step_name == 'from_austria':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id, reply_markup=None)
                bot.register_next_step_handler(call.message, get_from_city_other, call.message)

            else:
                city = getattr(__, value)
                user_data[user_id]['city'] = city
                bot.edit_message_text(text=f'{__.buying_cargo_origin_label} {city}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

                msg = bot.send_message(user_id, __.buying_cargo_destination, reply_markup=buying_cargo_to_iran_markup(__, category_key))

        elif step_name == 'to_austria':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id, reply_markup=None)
                bot.register_next_step_handler(call.message, get_to_city_other, call.message)
            else:
                city = getattr(__, value)
                user_data[user_id]['city2'] = city
                bot.edit_message_text(text=f'{__.buying_cargo_destination_label} {city}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

                msg = bot.send_message(user_id, __.buying_cargo_flight_date, reply_markup=None)
                bot.register_next_step_handler(call.message, get_flight_date)
                # bot.register_next_step_handler(msg, get_sub_city)

        elif step_name == 'to_iran':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id, reply_markup=None)
                bot.register_next_step_handler(call.message, get_to_city_other, call.message)
            else:
                city = getattr(__, value)
                user_data[user_id]['city2'] = city
                bot.edit_message_text(text=f'{__.buying_cargo_destination_label} {city}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

                msg = bot.send_message(user_id, __.buying_cargo_flight_date, reply_markup=None)
                bot.register_next_step_handler(call.message, get_flight_date)
                # bot.register_next_step_handler(msg, get_sub_city)

        elif step_name == 'pricing':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['price'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.price_label}{__.rent_agreemental}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

            msg = bot.send_message(user_id, __.buying_cargo_load)
            return bot.register_next_step_handler(call.message, get_cargo_load, msg)

            # msg = bot.send_message(user_id, __.rent_description, reply_markup=description_markup(__, category_key))
            # return bot.register_next_step_handler(call.message, get_description, msg)

        elif step_name == 'end_date':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['end_date'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.end_date_label}{__.rent_agreemental}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_contract_status, reply_markup=contract_status_markup(__, category_key))

        elif step_name == 'description':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['description'] = ''
            # user_data[user_id]['photos'] = []
            bot.edit_message_text(text=f'{__.description_label}{__.skip_btn}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            return ad_preview(call.message)

        elif step_name == 'ad_preview':
            if value == 'confirm':
                bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
                return ad_confirm(call.message)
            elif value == 'cancel':
                bot.clear_step_handler(call.message)

                if call.message.text:
                    bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id,
                                          reply_markup=None)
                elif call.message.caption:
                    bot.edit_message_caption(caption=__.rent_order_canceled, chat_id=user_id,
                                             message_id=call.message.id, reply_markup=None)

                # bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id, reply_markup=None)
                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))

    elif call_str.startswith('SELLING_CARGO'):
        category_key, step_name, value = call_str.split()
        print(call_str)
        print(category_key, step_name, value)

        @cancel_option
        def get_flight_date(message):
            user_data[user_id]['start_date'] = message.text

            msg = bot.send_message(message.from_user.id, __.buying_cargo_price, reply_markup=pricing_markup(__, category_key))
            bot.register_next_step_handler(message, get_price, msg)

        @cancel_option
        def get_cargo_load(message, msg):
            try:
                if message.text and int(message.text):
                    load = float(message.text)
                    user_data[user_id]['load'] = load
                    bot.edit_message_text(text=f'{__.buying_cargo_load_label} {load}', chat_id=user_id, message_id=msg.id, reply_markup=None)

                    msg = bot.send_message(user_id, __.rent_description, reply_markup=description_markup(__, category_key))
                    return bot.register_next_step_handler(call.message, get_description, msg)

            except Exception as r:
                msg = bot.send_message(message.from_user.id, __.buying_cargo_load)
                bot.register_next_step_handler(message, get_cargo_load, msg)

        @cancel_option
        def get_description(message, msg):
            user_data[user_id]['description'] = ''
            if message.text != __.skip_btn:
                user_data[user_id]['description'] = message.text

            bot.edit_message_text(text=f'{__.description_label}{message.text}', chat_id=user_id, message_id=msg.id,
                                  reply_markup=None)
            return ad_preview(call.message)

        @cancel_option
        def get_from_city_other(message, message_to_edit):
            user_data[user_id]['city'] = message.text
            bot.edit_message_text(text=f'{__.buying_cargo_origin_label}{message.text}', chat_id=user_id, message_id=message_to_edit.id, reply_markup=None)

            bot.send_message(user_id, __.buying_cargo_destination, reply_markup=buying_cargo_to_austria_markup(__, category_key))

        @cancel_option
        def get_to_city_other(message, message_to_edit):
            user_data[user_id]['city2'] = message.text
            bot.edit_message_text(text=f'{__.buying_cargo_destination_label}{message.text}', chat_id=user_id, message_id=message_to_edit.id, reply_markup=None)

            msg = bot.send_message(user_id, __.buying_cargo_flight_date, reply_markup=None)
            bot.register_next_step_handler(call.message, get_flight_date)

        @cancel_option
        def get_price(message, msg):
            try:
                if message.text and float(message.text):
                    price = float(message.text)
                    user_data[user_id]['price'] = price
                    bot.edit_message_text(text=f'{__.price_label}{price}', chat_id=user_id, message_id=msg.id, reply_markup=None)

                    msg = bot.send_message(message.from_user.id, __.buying_cargo_load)
                    bot.register_next_step_handler(message, get_cargo_load, msg)
            except Exception as r:
                msg = bot.send_message(message.from_user.id, __.buying_cargo_price, reply_markup=pricing_markup(__, category_key))
                bot.register_next_step_handler(message, get_price)

        if step_name == 'start':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            city_markup = select_2city_markup(__, category_key)
            bot.delete_message(chat_id=user_id, message_id=call.message.id)
            # bot.edit_message_text(text=__.rent_t1, chat_id=user_id, message_id=call.message.id, reply_markup=None)
            # bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.id, reply_markup=cancel_markup(__))
            bot.send_message(user_id, __.selling_cargo_t1, reply_markup=cancel_markup(__))
            time.sleep(0.2)
            msg = bot.send_message(user_id, __.selling_cargo_t2, reply_markup=city_markup)
            # bot.add_data(user_id)
            user_data[user_id] = {
                'id': f'{user_id}_{call.message.id}',
                'uid': user_id,
                'category': 'selling_cargo',
                'user_full_name': call.from_user.full_name,
                'product_name': '',
                'from_to_city': '',
                'city': '',
                'city2': '',
                'load': '',
                'sub_city': '',
                'start_date': '',
                'end_date': '',
                'contract_status': '',
                'pricing_type': '',
                'price': '',
                'euros': '',
                'toman_per_euro': '',
                'payment_methods': [],
                'description': '',
                'photos': [],
            }

        elif step_name == 'from_to_city':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'buying_cargo_ia':
                user_data[user_id]['city'] = __.buying_cargo_iran
                user_data[user_id]['city2'] = __.buying_cargo_austria
                user_data[user_id]['from_to_city'] = __.buying_cargo_ia
                bot.edit_message_text(text=f'{__.buying_cargo_od_label} {__.buying_cargo_ia_btn}', chat_id=user_id,
                                      message_id=call.message.id, reply_markup=None)

                msg = bot.send_message(user_id, __.buying_cargo_origin,
                                       reply_markup=buying_cargo_from_iran_markup(__, category_key))

            elif value == 'buying_cargo_ai':
                user_data[user_id]['city'] = __.buying_cargo_austria
                user_data[user_id]['city2'] = __.buying_cargo_iran
                user_data[user_id]['from_to_city'] = __.buying_cargo_ai
                bot.edit_message_text(text=f'{__.buying_cargo_od_label} {__.buying_cargo_ai_btn}', chat_id=user_id,
                                      message_id=call.message.id, reply_markup=None)

                msg = bot.send_message(user_id, __.buying_cargo_origin,
                                       reply_markup=buying_cargo_from_austria_markup(__, category_key))

        elif step_name == 'from_iran':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id, reply_markup=None)
                bot.register_next_step_handler(call.message, get_from_city_other, call.message)

            else:
                city = getattr(__, value)
                user_data[user_id]['city'] = city
                bot.edit_message_text(text=f'{__.buying_cargo_origin_label} {city}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

                msg = bot.send_message(user_id, __.buying_cargo_destination, reply_markup=buying_cargo_to_austria_markup(__, category_key))

        elif step_name == 'from_austria':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id, reply_markup=None)
                bot.register_next_step_handler(call.message, get_from_city_other, call.message)

            else:
                city = getattr(__, value)
                user_data[user_id]['city'] = city
                bot.edit_message_text(text=f'{__.buying_cargo_origin_label} {city}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

                msg = bot.send_message(user_id, __.buying_cargo_destination, reply_markup=buying_cargo_to_iran_markup(__, category_key))

        elif step_name == 'to_austria':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id, reply_markup=None)
                bot.register_next_step_handler(call.message, get_to_city_other, call.message)
            else:
                city = getattr(__, value)
                user_data[user_id]['city2'] = city
                bot.edit_message_text(text=f'{__.buying_cargo_destination_label} {city}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

                msg = bot.send_message(user_id, __.buying_cargo_flight_date, reply_markup=None)
                bot.register_next_step_handler(call.message, get_flight_date)
                # bot.register_next_step_handler(msg, get_sub_city)

        elif step_name == 'to_iran':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id, reply_markup=None)
                bot.register_next_step_handler(call.message, get_to_city_other, call.message)
            else:
                city = getattr(__, value)
                user_data[user_id]['city2'] = city
                bot.edit_message_text(text=f'{__.buying_cargo_destination_label} {city}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

                msg = bot.send_message(user_id, __.buying_cargo_flight_date, reply_markup=None)
                bot.register_next_step_handler(call.message, get_flight_date)
                # bot.register_next_step_handler(msg, get_sub_city)

        elif step_name == 'pricing':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['price'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.price_label}{__.rent_agreemental}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

            msg = bot.send_message(user_id, __.buying_cargo_load)
            return bot.register_next_step_handler(call.message, get_cargo_load, msg)

            # msg = bot.send_message(user_id, __.rent_description, reply_markup=description_markup(__, category_key))
            # return bot.register_next_step_handler(call.message, get_description, msg)

        elif step_name == 'end_date':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['end_date'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.end_date_label}{__.rent_agreemental}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_contract_status, reply_markup=contract_status_markup(__, category_key))

        elif step_name == 'description':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['description'] = ''
            # user_data[user_id]['photos'] = []
            bot.edit_message_text(text=f'{__.description_label}{__.skip_btn}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            return ad_preview(call.message)

        elif step_name == 'ad_preview':
            if value == 'confirm':
                bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
                return ad_confirm(call.message)
            elif value == 'cancel':
                bot.clear_step_handler(call.message)

                if call.message.text:
                    bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id,
                                          reply_markup=None)
                elif call.message.caption:
                    bot.edit_message_caption(caption=__.rent_order_canceled, chat_id=user_id,
                                             message_id=call.message.id, reply_markup=None)

                # bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id, reply_markup=None)
                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))

    elif call_str.startswith('BUYING_EURO'):
        @cancel_option
        def get_euros(message, msg):
            try:
                if message.text and int(message.text):
                    euros = int(message.text)
                    user_data[user_id]['euros'] = euros
                    bot.edit_message_text(text=f'{__.price_label}{euros}', chat_id=user_id, message_id=msg.id, reply_markup=None)

                    msg = bot.send_message(message.from_user.id, __.buying_euro_tomans, reply_markup=tomans_markup(__, category_key))
                    bot.register_next_step_handler(message, get_tomans, msg)
            except Exception as r:
                msg = bot.send_message(message.from_user.id, __.rent_price)
                bot.register_next_step_handler(message, get_euros, msg)

        @cancel_option
        def get_tomans(message, msg):
            try:
                if message.text and int(message.text):
                    toman_per_euro = int(message.text)
                    user_data[user_id]['toman_per_euro'] = toman_per_euro
                    bot.edit_message_text(text=f'{__.toman_per_euro_label}{toman_per_euro}', chat_id=user_id, message_id=msg.id, reply_markup=None)

                    transfer_methods = {
                        'euro_transfer_1': 0,
                        'euro_transfer_2': 0,
                        'euro_transfer_3': 0,
                        'euro_transfer_4': 0,
                        'euro_transfer_5': 0,
                        'euro_transfer_6': 0,
                        'euro_transfer_7': 0,
                        # 'euro_transfer_8': 0,
                    }
                    msg = bot.send_message(user_id, __.buying_euro_transfer, reply_markup=transfer_markup(__, category_key, transfer_methods))
                    # bot.register_next_step_handler(message, get_transfer, msg)
            except Exception as r:
                print(r)
                msg = bot.send_message(message.from_user.id, __.buying_euro_tomans)
                bot.register_next_step_handler(message, get_tomans, msg)

        category_key, step_name, value, *_ = call_str.split()
        print(call_str)
        print(category_key, step_name, value)

        @cancel_option
        def get_description(message, msg):
            user_data[user_id]['description'] = message.text

            bot.edit_message_text(text=f'{__.description_label}{message.text}', chat_id=user_id, message_id=msg.id, reply_markup=None)
            return ad_preview(call.message)

        if step_name == 'start':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            city_markup = select_city_markup(__, category_key)
            bot.delete_message(chat_id=user_id, message_id=call.message.id)
            bot.send_message(user_id, __.buying_euro_t1, reply_markup=cancel_markup(__))
            time.sleep(0.2)
            msg = bot.send_message(user_id, __.buying_euro_t2)
            user_data[user_id] = {
                'id': f'{user_id}_{call.message.id}',
                'uid': user_id,
                'category': 'buying_euro',
                'user_full_name': call.from_user.full_name,
                'product_name': '',
                'from_to_city': '',
                'city': '',
                'city2': '',
                'load': '',
                'sub_city': '',
                'start_date': '',
                'end_date': '',
                'contract_status': '',
                'pricing_type': '',
                'price': '',
                'euros': '',
                'toman_per_euro': '',
                'payment_methods': [],
                'description': '',
                'photos': [],
            }
            bot.register_next_step_handler(msg, get_euros, msg)

        elif step_name == 'tomans':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['toman_per_euro'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.toman_per_euro_label}{__.rent_agreemental}', chat_id=user_id, message_id=call.message.id, reply_markup=None)
            transfer_methods = {
                'euro_transfer_1': 0,
                'euro_transfer_2': 0,
                'euro_transfer_3': 0,
                'euro_transfer_4': 0,
                'euro_transfer_5': 0,
                'euro_transfer_6': 0,
                'euro_transfer_7': 0,
                # 'euro_transfer_8': 0,
            }
            msg = bot.send_message(user_id, __.buying_euro_transfer, reply_markup=transfer_markup(__, category_key, transfer_methods))
            # return bot.register_next_step_handler(call.message, get_transfer, msg)

        elif step_name == 'transfer':
            *_, payment_name, payment_state = call_str.split()

            if payment_name == 'NEXT':
                bot.edit_message_text(text=__.rent_description, chat_id=user_id, message_id=call.message.id, reply_markup=description_markup(__, category_key))
                return bot.register_next_step_handler(call.message, get_description, call.message)

            elif payment_name == 'OTHER':
                def handle_other_transfer(message, ):
                    user_data[user_id]['payment_methods_other'] = message.text

                    transfer_methods = {
                        'euro_transfer_1': 0,
                        'euro_transfer_2': 0,
                        'euro_transfer_3': 0,
                        'euro_transfer_4': 0,
                        'euro_transfer_5': 0,
                        'euro_transfer_6': 0,
                        'euro_transfer_7': 0,
                        # 'euro_transfer_8': 0,
                    }
                    for _ in user_data[user_id]['payment_methods']:
                        try:
                            getattr(__, _)
                            transfer_methods[_] = 1
                        except AttributeError:
                            continue

                    bot.edit_message_reply_markup(
                        chat_id=user_id,
                        message_id=call.message.id,
                        reply_markup=transfer_markup(__, category_key, transfer_methods, other_done=True)
                    )
                    bot.send_message(user_id, f'{__.other_transfer_label_set} {message.text}')
                    return bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)

                if user_data[user_id].get('payment_methods_other'):
                    return bot_answer_or_send(bot, call, 'ALREADY SELECTED!', show_alert=True, cache_time=2)

                bot.send_message(user_id, __.other_transfer_label)
                return bot.register_next_step_handler(call.message, handle_other_transfer)

            else:
                if payment_state == '1':
                    user_data[user_id]['payment_methods'].remove(payment_name)

                elif payment_state == '0':
                    user_data[user_id]['payment_methods'].append(payment_name)

                transfer_methods = {
                    'euro_transfer_1': 0,
                    'euro_transfer_2': 0,
                    'euro_transfer_3': 0,
                    'euro_transfer_4': 0,
                    'euro_transfer_5': 0,
                    'euro_transfer_6': 0,
                    'euro_transfer_7': 0,
                    # 'euro_transfer_8': 0,
                }
                for _ in user_data[user_id]['payment_methods']:
                    try:
                        getattr(__, _)
                        transfer_methods[_] = 1
                    except AttributeError:
                        continue

                bot.edit_message_reply_markup(
                    chat_id=user_id,
                    message_id=call.message.id,
                    reply_markup=transfer_markup(__, category_key, transfer_methods)
                )
                return bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)

        elif step_name == 'description':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['description'] = ''
            bot.edit_message_text(text=f'{__.description_label}{__.skip_btn}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            return ad_preview(call.message)
            # bot.send_message(user_id, __.rent_photos, reply_markup=photos_markup(__, category_key))
            # return bot.register_next_step_handler(call.message, get_photos)

        elif step_name == 'ad_preview':
            if value == 'confirm':
                bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
                return ad_confirm(call.message)
            elif value == 'cancel':
                bot.clear_step_handler(call.message)
                bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))

    elif call_str.startswith('SELLING_EURO'):
        @cancel_option
        def get_euros(message, msg):
            try:
                if message.text and int(message.text):
                    euros = int(message.text)
                    user_data[user_id]['euros'] = euros
                    bot.edit_message_text(text=f'{__.price_label}{euros}', chat_id=user_id, message_id=msg.id, reply_markup=None)

                    msg = bot.send_message(message.from_user.id, __.selling_euro_tomans, reply_markup=tomans_markup(__, category_key))
                    bot.register_next_step_handler(message, get_tomans, msg)
            except Exception as r:
                msg = bot.send_message(message.from_user.id, __.rent_price)
                bot.register_next_step_handler(message, get_euros, msg)

        @cancel_option
        def get_tomans(message, msg):
            try:
                if message.text and int(message.text):
                    toman_per_euro = int(message.text)
                    user_data[user_id]['toman_per_euro'] = toman_per_euro
                    bot.edit_message_text(text=f'{__.toman_per_euro_label}{toman_per_euro}', chat_id=user_id, message_id=msg.id, reply_markup=None)

                    transfer_methods = {
                        'euro_transfer_1': 0,
                        'euro_transfer_2': 0,
                        'euro_transfer_3': 0,
                        'euro_transfer_4': 0,
                        'euro_transfer_5': 0,
                        'euro_transfer_6': 0,
                        'euro_transfer_7': 0,
                        # 'euro_transfer_8': 0,
                    }
                    msg = bot.send_message(user_id, __.selling_euro_transfer, reply_markup=transfer_markup(__, category_key, transfer_methods))
                    # bot.register_next_step_handler(message, get_transfer, msg)
            except Exception as r:
                print(r)
                msg = bot.send_message(message.from_user.id, __.selling_euro_tomans)
                bot.register_next_step_handler(message, get_tomans, msg)

        category_key, step_name, value, *_ = call_str.split()
        print(call_str)
        print(category_key, step_name, value)

        @cancel_option
        def get_description(message, msg):
            user_data[user_id]['description'] = message.text

            bot.edit_message_text(text=f'{__.description_label}{message.text}', chat_id=user_id, message_id=msg.id, reply_markup=None)
            return ad_preview(call.message)

        if step_name == 'start':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            city_markup = select_city_markup(__, category_key)
            bot.delete_message(chat_id=user_id, message_id=call.message.id)
            bot.send_message(user_id, __.selling_euro_t1, reply_markup=cancel_markup(__))
            time.sleep(0.2)
            msg = bot.send_message(user_id, __.selling_euro_t2)
            user_data[user_id] = {
                'id': f'{user_id}_{call.message.id}',
                'uid': user_id,
                'category': 'selling_euro',
                'user_full_name': call.from_user.full_name,
                'product_name': '',
                'from_to_city': '',
                'city': '',
                'city2': '',
                'load': '',
                'sub_city': '',
                'start_date': '',
                'end_date': '',
                'contract_status': '',
                'pricing_type': '',
                'price': '',
                'euros': '',
                'toman_per_euro': '',
                'payment_methods': [],
                'description': '',
                'photos': [],
            }
            bot.register_next_step_handler(msg, get_euros, msg)

        elif step_name == 'tomans':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['toman_per_euro'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.toman_per_euro_label}{__.rent_agreemental}', chat_id=user_id, message_id=call.message.id, reply_markup=None)
            transfer_methods = {
                'euro_transfer_1': 0,
                'euro_transfer_2': 0,
                'euro_transfer_3': 0,
                'euro_transfer_4': 0,
                'euro_transfer_5': 0,
                'euro_transfer_6': 0,
                'euro_transfer_7': 0,
                # 'euro_transfer_8': 0,
            }
            msg = bot.send_message(user_id, __.selling_euro_transfer, reply_markup=transfer_markup(__, category_key, transfer_methods))
            # return bot.register_next_step_handler(call.message, get_transfer, msg)

        elif step_name == 'transfer':
            *_, payment_name, payment_state = call_str.split()

            if payment_name == 'NEXT':
                bot.edit_message_text(text=__.rent_description, chat_id=user_id, message_id=call.message.id, reply_markup=description_markup(__, category_key))
                return bot.register_next_step_handler(call.message, get_description, call.message)

            elif payment_name == 'OTHER':
                def handle_other_transfer(message, ):
                    user_data[user_id]['payment_methods_other'] = message.text

                    transfer_methods = {
                        'euro_transfer_1': 0,
                        'euro_transfer_2': 0,
                        'euro_transfer_3': 0,
                        'euro_transfer_4': 0,
                        'euro_transfer_5': 0,
                        'euro_transfer_6': 0,
                        'euro_transfer_7': 0,
                        # 'euro_transfer_8': 0,
                    }
                    for _ in user_data[user_id]['payment_methods']:
                        try:
                            getattr(__, _)
                            transfer_methods[_] = 1
                        except AttributeError:
                            continue

                    bot.edit_message_reply_markup(
                        chat_id=user_id,
                        message_id=call.message.id,
                        reply_markup=transfer_markup(__, category_key, transfer_methods, other_done=True)
                    )
                    bot.send_message(user_id, f'{__.other_transfer_label_set} {message.text}')
                    return bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)

                if user_data[user_id].get('payment_methods_other'):
                    return bot_answer_or_send(bot, call, 'ALREADY SELECTED!', show_alert=True, cache_time=2)

                bot.send_message(user_id, __.other_transfer_label)
                return bot.register_next_step_handler(call.message, handle_other_transfer)

            else:
                if payment_state == '1':
                    user_data[user_id]['payment_methods'].remove(payment_name)

                elif payment_state == '0':
                    user_data[user_id]['payment_methods'].append(payment_name)

                transfer_methods = {
                    'euro_transfer_1': 0,
                    'euro_transfer_2': 0,
                    'euro_transfer_3': 0,
                    'euro_transfer_4': 0,
                    'euro_transfer_5': 0,
                    'euro_transfer_6': 0,
                    'euro_transfer_7': 0,
                    # 'euro_transfer_8': 0,
                }
                for _ in user_data[user_id]['payment_methods']:
                    try:
                        getattr(__, _)
                        transfer_methods[_] = 1
                    except AttributeError:
                        continue

                bot.edit_message_reply_markup(
                    chat_id=user_id,
                    message_id=call.message.id,
                    reply_markup=transfer_markup(__, category_key, transfer_methods)
                )
                return bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)

        elif step_name == 'description':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['description'] = ''
            bot.edit_message_text(text=f'{__.description_label}{__.skip_btn}', chat_id=user_id,
                                  message_id=call.message.id, reply_markup=None)

            return ad_preview(call.message)
            # bot.send_message(user_id, __.rent_photos, reply_markup=photos_markup(__, category_key))
            # return bot.register_next_step_handler(call.message, get_photos)

        elif step_name == 'ad_preview':
            if value == 'confirm':
                bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
                return ad_confirm(call.message)
            elif value == 'cancel':
                bot.clear_step_handler(call.message)
                bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id,
                                      reply_markup=None)
                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))

    # SERVICES
    # NEEDS
    elif call_str.startswith('OPEN_ADS'):

        _, ads_state, user_id = call_str.split()

        user_ads: list[Ad] = session.query(Ad).filter_by(user=user, ad_status=ads_state).all()

        if not user_ads:
            return bot_answer_or_send(bot, call, f'You Dont have Ads in this state', show_alert=False, cache_time=0)

        user_ad = user_ads[0]

        ad_data: dict = json.loads(user_ad.data)

        print(ad_data)

        price_line = f"{__.price_eye}{__.rent_agreemental}" if ad_data['price'] == __.rent_agreemental else f"{__.price_eye} {format_number(ad_data['price'])} {__.euros_per} #{ad_data['pricing_type']}"

        price_line2 = f"{__.price_eye}{__.rent_agreemental}" if ad_data['price'] == __.rent_agreemental else f"{__.price_eye} {format_number(ad_data['price'])}"

        categories_templates_view_ad = {

            'rent': {

                'template': __.rent_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[price_line]': price_line,

                    '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',

                }

            },

            'room_rent': {

                'template': __.room_rent_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[price_line]': price_line,

                    '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',

                }

            },

            'room_applicant': {

                'template': __.room_applicant_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',

                }

            },

            'home_applicant': {

                'template': __.home_applicant_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',

                }

            },

            'meldezettel_applicant': {

                'template': __.meldezettel_applicant_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    # '[contract_status]': ad_data['contract_status'],

                    # '[price_line]': price_line,

                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if

                    ad_data['description'] else '',

                }

            },

            'meldezettel': {

                'template': __.meldezettel_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[price_line]': price_line,

                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if

                    ad_data['description'] else '',

                }

            },

            'selling_goods': {

                'template': __.selling_goods_user_view_ad,

                'template_replacer': {

                    '[product_name]': ad_data['product_name'],

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    # '[start_date]': ad_data['start_date'],

                    # '[end_date]': ad_data['end_date'],

                    # '[contract_status]': ad_data['contract_status'],

                    '[price_line2]': price_line2,

                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if

                    ad_data['description'] else '',

                }

            },

            'buying_goods': {

                'template': __.buying_goods_user_view_ad,

                'template_replacer': {

                    '[product_name]': ad_data['product_name'],

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    # '[start_date]': ad_data['start_date'],

                    # '[end_date]': ad_data['end_date'],

                    # '[contract_status]': ad_data['contract_status'],

                    '[price_line2]': price_line2,

                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if

                    ad_data['description'] else '',

                }

            },

            'buying_cargo': {
                'template': __.buying_cargo_user_view_ad,
                'template_replacer': {
                    '[from_to_city]': ad_data['from_to_city'],
                    '[start_date]': ad_data['start_date'],
                    '[city]': ad_data['city'],
                    '[city2]': ad_data['city2'],
                    '[load]': ad_data['load'],
                    '[price]': __.rent_agreemental if ad_data['price'] == __.rent_agreemental else format_number(ad_data['price']),
                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if
                    ad_data['description'] else '',
                }
            },
            'selling_cargo': {
                'template': __.selling_cargo_user_view_ad,
                'template_replacer': {
                    '[from_to_city]': ad_data['from_to_city'],
                    '[start_date]': ad_data['start_date'],
                    '[city]': ad_data['city'],
                    '[city2]': ad_data['city2'],
                    '[load]': ad_data['load'],
                    '[price]': __.rent_agreemental if ad_data['price'] == __.rent_agreemental else format_number(ad_data['price']),
                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if
                    ad_data['description'] else '',
                }
            },

            'buying_euro': {
                'template': __.buying_euro_user_view_ad,
                'template_replacer': {
                    '[euros]': ad_data['euros'],
                    '[toman_per_euro]': __.rent_agreemental if ad_data[
                                                                   'toman_per_euro'] == __.rent_agreemental else format_number(
                        ad_data['toman_per_euro']),
                    '[payment_methods]': ' '.join(map(lambda i: f'#{getattr(__, i)}', ad_data[
                        'payment_methods'])) + f" {ad_data.get('payment_methods_other')}" if ad_data.get(
                        'payment_methods_other') else "",
                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if ad_data[
                        'description'] else '',
                }
            },
            'selling_euro': {
                'template': __.selling_euro_user_view_ad,
                'template_replacer': {
                    '[euros]': ad_data['euros'],
                    '[toman_per_euro]': __.rent_agreemental if ad_data[
                                                                   'toman_per_euro'] == __.rent_agreemental else format_number(
                        ad_data['toman_per_euro']),
                    '[payment_methods]': ' '.join(map(lambda i: f'#{getattr(__, i)}', ad_data[
                        'payment_methods'])) + f" {ad_data.get('payment_methods_other')}" if ad_data.get(
                        'payment_methods_other') else "",
                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if ad_data[
                        'description'] else '',
                }
            },

        }
        message_template_dict = categories_templates_view_ad.get(user_ad.category)
        message_template_str = message_template_dict['template']
        message_template_replacer = message_template_dict['template_replacer']
        message_template = formatted(message_template_str, message_template_replacer)

        return bot.edit_message_text(
            text=message_template,
            chat_id=user_id,
            message_id=call.message.id,
            reply_markup=my_ads_markup(__, user_id, user_ad, len(user_ads))
        )

        # if ads_state == 'pending':
        #     return bot.edit_message_text(
        #         text=message_template,
        #         chat_id=user_id,
        #         message_id=call.message.id,
        #         reply_markup=my_ads_markup(__, user_id, user_ad, len(user_ads))
        #     )
        #
        # elif ads_state == 'completed':
        #     return bot.edit_message_text(
        #         text=message_template,
        #         chat_id=user_id,
        #         message_id=call.message.id,
        #         reply_markup=my_ads_markup(__, user_id, user_ad, len(user_ads))
        #     )
        #
        # elif ads_state == 'canceled':
        #     return bot.edit_message_text(
        #         text=message_template,
        #         chat_id=user_id,
        #         message_id=call.message.id,
        #         reply_markup=my_ads_markup(__, user_id, user_ad, len(user_ads))
        #     )

    elif call_str.startswith('AD_FORWARD'):

        _, user_id, ads_state, ad_id = call_str.split()

        last_user_ad: Ad = session.query(Ad).filter_by(user=user, id=ad_id).first()

        user_ads: list[Ad] = session.query(Ad).filter_by(user=user, ad_status=ads_state).all()

        index = user_ads.index(last_user_ad) + 1

        if index > len(user_ads) - 1:
            index = 0

            # return bot_answer_or_send(bot, call, f'You Dont have Ads in this state', show_alert=False, cache_time=0)

        next_ad_id = user_ads[index].id

        next_ad: Ad = session.query(Ad).filter_by(user=user, id=next_ad_id).first()

        print(next_ad)

        ad_data: dict = json.loads(next_ad.data)

        price_line = f"{__.price_eye}{__.rent_agreemental}" if ad_data['price'] == __.rent_agreemental else f"{__.price_eye} {format_number(ad_data['price'])} {__.euros_per} #{ad_data['pricing_type']}"

        price_line2 = f"{__.price_eye}{__.rent_agreemental}" if ad_data['price'] == __.rent_agreemental else f"{__.price_eye} {format_number(ad_data['price'])}"

        categories_templates_view_ad = {

            'rent': {

                'template': __.rent_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[price_line]': price_line,

                    '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',

                }

            },

            'room_rent': {

                'template': __.room_rent_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[price_line]': price_line,

                    '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',

                }

            },

            'room_applicant': {

                'template': __.room_applicant_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',

                }

            },

            'home_applicant': {

                'template': __.home_applicant_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',

                }

            },

            'meldezettel_applicant': {

                'template': __.meldezettel_applicant_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    # '[contract_status]': ad_data['contract_status'],

                    # '[price_line]': price_line,

                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if

                    ad_data['description'] else '',

                }

            },

            'meldezettel': {

                'template': __.meldezettel_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[price_line]': price_line,

                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if

                    ad_data['description'] else '',

                }

            },

            'selling_goods': {

                'template': __.selling_goods_user_view_ad,

                'template_replacer': {

                    '[product_name]': ad_data['product_name'],

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    # '[start_date]': ad_data['start_date'],

                    # '[end_date]': ad_data['end_date'],

                    # '[contract_status]': ad_data['contract_status'],

                    '[price_line2]': price_line2,

                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if

                    ad_data['description'] else '',

                }

            },

            'buying_goods': {

                'template': __.buying_goods_user_view_ad,

                'template_replacer': {

                    '[product_name]': ad_data['product_name'],

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    # '[start_date]': ad_data['start_date'],

                    # '[end_date]': ad_data['end_date'],

                    # '[contract_status]': ad_data['contract_status'],

                    '[price_line2]': price_line2,

                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if

                    ad_data['description'] else '',

                }

            },

            'buying_cargo': {
                'template': __.buying_cargo_user_view_ad,
                'template_replacer': {
                    '[from_to_city]': ad_data['from_to_city'],
                    '[start_date]': ad_data['start_date'],
                    '[city]': ad_data['city'],
                    '[city2]': ad_data['city2'],
                    '[load]': ad_data['load'],
                    '[price]': __.rent_agreemental if ad_data['price'] == __.rent_agreemental else format_number(
                        ad_data['price']),
                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if
                    ad_data['description'] else '',
                }
            },

            'selling_cargo': {
                'template': __.selling_cargo_user_view_ad,
                'template_replacer': {
                    '[from_to_city]': ad_data['from_to_city'],
                    '[start_date]': ad_data['start_date'],
                    '[city]': ad_data['city'],
                    '[city2]': ad_data['city2'],
                    '[load]': ad_data['load'],
                    '[price]': __.rent_agreemental if ad_data['price'] == __.rent_agreemental else format_number(
                        ad_data['price']),
                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if
                    ad_data['description'] else '',
                }
            },

            'buying_euro': {
                'template': __.buying_euro_user_view_ad,
                'template_replacer': {
                    '[euros]': ad_data['euros'],
                    '[toman_per_euro]': __.rent_agreemental if ad_data[
                                                                   'toman_per_euro'] == __.rent_agreemental else format_number(
                        ad_data['toman_per_euro']),
                    '[payment_methods]': ' '.join(map(lambda i: f'#{getattr(__, i)}', ad_data[
                        'payment_methods'])) + f" {ad_data.get('payment_methods_other')}" if ad_data.get(
                        'payment_methods_other') else "",
                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if ad_data[
                        'description'] else '',
                }
            },
            'selling_euro': {
                'template': __.selling_euro_user_view_ad,
                'template_replacer': {
                    '[euros]': ad_data['euros'],
                    '[toman_per_euro]': __.rent_agreemental if ad_data[
                                                                   'toman_per_euro'] == __.rent_agreemental else format_number(
                        ad_data['toman_per_euro']),
                    '[payment_methods]': ' '.join(map(lambda i: f'#{getattr(__, i)}', ad_data[
                        'payment_methods'])) + f" {ad_data.get('payment_methods_other')}" if ad_data.get(
                        'payment_methods_other') else "",
                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if ad_data[
                        'description'] else '',
                }
            },
        }

        message_template_dict = categories_templates_view_ad.get(next_ad.category)

        message_template_str = message_template_dict['template']

        message_template_replacer = message_template_dict['template_replacer']

        message_template = formatted(message_template_str, message_template_replacer)

        bot_answer_or_send(bot, call, f'', show_alert=False, cache_time=0)

        return bot.edit_message_text(

            text=message_template,

            chat_id=user_id,

            message_id=call.message.id,

            reply_markup=my_ads_markup(__, user_id, next_ad, len(user_ads))

        )

    elif call_str.startswith('AD_BACK'):

        _, user_id, ads_state, ad_id = call_str.split()

        last_user_ad: Ad = session.query(Ad).filter_by(user=user, id=ad_id).first()

        user_ads: list[Ad] = session.query(Ad).filter_by(user=user, ad_status=ads_state).all()

        index = user_ads.index(last_user_ad) - 1

        # return bot_answer_or_send(bot, call, f'You Dont have Ads in this state', show_alert=False, cache_time=0)

        next_ad_id = user_ads[index].id

        next_ad: Ad = session.query(Ad).filter_by(user=user, id=next_ad_id).first()

        ad_data: dict = json.loads(next_ad.data)

        price_line = f"{__.price_eye}{__.rent_agreemental}" if ad_data['price'] == __.rent_agreemental else f"{__.price_eye} {format_number(ad_data['price'])} {__.euros_per} #{ad_data['pricing_type']}"

        price_line2 = f"{__.price_eye}{__.rent_agreemental}" if ad_data['price'] == __.rent_agreemental else f"{__.price_eye} {format_number(ad_data['price'])}"

        categories_templates_view_ad = {

            'rent': {

                'template': __.rent_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[price_line]': price_line,

                    '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',

                }

            },
            'room_rent': {

                'template': __.room_rent_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[price_line]': price_line,

                    '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',

                }

            },

            'room_applicant': {

                'template': __.room_applicant_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',

                }

            },
            'home_applicant': {

                'template': __.home_applicant_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',

                }

            },

            'meldezettel_applicant': {

                'template': __.meldezettel_applicant_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    # '[contract_status]': ad_data['contract_status'],

                    # '[price_line]': price_line,

                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if

                    ad_data['description'] else '',

                }

            },
            'meldezettel': {

                'template': __.meldezettel_user_view_ad,

                'template_replacer': {

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    '[start_date]': ad_data['start_date'],

                    '[end_date]': ad_data['end_date'],

                    '[contract_status]': ad_data['contract_status'],

                    '[price_line]': price_line,

                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if

                    ad_data['description'] else '',

                }

            },

            'selling_goods': {

                'template': __.selling_goods_user_view_ad,

                'template_replacer': {

                    '[product_name]': ad_data['product_name'],

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    # '[start_date]': ad_data['start_date'],

                    # '[end_date]': ad_data['end_date'],

                    # '[contract_status]': ad_data['contract_status'],

                    '[price_line2]': price_line2,

                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if

                    ad_data['description'] else '',

                }

            },
            'buying_goods': {

                'template': __.buying_goods_user_view_ad,

                'template_replacer': {

                    '[product_name]': ad_data['product_name'],

                    '[city]': ad_data['city'],

                    '[sub_city]': ad_data['sub_city'],

                    # '[start_date]': ad_data['start_date'],

                    # '[end_date]': ad_data['end_date'],

                    # '[contract_status]': ad_data['contract_status'],

                    '[price_line2]': price_line2,

                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if

                    ad_data['description'] else '',

                }

            },

            'buying_cargo': {
                'template': __.buying_cargo_user_view_ad,
                'template_replacer': {
                    '[from_to_city]': ad_data['from_to_city'],
                    '[start_date]': ad_data['start_date'],
                    '[city]': ad_data['city'],
                    '[city2]': ad_data['city2'],
                    '[load]': ad_data['load'],
                    '[price]': __.rent_agreemental if ad_data['price'] == __.rent_agreemental else format_number(
                        ad_data['price']),
                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if
                    ad_data['description'] else '',
                }
            },
            'selling_cargo': {
                'template': __.selling_cargo_user_view_ad,
                'template_replacer': {
                    '[from_to_city]': ad_data['from_to_city'],
                    '[start_date]': ad_data['start_date'],
                    '[city]': ad_data['city'],
                    '[city2]': ad_data['city2'],
                    '[load]': ad_data['load'],
                    '[price]': __.rent_agreemental if ad_data['price'] == __.rent_agreemental else format_number(
                        ad_data['price']),
                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if
                    ad_data['description'] else '',
                }
            },

            'buying_euro': {
                'template': __.buying_euro_user_view_ad,
                'template_replacer': {
                    '[euros]': ad_data['euros'],
                    '[toman_per_euro]': __.rent_agreemental if ad_data[
                                                                   'toman_per_euro'] == __.rent_agreemental else format_number(
                        ad_data['toman_per_euro']),
                    '[payment_methods]': ' '.join(map(lambda i: f'#{getattr(__, i)}', ad_data[
                        'payment_methods'])) + f" {ad_data.get('payment_methods_other')}" if ad_data.get(
                        'payment_methods_other') else "",
                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if ad_data[
                        'description'] else '',
                }
            },
            'selling_euro': {
                'template': __.selling_euro_user_view_ad,
                'template_replacer': {
                    '[euros]': ad_data['euros'],
                    '[toman_per_euro]': __.rent_agreemental if ad_data[
                                                                   'toman_per_euro'] == __.rent_agreemental else format_number(
                        ad_data['toman_per_euro']),
                    '[payment_methods]': ' '.join(map(lambda i: f'#{getattr(__, i)}', ad_data[
                        'payment_methods'])) + f" {ad_data.get('payment_methods_other')}" if ad_data.get(
                        'payment_methods_other') else "",
                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if ad_data[
                        'description'] else '',
                }
            },

        }

        message_template_dict = categories_templates_view_ad.get(next_ad.category)

        message_template_str = message_template_dict['template']

        message_template_replacer = message_template_dict['template_replacer']

        message_template = formatted(message_template_str, message_template_replacer)

        bot_answer_or_send(bot, call, f'', show_alert=False, cache_time=0)

        return bot.edit_message_text(

            text=message_template,

            chat_id=user_id,

            message_id=call.message.id,

            reply_markup=my_ads_markup(__, user_id, next_ad, len(user_ads))

        )

    elif call_str.startswith('AD_DELETE'):
        def confirm_delete_ad(message):
            if message.text == __.cancel_t:
                bot_answer_or_send(bot, call, '', cache_time=2)
                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))
            with session:
                ad: Ad = session.query(Ad).filter_by(user=user, id=ad_id).first()
                if ad and ad.ad_status.name == 'pending':
                    session.delete(ad)
                    session.commit()
                    bot.delete_message(user_id, call.message.id)
                    bot_answer_or_send(bot, call, '', show_alert=False, cache_time=1)
                    return bot.send_message(user_id, __.pending_ad_deleted, reply_markup=user_main_menu_markup(__))
                else:
                    bot.send_message(user_id, __.ad_delete_error)

        # AD_DELETE {user_id} {user_ad.id}
        _, user_id, ad_id = call_str.split()
        bot.send_message(user_id, __.rent_confirm_delete_ad, reply_markup=confirm_delete_ad_markup(__))
        bot.register_next_step_handler(call.message, confirm_delete_ad)

    elif call_str.startswith('AD_EXPIRE'):
        def confirm_expire_ad(message):
            def clean(main_text, text_to_delete_its_line):
                lines = main_text.split('\n')
                cleaned_lines = [line for line in lines if text_to_delete_its_line not in line]
                result = '\n'.join(cleaned_lines)
                return result

            if message.text == __.cancel_t:
                bot_answer_or_send(bot, call, '', cache_time=2)
                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))
            with session:
                ad: Ad = session.query(Ad).filter_by(user=user, id=ad_id).first()
                ad_data: dict = json.loads(ad.data)
                if ad and ad.ad_status.name == 'completed':
                    ad.ad_status = 'expired'
                    new_ad_text_no_contact = clean(ad.channel_message_text, "tg://user?id")
                    new_text = new_ad_text_no_contact + '\n\n' + __.ad_expired_line

                    if ad_data['photos']:
                        bot.edit_message_caption(caption=new_text, chat_id=posting_channels[0], message_id=ad.channel_message_id)
                    else:
                        bot.edit_message_text(text=new_text, chat_id=posting_channels[0], message_id=ad.channel_message_id)

                    session.commit()

                    bot.delete_message(user_id, call.message.id)
                    bot_answer_or_send(bot, call, '', show_alert=False, cache_time=1)
                    return bot.send_message(user_id, __.ad_expired, reply_markup=user_main_menu_markup(__))
                else:
                    bot.send_message(user_id, __.ad_expired_error)

        # AD_DELETE {user_id} {user_ad.id}
        _, user_id, ad_id = call_str.split()
        bot.send_message(user_id, __.rent_confirm_expire_ad, reply_markup=confirm_delete_ad_markup(__))
        bot.register_next_step_handler(call.message, confirm_expire_ad)


def user_help(message, bot):
    user_id = message.from_user.id

    with Session() as session:
        user = session.query(User).filter_by(id=user_id).first()

    __ = set_lang(user.language_code)

    if not check_user_in_channels(user_id):
        return bot.send_message(message.from_user.id, f"{__.subscribe_first_m}\n {_N.join(force_subscribe_channels)}")

    bot.send_message(
        user_id,
        text=__.help_command_message,
    )


def user_lang(message, bot):
    user_id = message.from_user.id

    with Session() as session:
        user = session.query(User).filter_by(id=user_id).first()

    __ = set_lang(user.language_code)

    if not check_user_in_channels(user_id):
        return bot.send_message(message.from_user.id, f"{__.subscribe_first_m}\n {_N.join(force_subscribe_channels)}")

    bot.send_message(
        user_id,
        text=__.change_language_msg,  # todo add langauge change
        # reply_markup=change_language_markup(user)
    )


def add_user_handlers(bot: TeleBot):
    bot.register_message_handler(user_start, commands=['start'], pass_bot=True)
    bot.register_message_handler(user_help, commands=['help'], pass_bot=True)
    bot.register_message_handler(user_lang, commands=['lang'], pass_bot=True)

    bot.register_message_handler(
        callback=user_message,
        content_types=['text', 'photo', 'document'],
        chat_types=['private'],
        # func=lambda c: True,
        pass_bot=True
    )

    bot.register_callback_query_handler(user_callback_query, func=lambda c: True, pass_bot=True)
