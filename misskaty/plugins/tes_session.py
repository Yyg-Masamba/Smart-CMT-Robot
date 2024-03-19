# This plugin to learn session using pyrogram
from pyrogram.types import Message

from misskaty import app


@app.on_cmd("session")
async def session(_, ctx: Message):
    nama = await ctx.chat.ask("Ketikkan namamu:")
    umur = await ctx.chat.ask("Ketikkan umurmu")
    alamat = await ctx.chat.ask("Ketikkan alamatmu:")
    await app.send_msg(
        ctx.chat.id,
        f"Namamu Adalah: {nama.text}\nUmur Kamu Adalah: {umur.text}\nAlamatmu Adalah: {alamat.text}",
    )
