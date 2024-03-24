"""
MIT License

Copyright (c) 2023 SI_NN_ER_LS
Copyright (c) 2023 MissKatyPyro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import uuid
import asyncio
from database.feds_db import *

from misskaty import app, BOT_ID
from misskaty.vars import SUDO, LOG_GROUP_ID, COMMAND_HANDLER

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from misskaty.helper.functions import extract_user, extract_user_and_reason
from pyrogram.errors import FloodWait, PeerIdInvalid
from misskaty.core.decorator.errors import capture_err

__MODULE__ = "Federation"
__HELP__ = """
Semuanya menyenangkan, bahkan seorang pengirim spam mulai memasuki grupmu, dan kau harus memblokirnya. Lalu kau harus blokir lagi, dan lebih banyak lagi, dan itu menyakitkan.
Tapi grupmu banyak, dan kau tak mau spammer ini ada digrupmu - Bagaimana  caramu mengatasinya? Apa kau harus blokir manual, di semua grupmu?\n
**Tidak lagi!** Dengan Federasi, kau bisa buat larangan dalam satu obrolan dengan semua obrolan lainnya.\n
Bahkan kau bisa angkat admin federasi, agar admin tepercayamu bisa memblokir semua spammer dari obrolan yang mau kau lindungi.\n\n
"""

SUPPORT_CHAT = "@smartcmtrobot"


@app.on_message(filters.command("newfed", COMMAND_HANDLER))
@capture_err
async def new_fed(self, message):
    chat = message.chat
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_msg(
            "Federasi cuma bisa dibuat dengan mengirim pesan pribadi padaku."
        )
    if len(message.command) < 2:
        return await message.reply_msg("Silakan tulis nama federasi!")
    fednam = message.text.split(None, 1)[1]
    if fednam != "":
        fed_id = str(uuid.uuid4())
        fed_name = fednam
        x = await fedsdb.update_one(
            {"fed_id": fed_id},
            {
                "$set": {
                    "fed_name": str(fed_name),
                    "owner_id": int(user.id),
                    "fadmins": [],
                    "owner_mention": user.mention,
                    "banned_users": [],
                    "chat_ids": [],
                    "log_group_id": LOG_GROUP_ID,
                }
            },
            upsert=True,
        )
        if not x:
            return await message.reply_msg(
                f"Tidak bisa melakukan federasi! Silakan hubungi {SUPPORT_CHAT} jika masalah terus berlanjut."
            )

        await message.reply_msg(
            f"**Kau berhasil membuat federasi baru!**\nNama: `{fed_name}`\nID: `{fed_id}`\n\nGunakan perintah ini untuk bergabung dengan federasi:\n`/joinfed {fed_id}`",
            parse_mode=ParseMode.MARKDOWN,
        )
        try:
            await app.send_message(
                LOG_GROUP_ID,
                f"Federasi Baru: <b>{fed_name}</b>\nID: <pre>{fed_id}</pre>",
                parse_mode=ParseMode.HTML,
            )
        except:
            self.log.info("Tidak bisa mengirim pesan ke EVENT_LOGS")
    else:
        await message.reply_text("Mohon tuliskan nama federasinya")


@app.on_message(filters.command("delfed", COMMAND_HANDLER))
@capture_err
async def del_fed(client, message):
    chat = message.chat
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(
            "Federasi cuma bisa dihapus dengan mengirim pesan pribadi kepadaku."
        )
    args = message.text.split(" ", 1)
    if len(args) <= 1:
        return await message.reply_text("What should I delete?")
    is_fed_id = args[1].strip()
    getinfo = await get_fed_info(is_fed_id)
    if getinfo is False:
        return await message.reply_text("This federation does not exist.")
    if getinfo["owner_id"] == user.id or user.id not in SUDO:
        fed_id = is_fed_id
    else:
        return await message.reply_text("Only federation owners can do this!")
    is_owner = await is_user_fed_owner(fed_id, user.id)
    if is_owner is False:
        return await message.reply_text("Only federation owners can do this!")
    await message.reply_text(
        f"""Yakin mau menghapus federasimu? Tapi tak bsia lagi dipulihkan, seluruh daftar laranganmu akan hilang, dan '{getinfo["fed_name"]}' akan hilang selamanya.""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⚠️ Hapus Federasi ⚠️",
                        callback_data=f"rmfed_{fed_id}",
                    )
                ],
                [InlineKeyboardButton("Cancel", callback_data="rmfed_cancel")],
            ]
        ),
    )


