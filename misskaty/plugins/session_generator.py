import traceback
from logging import getLogger

from pyrogram import Client, filters
from pyrogram.errors import (
    ApiIdInvalid,
    ListenerTimeout,
    PasswordHashInvalid,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
    SessionPasswordNeeded,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)
from telethon.sessions import StringSession

from misskaty import app
from misskaty.vars import API_HASH, API_ID, COMMAND_HANDLER

LOGGER = getLogger("Smart-CMT-Robot")

__MODULE__ = "SessionGen"
__HELP__ = """
/genstring - Membuat sesi string menggunakan bot ini. Hanya mendukung Pyrogram v2 dan Telethon.
"""


ask_ques = "**» Pilih library yang kau inginkan untuk menghasilkan string :**\n\nCatatan: Aku tak mengambil informasi pribadi apa pun dari fitur ini, kau bisa gunakan botmu sendiri jika mau."
buttons_ques = [
    [
        InlineKeyboardButton("Pyrogram", callback_data="pyrogram"),
        InlineKeyboardButton("Telethon", callback_data="telethon"),
    ],
    [
        InlineKeyboardButton("Pyrogram Bot", callback_data="pyrogram_bot"),
        InlineKeyboardButton("Telethon Bot", callback_data="telethon_bot"),
    ],
]

gen_button = [
    [InlineKeyboardButton(text="🖲 Generate Session 🖲", callback_data="genstring")]
]


async def is_batal(msg):
    if msg.text == "/cancel":
        await msg.reply(
            "**» Membatalkan proses pembuatan sesi string yang sedang berlangsung!**",
            quote=True,
            reply_markup=InlineKeyboardMarkup(gen_button),
        )
        return True
    elif msg.text == "/skip":
        return False
    elif msg.text.startswith("/"):  # Bot Commands
        await msg.reply(
            "**» Membatalkan proses pembuatan sesi string yang sedang berlangsung!**",
            quote=True,
        )
        return True
    else:
        return False


@app.on_callback_query(
    filters.regex(pattern=r"^(genstring|pyrogram|pyrogram_bot|telethon_bot|telethon)$")
)
async def callbackgenstring(bot, callback_query):
    query = callback_query.matches[0].group(1)
    if query == "genstring":
        await callback_query.answer()
        await callback_query.message.reply(
            ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques)
        )
    elif query.startswith("pyrogram") or query.startswith("telethon"):
        try:
            if query == "pyrogram":
                await callback_query.answer()
                await generate_session(bot, callback_query.message)
            elif query == "pyrogram_bot":
                await callback_query.answer(
                    "» Generator sesi akan menggunakan Pyrogram v2.", show_alert=True
                )
                await generate_session(bot, callback_query.message, is_bot=True)
            elif query == "telethon_bot":
                await callback_query.answer()
                await generate_session(
                    bot, callback_query.message, telethon=True, is_bot=True
                )
            elif query == "telethon":
                await callback_query.answer()
                await generate_session(bot, callback_query.message, telethon=True)
        except Exception as e:
            LOGGER.error(traceback.format_exc())
            ERROR_MESSAGE = (
                "Ada yang salah. \n\n**ERROR** : {} "
                "\n\n**Harap teruskan pesan ini ke Majikanku**, jika pesan ini "
                "tidak mengandung data sensitif apa pun "
                "karena kesalahan ini **tidak dicatat oleh bot.** !"
            )
            await callback_query.message.reply(ERROR_MESSAGE.format(str(e)))


@app.on_message(
    filters.private & ~filters.forwarded & filters.command("genstring", COMMAND_HANDLER)
)
async def genstringg(_, msg):
    await msg.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))


