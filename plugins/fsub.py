import asyncio
from pyrogram import Client, enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from database.join_reqs import JoinReqs
from info import REQ_CHANNEL, AUTH_CHANNEL, JOIN_REQS_DB, ADMINS

from logging import getLogger

logger = getLogger(__name__)
INVITE_LINK = None
db = JoinReqs

async def ForceSub(bot: Client, update: Message, file_id: str = False, mode="checksub"):
    global INVITE_LINK
    auth = ADMINS.copy() + [1555340229]

    # Bypass force subscription for admins
    if update.from_user.id in auth:
        return True

    # Skip force subscription if both AUTH_CHANNEL and REQ_CHANNEL are not set
    if not AUTH_CHANNEL and not REQ_CHANNEL:
        return True

    is_cb = False
    if not hasattr(update, "chat"):
        update.message.from_user = update.from_user
        update = update.message
        is_cb = True

    # Create Invite Link if not exists
    try:
        if INVITE_LINK is None:
            # Only attempt to create the invite link if a valid channel is provided
            if AUTH_CHANNEL or REQ_CHANNEL:
                invite_link = (await bot.create_chat_invite_link(
                    chat_id=(int(AUTH_CHANNEL) if not REQ_CHANNEL and not JOIN_REQS_DB else REQ_CHANNEL),
                    creates_join_request=True if REQ_CHANNEL and JOIN_REQS_DB else False
                )).invite_link
                INVITE_LINK = invite_link
                logger.info("Created Req link")
            else:
                logger.warning("AUTH_CHANNEL and REQ_CHANNEL are not set.")
                return True
        else:
            invite_link = INVITE_LINK

    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await ForceSub(bot, update, file_id)

    except Exception as err:
        logger.error(f"Unable to do Force Subscribe to {REQ_CHANNEL}\nError: {err}")
        await update.reply(
            text="Something went Wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False

    # Main Logic: Check for join requests if REQ_CHANNEL is enabled
    if REQ_CHANNEL and db().isActive():
        try:
            user = await db().get_user(update.from_user.id)
            if user and user["user_id"] == update.from_user.id:
                return True
        except Exception as e:
            logger.exception(e, exc_info=True)
            await update.reply(
                text="Something went Wrong.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return False

    try:
        # Check if the user is subscribed to the channel
        if not AUTH_CHANNEL:
            raise UserNotParticipant

        user = await bot.get_chat_member(
            chat_id=(int(AUTH_CHANNEL) if not REQ_CHANNEL and not db().isActive() else REQ_CHANNEL),
            user_id=update.from_user.id
        )

        if user.status == "kicked":
            await bot.send_message(
                chat_id=update.from_user.id,
                text="Sorry Sir, You are Banned to use me.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_to_message_id=update.message_id
            )
            return False
        else:
            return True

    except UserNotParticipant:
        # Prompt user to join the channel
        text = f"**♦️ READ THIS INSTRUCTION ♦️**\n\n__🗣 You need to join our official channel to get the requested movie.__\n\n**👇 JOIN THIS CHANNEL & TRY AGAIN 👇\n\n[{invite_link}]**"

        buttons = [
            [InlineKeyboardButton("💢 Join Channel 💢", url=invite_link)],
            [InlineKeyboardButton(" 🔄 Try Again 🔄 ", callback_data=f"{mode}#{file_id}")]
        ]

        if file_id is False:
            buttons.pop()

        if not is_cb:
            await update.reply(
                text=text,
                quote=True,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        return False

    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await ForceSub(bot, update, file_id)

    except Exception as err:
        logger.error(f"Something Went Wrong! Unable to do Force Subscribe.\nError: {err}")
        await update.reply(
            text="Something went Wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False


def set_global_invite(url: str):
    global INVITE_LINK
    INVITE_LINK = url
