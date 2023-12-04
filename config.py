import os

# import telebot
# import logging
# logger = telebot.logger
# logger.setLevel(logging.WARNING)

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
ADMIN_PATH = os.path.join(PROJECT_PATH, 'Admin')
JSON_PATH = os.path.join(PROJECT_PATH, 'Json')

with open(os.path.join(PROJECT_PATH, 'Data', 'admins.txt'), 'r') as file:
    ADMINS_IDS = [line.strip() for line in file]
print("ADMINS_IDS", ADMINS_IDS)

with open(os.path.join(PROJECT_PATH, 'Data', 'force_subscribe_channels.txt'), 'r') as file:
    force_subscribe_channels = [line.strip() for line in file]
print("force_subscribe_channels", force_subscribe_channels)

with open(os.path.join(PROJECT_PATH, 'Data', 'posting_channels.txt'), 'r') as file:
    posting_channels = [line.strip() for line in file]
print("posting_channels", posting_channels)
