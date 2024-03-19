import time
from asyncio import sleep

from pyrogram import enums, filters
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    UserAdminInvalid,
)
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden

from misskaty import app
from misskaty.vars import COMMAND_HANDLER

__MODULE__ = "Inkick"
__HELP__ = """"
/instatus - Melihat status anggota grup.
/ban_ghosts - Hapus akun yang dihapus dari grup.
"""


@app.on_message(
    filters.incoming & ~filters.private & filters.command(["inkick"], COMMAND_HANDLER)
)
@app.adminsOnly("can_restrict_members")
async def inkick(_, message):
    user = await app.get_chat_member(message.chat.id, message.from_user.id)
    if user.status.value in ("administrator", "owner"):
        if len(message.command) > 1:
            input_str = message.command
            sent_message = await message.reply_text(
                "🚮**Sedang membersihkan user, mungkin butuh waktu beberapa saat...**"
            )
            count = 0
            async for member in app.get_chat_members(message.chat.id):
                if member.user.is_bot:
                    continue
                if (
                    member.user.status.value in input_str
                    and member.status.value not in ("administrator", "owner")
                ):
                    try:
                        await message.chat.ban_member(member.user.id)
                        count += 1
                        await sleep(1)
                        await message.chat.unban_member(member.user.id)
                    except (ChatAdminRequired, UserAdminInvalid):
                        await sent_message.edit(
                            "❗**Oh tidak, aku bukan admin disini**\n__Aku pergi dari sini, masukkan aku kembali dengan izin banned pengguna.__"
                        )
                        await app.leave_chat(message.chat.id)
                        break
                    except FloodWait as e:
                        await sleep(e.value)
                        await message.chat.ban_member(member.user.id)
                        await message.chat.unban_member(member.user.id)
            try:
                await sent_message.edit(
                    f"✔️ **Berhasil menendang {count} pengguna berdasarkan argumen.**"
                )

            except ChatWriteForbidden:
                await app.leave_chat(message.chat.id)
        else:
            await message.reply_text(
                "❗ **Dibutuhkan Perintah**\n__Lihat /help dalam pesan pribadi untuk informasi lebih lanjut.__"
            )
    else:
        sent_message = await message.reply_text(
            "❗ **Jadi admin dulu baru bisa.**"
        )
        await sleep(5)
        await sent_message.delete()


# Kick User Without Username
@app.on_message(
    filters.incoming & ~filters.private & filters.command(["uname"], COMMAND_HANDLER)
)
@app.adminsOnly("can_restrict_members")
async def uname(_, message):
    user = await app.get_chat_member(message.chat.id, message.from_user.id)
    if user.status.value in ("administrator", "owner"):
        sent_message = await message.reply_text(
            "🚮**Sedang membersihkan user, mungkin butuh waktu beberapa saat...**"
        )
        count = 0
        async for member in app.get_chat_members(message.chat.id):
            if not member.user.username and member.status.value not in (
                "administrator",
                "owner",
            ):
                try:
                    await message.chat.ban_member(member.user.id)
                    count += 1
                    await sleep(1)
                    await message.chat.unban_member(member.user.id)
                except (ChatAdminRequired, UserAdminInvalid):
                    await sent_message.edit(
                        "❗**Oh tidakk, aku bukan admin disini**\n__Aku pergi dari sini, masukkan aku kembali dengan izin banned pengguna.__"
                    )
                    await app.leave_chat(message.chat.id)
                    break
                except FloodWait as e:
                    await sleep(e.value)
                    await message.chat.ban_member(member.user.id)
                    await message.chat.unban_member(member.user.id)
        try:
            await sent_message.edit(
                f"✔️ **Berhasil menendang {count} pengguna berdasarkan argumen.**"
            )

        except ChatWriteForbidden:
            await app.leave_chat(message.chat.id)
    else:
        sent_message = await message.reply_text(
            "❗ **Jadi admin dulu baru bisa.**"
        )
        await sleep(5)
        await sent_message.delete()


