from typing import Callable, Any, Tuple, Union
import shutil

from sqlalchemy.orm import make_transient

from User.rent_markups import cancel_markup, cancel_confirm_markup
from config import ADMINS_IDS, posting_channels, PROJECT_PATH

from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import Message, InputFile
from telebot.types import User as TUser
from telebot.util import antiflood

from Admin.reply_markups import *

# from Modules.Base.User import users, TelegramUser
from Modules.Base.languages import set_lang, initialize_languages

from Database.db import Session
from Database.models import User, AdStatusEnum

from time import sleep


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


def is_admin(request):
    return str(request.from_user.id) in ADMINS_IDS


# def get_user(user_id):
#     user = users.get(user_id)
#     if user:
#         return user
#
#     with Session() as session:
#         return session.query(User).filter_by(id=user_id).first()


def update_user(user: TUser, database_user: User):
    with Session() as session:
        # Update all fields if they have changed
        for variable in ['first_name', 'last_name', 'username']:
            if getattr(database_user, variable) != getattr(user, variable):
                setattr(database_user, variable, getattr(user, variable))
        session.commit()


def get_or_create_user(session: Session, user_id: int, message: Message):
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        for variable in ['first_name', 'last_name', 'username']:
            if getattr(user, variable) != getattr(message.from_user, variable):
                setattr(user, variable, getattr(message.from_user, variable))
        session.commit()

    else:
        user = User(
            id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            language_code=message.from_user.language_code,
        )
        session.add(user)
        session.commit()

    make_transient(user)
    return user


def antiflood_decorator(function: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: Tuple, number_retries: int = 5, **kwargs: Any) -> Union[None, Any]:
        for _ in range(number_retries - 1):
            try:
                return function(*args, **kwargs)
            except ApiTelegramException as ex:
                if ex.error_code == 429:
                    sleep(ex.result_json['parameters']['retry_after'])
                else:
                    print(ex)

        else:
            return function(*args, **kwargs)

    return wrapper


def admin_start(message: Message, bot: TeleBot):
    # logger.warning(message)
    admin_id = message.from_user.id

    # Perform database operation using SQLAlchemy with a scoped session
    with Session() as session:
        admin = session.query(User).filter_by(id=message.from_user.id).first()
        if admin:
            for variable in ['first_name', 'last_name', 'username']:
                if getattr(admin, variable) != getattr(message.from_user, variable):
                    setattr(admin, variable, getattr(message.from_user, variable))
            session.commit()

        else:
            admin = User(
                id=message.from_user.id,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                username=message.from_user.username,
                language_code=message.from_user.language_code,
            )
            session.add(admin)
            session.commit()

        first_name = admin.first_name
        print('admin', admin)
        print('first_name', admin.first_name)

    __ = set_lang(admin.language_code)

    bot.send_message(
        admin_id,
        text=f"Welcome {admin.first_name}!, this is your Dashboard",
        reply_markup=admin_main_menu_markup(__)
    )


