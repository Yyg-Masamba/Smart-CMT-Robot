# * @author        Pea Masamba <comelmuewa831@gmail.com>
# * @date          2023-06-21 22:12:27
# * @projectName   Smart-CMT-Robot
# * Copyright ©peamasamba All rights reserved
import time
from logging import ERROR, INFO, StreamHandler, basicConfig, getLogger, handlers

from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from async_pymongo import AsyncClient
from pymongo import MongoClient
from pyrogram import Client

from misskaty.core import misskaty_patch
from misskaty.vars import (
    API_HASH,
    API_ID,
    BOT_TOKEN,
    DATABASE_NAME,
    DATABASE_URI,
    TZ,
    USER_SESSION,
)

basicConfig(
    level=INFO,
    format="[%(levelname)s] - [%(asctime)s - %(name)s - %(message)s] -> [%(module)s:%(lineno)d]",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        handlers.RotatingFileHandler("MissKatyLogs.txt", mode="w+", maxBytes=5242880, backupCount=1),
        StreamHandler(),
    ],
)
getLogger("pyrogram").setLevel(ERROR)
getLogger("openai").setLevel(ERROR)
getLogger("httpx").setLevel(ERROR)
getLogger("iytdl").setLevel(ERROR)

MOD_LOAD = []
MOD_NOLOAD = ["subscene_dl"]
HELPABLE = {}
cleanmode = {}
botStartTime = time.time()
misskaty_version = "v2.11.2 - Stable"

# Pyrogram Bot Client
app = Client(
    "SmartCMTRoBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    mongodb=dict(connection=AsyncClient(DATABASE_URI), remove_peers=False),
    sleep_threshold=180,
    app_version="MissKatyPyro Stable",
    workers=50,
    max_concurrent_transmissions=20,
)

# Pyrogram UserBot Client
user = Client(
    "Smart-CMT-Robot",
    session_string=USER_SESSION,
    mongodb=dict(connection=AsyncClient(DATABASE_URI), remove_peers=False),
    sleep_threshold=180,
)

jobstores = {
    "default": MongoDBJobStore(
        client=MongoClient(DATABASE_URI), database=DATABASE_NAME, collection="nightmode"
    )
}
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=TZ)

app.start()
BOT_ID = app.me.id
BOT_NAME = app.me.first_name
BOT_USERNAME = app.me.username
if USER_SESSION:
    user.start()
    UBOT_ID = user.me.id
    UBOT_NAME = user.me.first_name
    UBOT_USERNAME = user.me.username
else:
    UBOT_ID = None
    UBOT_NAME = None
    UBOT_USERNAME = None