@app.on_message(
    filters.incoming
    & ~filters.private
    & filters.command(["ban_ghosts"], COMMAND_HANDLER)
)
@app.adminsOnly("can_restrict_members")
async def rm_delacc(_, message):
    user = await app.get_chat_member(message.chat.id, message.from_user.id)
    if user.status.value in ("administrator", "owner"):
        sent_message = await message.reply_text(
            "🚮**Sedang membersihkan user, mungkin butuh waktu...**"
        )
        count = 0
        async for member in app.get_chat_members(message.chat.id):
            if member.user.is_deleted and member.status.value not in (
                "administrator",
                "owner",
            ):
                try:
                    await message.chat.ban_member(member.user.id)
                    count += 1
                    await sleep(1)
                    await message.chat.unban_member(member.user.id)
                except (ChatAdminRequired, UserAdminInvalid):
                    await sent_message.edit(
                        "❗**Oh Tidak, aku bukan dmin di grup ini. Jadikan aku admin dulu untuk <b>memblokir member</b>."
                    )
                    break
                except FloodWait as e:
                    await sleep(e.value)
                    await message.chat.ban_member(member.user.id)
                    await message.chat.unban_member(member.user.id)
        if count == 0:
            return await sent_message.edit_msg(
                "Tidak ada akun yang dihapus dalam obrolan ini."
            )
        await sent_message.edit_msg(f"✔️ **Berhasil menendang {count} akun terhapus.**")
    else:
        sent_message = await message.reply_text(
            "❗ **Jadi admin atau owner grup dulu baru bisa.**"
        )
        await sleep(5)
        await sent_message.delete()


@app.on_message(
    filters.incoming & ~filters.private & filters.command(["instatus"], COMMAND_HANDLER)
)
@app.adminsOnly("can_restrict_members")
async def instatus(client, message):
    bstat = await app.get_chat_member(message.chat.id, client.me.id)
    if bstat.status.value != "administrator":
        return await message.reply_msg(
            "Tolong berikan semua izin admin dasar, untuk menjalankan perintah ini."
        )
    start_time = time.perf_counter()
    user = await app.get_chat_member(message.chat.id, message.from_user.id)
    count = await app.get_chat_members_count(message.chat.id)
    if user.status in (
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER,
    ):
        sent_message = await message.reply_text(
            "**Lagi mengumpulkan informasi member disini...**"
        )
        recently = 0
        within_week = 0
        within_month = 0
        long_time_ago = 0
        deleted_acc = 0
        premium_acc = 0
        no_username = 0
        restricted = 0
        banned = 0
        uncached = 0
        bot = 0
        async for _ in app.get_chat_members(
            message.chat.id, filter=enums.ChatMembersFilter.BANNED
        ):
            banned += 1
        async for _ in app.get_chat_members(
            message.chat.id, filter=enums.ChatMembersFilter.RESTRICTED
        ):
            restricted += 1
        async for member in app.get_chat_members(message.chat.id):
            user = member.user
            if user.is_deleted:
                deleted_acc += 1
            elif user.is_bot:
                bot += 1
            elif user.is_premium:
                premium_acc += 1
            elif not user.username:
                no_username += 1
            elif user.status.value == "recently":
                recently += 1
            elif user.status.value == "last_week":
                within_week += 1
            elif user.status.value == "last_month":
                within_month += 1
            elif user.status.value == "long_ago":
                long_time_ago += 1
            else:
                uncached += 1
        end_time = time.perf_counter()
        timelog = "{:.2f}".format(end_time - start_time)
        await sent_message.edit_msg(
            "<b>☮️ {}\n👨‍👨‍👦 {} Anggota\n——————\n👁‍🗨 Informasi Status Anggota\n——————\n</b>⌚️ <code>recently</code>: {}\n🕒 <code>Minggu Lalu</code>: {}\n🧭 <code>Bulan Lallu</code>: {}\n🕰 <code>Sudah Lama</code>: {}\n🉑 Tanpa Username: {}\n🤐 Dibatasi: {}\n🚫 Diblokir: {}\n👻 Deleted Account (<code>/ban_ghosts</code>): {}\n🤖 Bot: {}\n⭐️ Premium User: {}\n👽 UnCached: {}\n\n⏲ Waktu eksekusi {} detik.".format(
                message.chat.title,
                count,
                recently,
                within_week,
                within_month,
                long_time_ago,
                no_username,
                restricted,
                banned,
                deleted_acc,
                bot,
                premium_acc,
                uncached,
                timelog,
            )
        )
    else:
        sent_message = await message.reply_text(
            "❗ **Jadi admin atau owner grup dulu baru bisa.**"
        )
        await sleep(5)
        await sent_message.delete()