@app.on_message(filters.command("fedtransfer", COMMAND_HANDLER))
@capture_err
async def fedtransfer(client, message):
    chat = message.chat
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(
            "Federations can only be transferred by privately messaging me."
        )
    is_feds = await get_feds_by_owner(int(user.id))
    if not is_feds:
        return await message.reply_text("**Kau belum buat federasi apa pun.**")
    if len(message.command) < 2:
        return await message.reply_text(
            "**Tentukan user atau membalas pesan mereka!**"
        )
    user_id, fed_id = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("I can't find that user.")
    if not fed_id:
        return await message.reply(
            "you need to provide a Fed Id.\n\nUsage:\n/fedtransfer @usename Fed_Id."
        )
    is_owner = await is_user_fed_owner(fed_id, user.id)
    if is_owner is False:
        return await message.reply_text("Only federation owners can do this!")
    await message.reply_text(
        "**You sure you want to transfer your federation? This cannot be reverted.**",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⚠️ Transfer Federation ⚠️",
                        callback_data=f"trfed_{user_id}|{fed_id}",
                    )
                ],
                [InlineKeyboardButton("Cancel", callback_data="trfed_cancel")],
            ]
        ),
    )


@app.on_message(filters.command("myfeds", COMMAND_HANDLER))
@capture_err
async def myfeds(client, message):
    user = message.from_user
    is_feds = await get_feds_by_owner(int(user.id))

    if is_feds:
        response_text = "\n\n".join(
            [
                f"{i + 1}.\n**Fed Name:** {fed['fed_name']}\n**Fed Id:** `{fed['fed_id']}`"
                for i, fed in enumerate(is_feds)
            ]
        )
        await message.reply_text(
            f"**Here are the federations you have created:**\n\n{response_text}"
        )
    else:
        await message.reply_text("**You haven't created any federations.**")


@app.on_message(filters.command("renamefed", COMMAND_HANDLER))
@capture_err
async def rename_fed(client, message):
    user = message.from_user
    msg = message
    args = msg.text.split(None, 2)

    if len(args) < 3:
        return await msg.reply_text("usage: /renamefed <fed_id> <newname>")

    fed_id, newname = args[1], args[2]
    verify_fed = await get_fed_info(fed_id)

    if not verify_fed:
        return await msg.reply_text("This fed does not exist in my database!")

    if await is_user_fed_owner(fed_id, user.id):
        fedsdb.update_one(
            {"fed_id": str(fed_id)},
            {"$set": {"fed_name": str(newname), "owner_id": int(user.id)}},
            upsert=True,
        )
        await msg.reply_text(f"Successfully renamed your fed name to {newname}!")
    else:
        await msg.reply_text("Only federation owner can do this!")


@app.on_message(filters.command(["setfedlog", "unsetfedlog"], COMMAND_HANDLER))
@capture_err
async def fed_log(client, message):
    chat = message.chat
    user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "Send this command on the chat which you need to set as fed log channel."
        )
    member = await app.get_chat_member(chat.id, user.id)
    if member.status in [
        ChatMemberStatus.OWNER,
        ChatMemberStatus.ADMINISTRATOR,
    ]:
        if len(message.command) < 2:
            return await message.reply_text(
                "Please provide the Id of the federation with the command!"
            )
        fed_id = message.text.split(" ", 1)[1].strip()
        info = await get_fed_info(fed_id)
        if info is False:
            return await message.reply_text("This federation does not exist.")
        if await is_user_fed_owner(fed_id, user.id):
            log_group_id = LOG_GROUP_ID if "/unsetfedlog" in message.text else chat.id
            loged = await set_log_chat(fed_id, log_group_id)
            if "/unsetfedlog" in message.text:
                return await message.reply_text("log channel removed successfully.")
            else:
                await message.reply_text("log channel set successfully.")
    else:
        await message.reply_text(
            "You need to be the chat owner or admin to use this command."
        )