def admin_message(message, bot: TeleBot):
    def cancel_option(func):
        def wrapper(message: Message, *args, **kwargs):
            if message.text and message.text == __.cancel_t:
                return bot.send_message(message.from_user.id,
                                        f"Welcome {message.from_user.first_name}!, this is your Dashboard",
                                        reply_markup=admin_main_menu_markup(__))
            return func(message, *args, **kwargs)

        return wrapper

    # logger.warning(message)
    command = message.text
    admin_id = message.chat.id
    # admin = get_user(admin_id)
    with Session() as session:
        admin = session.query(User).filter_by(id=admin_id).first()

    __ = set_lang(admin.language_code)

    def command_1():
        with session:
            users_count = session.query(User).count()
        bot.send_message(admin_id, formatted(__.admin_mm_btn_1a, {
            '[users_count]': users_count,
        }))

    def command_2():
        def take_xlsx_file(message: Message, __):
            if message.text and message.text == __.cancel_t:
                return bot.send_message(message.from_user.id, "Canceled!", reply_markup=admin_main_menu_markup(__))

            try:
                # Check if the message contains a document
                if message.document:
                    file_info = bot.get_file(message.document.file_id)
                    downloaded_file_path = os.path.join(PROJECT_PATH, "temp.xlsx")

                    # Download the file from Telegram
                    file_content = bot.download_file(file_info.file_path)

                    # Save the downloaded content to a file
                    with open(downloaded_file_path, 'wb') as file:
                        file.write(file_content)

                    # Move the file to the project path with the desired name
                    new_file_path = os.path.join(PROJECT_PATH, "STR.xlsx")
                    shutil.move(downloaded_file_path, new_file_path)

                    initialize_languages()
                    # get new STR()
                    __ = STR('fa')
                    # update bot description
                    bot.set_my_description(__.bot_description)
                    bot.set_my_short_description(__.short_description)

                    print(f"File copied to: {new_file_path}")
                    bot.send_message(admin_id, "File Copied!", reply_markup=admin_main_menu_markup(__))
                else:
                    bot.send_message(admin_id, "No document found in the message.")
            except Exception as e:
                bot.send_message(admin_id, f"Error: {e}")

        bot.send_message(admin_id, __.admin_mm_btn_2a, reply_markup=admin_change_lang_file(__))
        bot.register_next_step_handler(message, take_xlsx_file, __)

    def command_3():
        try:
            with session:
                pending_ads: list[Ad] = session.query(Ad).filter_by(ad_status=AdStatusEnum.pending).all()
        except Exception:
            bot.send_message(message.from_user.id, text="""Error""", )
        else:
            if not pending_ads:
                return bot.send_message(text="No Pending Ads To Show", chat_id=admin_id)

            for pending_ad in pending_ads:
                ad_data: dict = json.loads(pending_ad.data)

                price_line = f"{__.price_eye}{__.rent_agreemental}" if ad_data['price'] == __.rent_agreemental else f"{__.price_eye} {format_number(ad_data['price'])} {__.euros_per} #{ad_data['pricing_type']}"
                price_line2 = f"{__.price_eye}{__.rent_agreemental}" if ad_data['price'] == __.rent_agreemental else f"{__.price_eye} {format_number(ad_data['price'])}"

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
                            '[city]': ad_data['city'],
                            '[sub_city]': ad_data['sub_city'],
                            '[start_date]': ad_data['start_date'],
                            '[end_date]': ad_data['end_date'],
                            # '[contract_status]': ad_data['contract_status'],
                            # '[price_line]': price_line,
                            '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if
                            ad_data['description'] else '',
                            '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                        }
                    },
                    'meldezettel': {
                        'template': __.meldezettel_admin_preview,
                        'template_replacer': {
                            '[city]': ad_data['city'],
                            '[sub_city]': ad_data['sub_city'],
                            '[start_date]': ad_data['start_date'],
                            '[end_date]': ad_data['end_date'],
                            '[contract_status]': ad_data['contract_status'],
                            '[price_line]': price_line,
                            '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if
                            ad_data['description'] else '',
                            '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                        }
                    },

                    'selling_goods': {
                        'template': __.selling_goods_admin_preview,
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
                            '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                        }
                    },
                    'buying_goods': {
                        'template': __.buying_goods_admin_preview,
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
                            '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                        }
                    },
                }

                # price_line = f"{__.price_eye}{__.rent_agreemental}" if ad_data['price'] == __.rent_agreemental else f"{__.price_eye} {format_number(ad_data['price'])} {__.euros_per} #{ad_data['pricing_type']}"
                # admin_templates_preview = {
                #     'rent': {
                #         'template': __.rent_user_view_ad,
                #         'template_replacer': {
                #             '[city]': ad_data['city'],
                #             '[sub_city]': ad_data['sub_city'],
                #             '[start_date]': ad_data['start_date'],
                #             '[end_date]': ad_data['end_date'],
                #             '[contract_status]': ad_data['contract_status'],
                #             '[price_line]': price_line,
                #             '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data[
                #                 'description'] else '',
                #             '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                #         }
                #     },
                #     'room_rent': {
                #         'template': __.room_rent_user_view_ad,
                #         'template_replacer': {
                #             '[city]': ad_data['city'],
                #             '[sub_city]': ad_data['sub_city'],
                #             '[start_date]': ad_data['start_date'],
                #             '[end_date]': ad_data['end_date'],
                #             '[contract_status]': ad_data['contract_status'],
                #             '[price_line]': price_line,
                #             '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data[
                #                 'description'] else '',
                #             '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                #         }
                #     },
                #     'room_applicant': {
                #         'template': __.room_applicant_user_view_ad,
                #         'template_replacer': {
                #             '[city]': ad_data['city'],
                #             '[sub_city]': ad_data['sub_city'],
                #             '[start_date]': ad_data['start_date'],
                #             '[end_date]': ad_data['end_date'],
                #             '[contract_status]': ad_data['contract_status'],
                #             '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data[
                #                 'description'] else '',
                #             '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                #         }
                #     },
                #     'home_applicant': {
                #         'template': __.home_applicant_user_view_ad,
                #         'template_replacer': {
                #             '[city]': ad_data['city'],
                #             '[sub_city]': ad_data['sub_city'],
                #             '[start_date]': ad_data['start_date'],
                #             '[end_date]': ad_data['end_date'],
                #             '[contract_status]': ad_data['contract_status'],
                #             '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data[
                #                 'description'] else '',
                #             '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                #         }
                #     },
                # }

                message_template_dict = admin_templates_preview.get(pending_ad.category)
                message_template_str = message_template_dict['template']
                message_template_replacer = message_template_dict['template_replacer']
                admin_preview_template = formatted(message_template_str, message_template_replacer)

                # message_template_str = categories_templates_preview.get(pending_ad.category)
                # admin_preview_template = formatted(message_template_str, {
                #     '[city]': ad_data['city'],
                #     '[sub_city]': ad_data['sub_city'],
                #     '[start_date]': ad_data['start_date'],
                #     '[end_date]': ad_data['end_date'],
                #     '[contract_status]': ad_data['contract_status'],
                #     '[pricing_type]': ad_data['pricing_type'],
                #     '[price]': format_number(ad_data['price']),
                #     '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',
                #     '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                # })

                if ad_data['photos']:
                    bot.send_photo(
                        photo=ad_data['photos'][0],
                        caption=admin_preview_template,
                        chat_id=admin_id,
                        reply_markup=admin_ad_preview_markup(__, ad_data['uid'], pending_ad.id)
                    )
                else:
                    bot.send_message(
                        text=admin_preview_template,
                        chat_id=admin_id,
                        reply_markup=admin_ad_preview_markup(__, ad_data['uid'], pending_ad.id)
                    )

    def command_4():
        @antiflood_decorator
        def broadcast_message(user_id: int, message: Message):
            try:
                return bot.forward_message(chat_id=user_id, from_chat_id=message.from_user.id, message_id=message.id)
            except ApiTelegramException:
                return False
            except Exception:
                return False

        @cancel_option
        def handle_broadcast_message(message: Message, all_users: list[User]):
            done_send_count = 0
            unsuccessful_send_count = 0
            for user in all_users:
                if broadcast_message(user.id, message):
                    done_send_count += 1
                else:
                    unsuccessful_send_count += 1

            bot.send_message(admin_id, f'Done Sending to {done_send_count} user! \n Unsuccessful: {unsuccessful_send_count}', reply_markup=admin_main_menu_markup(__))

        # return bot.send_message(admin_id, 'Not Ready yet')
        users = session.query(User).all()
        bot.send_message(admin_id, 'Send your message:', reply_markup=cancel_markup(__))
        return bot.register_next_step_handler(message, handle_broadcast_message, users)

    # def command_5():
    #     @cancel_option
    #     def handle_turn_off(message: Message):
    #         if message.text == __.confirm_t:
    #             bot.send_message(admin_id, f'Bot Turning Off...', reply_markup=admin_main_menu_markup(__))
    #             bot.stop_bot()
    #             quit()
    #
    #     bot.send_message(admin_id, 'Turn Off Bot:', reply_markup=cancel_confirm_markup(__))
    #     return bot.register_next_step_handler(message, handle_turn_off)

    # not_known_command
    def unknown_command():
        bot.send_message(admin_id, __.unknown_command)

    commands = {
        __.admin_mm_btn_1: command_1,
        __.admin_mm_btn_2: command_2,
        __.admin_mm_btn_3: command_3,
        __.admin_mm_btn_4: command_4,
        # __.admin_mm_btn_5: command_5,
    }
    func = commands.setdefault(command, unknown_command)
    func()


