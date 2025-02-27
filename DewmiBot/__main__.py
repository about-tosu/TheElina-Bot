import html
import importlib
import json
import re
import time
import traceback
from sys import argv
from typing import Optional

from telegram import (
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ParseMode,
    Update,
    User,
)
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown

from DewmiBot import (
    ALLOW_EXCL,
    BL_CHATS,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    SUPPORT_CHAT,
    TOKEN,
    URL,
    WEBHOOK,
    StartTime,
    dispatcher,
    pbot,
    telethn,
    updater,
)

from DewmiBot.modules import ALL_MODULES
from DewmiBot.modules.helper_funcs.alternate import typing_action
from DewmiBot.modules.helper_funcs.chat_status import is_user_admin
from DewmiBot.modules.helper_funcs.misc import paginate_modules
from DewmiBot.modules.helper_funcs.readable_time import get_readable_time

PM_START_TEXT = """
ʜᴇʏ ᴛʜᴇʀᴇ! [👋](https://telegra.ph/file/8538d6790c194e6066d49-98546f355407c7c78b.jpg), My Name Is  *Ξ L I N Λ 👸*. 

ɪ ᴄᴀɴ ʜᴇʟᴘ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘs ᴡɪᴛʜ ᴜsᴇғᴜʟ ғᴇᴀᴛᴜʀᴇs, ғᴇᴇʟ ғʀᴇᴇ ᴛᴏ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs! 
ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ᴀs *ᴀᴅᴍɪɴ* ᴛᴏ ʟᴇᴛ ᴍᴇ ɢᴇᴛ ɪɴ ᴀᴄᴛɪᴏɴ!

⁉️ 𝐖𝐇𝐀𝐓 𝐀𝐑𝐄 𝐓𝐇𝐄 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒? ⁉️
ʜɪᴛ  /help ᴛᴏ sᴇᴇ *ᴀʟʟ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅs* ᴀɴᴅ ʜᴏᴡ ᴛʜᴇʏ ᴡᴏʀᴋ!
"""

PM_IMG = "https://envs.sh/jQH.jpg"


HELP_STRINGS = f"""
*⚊❮❮❮『 Ξ L I N Λ  HΞLP MΞИU 』❯❯❯⚊*

ʜᴇʏ !👋 ɪ'ᴍ  Ξ L I N Λ [👸](https://telegra.ph/file/8538d6790c194e6066d49-98546f355407c7c78b.jpg)

ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ғᴜɴᴛɪᴏɴs ᴡɪʟʟ ʜᴇʟᴘғᴜʟ ᴛᴏ ʏᴏᴜ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ. 😇

""".format(
    dispatcher.bot.first_name,
    "" if not ALLOW_EXCL else "\nAll commands can either be used with / or !.\n",
)


DONATE_STRING = """
ʜᴀʏ, ɢʟᴀᴅ ᴛᴏ ʜᴇʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴏɴᴀᴛᴇ! 
ʏᴏᴜ ᴄᴀɴ ᴅᴏɴᴀᴛᴇ ᴛᴏ ᴛʜᴇ ᴏɢɪɢɪɴᴀʟ ᴡʀɪᴛᴇʀ's ᴏғ ᴛʜᴇ ʙᴀsᴇ ᴄᴏᴅᴇ,
sᴜᴘᴘᴏʀᴛ ᴛʜᴇᴍ [ᴛᴏsᴜ](http://t.me/about_tosuu)
"""

BUTTONS = [
    [
        InlineKeyboardButton(
            text="ᴀᴅᴅ ᴍᴇ ✚", url="http://t.me/Elina_Roxbot?startgroup=true"),
    ],
    [
        InlineKeyboardButton(text="ᴜᴘᴅᴀᴛᴇs", url=f"https://t.me/Elina_Roxbot_News"),
        InlineKeyboardButton(
            text="ʙᴏᴛ 𝙨ᴜᴘᴘᴏʀᴛ", url=f"https://t.me/Elina_Roxbot_Support"
        ),
    ],
    [
        InlineKeyboardButton(text="ᴄʜᴀᴛ ɢʀᴏᴜᴘ", url=f"https://t.me/anime_x_group"),
        InlineKeyboardButton(
            text="ᴀʙᴏᴜᴛ", callback_data="aboutmanu_"
        ),
    ],
    [
        InlineKeyboardButton(text="ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs", url=f"http://t.me/Elina_Roxbot?start=help"),
    ],
]
IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
USER_BOOK = []
DATA_IMPORT = []
DATA_EXPORT = []

CHAT_SETTINGS = {}
USER_SETTINGS = {}

GDPR = []

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("DewmiBot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if not imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__gdpr__"):
        GDPR.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__user_book__"):
        USER_BOOK.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id, text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
    )


@run_async
def test(update, context):
    try:
        print(update)
    except:
        pass
    update.effective_message.reply_text(
        "Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN
    )
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)


