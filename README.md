# Telegram Ads Bot

## Setup:

### Create a `.env` file
```dotenv
ADMINS=416269937,449396427
FORCE_SUBSCRIBE_CHANNELS=@testingpostad,@testingpostad2
POSTING_CHANNELS=@testingpostad

APP_ID=
API_HASH=
CLIENT_NAME=
CLIENT_PHONE=
CLIENT_PASSWORD=

BOT_TOKEN=
BOT_USERNAME=

DATABASE_URL=sqlite:///telegram.db
```
* #### `ADMINS` add telegram id for admin/admins
* #### `FORCE_SUBSCRIBE_CHANNELS` add the channels you want force users to subscribe to.
* #### `POSTING_CHANNELS` the channel where all ads will get sent
* #### `APP_ID` + `API_HASH` from [link](https://my.telegram.org/auth?to=apps)
* #### `CLIENT_NAME`: Put Any Name Here.
* #### `CLIENT_PHONE`: Your telegram phone withg the country code Ex: +201271825197
* #### `CLIENT_PASSWORD`: If your telegram account has password
* #### `BOT_TOKEN` + `BOT_USERNAME`: From BotFather [link](https://t.me/BotFather)
___
### Run `start.bat` once and a new session will get created and the app will ternimated
___
### Now run `start.bat` again once.
___