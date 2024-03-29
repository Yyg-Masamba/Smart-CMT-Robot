from curses.ascii import isblank
from pyrogram import Client, filters
from pyrogram.errors import ChannelPrivate, PeerIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from database.users_chats_db import db
from misskaty import app
from misskaty.helper.localization import use_chat_lang
from misskaty.vars import COMMAND_HANDLER, LOG_CHANNEL, SUDO, SUPPORT_CHAT


@app.on_message(filters.incoming & filters.private, group=-5)
async def ban_reply(_, ctx: Message):
    if not ctx.from_user:
        return
    isban, alesan = await db.get_ban_status(ctx.from_user.id)
    if isban:
        await ctx.reply_msg(
            f'Maaf, kau dilarang untuk menggunakanku. \nAlasan Pelarangan: {alesan["reason"]}'
        )
        await ctx.stop_propagation()


@app.on_message(filters.group & filters.incoming, group=-2)
@use_chat_lang()
async def grp_bd(self: Client, ctx: Message, strings):
    if not ctx.from_user:
        return
    if not await db.is_chat_exist(ctx.chat.id):
        try:
            total = await self.get_chat_members_count(ctx.chat.id)
        except ChannelPrivate:
            await ctx.stop_propagation()
        r_j = ctx.from_user.mention if ctx.from_user else "Anonymous"
        await self.send_message(
            LOG_CHANNEL,
            strings("log_bot_added", context="grup_tools").format(
                ttl=ctx.chat.title, cid=ctx.chat.id, tot=total, r_j=r_j
            ),
        )
        await db.add_chat(ctx.chat.id, ctx.chat.title)
    chck = await db.get_chat(ctx.chat.id)
    if chck["is_disabled"]:
        buttons = [
            [InlineKeyboardButton("Support", url=f"https://t.me/{SUPPORT_CHAT}")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        vazha = await db.get_chat(ctx.chat.id)
        try:
            k = await ctx.reply_msg(
                f"OBROLAN TIDAK DIIZINKAN 🈴\n\nMajikanku melarangku bekerja di sini!\nAlasan : <code>{vazha['reason']}</code>.",
                reply_markup=reply_markup,
            )
            await k.pin()
        except:
            pass
        try:
            await self.leave_chat(ctx.chat.id)
        except:
            pass
        await ctx.stop_propagation()


@app.on_message(filters.command("banuser", COMMAND_HANDLER) & filters.user(SUDO))
async def ban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply("Give me a user id / username")
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply(
            "Ini adalah pengguna yang tidak valid, pastikan aku pernah bertemu dengannya."
        )
    except IndexError:
        return await message.reply("This might be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f"Error - {e}")
    else:
        isban, alesan = await db.get_ban_status(k.id)
        if isban:
            return await message.reply(
                f"{k.mention} sudah dilarang\n<b>Alasan:</b> {alesan['reason']}"
            )
        await db.ban_user(k.id, reason)
        await message.reply(f"Berhasil memblokir pengguna {k.mention}!!\n<b>Alasan:</b> {reason}")


@app.on_message(filters.command("unbanuser", COMMAND_HANDLER) & filters.user(SUDO))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply("Give me a user id / username")
    r = message.text.split(None)
    chat = message.text.split(None, 2)[1] if len(r) > 2 else message.command[1]
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply(
            "Ini pengguna yang tidak valid, pastikan dia pernah bertemu sebelumnya."
        )
    except IndexError:
        return await message.reply("This might be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f"Error - {e}")
    else:
        jar = await db.get_ban_status(k.id)
        if not jar["is_banned"]:
            return await message.reply(f"{k.mention} is not yet banned.")
        await db.remove_ban(k.id)
        await message.reply(f"Berhasil membuka blokir pengguna {k.mention}!!!")


@app.on_message(filters.command("disablechat", COMMAND_HANDLER) & filters.user(SUDO))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply("Give me a chat id")
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat_ = int(chat)
    except:
        return await message.reply("Berikan ID Obrolan yang Valid")
    cha_t = await db.get_chat(chat_)
    if not cha_t:
        return await message.reply("Obrolan Tak Ditemukan di DB")
    if cha_t["is_disabled"]:
        return await message.reply(
            f"Obrolan ini sudah dinonaktifkan:\nAlasan-<code> {cha_t['reason']} </code>"
        )
    await db.disable_chat(chat_, reason)
    await message.reply("Obrolan Berhasil Dinonaktifkan")
    try:
        buttons = [
            [InlineKeyboardButton("Support", url=f"https://t.me/{SUPPORT_CHAT}")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_,
            text=f"<b>Halo temanku, \nMajikanku menyuruhku untuk keluar dari grup, jadi aku pergi! Jika mau memasukkanku lagi, hubungi Majikanku.</b> \nAlasan : <code>{reason}</code>",
            reply_markup=reply_markup,
        )
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f"Error - {e}")


@app.on_message(filters.command("enablechat", COMMAND_HANDLER) & filters.user(SUDO))
async def re_enable_chat(_, ctx: Message):
    if len(ctx.command) == 1:
        return await ctx.reply("Berikan id chat")
    chat = ctx.command[1]
    try:
        chat_ = int(chat)
    except:
        return await ctx.reply("Berikan ID Obrolan yang Valid")
    sts = await db.get_chat(int(chat))
    if not sts:
        return await ctx.reply("Obrolan Tidak Ditemukan di DB!")
    if not sts.get("is_disabled"):
        return await ctx.reply("Obrolan ini belum dinonaktifkan.")
    await db.re_enable_chat(chat_)
    await ctx.reply("Chat Berhasil diaktifkan kembali")
