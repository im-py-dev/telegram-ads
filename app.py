import sys

import telethon_client

import telebot
from telebot.types import BotCommand

from User.handlers import *
from Admin.handlers import *

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_KEY, parse_mode='HTML', num_threads=5)

try:
    bot.get_me()
except telebot.apihelper.ApiTelegramException as _:
    print("Bot Token is not valid")
    sys.exit()

# commands_dict = {
#     'start': "Start the bot 🤖",
#     'help': "Get help 📞",
#     # 'lang': "change language 🇬🇧 🇸🇦",
# }
# commands_list = []
# for command, desc in commands_dict.items():
#     commands_list.append(BotCommand(command, desc))
# bot.set_my_commands(commands_list)

try:
    tmp = STR('fa')
    bot.set_my_description(tmp.bot_description)
    bot.set_my_short_description(tmp.short_description)
    # bot.set_my_short_description(tmp.short_description)
    # del tmp
except Exception as r:
    print(r)

# bot.set_my_description(os.getenv('BOT_DESCRIPTION'))
# bot.set_my_short_description(os.getenv('BOT_SHORT_DESCRIPTION'))

print("BOT started...")


# ADMIN FIRST REQUIRED
add_admin_handlers(bot)

# THEN USERS
add_user_handlers(bot)


while True:
    try:
        bot.polling(non_stop=True, interval=0, timeout=0)
    except Exception as _:
        print('Exception:', _)
        sleep(1)