@app.on_message(filters.command("chatfed", COMMAND_HANDLER))
@capture_err
async def fed_chat(self, message):
    chat = message.chat
    user = message.from_user
    fed_id = await get_fed_id(chat.id)

    member = await self.get_chat_member(chat.id, user.id)
    if member.status not in [
        ChatMemberStatus.OWNER,
        ChatMemberStatus.ADMINISTRATOR,
    ]:
        return await message.reply_text("You must be an admin to execute this command")

    if not fed_id:
        return await message.reply_text("This group is not in any federation!")
    info = await get_fed_info(fed_id)

    text = f'This group is part of the following federation:\n{info["fed_name"]} (ID: <code>{fed_id}</code>)'
    await message.reply_text(text, parse_mode=ParseMode.HTML)


@app.on_message(filters.command("joinfed", COMMAND_HANDLER))
@capture_err
async def join_fed(self, message):
    chat = message.chat
    user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "This command is specific to groups, not our pm!",
        )

    member = await self.get_chat_member(chat.id, user.id)
    fed_id = await get_fed_id(int(chat.id))

    if (
        user.id in SUDO or member.status != ChatMemberStatus.OWNER
    ) and user.id not in SUDO:
        return await message.reply_text("Only group creators can use this command!")
    if fed_id:
        return await message.reply_text("You cannot join two federations from one chat")
    args = message.text.split(" ", 1)
    if len(args) > 1:
        fed_id = args[1].strip()
        getfed = await search_fed_by_id(fed_id)
        if getfed is False:
            return await message.reply_text("Please enter a valid federation ID")

        x = await chat_join_fed(fed_id, chat.title, chat.id)
        if not x:
            return await message.reply_text(
                f"Failed to join federation! Please contact {SUPPORT_CHAT} if this problem persists!"
            )

        if get_fedlog := getfed["log_group_id"]:
            await app.send_message(
                get_fedlog,
                f'Chat **{chat.title}** has joined the federation **{getfed["fed_name"]}**',
                parse_mode=ParseMode.MARKDOWN,
            )

        await message.reply_text(
            f'This group has joined the federation: {getfed["fed_name"]}!'
        )
    else:
        await message.reply_text(
            "You need to specify which federation you're asking about by giving me a FedID!"
        )


@app.on_message(filters.command("leavefed", COMMAND_HANDLER))
@capture_err
async def leave_fed(client, message):
    chat = message.chat
    user = message.from_user

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "This command is specific to groups, not our pm!",
        )

    fed_id = await get_fed_id(int(chat.id))
    fed_info = await get_fed_info(fed_id)

    member = await app.get_chat_member(chat.id, user.id)
    if member.status == ChatMemberStatus.OWNER or user.id in SUDO:
        if await chat_leave_fed(int(chat.id)) is True:
            if get_fedlog := fed_info["log_group_id"]:
                await app.send_message(
                    get_fedlog,
                    f'Chat **{chat.title}** has left the federation **{fed_info["fed_name"]}**',
                    parse_mode=ParseMode.MARKDOWN,
                )
            await message.reply_text(
                f'This group has left the federation {fed_info["fed_name"]}!'
            )
        else:
            await message.reply_text(
                "How can you leave a federation that you never joined?!"
            )
    else:
        await message.reply_text("Only group creators can use this command!")


