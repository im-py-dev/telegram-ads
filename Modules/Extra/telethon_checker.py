import json
import os
import asyncio
import functools
import time
from typing import List

from telebot.types import ChatMemberMember, ChatMemberOwner, ChatMemberAdministrator
from telethon.tl.types import User, ReplyKeyboardMarkup, KeyboardButtonRow, KeyboardButtonUrl, Message, \
    MessageEntityCustomEmoji, InputStickerSetShortName
from telethon.tl.functions.messages import GetStickerSetRequest

from telethon.sync import TelegramClient
from telethon import Button
from telethon.tl.types.messages import StickerSet

from config import PROJECT_PATH, force_subscribe_channels, JSON_PATH, posting_channel
from dotenv import load_dotenv

# from functools import lru_cache
from telebot import TeleBot

load_dotenv()

API_ID = int(os.getenv('APP_ID'))
API_HASH = os.getenv('API_HASH')
session_name = os.getenv('CLIENT_NAME')

loop = asyncio.new_event_loop()
client = TelegramClient(os.path.join(PROJECT_PATH, 'sessions', f'{session_name}.session'), API_ID, API_HASH)
client.parse_mode = 'html'


def utf16_length(string):
    utf16_bytes = string.encode('utf-16le')
    utf16_length = len(utf16_bytes) // 2
    return utf16_length


# with (client):
#     # from telethon.tl.types import ReplyInlineMarkup
#     # Define buttons
#     # reply_markup = ReplyInlineMarkup(rows=[
#     #     KeyboardButtonRow(
#     #         buttons=[
#     #             KeyboardButtonUrl(
#     #                 text='click me',
#     #                 url='https://bard.google.com',
#     #             )
#     #         ]
#     #     )
#     # ])
#     # reply_markup = Button.inline('Click me', b'click_data')
#     entity = client.get_entity('SY_Aloosh')
#
#     # messages: list[Message] = client.get_messages(entity, limit=10)
#     # for message in messages:
#     #     print(message.to_json())
#     #     quit()
#
#     pack_short_name = 'CenterOfEmoji21155410'
#     sticker_set: StickerSet = client(GetStickerSetRequest(
#         stickerset=InputStickerSetShortName(pack_short_name),
#         hash=0
#     ))
#
#     # sticker_set.documents[:50]
#     # target_message = ""
#     # extra_offset = 0
#     # for idx, document in enumerate(target_message):
#     #     document_id = document.id
#     #     alt = document.attributes[1].alt
#     #     # if alt != '⛰':
#     #     #     continue
#     #     offset = idx + extra_offset
#     #     emoji_id = document.attributes[1].stickerset.id
#     #     emoji_access_hash = document.attributes[1].stickerset.access_hash
#     #     message = client.send_message(
#     #         "SY_Aloosh",
#     #         message=alt,
#     #         formatting_entities=[MessageEntityCustomEmoji(
#     #             offset=offset,
#     #             length=utf16_length(alt),
#     #             document_id=document_id,
#     #         )],
#     #         silent=True
#     #     )
#     #     extra_offset += utf16_length(alt)
#     #     print(f"""
#     #     alt={alt}
#     #     offset={offset}
#     #     length={utf16_length(alt)}
#     #     document_id={document_id}
#     #     """)
#     #
#     # quit()
#     # print(message.to_dict())
#
#     # Check if the file exists
#
#     if os.path.exists(JSON_PATH):
#         # Read icons_data from the file
#         with open(f"{JSON_PATH}/icons.json", 'r', encoding='UTF-16') as file:
#             entities = json.load(file)
#
#     target_message = """1321🗂3213213🧑‍💻312312🧳312312🚕321"""
#     formatting_entities = []
#     extra_offset = 0
#     for idx, char in enumerate(target_message):
#         if char in entities.keys():
#             print("char found", char)
#             document_id = entities[char]["document_id"]
#             length = entities[char]["length"]
#             # length = utf16_length(char)
#             # set offset
#             offset = idx + extra_offset
#             print("offset", offset)
#             print("length", length)
#             print("document_id", document_id)
#             print("=" * 10)
#             entities[char]["offset"] = offset
#             formatting_entities.append(
#                 MessageEntityCustomEmoji(
#                     offset=offset,
#                     length=length,
#                     document_id=document_id,
#                 )
#             )
#             extra_offset += length - 1
#
#     print('formatting_entities')
#     print(len(formatting_entities))
#     message = client.send_message(
#         "SY_Aloosh",
#         message=target_message,
#         formatting_entities=formatting_entities,
#         silent=True
#     )
#     print(message.to_dict())
#     input('>>')
#
#     client.send_message(
#         entity='@sy_aloosh',
#         message='🔠',
#         # buttons=reply_markup,
#         # buttons=KeyboardButtonRow( [] )
#     )


