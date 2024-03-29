from database import dbname

from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    ChatJoinRequest,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from misskaty import app
from misskaty.vars import SUDO, COMMAND_HANDLER
from misskaty.core.decorator.permissions import adminsOnly, member_permissions

approvaldb = dbname["autoapprove"]

# For /help menu
__MODULE__ = "Autoapprove"
__HELP__ = """
perintah: /autoapprove

Modul ini membantu otomatis menerima permintaan bergabung dengan obrolan yang dikirim oleh user lewat link undangan grupmu
"""


@app.on_message(filters.command("autoapprove", COMMAND_HANDLER) & filters.group)
@adminsOnly("can_change_info")
async def approval_command(_, message: Message):
    chat_id = message.chat.id
    if (await approvaldb.count_documents({"chat_id": chat_id})) > 0:
        keyboard_OFF = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Turn OFF", callback_data="approval_off")]]
        )
        await message.reply(
            "**Persetujuan otomatis untuk obrolan ini: Diaktifkan.**",
            reply_markup=keyboard_OFF,
        )
    else:
        keyboard_ON = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Turn ON", callback_data="approval_on")]]
        )
        await message.reply(
            "**Persetujuan otomatis untuk obrolan ini: Dinonaktifkan.**",
            reply_markup=keyboard_ON,
        )


@app.on_callback_query(filters.regex("approval(.*)"))
async def approval_cb(_, cb: CallbackQuery):
    chat_id = cb.message.chat.id
    from_user = cb.from_user

    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        if from_user.id not in SUDO:
            return await cb.answer(
                f"Anda tidak memiliki izin.\n Izin: {permission}",
                show_alert=True,
            )

    command_parts = cb.data.split("_", 1)
    option = command_parts[1]

    if option == "on":
        if await approvaldb.count_documents({"chat_id": chat_id}) == 0:
            approvaldb.insert_one({"chat_id": chat_id})
            keyboard_off = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Matikan", callback_data="approval_off"
                        )
                    ]
                ]
            )
            await cb.edit_message_text(
                "**Persetujuan otomatis untuk obrolan ini: Diaktifkan.**",
                reply_markup=keyboard_off,
            )
    elif option == "off":
        if await approvaldb.count_documents({"chat_id": chat_id}) > 0:
            approvaldb.delete_one({"chat_id": chat_id})
            keyboard_on = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Nyalakan", callback_data="approval_on"
                        )
                    ]
                ]
            )
            await cb.edit_message_text(
                "**Persetujuan otomatis untuk obrolan ini: Dinonaktifkan.**",
                reply_markup=keyboard_on,
            )
    return await cb.answer()


@app.on_chat_join_request(filters.group)
async def accept(_, message: ChatJoinRequest):
    chat = message.chat
    user = message.from_user
    if (await approvaldb.count_documents({"chat_id": chat.id})) > 0:
        await app.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
