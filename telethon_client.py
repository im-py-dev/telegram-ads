import asyncio
import os
from telethon.sync import TelegramClient
from telethon.errors import rpcerrorlist
from config import PROJECT_PATH

from dotenv import load_dotenv

load_dotenv()


class MyTelegramClient(TelegramClient):
    def __init__(self, client_name, client_data, active_app, sessions_path):
        self.name = client_name
        self.phone = client_data['phone']
        self.password = client_data['password']
        self.api_id = active_app['api_id']
        self.api_hash = active_app['api_hash']
        self.session_path = os.path.join(sessions_path, f"{self.name}.session")
        super().__init__(self.session_path, self.api_id, self.api_hash)

    async def login(self):
        await self.connect()

        if not await self.is_user_authorized():
            await self.send_code_request(self.phone)
            code = input('Code:')

            try:
                await self.sign_in(phone=self.phone, code=code)
            except rpcerrorlist.SessionPasswordNeededError as r:
                print("SessionPasswordNeededError", r)
                try:
                    await self.sign_in(password=self.password)
                except ValueError as r:
                    print("Password is invalid", r)
                    exit()
            finally:
                me = await self.get_me()
                print(f'New Login: [User {me.username}]')
                await self.disconnect()
        else:
            me = await self.get_me()
            os.system('cls')
            print(f'Login Successful: [User {me.username}]')
            await self.disconnect()

    async def get_messages(self, channel_id, offset_date=None, reverse=True):
        messages = []
        async for message in self.iter_messages(channel_id, offset_date=offset_date, reverse=True):
            messages.append(message)
        return messages

    async def __aenter__(self):
        if not self.is_connected():
            await self.connect()

        if not await self.is_user_authorized():
            await self.send_code_request(self.phone)
            code = input('Code:')

            try:
                await self.sign_in(phone=self.phone, code=code)
            except rpcerrorlist.SessionPasswordNeededError:
                await self.sign_in(password=self.password)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


async def choose_session_or_input():
    sessions_path = os.path.join(os.getcwd(), "sessions")
    session_files = [f for f in os.listdir(sessions_path) if f.endswith('.session')]

    if session_files:
        print("Available sessions:")
        for i, session in enumerate(session_files, 1):
            print(f"{i}. {session}")

        choice = int(input("Choose a session (enter the corresponding number): "))
        chosen_session = session_files[choice - 1].split('.session')[0]
    else:
        chosen_session = input("No sessions found. Enter a new session name: ")

    return chosen_session


async def main():
    project_path = os.getcwd()

    session_name = os.getenv('CLIENT_NAME')
    # session_name = await choose_session_or_input()

    # APP_ID = int(os.getenv('APP_ID'))
    # API_HASH = os.getenv('API_HASH')
    # CLIENT_PHONE = os.getenv('CLIENT_PHONE')
    # CLIENT_PASSWORD = os.getenv('CLIENT_PASSWORD')

    tmp = MyTelegramClient(
        client_name=session_name,
        client_data={
            "phone": os.getenv('CLIENT_PHONE'),
            "password": os.getenv('CLIENT_PASSWORD')
        },
        active_app={
            "api_id": int(os.getenv('APP_ID')),
            "api_hash": os.getenv('API_HASH')
        },
        sessions_path=os.path.join(project_path, "sessions"),
    )

    await tmp.login()
    auth = await tmp.is_user_authorized()
    if not auth:
        print("Error in Telethon Client")
        exit()
    await tmp.connect()
    # me = await telethon_client.get_me()
    # print(me.first_name)
    return tmp


# telethon_client = asyncio.run(main())
sessions_path = os.path.join(PROJECT_PATH, 'sessions')
session_name = os.getenv('CLIENT_NAME')
file_path = os.path.join(sessions_path, f'{session_name}.session')

if not os.path.isfile(file_path):
    print("Sission Not Found, Create new one...")
    os.mkdir(sessions_path)
    telethon_client = asyncio.run(main())
    print("Session created, please restart the app now")
    exit()

# if __name__ == "__main__":
#     telethon_client = asyncio.run(main())
#     print('Client', telethon_client)