@app.on_message(filters.command("fedchats", COMMAND_HANDLER))
@capture_err
async def fed_chat(client, message):
    chat = message.chat
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(
            "Fedchats can only be checked by privately messaging me."
        )
    if len(message.command) < 2:
        return await message.reply_text(
            "Please write the Id of the federation!\n\nUsage:\n/fedchats fed_id"
        )
    args = message.text.split(" ", 1)
    if len(args) > 1:
        fed_id = args[1].strip()
        info = await get_fed_info(fed_id)
        if info is False:
            return await message.reply_text("This federation does not exist.")
        fed_owner = info["owner_id"]
        fed_admins = info["fadmins"]
        all_admins = [fed_owner] + fed_admins + [int(BOT_ID)]
        if user.id not in all_admins and user.id not in SUDO:
            return await message.reply_text(
                "You need to be a Fed Admin to use this command"
            )

        chat_ids, chat_names = await chat_id_and_names_in_fed(fed_id)
        if not chat_ids:
            return await message.reply_text("There are no chats in this federation!")
        text = "\n".join(
            [
                f"${chat_name} [`{chat_id}`]"
                for chat_id, chat_name in zip(chat_ids, chat_names)
            ]
        )
        await message.reply_text(
            f"**Here are the list of chats connected to this federation:**\n\n{text}"
        )


@app.on_message(filters.command("fedinfo", COMMAND_HANDLER))
@capture_err
async def fed_info(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide the Fed Id to get information!")

    fed_id = message.text.split(" ", 1)[1].strip()
    fed_info = await get_fed_info(fed_id)

    if not fed_info:
        return await message.reply_text("Federation not found.")

    fed_name = fed_info.get("fed_name")
    owner_mention = fed_info.get("owner_mention")
    fadmin_count = len(fed_info.get("fadmins", []))
    banned_users_count = len(fed_info.get("banned_users", []))
    chat_ids_count = len(fed_info.get("chat_ids", []))

    reply_text = (
        f"**Federation Information:**\n\n"
        f"**Fed Name:** {fed_name}\n"
        f"**Owner:** {owner_mention}\n"
        f"**Number of Fed Admins:** {fadmin_count}\n"
        f"**Number of Banned Users:** {banned_users_count}\n"
        f"**Number of Chats:** {chat_ids_count}"
    )

    await message.reply_text(reply_text)


@app.on_message(filters.command("fedadmins", COMMAND_HANDLER))
@capture_err
async def get_all_fadmins_mentions(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide me the Fed Id to search!")

    fed_id = message.text.split(" ", 1)[1].strip()
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text("Federation not found.")

    fadmin_ids = fed_info.get("fadmins", [])
    if not fadmin_ids:
        return await message.reply_text(f"**Owner: {fed_info['owner_mention']}\n\nNo fadmins found in the federation.")

    user_mentions = []
    for user_id in fadmin_ids:
        try:
            user = await app.get_users(int(user_id))
            user_mentions.append(f"● {user.mention}[`{user.id}`]")
        except Exception:
            user_mentions.append(f"● `Admin🥷`[`{user_id}`]")
    reply_text = f"**Owner: {fed_info['owner_mention']}\n\nList of fadmins:**\n" + "\n".join(user_mentions)
    await message.reply_text(reply_text)


@app.on_message(filters.command("fpromote", COMMAND_HANDLER))
@capture_err
async def fpromote(client, message):
    chat = message.chat
    user = message.from_user
    msg = message

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "This command is specific to groups, not our pm!",
        )

    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text(
            "You need to add a federation to this chat first!"
        )

    if await is_user_fed_owner(fed_id, user.id) or user.id in SUDO:
        user_id = await extract_user(msg)

        if user_id is None:
            return await message.reply_text("Failed to extract user from the message.")
        check_user = await check_banned_user(fed_id, user_id)
        if check_user:
            user = await app.get_users(user_id)
            reason = check_user["reason"]
            date = check_user["date"]
            return await message.reply_text(
                f"**User {user.mention} was Fed Banned.\nyou can unban the user and promote.\n\nReason: {reason}.\nDate: {date}.**"
            )

        getuser = await search_user_in_fed(fed_id, user_id)
        info = await get_fed_info(fed_id)
        get_owner = info["owner_id"]

        if user_id == get_owner:
            return await message.reply_text(
                "You do know that the user is the federation owner, right? RIGHT?"
            )

        if getuser:
            return await message.reply_text(
                "I cannot promote users who are already federation admins! Can remove them if you want!"
            )

        if user_id == BOT_ID:
            return await message.reply_text(
                "I already am a federation admin in all federations!"
            )
        res = await user_join_fed(str(fed_id), user_id)
        if res:
            await message.reply_text("Successfully Promoted!")
        else:
            await message.reply_text("Failed to promote!")
    else:
        await message.reply_text("Only federation owners can do this!")


@app.on_message(filters.command("fdemote", COMMAND_HANDLER))
@capture_err
async def fdemote(client, message):
    chat = message.chat
    user = message.from_user
    msg = message

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "This command is specific to groups, not our pm!",
        )

    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text(
            "You need to add a federation to this chat first!"
        )

    if await is_user_fed_owner(fed_id, user.id) or user.id in SUDO:
        user_id = await extract_user(msg)

        if user_id is None:
            return await message.reply_text("Failed to extract user from the message.")

        if user_id == BOT_ID:
            return await message.reply_text(
                "The thing you are trying to demote me from will fail to work without me! Just saying."
            )

        if await search_user_in_fed(fed_id, user_id) is False:
            return await message.reply_text(
                "I cannot demote people who are not federation admins!"
            )

        res = await user_demote_fed(fed_id, user_id)
        if res is True:
            await message.reply_text("Demoted from a Fed Admin!")
        else:
            await message.reply_text("Demotion failed!")
    else:
        await message.reply_text("Only federation owners can do this!")


