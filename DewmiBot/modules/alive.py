"""
MIT License

Copyright (c) 2022 Aʙɪsʜɴᴏɪ

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

import random
from sys import version_info

from pyrogram import __version__ as pver
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram import __version__ as lver
from telethon import __version__ as tver

from DewmiBot import pgram

ASAU = [
    [
        InlineKeyboardButton(text="ᴜᴘᴅᴀᴛᴇꜱ", url=f"https://t.me/Elina_Roxbot_News"),
        InlineKeyboardButton(text="ꜱᴜᴘᴘᴏʀᴛ", url=f"https://t.me/Elina_Roxbot_support"),
    ],
    [
        InlineKeyboardButton(
            text="ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ 💫",
            url=f"https://t.me/Elina_Roxbot?startgroup=true",
        ),
    ],
]


@pgram.on_message(filters.command("alive"))
async def awake(_, message: Message):
    await message.reply_photo(
        random.choice("https://telegra.ph/file/64c5b7990163324c33ec4-2d965458e22899ffa7.jpg"),
        caption=f"""**ʜᴇʏ, ɪ ᴀᴍ 『 ＥＬＩＮＡ 』 **
     ━━━━━━━━ 🝮✿🝮 ━━━━━━━━
♛ **ᴅᴇᴠᴏᴛᴇᴅ ᴛᴏ :** [𝘿𝙖𝙢𝙞𝙖𝙣](https://t.me/its_damiann)
» **ʟɪʙʀᴀʀʏ ᴠᴇʀsɪᴏɴ :** `13.15`
» **ᴛᴇʟᴇᴛʜᴏɴ ᴠᴇʀsɪᴏɴ :** `1.31.0`
» **ᴘʏʀᴏɢʀᴀᴍ ᴠᴇʀsɪᴏɴ :** `2.0.106`
» **ᴘʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ :** `3.11.10`
» **ʙᴏᴛ ᴠᴇʀꜱɪᴏɴ :** `1.0`
     ━━━━━━━━ 🝮✿🝮 ━━━━━━━━""",
        reply_markup=InlineKeyboardMarkup(ASAU),
    )


__mod_name__ = "𝙰ʟɪᴠᴇ"