async def generate_session(bot, msg, telethon=False, is_bot: bool = False):
    ty = "Telethon" if telethon else "Pyrogram"
    if is_bot:
        ty += " Bot"
    await msg.reply(f"Mencoba menjalankan **{ty}** generator sesi...")
    api_id_msg = await msg.chat.ask(
        "Silakan kirimkan **API_ID** untuk melanjutkan.\n\nKlik /skip untuk menggunakan api bot.",
        filters=filters.text,
    )
    if await is_batal(api_id_msg):
        return
    if api_id_msg.text == "/skip":
        api_id = API_ID
        api_hash = API_HASH
    else:
        try:
            api_id = int(api_id_msg.text)
            await api_id_msg.delete()
        except ValueError:
            return await api_id_msg.reply(
                "**API_ID** harus berupa bilangan bulat, mulai buat sesimu lagi.",
                quote=True,
                reply_markup=InlineKeyboardMarkup(gen_button),
            )
        api_hash_msg = await msg.chat.ask(
            "» Sekarang silakan kirimkan **API_HASH** untuk melanjutkan.", filters=filters.text
        )
        if await is_batal(api_hash_msg):
            return
        api_hash = api_hash_msg.text
        await api_hash_msg.delete()
    t = (
        "Silahkan kirimkan **BOT_TOKEN** untuk melanjutkan.\nContoh : `5432198765:abcdanonymousterabaaplol`'"
        if is_bot
        else "» Silahkan kirimkan **PHONE_NUMBER** dengan kode negara yang kau mau untuk menghasilkan sesi. \nCONTOH : `+6286356837789`'"
    )
    phone_number_msg = await msg.chat.ask(t, filters=filters.text)
    if await is_batal(phone_number_msg):
        return
    phone_number = phone_number_msg.text
    await phone_number_msg.delete()
    if not is_bot:
        await msg.reply("» Mencoba mengirim OTP ke nomor yang diberikan...")
    else:
        await msg.reply("» Mencoba masuk menggunakan Bot Token...")
    if telethon and is_bot or telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif is_bot:
        client = Client(
            name="bot",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=phone_number,
            in_memory=True,
        )
    else:
        client = Client(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)
    await client.connect()
    try:
        code = None
        if not is_bot:
            if telethon:
                code = await client.send_code_request(phone_number)
            else:
                code = await client.send_code(phone_number)
    except (ApiIdInvalid, ApiIdInvalidError):
        return await msg.reply(
            "» Kombinasi **API_ID** and **API_HASH** kamu tidak cocok. \n\nSilakan buat sesi-mu lagi.",
            reply_markup=InlineKeyboardMarkup(gen_button),
        )
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        return await msg.reply(
            "» **PHONE_NUMBER** kamu tidak terdaftar dalam akun mana pun di Telegram.\n\nSilakan mulai membuat sesimu lagi.",
            reply_markup=InlineKeyboardMarkup(gen_button),
        )
    try:
        phone_code_msg = None
        if not is_bot:
            phone_code_msg = await msg.chat.ask(
                "» Kirimkan **OTP** yang kau terima dari Telegram ke akunmu.\nJika OTP is `12345`, **silahkan kirim seperti ini** `1 2 3 4 5`.",
                filters=filters.text,
                timeout=600,
            )
            if await is_batal(phone_code_msg):
                return
    except ListenerTimeout:
        return await msg.reply(
            "» Batas waktu yang dicapai 10 menit.\n\nSilakan mulai buat sesimu lagi.",
            reply_markup=InlineKeyboardMarkup(gen_button),
        )
    if not is_bot:
        phone_code = phone_code_msg.text.replace(" ", "")
        await phone_code_msg.delete()
        try:
            if telethon:
                await client.sign_in(phone_number, phone_code, password=None)
            else:
                await client.sign_in(phone_number, code.phone_code_hash, phone_code)
        except (PhoneCodeInvalid, PhoneCodeInvalidError):
            return await msg.reply(
                "» OTP yang Anda kirimkan **salah.**\n\nSilakan mulai buat sesimu lagi.",
                reply_markup=InlineKeyboardMarkup(gen_button),
            )
        except (PhoneCodeExpired, PhoneCodeExpiredError):
            return await msg.reply(
                "» OTP yang Anda kirimkan sudah **expired.**\n\nSilakan mulai buat sesimu lagi.",
                reply_markup=InlineKeyboardMarkup(gen_button),
            )
        except (SessionPasswordNeeded, SessionPasswordNeededError):
            try:
                two_step_msg = await msg.chat.ask(
                    "» Masukkan kata sandi **Verifikasi Dua Langkah** kamu untuk melanjutkan.",
                    filters=filters.text,
                    timeout=300,
                )
            except ListenerTimeout:
                return await msg.reply(
                    "» Batas waktu yang dicapai 5 menit.\n\nSilakan mulai buat sesimu lagi.",
                    reply_markup=InlineKeyboardMarkup(gen_button),
                )
            try:
                password = two_step_msg.text
                await two_step_msg.delete()
                if telethon:
                    await client.sign_in(password=password)
                else:
                    await client.check_password(password=password)
                if await is_batal(api_id_msg):
                    return
            except (PasswordHashInvalid, PasswordHashInvalidError):
                return await two_step_msg.reply(
                    "» Kata sandi yang kau kirimkan salah.\n\nSilakan mulai buat sesimu lagi.",
                    quote=True,
                    reply_markup=InlineKeyboardMarkup(gen_button),
                )
    elif telethon:
        try:
            await client.start(bot_token=phone_number)
        except Exception as err:
            return await msg.reply(err)
    else:
        try:
            await client.sign_in_bot(phone_number)
        except Exception as err:
            return await msg.reply(err)
    if telethon:
        string_session = client.session.save()
    else:
        string_session = await client.export_session_string()
    text = f"**Ini {ty} String Session-mu** \n\n`{string_session}` \n\n**Dibuat oleh :** @{bot.me.username}\n🗒 **Catatan :** Jangan bagikan ke siapa pun dan jangan lupa dukung yang punya bot ini jika suka."
    try:
        if not is_bot:
            await client.send_message("me", text)
        else:
            await bot.send_message(msg.chat.id, text)
    except KeyError:
        pass
    await client.disconnect()
    await bot.send_message(
        msg.chat.id,
        f'» Berhasil membuat {"Telethon" if telethon else "Pyrogram"} String Sessionmu.\n\nSilakan periksa di pesan tersimpan untuk mendapatkannya! \n\n**Bot Pembuat String oleh ** @smartcmtrobot',
    )