@app.on_message(filters.command(["fban", "sfban"], COMMAND_HANDLER))
@capture_err
async def fban_user(client, message):
    chat = message.chat
    from_user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups, not our pm!.")
    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text("**This chat is not a part of any federation.")
    info = await get_fed_info(fed_id)
    fed_admins = info["fadmins"]
    fed_owner = info["owner_id"]
    all_admins = [fed_owner] + fed_admins + [int(BOT_ID)]
    if from_user.id not in all_admins and from_user.id not in SUDO:
        return await message.reply_text(
            "You need to be a Fed Admin to use this command"
        )
    if len(message.command) < 2:
        return await message.reply_text(
            "**You needed to specify a user or reply to their message!**"
        )
    user_id, reason = await extract_user_and_reason(message)
    try:
        user = await app.get_users(user_id)
    except PeerIdInvalid:
        return await message.reply_msg("Sorry, i never meet this user. So i cannot fban.")
    if not user_id:
        return await message.reply_text("I can't find that user.")
    if user_id in all_admins or user_id in SUDO:
        return await message.reply_text("I can't ban that user.")
    check_user = await check_banned_user(fed_id, user_id)
    if check_user:
        reason = check_user["reason"]
        date = check_user["date"]
        return await message.reply_text(
            f"**User {user.mention} was already Fed Banned.\n\nReason: {reason}.\nDate: {date}.**"
        )
    if not reason:
        return await message.reply("No reason provided.")

    served_chats, _ = await chat_id_and_names_in_fed(fed_id)
    m = await message.reply_text(
        f"**Fed Banning {user.mention}!**"
        + f" **This Action Should Take About {len(served_chats)} Seconds.**"
    )
    await add_fban_user(fed_id, user_id, reason)
    number_of_chats = 0
    for served_chat in served_chats:
        try:
            chat_member = await app.get_chat_member(served_chat, user.id)
            if chat_member.status == ChatMemberStatus.MEMBER:
                await app.ban_chat_member(served_chat, user.id)
                if served_chat != chat.id:
                    if not message.text.startswith("/s"):
                        await app.send_message(
                            served_chat, f"**Fed Banned {user.mention} !**"
                        )
                number_of_chats += 1
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(int(e.value))
        except Exception:
            pass
    try:
        await app.send_message(
            user.id,
            f"Hello, You have been fed banned by {from_user.mention}, You can appeal for this ban by talking to him.",
        )
    except Exception:
        pass
    await m.edit(f"Fed Banned {user.mention} !")
    ban_text = f"""
__**New Federation Ban**__
**Origin:** {message.chat.title} [`{message.chat.id}`]
**Admin:** {from_user.mention}
**Banned User:** {user.mention}
**Banned User ID:** `{user_id}`
**Reason:** __{reason}__
**Chats:** `{number_of_chats}`"""
    try:
        m2 = await app.send_message(
            info["log_group_id"],
            text=ban_text,
            disable_web_page_preview=True,
        )
        await m.edit(
            f"Fed Banned {user.mention} !\nAction Log: {m2.link}",
            disable_web_page_preview=True,
        )
    except Exception:
        await message.reply_text(
            "User Fbanned, But This Fban Action Wasn't Logged, Add Me In LOG_GROUP"
        )


