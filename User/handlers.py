import time

# from User.reply_markups2 import select_city_markup2, end_date_markup2, contract_status_markup2, pricing_type_markup2, \
#     pricing_markup2, description_markup2, photos_markup2, photo_markup2, ad_preview_markup2, rent_cancel_markup
from config import ADMINS_IDS, force_subscribe_channels

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
    # bot.answer_callback_query(call.id, call_data)

    with Session() as session:
        # Check if the user already exists
        user = session.query(User).filter_by(id=user_id).first()

    __ = set_lang(user.language_code)

    if not check_user_in_channels(user_id):
        return bot.send_message(call.message.from_user.id, f"{__.subscribe_first_m}\n {_N.join(force_subscribe_channels)}")

    if call_str.startswith('RENT2'):
        _, step_name, value = call_str.split()
        # start_rent2(step_name, value)

    if call_str.startswith('RENT'):
        def cancel_option(func):
            def wrapper(message: Message, *args, **kwargs):
                if message.text and message.text == __.cancel_t:
                    return bot.send_message(message.from_user.id, __.canceled_t, reply_markup=user_main_menu_markup(__))
                return func(message, *args, **kwargs)

            return wrapper

        @cancel_option
        def get_city_name(message, message_to_edit):
            user_data[user_id]['city'] = message.text
            bot.edit_message_text(text=f'{__.city_label}{message.text}', chat_id=user_id, message_id=message_to_edit.id, reply_markup=None)

            msg = bot.send_message(user_id, __.rent_sub_city, reply_markup=None)
            bot.register_next_step_handler(msg, get_sub_city)

        @cancel_option
        def get_city_from_other(message, message_to_edit):
            user_data[user_id]['city'] = message.text
            bot.edit_message_text(text=f'{__.city_label}{message.text}', chat_id=user_id, message_id=message_to_edit.id,reply_markup=None)
            msg = bot.send_message(user_id, __.rent_sub_city, reply_markup=None)
            bot.register_next_step_handler(msg, get_sub_city)

        @cancel_option
        def get_sub_city(message):
            user_data[user_id]['sub_city'] = message.text

            bot.send_message(user_id, __.rent_start_date, reply_markup=None)
            bot.register_next_step_handler(message, get_start_date)

        @cancel_option
        def get_start_date(message):
            user_data[user_id]['start_date'] = message.text

            msg = bot.send_message(message.from_user.id, __.rent_end_date, reply_markup=end_date_markup(__, ))
            bot.register_next_step_handler(message, get_end_date, msg)

        @cancel_option
        def get_end_date(message, msg):
            user_data[user_id]['end_date'] = message.text
            bot.edit_message_text(text=f'{__.end_date_label}{message.text}', chat_id=user_id, message_id=msg.id, reply_markup=None)
            bot.send_message(message.from_user.id, __.rent_contract_status, reply_markup=contract_status_markup(__, ))
            # bot.register_next_step_handler(message, get_contract_status)

        @cancel_option
        def get_contract_status(message):
            # todo from call
            # user_data['contract_status'] = True if message.text == 'With contract' else False
            user_data[user_id]['contract_status'] = message.text
            bot.send_message(message.from_user.id, __.rent_pricing_type, reply_markup=pricing_type_markup(__, ))

        @cancel_option
        def get_pricing_type(message):
            # todo add call
            user_data[user_id]['pricing_type'] = message.text

            bot.send_message(message.from_user.id, __.rent_price, reply_markup=pricing_markup(__, ))
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
                    bot.edit_message_text(text=f'{__.price_label}{price}', chat_id=user_id, message_id=msg.id, reply_markup=None)
                    bot.send_message(message.from_user.id, __.rent_description, reply_markup=description_markup(__, ))
                    bot.register_next_step_handler(message, get_description)
            except Exception as r:
                bot.send_message(message.from_user.id, __.rent_price)
                bot.register_next_step_handler(message, get_price)

        @cancel_option
        def get_description(message, msg):
            user_data[user_id]['description'] = ''
            if message.text != __.skip_btn:
                user_data[user_id]['description'] = message.text

            bot.edit_message_text(text=f'{__.description_label}{message.text}', chat_id=user_id, message_id=msg.id, reply_markup=None)

            bot.send_message(message.from_user.id, __.rent_photos, reply_markup=photos_markup(__))
            user_data[user_id]['photos'] = []

            bot.register_next_step_handler(message, get_photos)

        @cancel_option
        def get_photos(message):
            if message.text == __.rent_without_photo:
                user_data[user_id]['photos'] = []
                ad_preview(message)

            elif message.photo:
                user_data[user_id]['photos'].append(message.photo[0].file_id)
                bot.send_message(message.from_user.id, __.rent_photos_done, reply_markup=photo_markup(__))
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
                bot.send_message(message.from_user.id, __.rent_photos_done, reply_markup=photo_markup(__))
                bot.register_next_step_handler(message, get_photo)

            else:
                bot.send_message(message.from_user.id, __.rent_photo_error2)
                bot.register_next_step_handler(message, get_photos)

        @cancel_option
        def ad_preview(message):
            msg = bot.send_message(user_id, __.rent_creating_ad)
            ad_preview_template = formatted(__.rent_user_preview, {
                '[city]': user_data[user_id]['city'],
                '[sub_city]': user_data[user_id]['sub_city'],
                '[start_date]': user_data[user_id]['start_date'],
                '[end_date]': user_data[user_id]['end_date'],
                '[contract_status]': user_data[user_id]['contract_status'],
                '[pricing_type]': user_data[user_id]['pricing_type'],
                '[price]': format_number(user_data[user_id]['price']),
                '[description]': f"\n{__.description_label}\n{user_data[user_id]['description']}\n" if user_data[user_id]['description'] else '',
            })

            if user_data[user_id]['photos']:
                bot.send_photo(photo=user_data[user_id]['photos'][0], caption=ad_preview_template, chat_id=user_id,
                               reply_markup=ad_preview_markup(__))
            else:
                bot.send_message(text=ad_preview_template, chat_id=user_id,
                                 reply_markup=ad_preview_markup(__))

            bot.delete_message(chat_id=user_id, message_id=message.id)
            bot.delete_message(chat_id=user_id, message_id=msg.message_id)
            # bot.register_next_step_handler(message, ad_confirm)

        def ad_confirm(message):
            try:
                with session:
                    new_ad = Ad(
                        user_id=user.id,
                        category='rent',
                        data=json.dumps(user_data[user_id]),
                    )
                    session.add(new_ad)
                    session.commit()
                    ad_id = new_ad.id
            except Exception as r:
                print(r)
                bot.send_message(user_id, text=__.error_t, reply_markup=user_main_menu_markup(__))

            else:
                admin_preview_template = formatted(__.rent_admin_preview, {
                    '[city]': user_data[user_id]['city'],
                    '[sub_city]': user_data[user_id]['sub_city'],
                    '[start_date]': user_data[user_id]['start_date'],
                    '[end_date]': user_data[user_id]['end_date'],
                    '[contract_status]': user_data[user_id]['contract_status'],
                    '[pricing_type]': user_data[user_id]['pricing_type'],
                    '[price]': format_number(user_data[user_id]['price']),
                    '[description]': f"\nDescription:\n{user_data[user_id]['description']}\n" if user_data[user_id]['description'] else '',
                    '[advertiser]': f"<a href='tg://user?id={user_data[user_id]['uid']}'>{user_data[user_id]['user_full_name']}</a>",
                })
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
                bot.edit_message_text(text=__.rent_thank_you_msg, chat_id=user_id, message_id=message.id, reply_markup=None)
                bot.edit_message_reply_markup(chat_id=user_id, message_id=message.id, reply_markup=user_main_menu_markup(__))
                # bot.send_message(user_id,text=__.rent_thank_you_msg,reply_markup=user_main_menu_markup(__))

        _, step_name, value = call_str.split()
        print(call_str)
        print(_, step_name, value)

        if step_name == 'start':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            city_markup = select_city_markup(__)
            bot.delete_message(chat_id=user_id, message_id=call.message.id)
            # bot.edit_message_text(text=__.rent_t1, chat_id=user_id, message_id=call.message.id, reply_markup=None)
            # bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.id, reply_markup=cancel_markup(__))
            bot.send_message(user_id, __.rent_t1, reply_markup=cancel_markup(__))
            time.sleep(0.1)
            msg = bot.send_message(user_id, __.rent_t2, reply_markup=city_markup)
            # bot.add_data(user_id)
            user_data[user_id] = {
                'id': f'{user_id}_{call.message.id}', 'uid': user_id, 'category': 'Rent', 'user_full_name': call.from_user.full_name
            }
            bot.register_next_step_handler(msg, get_city_name, msg)

        if step_name == 'city':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            if value == 'other':
                bot.edit_message_text(text=__.rent_other_city, chat_id=user_id, message_id=call.message.id, reply_markup=None)
                bot.register_next_step_handler(call.message, get_city_from_other, call.message)
            else:
                city = getattr(__, value)
                user_data[user_id]['city'] = city
                bot.edit_message_text(text=f'{__.city_label}{city}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

                msg = bot.send_message(user_id, __.rent_sub_city, reply_markup=None)
                bot.register_next_step_handler(msg, get_sub_city)

        if step_name == 'end_date':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['end_date'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.end_date_label}{__.rent_agreemental}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_contract_status, reply_markup=contract_status_markup(__, ))

        if step_name == 'contract_status':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            contract_state = __.rent_with_contract if value == "with_contract" else __.rent_without_contract
            user_data[user_id]['contract_status'] = contract_state
            bot.edit_message_text(text=f'{__.contract_state_label}{contract_state}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_pricing_type, reply_markup=pricing_type_markup(__, ))

        if step_name == 'pricing_type':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            pricing_type = __.rent_daily if value == "daily" else __.rent_monthly
            user_data[user_id]['pricing_type'] = pricing_type
            msg = bot.edit_message_text(text=f'{__.pricing_type_label}{pricing_type}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_price, reply_markup=pricing_markup(__, ))
            return bot.register_next_step_handler(call.message, get_price, msg)

        if step_name == 'pricing':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['price'] = __.rent_agreemental
            bot.edit_message_text(text=f'{__.price_label}{__.rent_agreemental}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

            msg = bot.send_message(user_id, __.rent_description, reply_markup=description_markup(__, ))
            return bot.register_next_step_handler(call.message, get_description, msg)

        if step_name == 'description':
            bot_answer_or_send(bot, call, '', show_alert=False, cache_time=2)
            bot.clear_step_handler(call.message)

            user_data[user_id]['description'] = ''
            user_data[user_id]['photos'] = []
            bot.edit_message_text(text=f'{__.description_label}{__.skip_btn}', chat_id=user_id, message_id=call.message.id, reply_markup=None)

            bot.send_message(user_id, __.rent_photos, reply_markup=photos_markup(__))
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
                bot.edit_message_text(text=__.rent_order_canceled, chat_id=user_id, message_id=call.message.id, reply_markup=None)
                return bot.send_message(user_id, __.canceled_t, reply_markup=user_main_menu_markup(__))

    elif call_str.startswith('OPEN_ADS'):
        _, ads_state, user_id = call_str.split()
        user_ads: list[Ad] = session.query(Ad).filter_by(user=user, ad_status=ads_state).all()
        if not user_ads:
            return bot_answer_or_send(bot, call, f'You Dont have Ads in this state', show_alert=False, cache_time=0)

        user_ad = user_ads[0]
        ad_data: dict = json.loads(user_ad.data)
        print(ad_data)
        # 💠 ✅️️️️ #rent ✅️️️️💠
        # 📍 related to the city: #[city]
        # 🔎 Area: [sub_city]
        # 🗓️️ Date: From [start_date] until [end_date]
        # 📝 Type of contract: #[contract_status]
        # 👁 Price: [price] euros per [pricing_type]
        # [description]
        # Contact the [advertiser]
        message_template = formatted(__.rent_user_view_ad, {
            '[city]': ad_data['city'],
            '[sub_city]': ad_data['sub_city'],
            '[start_date]': ad_data['start_date'],
            '[end_date]': ad_data['end_date'],
            '[contract_status]': ad_data['contract_status'],
            '[pricing_type]': ad_data['pricing_type'],
            '[price]': format_number(ad_data['price']),
            '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',
        })

        if ads_state == 'pending':
            # user_ad = user_ads[0]
            # ad_data: dict = json.loads(user_ad.data)
            #             message_template = f"""
            # City: {ad_data.get('city')}
            # Distirict: {ad_data.get('sub_city')}
            # Start Date: {ad_data.get('start_date')}
            # End Date: {ad_data.get('end_date')}
            # Status: {ad_data.get('contract_status')}
            # Pricing: {ad_data.get('pricing_type')}
            # Price: {ad_data.get('price')}
            # Description: {ad_data.get('description')}
            # """
            return bot.edit_message_text(
                text=message_template,
                chat_id=user_id,
                message_id=call.message.id,
                reply_markup=my_ads_markup(__, user_id, user_ad, len(user_ads))
            )
        elif ads_state == 'completed':
            return bot.edit_message_text(
                text=message_template,
                chat_id=user_id,
                message_id=call.message.id,
                reply_markup=my_ads_markup(__, user_id, user_ad, len(user_ads))
            )
        elif ads_state == 'canceled':
            return bot.edit_message_text(
                text=message_template,
                chat_id=user_id,
                message_id=call.message.id,
                reply_markup=my_ads_markup(__, user_id, user_ad, len(user_ads))
            )

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
        message_template = formatted(__.rent_user_view_ad, {
            '[city]': ad_data['city'],
            '[sub_city]': ad_data['sub_city'],
            '[start_date]': ad_data['start_date'],
            '[end_date]': ad_data['end_date'],
            '[contract_status]': ad_data['contract_status'],
            '[pricing_type]': ad_data['pricing_type'],
            '[price]': format_number(ad_data['price']),
            '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',
        })

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
        message_template = formatted(__.rent_user_view_ad, {
            '[city]': ad_data['city'],
            '[sub_city]': ad_data['sub_city'],
            '[start_date]': ad_data['start_date'],
            '[end_date]': ad_data['end_date'],
            '[contract_status]': ad_data['contract_status'],
            '[pricing_type]': ad_data['pricing_type'],
            '[price]': format_number(ad_data['price']),
            '[description]': f"Description:\n{ad_data['description']}" if ad_data['description'] else '',
        })

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
                    bot.send_message(user_id, __.error3)

        # AD_DELETE {user_id} {user_ad.id}
        _, user_id, ad_id = call_str.split()
        bot.send_message(user_id, __.rent_confirm_delete_ad, reply_markup=confirm_delete_ad_markup(__))
        bot.register_next_step_handler(call.message, confirm_delete_ad)


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
        text=__.change_language_msg, #todo add langauge change
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
