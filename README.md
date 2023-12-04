# Telegram Ads Bot

## Setup:
___
### Change .txt files at /Data:
* #### `admins.txt` add telegram id for admin/admins
* #### `force_subscribe_channels.txt` add the channels you want force users to subscribe to.
* #### `posting_channels.txt` the channel where all ads will shared
___
### Create a `.env` file
```dotenv
APP_ID=
API_HASH=
CLIENT_NAME=
CLIENT_PHONE=
CLIENT_PASSWORD=

BOT_TOKEN=
BOT_USERNAME=

DATABASE_URL=sqlite:///telegram.db
```
* #### APP_ID + API_HASH from [link](https://my.telegram.org/auth?to=apps)
* #### CLIENT_NAME: Put Any Name Here.
* #### CLIENT_PHONE: Your telegram phone withg the country code Ex: +201271825197
* #### CLIENT_PASSWORD: If your telegram account has password
* #### BOT_TOKEN + BOT_USERNAME: From BotFather [link](https://t.me/BotFather)
___
### Now Run `app.py` once and a new session will get created and the app will ternimated
### Then You will run `app.py` again once.