@app.on_message(filters.command(["unfban", "sunfban"], COMMAND_HANDLER))
@capture_err
async def funban_user(client, message):
    chat = message.chat
    from_user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("This command is specific to groups, not our pm!.")
        return
    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text("**This chat is not a part of any federation.")
    info = await get_fed_info(fed_id)
    fed_admins = info["fadmins"]
    fed_owner = info["owner_id"]
    all_admins = [fed_owner] + fed_admins + [int(BOT_ID)]
    if from_user.id not in all_admins and from_user.id not in SUDO:
        return await message.reply_text(
            "You need to be a Fed Admin to use this command"
        )
    if len(message.command) < 2:
        return await message.reply_text(
            "**Kau harus tentukan user atau membalas pesan mereka!**"
        )
    user_id, reason = await extract_user_and_reason(message)
    user = await app.get_users(user_id)
    if not user_id:
        return await message.reply_text("I can't find that user.")
    if user_id in all_admins or user_id in SUDO:
        return await message.reply_text("**How can an admin ever be banned!.**")
    check_user = await check_banned_user(fed_id, user_id)
    if not check_user:
        return await message.reply_text(
            "**I can't unban a user who was never fedbanned.**"
        )
    if not reason:
        return await message.reply("No reason provided.")

    served_chats, _ = await chat_id_and_names_in_fed(fed_id)
    m = await message.reply_text(
        f"**Fed UnBanning {user.mention}!**"
        + f" **Tindakan cuma {len(served_chats)} Sebentar.**"
    )
    await remove_fban_user(fed_id, user_id)
    number_of_chats = 0
    for served_chat in served_chats:
        try:
            chat_member = await app.get_chat_member(served_chat, user.id)
            if chat_member.status == ChatMemberStatus.BANNED:
                await app.unban_chat_member(served_chat, user.id)
                if served_chat != chat.id:
                    if not message.text.startswith("/s"):
                        await app.send_message(
                            served_chat, f"**Fed UnBanned {user.mention} !**"
                        )
                number_of_chats += 1
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(int(e.value))
        except Exception:
            pass
    try:
        await app.send_message(
            user.id,
            f"Halo, kau sudah diberi makan tanpa larangan oleh {from_user.mention}, berterima kasilah atas tindakannya.",
        )
    except Exception:
        pass
    await m.edit(f"Fed UnBanned {user.mention} !")
    ban_text = f"""
__**Pelarangan Federasi Baru**__
**Asal:** {message.chat.title} [`{message.chat.id}`]
**Admin:** {from_user.mention}
**User Tidak Dilarang:** {user.mention}
**ID User Tidak Dilarang:** `{user_id}`
**Alasan:** __{reason}__
**Obrolan:* `{number_of_chats}`"""
    try:
        m2 = await app.send_message(
            info["log_group_id"],
            text=ban_text,
            disable_web_page_preview=True,
        )
        await m.edit(
            f"Fed Tidak Dilarang {user.mention} !\nCatatan Tindakan: {m2.link}",
            disable_web_page_preview=True,
        )
    except Exception:
        await message.reply_text(
            "User FUnbanned, Tepi Tindakan Fban Ini Tidak Tercatat, Tambahkan aku Di LOG_GROUP"
        )