@run_async
def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            update.effective_message.reply_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(BUTTONS),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60, 
            )
    else:
        update.effective_message.reply_text(
            " I'm awake already!\n<b>Haven't slept since:</b> <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

    except TimedOut:
        print("no nono3")
    except NetworkError:
        print("no nono4")
    except ChatMigrated as err:
        print("no nono5")
        print(err)
    except TelegramError:
        print(error)


@run_async
def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "⚊❮❮❮『 HΞLP FO𝚁 *{}* MODULΞ 』❯❯❯⚊".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="🔙ʙᴀᴄᴋ", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            update.effective_message.reply_photo(
                PM_IMG,
                HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()
    except Exception as e:
        query.message.edit_text(e)
        LOGGER.exception("Exception in help buttons. %s", str(query.data))


@run_async
def DewmiBot_about_callback(update, context):
    query = update.callback_query
    if query.data == "aboutmanu_":
        query.message.edit_text(
            text=f"** ʜᴇʀᴇ's ʙᴀsɪᴄ ʜᴇʟᴘ ʀᴇɢᴀʀᴅɪɴɢ* *ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ? **"
            f"\n\n ғɪʀsᴛʟʏ ᴀᴅᴅ  *{dispatcher.bot.first_name}*  ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ʙʏ ᴘʀᴇssɪɴɢ [here](http://t.me/Elina_Roxbot?startgroup=true)\n"
            f"\n\n ᴀғᴛᴇʀ ᴀᴅᴅɪɴɢ ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ᴍᴀɴᴜᴀʟʟʏ ᴡɪᴛʜ ғᴜʟʟ ʀɪɢʜᴛs ғᴏʀ ғᴀsᴛᴇʀ ᴇxᴘᴇʀɪᴇɴᴄᴇ.\n"
            f"\n\n ᴛʜᴀɴ sᴇɴᴅ `/admincache@Elina_Roxbot` ɪɴ ᴛʜᴀᴛ ᴄʜᴀᴛ ᴛᴏ ʀᴇғʀᴇsʜ ᴀᴅᴍɪɴ ʟɪsᴛ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ.\n"
            f"\n\n *ᴀʟʟ ᴅᴏɴᴇ ɴᴏᴡ ᴜsᴇ ʙᴇʟᴏᴡ ɢɪᴠᴇɴ ʙᴜᴛᴛᴏɴ's ᴛᴏ ᴋɴᴏᴡ ᴀʙᴏᴜᴛ ᴜsᴇ!*\n"
            f"",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                    InlineKeyboardButton(text="Aᴅᴍɪɴ", callback_data="aboutmanu_credit"),
                    InlineKeyboardButton(text="Nᴏᴛᴇs", callback_data="aboutmanu_permis"),
                 ],
                 [
                    InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", callback_data="aboutmanu_spamprot"),
                    InlineKeyboardButton(text="Cʀᴇᴅɪᴛ", callback_data="aboutmanu_tac"),
                 ],
                    [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data="aboutmanu_back")],
                ]
            ),
        )
    elif query.data == "aboutmanu_back":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(BUTTONS),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
        )

    elif query.data == "aboutmanu_credit":
        query.message.edit_text(
            text=f"*Let's make your group bot effective now*"
            f"\nCongragulations, @Elina_Roxbot now ready to manage your group."
            f"\n\n*Admin Tools*"
            f"\nBasic Admin tools help you to protect and powerup your group."
            f"\nYou can ban members, Kick members, Promote someone as admin through commands of bot."
            f"\n\n*Welcome*"
            f"\nLets set a welcome message to welcome new users coming to your group."
            f"send `/setwelcome [message]` to set a welcome message!",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data="aboutmanu_")]]
            ),
        )
        

    elif query.data == "aboutmanu_permis":
        query.message.edit_text(
            text=f"<b> sᴇᴛᴛɪɴɢ ᴜᴘ ɴᴏᴛᴇs</b>"
            f"\nʏᴏᴜ ᴄᴀɴ sᴀᴠᴇ ᴍᴇssᴀɢᴇ/ᴍᴇᴅɪᴀ/ᴀᴜᴅɪᴏ ᴏʀ ᴀɴʏᴛʜɪɴɢ ᴀs ɴᴏᴛᴇs"
            f"\nᴛᴏ ɢᴇᴛ ᴀ ɴᴏᴛᴇ sɪᴍᴘʟʏ ᴜsᴇ # ᴀᴛ ᴛʜᴇ ʙᴇɢɪɴɴɪɴɢ ᴏғ ᴀ ᴡᴏʀᴅ"
            f"\n\nʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ sᴇᴛ ʙᴜᴛᴛᴏɴs ғᴏʀ ɴᴏᴛᴇs ᴀɴᴅ ғɪʟᴛᴇʀs (ʀᴇғᴇʀ ʜᴇʟᴘ ᴍᴇɴᴜ)",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data="aboutmanu_")]]
            ),
        )
    elif query.data == "aboutmanu_spamprot":
        query.message.edit_text(
            text="* @Elina_Roxbot support chats*"
            "\nJoin Support Group/Channel",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url="https://t.me/nothing_bots_support"),
                    InlineKeyboardButton(text="ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ", url="https://t.me/nothing_bots_updates"),
                 ],
                 [
                    InlineKeyboardButton(text="🖲ᴇʟɪɴᴀ sᴜᴘᴘᴏʀᴛ🖲", url="https://t.me/Elina_Roxbot_support"),
                    InlineKeyboardButton(text="ᴇʟɪɴᴀ Uᴘᴅᴀᴛᴇs", url="https://t.me/Elina_Roxbot_News"),
                 ],
                 [
                    InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data="aboutmanu_"),
                 
                 ],
                ]
            ),
        )
    elif query.data == "aboutmanu_tac":
        query.message.edit_text(
            text=f"* ᴄʀᴇᴅɪᴛs  ғᴏʀ @Elina_Roxbot  ＤＥＶ *\n"
            f"\n ᴅᴇᴠ ᴀʙᴏᴜᴛ ᴛʜᴇ ʙᴏᴛs ɪ ᴄᴏᴅᴇᴅ ᴀɴᴅ ᴄʀᴇᴀᴛᴇ ＥＬＩＮＡ"
            f"\n Special credits [𝙏𝙤𝙨𝙪❤‍🩹](https://github.com/about-tosuu)"
            f"\n ғɪɴᴀʟʟʏ ᴍʏ sᴘᴇᴄɪᴀʟ ᴛʜᴀɴᴋs ᴛᴏ ʏᴏᴜ ғᴏʀ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="ᴅᴇᴠ", url="https://t.me/its_damiann"),
                    InlineKeyboardButton(text="ᴀʙᴏᴜᴛ ᴅᴇᴠ", url="https://t.me/about_tosuu"),
                 ],   
                ]
            ),
        )