def admin_callback_query(call, bot: TeleBot):
    # logger.warning(call)
    admin_id = call.from_user.id
    call_str = str(call.data)

    with Session() as session:
        admin = session.query(User).filter_by(id=admin_id).first()
        print(admin)

    __ = set_lang(admin.language_code)

    if call_str.startswith("ADMIN_AD_REVIEW"):
        # ADMIN_AD_REVIEW ACCEPT  {user_id} {new_ad_id}
        _, command_str, user_id, new_ad_id = call_str.split()
        print(_, command_str, user_id, new_ad_id)
        with session:
            user_ad: Ad = session.query(Ad).filter_by(user_id=user_id, id=new_ad_id).first()
            print(user_ad)
        ad_data: dict = json.loads(user_ad.data)
        # found_ad = next((item for item in load_json('pending_ads.json') if item["id"] == ad_id), None)

        if command_str == "ACCEPT":
            def confirm_accept(message):
                if message.text == __.cancel_t:
                    bot_answer_or_send(bot, call, '', show_alert=False, cache_time=1)
                    return bot.send_message(admin_id, __.canceled_t, reply_markup=admin_main_menu_markup(__))
                elif message.text == __.confirm_t:
                    try:
                        with session:
                            user_ad: Ad = session.query(Ad).filter_by(user_id=user_id, id=new_ad_id).first()
                            ad_id = user_ad.id
                            ad_category = user_ad.category
                            user_ad.ad_status = 'completed'
                            session.commit()
                    except Exception as r:
                        print(r)
                    else:
                        price_line = f"{__.price_eye}{__.rent_agreemental}" if ad_data['price'] == __.rent_agreemental else f"{__.price_eye} {format_number(ad_data['price'])} {__.euros_per} #{ad_data['pricing_type']}"
                        price_line2 = f"{__.price_eye}{__.rent_agreemental}" if ad_data['price'] == __.rent_agreemental else f"{__.price_eye} {format_number(ad_data['price'])}"

                        categories_templates_channel = {
                            'rent': {
                                'template': __.rent_channel_message,
                                'template_replacer': {
                                    '[city]': ad_data['city'],
                                    '[sub_city]': ad_data['sub_city'],
                                    '[start_date]': ad_data['start_date'],
                                    '[end_date]': ad_data['end_date'],
                                    '[contract_status]': ad_data['contract_status'],
                                    '[price_line]': price_line,
                                    '[description]': f"\nDescription:\n{ad_data['description']}\n" if ad_data['description'] else '',
                                    '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                                }
                            },
                            'room_rent': {
                                'template': __.room_rent_channel_message,
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
                                'template': __.room_applicant_channel_message,
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
                                'template': __.home_applicant_channel_message,
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
                                'template': __.meldezettel_channel_message,
                                'template_replacer': {
                                    '[city]': ad_data['city'],
                                    '[sub_city]': ad_data['sub_city'],
                                    '[start_date]': ad_data['start_date'],
                                    '[end_date]': ad_data['end_date'],
                                    # '[contract_status]': ad_data['contract_status'],
                                    # '[price_line]': price_line,
                                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if
                                    ad_data['description'] else '',
                                    '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                                }
                            },
                            'meldezettel': {
                                'template': __.meldezettel_channel_message,
                                'template_replacer': {
                                    '[city]': ad_data['city'],
                                    '[sub_city]': ad_data['sub_city'],
                                    '[start_date]': ad_data['start_date'],
                                    '[end_date]': ad_data['end_date'],
                                    '[contract_status]': ad_data['contract_status'],
                                    '[price_line]': price_line,
                                    '[description]': f"\n{__.description_label}\n{ad_data['description']}\n" if
                                    ad_data['description'] else '',
                                    '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                                }
                            },

                            'selling_goods': {
                                'template': __.selling_goods_channel_message,
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
                                    '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                                }
                            },
                            'buying_goods': {
                                'template': __.buying_goods_channel_message,
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
                                    '[advertiser]': f"<a href='tg://user?id={ad_data['uid']}'>{ad_data['user_full_name']}</a>",
                                }
                            },

                        }
                        message_template_dict = categories_templates_channel.get(ad_category)
                        message_template_str = message_template_dict['template']
                        message_template_replacer = message_template_dict['template_replacer']
                        rent_channel_message = formatted(message_template_str, message_template_replacer)

                        for posting_channel in posting_channels:
                            if ad_data.get('photos'):
                                bot.send_photo(
                                    chat_id=posting_channel,
                                    photo=ad_data.get('photos')[0],
                                    caption=rent_channel_message,
                                    reply_markup=rent_channel_markup(__, ad_id),
                                )
                            else:
                                bot.send_message(
                                    chat_id=posting_channel,
                                    text=rent_channel_message,
                                    # reply_markup=
                                )

                        bot_answer_or_send(bot, call, __.rent_confirmed_ad_admin, show_alert=True, cache_time=5 * 1)
                        bot.delete_message(admin_id, call.message.id)
                        bot.send_message(user_id, __.rent_confirmed_ad)
                        return bot.send_message(admin_id, __.confirmed_t, reply_markup=admin_main_menu_markup(__))

            bot.send_message(admin_id, __.confirm_action_ask, reply_markup=admin_confirm_action_markup(__))
            bot.register_next_step_handler(call.message, confirm_accept)

        elif command_str == "DECLINE":
            def confirm_decline(message):
                if message.text == __.cancel_t:
                    bot_answer_or_send(bot, call, '', show_alert=False, cache_time=1)
                    return bot.send_message(admin_id, __.canceled_t, reply_markup=admin_main_menu_markup(__))

                reason = None
                if message.text != __.confirm_t:
                    reason = message.text
                try:
                    with session:
                        user_ad: Ad = session.query(Ad).filter_by(user_id=user_id, id=new_ad_id).first()
                        user_ad.ad_status = 'canceled'
                        session.commit()
                except Exception as r:
                    print(r)
                else:
                    # with session:
                    #     session.delete(user_ad)
                    #     session.commit()
                    bot_answer_or_send(bot, call, __.rent_declined_ad_admin, show_alert=True, cache_time=5 * 1)
                    bot.delete_message(admin_id, call.message.id)
                    bot.send_message(user_id, __.rent_declined_ad)
                    if reason:
                        bot.send_message(user_id, f"{__.reason_t}{reason}")
                    return bot.send_message(admin_id, __.confirmed_t, reply_markup=admin_main_menu_markup(__))

            bot.send_message(admin_id, __.confirm_action_ask, reply_markup=admin_decline_action_markup(__))
            bot.register_next_step_handler(call.message, confirm_decline)


def admin_help(message, bot: TeleBot):
    admin_id = message.from_user.id

    with Session() as session:
        user = session.query(User).filter_by(id=admin_id).first()

    __ = set_lang(user.language_code)

    bot.send_message(
        admin_id,
        text=__.help_command_message,
    )


def admin_lang(message, bot):
    admin_id = message.from_user.id

    with Session() as session:
        user = session.query(User).filter_by(id=admin_id).first()

    __ = set_lang(user.language_code)

    bot.send_message(
        admin_id,
        text=__.change_language_msg,  # todo add langauge change
        # reply_markup=change_language_markup(user)
    )


def add_admin_handlers(bot: TeleBot):
    bot.register_message_handler(
        callback=admin_start,
        commands=['start'],
        func=is_admin,
        pass_bot=True
    )

    bot.register_message_handler(
        callback=admin_help,
        commands=['help'],
        func=is_admin,
        pass_bot=True
    )

    bot.register_message_handler(
        callback=admin_lang,
        commands=['lang'],
        func=is_admin,
        pass_bot=True
    )

    bot.register_message_handler(
        callback=admin_message,
        content_types=['text', 'photo', 'document'],
        chat_types=['private'],
        func=is_admin,
        pass_bot=True
    )

    bot.register_callback_query_handler(admin_callback_query, func=is_admin, pass_bot=True)