@app.on_message(filters.command("fedstat", COMMAND_HANDLER))
async def fedstat(client, message):
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        await message.reply_text(
            "Status Larangan Federasi cuma bisa diperiksa dengan mengirim pesan pribadi padamu."
        )
        return
    if len(message.command) < 2:
        await message.reply_text("Please provide me the user name and Fed Id!")
        return
    user_id, fed_id = await extract_user_and_reason(message)
    if not user_id:
        user_id = message.from_user.id
        fed_id = message.text.split(" ", 1)[1].strip()
    if not fed_id:
        return await message.reply_text(
            "Berikan Fed Id beserta perintah untuk mencari."
        )
    info = await get_fed_info(fed_id)
    if not info:
        await message.reply_text("Please enter a valid fed id")
    else:
        check_user = await check_banned_user(fed_id, user_id)
        if check_user:
            user = await app.get_users(user_id)
            reason = check_user["reason"]
            date = check_user["date"]
            return await message.reply_text(
                f"**Feed {user.mention} user diblokir karena\n\nAlasan: {reason}.\nDate: {date}.**"
            )
        else:
            await message.reply_text(
                f"**User {user.mention} tak dilarang di federasi ini.**"
            )


@app.on_message(filters.command("fbroadcast", COMMAND_HANDLER))
@capture_err
async def fbroadcast_message(client, message):
    chat = message.chat
    from_user = message.from_user
    reply_message = message.reply_to_message
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("Perintah ini khusus untuk grup, bukan untuk pm!.")
        return
    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text("**Obrolan ini bukan bagian dari federasi mana pun.")
    info = await get_fed_info(fed_id)
    fed_owner = info["owner_id"]
    fed_admins = info["fadmins"]
    all_admins = [fed_owner] + fed_admins + [int(BOT_ID)]
    if from_user.id not in all_admins and from_user.id not in SUDO:
        return await message.reply_text(
            "Jadilah Admin Fed jika mau gunakan perintah ini."
        )
    if not reply_message:
        return await message.reply_text(
            "**Kau haurs balas pesan teks untuk menyiarkannya.**"
        )
    sleep_time = 0.1

    if reply_message.text:
        text = reply_message.text.markdown
    else:
        return await message.reply_text("Kau hanya bisa menyiarkan pesan teks.")

    reply_markup = None
    if reply_message.reply_markup:
        reply_markup = InlineKeyboardMarkup(reply_message.reply_markup.inline_keyboard)
    sent = 0
    chats, _ = await chat_id_and_names_in_fed(fed_id)
    m = await message.reply_text(
        f"Siaran sedang berlangsung, butuh waktu {len(chats) * sleep_time} beberapa detik."
    )
    for i in chats:
        try:
            await app.send_message(
                i,
                text=text,
                reply_markup=reply_markup,
            )
            sent += 1
            await asyncio.sleep(sleep_time)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass
    await m.edit(f"**Pesan yang disiarkan di {sent} Obrolan.**")


@app.on_callback_query(filters.regex("rmfed_(.*)"))
async def del_fed_button(client, cb):
    query = cb.data
    userid = cb.message.chat.id
    fed_id = query.split("_")[1]

    if fed_id == "cancel":
        await cb.message.edit_text("Penghapusan federasi dibatalkan")
        return

    getfed = await get_fed_info(fed_id)
    if getfed:
        if delete := fedsdb.delete_one({"fed_id": str(fed_id)}):
            await cb.message.edit_text(
                f'kau sudah menghapus Federasi-mu!   Sekarang semua Grup yang terhubung `{getfed["fed_name"]}` tidak memiliki Federasi.',
                parse_mode=ParseMode.MARKDOWN,
            )


