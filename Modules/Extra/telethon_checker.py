import os
import asyncio
import functools
import time
from typing import List

from telethon.tl.types import User, ReplyKeyboardMarkup, KeyboardButtonRow
from telethon.sync import TelegramClient
from telethon import Button

from config import PROJECT_PATH, force_subscribe_channels
from dotenv import load_dotenv
# from functools import lru_cache


load_dotenv()

API_ID = int(os.getenv('APP_ID'))
API_HASH = os.getenv('API_HASH')
session_name = os.getenv('CLIENT_NAME')

loop = asyncio.new_event_loop()
client = TelegramClient(os.path.join(PROJECT_PATH, 'sessions', f'{session_name}.session'), API_ID, API_HASH)
client.parse_mode = 'html'

# with client:
#     from telethon.tl.types import ReplyInlineMarkup
#
#     # Define buttons
#     reply_markup = ReplyInlineMarkup(rows=[
#         KeyboardButtonRow(
#             buttons=[
#                 KeyboardButtonUrl(
#                     text='click me',
#                     url='https://bard.google.com',
#                 )
#             ]
#         )
#     ])
#     reply_markup = Button.inline('Click me', b'click_data')
#
#     client.send_message(
#     entity='@sy_aloosh',
#     message='123',
#     buttons=reply_markup,
#     # buttons=KeyboardButtonRow( [] )
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
@cached_function_with_ttl(maxsize=100, ttl_seconds=30)
def check_user_in_channels(user_id: int):
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
