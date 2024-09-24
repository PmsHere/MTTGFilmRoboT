#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

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
    
    # Allow admins to bypass subscription checks
    if update.from_user.id in auth:
        return True

    # If neither AUTH_CHANNEL nor REQ_CHANNEL is set, allow user to proceed
    if not AUTH_CHANNEL and not REQ_CHANNEL:
        return True

    is_cb = False
    if not hasattr(update, "chat"):
        update.message.from_user = update.from_user
        update = update.message
        is_cb = True

    # Create Invite Link if it does not exist
    try:
        if INVITE_LINK is None:
            invite_link = (await bot.create_chat_invite_link(
                chat_id=(int(AUTH_CHANNEL) if not REQ_CHANNEL and not JOIN_REQS_DB else REQ_CHANNEL),
                creates_join_request=True if REQ_CHANNEL and JOIN_REQS_DB else False
            )).invite_link
            INVITE_LINK = invite_link
            logger.info("Created Request link")
        else:
            invite_link = INVITE_LINK

    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await ForceSub(bot, update, file_id)

    except Exception as err:
        logger.error(f"Unable to do Force Subscribe to {REQ_CHANNEL}\nError: {err}")
        await update.reply(
            text="Something went wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False

    # Main Logic
    if REQ_CHANNEL and db().isActive():
        try:
            # Check if User is Requested to Join Channel
            user = await db().get_user(update.from_user.id)
            if user and user["user_id"] == update.from_user.id:
                return True
        except Exception as e:
            logger.exception("Error checking user in join requests: %s", str(e))
            await update.reply(
                text="Something went wrong.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return False

    try:
        # If REQ_CHANNEL is False, skip the subscription check
        if REQ_CHANNEL is False:
            return True  # Skip further checks if REQ_CHANNEL is False

        if not AUTH_CHANNEL:
            raise UserNotParticipant  # If AUTH_CHANNEL is not set, treat user as not a participant

        # Check if User is Already Joined Channel
        user = await bot.get_chat_member(
            chat_id=(int(AUTH_CHANNEL) if not REQ_CHANNEL and not db().isActive() else REQ_CHANNEL), 
            user_id=update.from_user.id
        )
        
        if user.status == "kicked":
            await bot.send_message(
                chat_id=update.from_user.id,
                text="Sorry, you are banned from using me.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_to_message_id=update.message_id
            )
            return False

        return True

    except UserNotParticipant:
        # Message for users who need to join the channel
        text = (f"**♦️ READ THIS INSTRUCTION ♦️**\n\n__🗣 നിങ്ങൾ ചോദിക്കുന്ന സിനിമകൾ നിങ്ങൾക്ക് ലഭിക്കണം എന്നുണ്ടെങ്കിൽ നിങ്ങൾ താഴെ കൊടുത്തിട്ടുള്ള ചാനലിൽ ജോയിൻ ചെയ്യണം. ജോയിൻ ചെയ്ത ശേഷം വീണ്ടും ഗ്രൂപ്പിൽ പോയി ആ ബട്ടനിൽ അമർത്തിയാൽ നിങ്ങൾക്ക് ഞാൻ ആ സിനിമ പ്രൈവറ്റ് ആയി അയച്ചു തരുന്നതാണ്..😍\n\n🗣 In Order To Get The Movie Requested By You in Our Groups, You Will Have To Join Our Official Channel First. After That, Try Accessing That Movie Again From Our Group. I'll Send You That Movie Privately 🙈__\n\n**👇 JOIN THIS CHANNEL & TRY 👇\n\n[{invite_link}]**")

        buttons = [
            [
                InlineKeyboardButton("💢 Join My Channel 💢", url=invite_link)
            ],
            [
                InlineKeyboardButton("🔄 Try Again 🔄", callback_data=f"{mode}#{file_id}")
            ]
        ]

        if file_id is False:
            buttons.pop()

        if not is_cb:
            await update.reply(
                text=text,
                quote=True,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
        return False

    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await ForceSub(bot, update, file_id)

    except Exception as err:
        logger.error(f"Something went wrong! Unable to do Force Subscribe.\nError: {err}")
        await update.reply(
            text="Something went wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False

def set_global_invite(url: str):
    global INVITE_LINK
    INVITE_LINK = url

def get_invite_link():
    return INVITE_LINK