@app.on_callback_query(filters.regex("trfed_(.*)"))
async def fedtransfer_button(client, cb):
    query = cb.data
    userid = cb.message.chat.id
    data = query.split("_")[1]

    if data == "cancel":
        await cb.message.edit_text("Penghapusan federasi dibatalkan")
        return
    data2 = data.split("|", 1)
    new_owner_id = int(data2[0])
    fed_id = data2[1]
    transferred = await transfer_owner(fed_id, userid, new_owner_id)
    if transferred:
        await cb.message.edit_text(
            "**Berhasil mengalihkan kepemilikan ke majikan baru.**"
        )


@app.on_callback_query(filters.regex("fed_(.*)"))
async def fed_owner_help(client, cb):
    query = cb.data
    userid = cb.message.chat.id
    data = query.split("_")[1]
    if data == "owner":
        text = """**👑 Khusus Pemilik Fed:**
 • /newfed <fed_name>**:** Membuat Federasi, Satu diizinkan per user.
 • /renamefed <fed_id> <new_fed_name>**:** Mengganti nama fed id menjadi nama baru.
 • /delfed <fed_id>**:** Menghapus Federasi, dan info apa pun terkait dengannya. Tidak akan membatalkan user yang diblokir.
 • /myfeds**:** Untuk membuat daftar federasi yang sudah kau buat.
 • /fedtransfer <new_owner> <fed_id>**:**Untuk mengalihkan kepemilikan fed ke orang lain.
 • /fpromote <user>**:** Mengangkat user jadi admin federasi. Mengaktifkan semua perintah untuk user di bawah "Fed Admin".
 • /fdemote <user>**:** Memecat User dari Federasi admin ke User normal.
 • /setfedlog <fed_id>**:** Menetapkan grup sebagai basis laporan log umpan untuk federasi.
 • /unsetfedlog <fed_id>**:** Menghapus grup sebagai basis laporan log feed untuk federasi.
 • /fbroadcast **:** Menyiarkan pesan ke semua grup yang sudah gabung dengan feedmu. """
    elif data == "admin":
        text = """**🔱 Admin Fed:**
 • /fban <user> <reason>**:** Fed memban user.
 • /sfban**:** Mencekal user tanpa mengirim pemberitahuan ke obrolan.
 • /unfban <user> <reason>**:** Menghapus larangan makan untuk user.
 • /sunfban**:** Membatalkan pencekalan user tanpa mengirim pemberitahuan.
 • /fedadmins**:** Menampilkan admin Federasi.
 • /fedchats <FedID>**:** Dapatkan semua obrolan yang terhubung di Federasi.
 • /fbroadcast **:** Menyiarkan pesan ke semua grup yang telah bergabung dengan feednmu.
 """
    else:
        text = """**Perintah User:**
• /fedinfo <FedID>: Informasi mengenai federasi.
• /fedadmins <FedID>: Buat daftar admin dalam sebuah federasi.
• /joinfed <FedID>: Bergabung dengan obrolan saat ini ke federasi. Obrolan cuma bisa gabung dengan satu federasi. Hanya majikan obrolan.
• /leavefed: Keluar dari federasi saat ini. Hanya majikan obrolan yang bisa.
• /fedstat <FedID>: Memberikan informasi tentang laranganmu di federasi.
• /fedstat <user ID> <FedID>: Memberikan informasi tentang larangan user dalam federasi.
• /chatfed: Informasi tentang federasi tempat obrolan saat ini berlangsung.
"""
    await cb.message.edit(
        text,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Back", callback_data="help_module(federation)"
                    ),
                ]
            ]
        ),
        parse_mode=ParseMode.MARKDOWN,
    )