def cached_function_with_ttl(maxsize, ttl_seconds):
    def decorator(func):
        cache = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))

            # Check if the result is already in the cache and not expired
            if key in cache and time.time() - cache[key]['timestamp'] < ttl_seconds:
                return cache[key]['result']

            # Compute the result
            result = func(*args, **kwargs)

            # Update the cache with the new result and timestamp
            cache[key] = {'result': result, 'timestamp': time.time()}

            # Prune the cache if it exceeds the specified maxsize
            if len(cache) > maxsize:
                oldest_key = min(cache, key=lambda k: cache[k]['timestamp'])
                del cache[oldest_key]

            return result

        return wrapper

    return decorator


def check_user_in_channel(user_id: int, channel_username: str):
    channel_info = client.get_entity(channel_username)
    channel_members: List[User] = client.get_participants(channel_info)
    found_user = next((member for member in channel_members if member.id == user_id), None)
    print('>> ', bool(found_user), user_id, channel_username)
    return found_user


# @lru_cache(maxsize=30)
# @cached_function_with_ttl(maxsize=100, ttl_seconds=5)
def check_user_in_channels(user_id: int, bot: TeleBot):
    print(f"{user_id=}")
    print(f"{posting_channel=}")
    data = bot.get_chat_member(chat_id=posting_channel, user_id=user_id)
    print("DATA TYPE", type(data))
    print("DATA", data)
    print(isinstance(bot.get_chat_member(chat_id=posting_channel, user_id=user_id), ChatMemberMember))

    return all([
        any([
            isinstance(bot.get_chat_member(chat_id=force_subscribe_channel, user_id=user_id), ChatMemberOwner),
            isinstance(bot.get_chat_member(chat_id=force_subscribe_channel, user_id=user_id), ChatMemberAdministrator),
            isinstance(bot.get_chat_member(chat_id=force_subscribe_channel, user_id=user_id), ChatMemberMember),
        ])
        for force_subscribe_channel in force_subscribe_channels
    ])


@cached_function_with_ttl(maxsize=100, ttl_seconds=30)
def check_user_in_channels2(user_id: int):
    channels_to_check = force_subscribe_channels
    asyncio.set_event_loop(loop)

    with client:
        return all(check_user_in_channel(user_id, channel_username) for channel_username in channels_to_check)


def send_ad_to_channel(channel_username: str, message_html: str):
    asyncio.set_event_loop(loop)

    with client:
        channel = client.get_entity(channel_username)
        return client.send_message(
            entity=channel_username,
            message=message_html,
            parse_mode='HTML',
        )


def send_ad_photo_to_channel(channel_username: str, message_html: str, photo_path: str):
    asyncio.set_event_loop(loop)

    buttons = [
        KeyboardButtonRow(
            [
                # KeyboardButtonUrl(text='View Photos', url=f'https://t.me/'),
                Button.inline('Click me', b'clk1')
            ]
        ),
    ]
    inline_markup = ReplyKeyboardMarkup(buttons)

    # reply_markup = [
    #     [Button.text('Reply Button', resize=True)]
    # ]
    inline_markup = [
        [Button.inline('Click me', b'clk1')]
    ]

    with client:
        # return client.send_file(channel_username, photo_path)
        return client.send_message(
            entity=channel_username,
            message=message_html,
            file=photo_path,
            buttons=inline_markup,
            # buttons=KeyboardButtonRow( [] )
        )

        # send_media_request = SendMediaRequest(
        #     peer=channel_username,
        #     media=InputMediaPhoto(id=photo_path),
        #     message=message_html,
        #     reply_markup=inline_markup,
        # )

        # Send the media with reply markup
        # return client.invoke(send_media_request)