@run_async
@typing_action
def get_help(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="ʜᴇʟᴘ",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "Contact me in PM to get the list of possible commands.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ʜᴇʟᴘ",
                            url="t.me/{}?start=help".format(context.bot.username),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="ꜱᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ",
                            url="https://t.me/Elina_Roxbot_support",
                        )
                    ],
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


@run_async
def settings_button(update, context):
    query = update.callback_query
    user = update.effective_user
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = context.bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="🔙 ʙᴀᴄᴋ",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = context.bot.get_chat(chat_id)
            query.message.edit_text(
                "Hi there! There are quite a few settings for *{}* - go ahead and pick what "
                "you're interested in.".format(chat.title),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = context.bot.get_chat(chat_id)
            query.message.edit_text(
                "Hi there! There are quite a few settings for *{}* - go ahead and pick what "
                "you're interested in.".format(chat.title),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = context.bot.get_chat(chat_id)
            query.message.edit_text(
                text="Hi there! There are quite a few settings for *{}* - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()
    except Exception as excp:
        if excp.message == "Message is not modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message can't be deleted":
            pass
        else:
            query.message.edit_text(excp.message)
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


@run_async
def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="sᴇᴛᴛɪɴɢs",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)


def migrate_chats(update, context):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def is_chat_allowed(update, context):
    if len(WHITELIST_CHATS) != 0:
        chat_id = update.effective_message.chat_id
        if chat_id not in WHITELIST_CHATS:
            context.bot.send_message(
                chat_id=update.message.chat_id, text="Unallowed chat! Leaving..."
            )
            try:
                context.bot.leave_chat(chat_id)
            finally:
                raise DispatcherHandlerStop
    if len(BL_CHATS) != 0:
        chat_id = update.effective_message.chat_id
        if chat_id in BL_CHATS:
            context.bot.send_message(
                chat_id=update.message.chat_id, text="Unallowed chat! Leaving..."
            )
            try:
                context.bot.leave_chat(chat_id)
            finally:
                raise DispatcherHandlerStop
    if len(WHITELIST_CHATS) != 0 and len(BL_CHATS) != 0:
        chat_id = update.effective_message.chat_id
        if chat_id in BL_CHATS:
            context.bot.send_message(
                chat_id=update.message.chat_id, text="Unallowed chat, leaving"
            )
            try:
                context.bot.leave_chat(chat_id)
            finally:
                raise DispatcherHandlerStop
    else:
        pass


@run_async
def donate(update: Update, context: CallbackContext):
    update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )
        update.effective_message.reply_text(
            "You can also donate to the person currently running me "
            "[here]({})".format(DONATION_LINK),
            parse_mode=ParseMode.MARKDOWN,
        )

    else:
        pass


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendMessage(f"@{SUPPORT_CHAT}", "ʏᴇs! ɪ'ᴍ ᴏɴʟɪɴᴇ ✅")
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    # test_handler = CommandHandler("test", test)
    start_handler = CommandHandler("start", start, pass_args=True)

    help_handler = CommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_")

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_")

    about_callback_handler = CallbackQueryHandler(
        DewmiBot_about_callback, pattern=r"aboutmanu_"
    )

    donate_handler = CommandHandler("donate", donate)

    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)
    is_chat_allowed_handler = MessageHandler(Filters.group, is_chat_allowed)

    # dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(is_chat_allowed_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_handler)

    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)
            client.run_until_disconnected()

    else:
        LOGGER.info("Using long polling.")
        updater.start_polling(timeout=15, read_latency=4, clean=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
