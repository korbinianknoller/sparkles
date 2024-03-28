import asyncio
import logging
import sys
import datetime
from os import getenv
from io import BytesIO
import random
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from enum import Enum
from aiogram.types import (
    Message, 
    FSInputFile,
    BufferedInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram import F
from aiogram.enums.chat_member_status import ChatMemberStatus
from captcha.image import ImageCaptcha
import db
import layouts
from callback_actions import CustomCallBacksActions
import bot_helpers

class UserType(Enum):
    NO_USER = 1
    VERIFIED_USER = 2
    NOT_VERIFIED_USER = 3



logger = logging.getLogger(__name__)

print("ready to move")

TOKEN = getenv("BOT_TOKEN")

sparkz_store_channel_id = "@sparkzstore"

sparkz_store_group_id = "@sparkz_store"

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

def generate_captcha():
    return random.randint(100000, 999999)

def write_bytesio_to_file(filename: str, bytesio: BytesIO):
    """
    Write the contents of the given BytesIO to a file.
    Creates the file or overwrites the file if it does
    not exist yet. 
    """
    with open(filename, "wb") as outfile:
        # Copy the BytesIO stream to the output file
        outfile.write(bytesio.getbuffer().tobytes())

# Store CAPTCHA data (chat_id, captcha_string) in a dictionary

def check_verification(id: int) -> UserType:
    capt = db.Captcha.objects(user_id=id)
    if len(capt) < 1:
        return UserType.NO_USER
    elif capt[0].verified == True:
        return UserType.VERIFIED_USER
    return UserType.NOT_VERIFIED_USER

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`

    try:
        print("get fonts")
        custom_fonts = ['fonts/alex.ttf', 'fonts/bodon.ttf']
        print("fonts gotten")
        captcha = ImageCaptcha(fonts=custom_fonts, width=360, height=160)
        # Generate a CAPTCHA
        data = generate_captcha()
        print(data)
        capt = db.Captcha.objects(user_id=message.chat.id)
        if len(capt) < 1:
            capt = db.Captcha(user_id=message.chat.id, data=data, created_at=datetime.datetime.now())
            capt.save()
        else:
            capt.update(data=data)

        data = str(data)
        print("write image to container")
        captcha_image = captcha.generate(data)
        # captcha.write(data, 'out.png')

        # write_bytesio_to_file("out.png", captcha_image)
        print("image written")
        # print(captcha_image)

        image_file = BufferedInputFile(captcha_image.getbuffer().tobytes(), "out.png")

        print("image gotten")
        
        await message.answer_photo(photo=image_file, caption="Prove You're Human (Type in chat below 👇)")
    except Exception as e:
        print(e)


@dp.message(F.text.regexp(r"\d\d\d\d\d\d").as_("digits"))
async def verify_captcha(message: Message):
    try:
        captcha_data = db.Captcha.objects(user_id=message.chat.id)

        if check_verification(message.chat.id) == UserType.VERIFIED_USER:
            await message.answer("<b> ⚠️ Already Verified </b>")
            return
        
        if check_verification(message.chat.id) == UserType.NO_USER:
            await message.answer("<b>Please Verify You're Human First (Click the start Command or type '/start' to begin)</b>")
            return

        captcha_data, *_ = captcha_data

        print(captcha_data)
        print(message.text)

        if captcha_data.data and captcha_data.data == int(message.text):
             db.Captcha.objects(user_id=message.chat.id).update(set__verified=True)
             await message.answer(layouts.welcome_message(message.from_user.first_name))
             await asyncio.sleep(1)
             await message.answer("<b>Submit your solana wallet address 👇👇👇 (use phantom or solflare) </b>")
        else:
            await message.answer("⚠️ Captcha Failed! Please try again.")
            await command_start_handler(message)
        
    except Exception as e:
        print(e)

@dp.message(F.text.regexp("[1-9A-HJ-NP-Za-km-z]{32,44}"))
async def solana_verify(message: Message):
    try:
        if check_verification(message.chat.id) is UserType.NO_USER:
            await message.answer("<b>Please Verify You're Human First (Click the start Command or type '/start' to begin)</b>")
            return
        
        await message.answer("<i> checking wallet address...</i>")

        user = db.User.objects(user_id=message.chat.id)

        if len(user) > 0:
            user, *_ = user
        else:
            user = db.User(
                user_id=message.chat.id, 
                solana_address=message.text, 
                from_user_id=message.from_user.id,
                created_at=datetime.datetime.now(),
                referral="referral:" + str(message.chat.id),
                token_balance = 0
                )
            user.save()
        await asyncio.sleep(1.5)
        print("user", user)
        await message.answer(
            layouts.address_verified(user.solana_address),
            reply_markup= InlineKeyboardMarkup(
                     inline_keyboard=[
                         [InlineKeyboardButton(text="Press 🪂Airdrop to begin the airdrop tasks.", callback_data=CustomCallBacksActions(func_name="solana_verify", action="airdrop").pack())],
                         [InlineKeyboardButton(text="Press 👥Referral to get the unique referral link of the linked wallet.", callback_data=CustomCallBacksActions(func_name="solana_verify", action="referral").pack())],
                         [InlineKeyboardButton(text="Press 💰Balance to see the accumulated balances of the linked wallet.", callback_data=CustomCallBacksActions(func_name="solana_verify", action="balance").pack())]
                    ])
            )
    except Exception as e:
        print(e)



@dp.callback_query(CustomCallBacksActions.filter(F.func_name == "solana_verify"))
async def callback_solana_verify(callback_query: CallbackQuery, bot: Bot) -> None:
   
    try:
        if check_verification(callback_query.message.chat.id) is UserType.NO_USER:
            await callback_query.message.answer("<b>Please Verify You're Human First (Click the start Command or type '/start' to begin)</b>")
            return
        
        
        if callback_query.data.endswith("airdrop"):
            await callback_query.message.answer(layouts.airdrop_message(), reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="✅ DONE", callback_data=CustomCallBacksActions(func_name="callback_solana_verify", action="airdrop_done").pack())]
                ]
            ))

        elif callback_query.data.endswith("referral"):
            user = db.User.objects(from_user_id=callback_query.from_user.id)
            await bot_helpers.get_referral_helper(user, callback_query.message)
        else:
            user = db.User.objects(from_user_id=callback_query.from_user.id)
            await bot_helpers.get_balance_helper(user, callback_query.message)
    except Exception as e:
        print(e)



@dp.callback_query(CustomCallBacksActions.filter((F.func_name == "callback_solana_verify") & (F.action == "airdrop_done")))
async def done_callback_airdrop_done(callback_query: CallbackQuery, bot: Bot):
    try:
        print(callback_query.from_user)
        if check_verification(callback_query.message.chat.id) is UserType.NO_USER:
            await callback_query.message.answer("<b>Please Verify You're Human First (Click the start Command or type '/start' to begin)</b>")
            return
        
        channel_member = await bot.get_chat_member(chat_id=sparkz_store_channel_id, user_id=callback_query.from_user.id)
        
        group_member = await bot.get_chat_member(chat_id=sparkz_store_group_id, user_id=callback_query.from_user.id)

        print(channel_member)

        print(group_member)
        if channel_member.status is ChatMemberStatus.LEFT:
            await callback_query.message.answer("⚠️ Challenge not completed ⚠️")
            await callback_query.message.reply(""" 
Join our <a href='https://t.me/sparkzstore'>Official Channel</a> 
                                            
Click on ✅ DONE to verify
                                            """,
                    reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=[
                        [InlineKeyboardButton(text="✅ DONE", callback_data=CustomCallBacksActions(func_name="callback_solana_verify", action="airdrop_done").pack())]
                    ]
                ))
            return
        
        elif group_member.status == ChatMemberStatus.LEFT:
            await callback_query.message.answer("⚠️ Challenge not done ⚠️")
            await callback_query.message.reply(""" 
Join group our <a href="https://t.me/sparkz_store">Official Group</a> \

Click on ✅ DONE to verify""",
                    reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=[
                        [InlineKeyboardButton(text="✅ DONE", callback_data=CustomCallBacksActions(func_name="callback_solana_verify", action="airdrop_done").pack())]
                    ]
                ))
            return
        
        user = db.User.objects(user_id=callback_query.message.chat.id)

        if len(user) > 0:
            user, *_ = user
            await callback_query.message.answer(layouts.air_drop_task(user.solana_address), 
                                                reply_markup=InlineKeyboardMarkup(
                                                    inline_keyboard=[
                                                        [InlineKeyboardButton(text="✅ VERIFY AIRDROP DATA", callback_data=CustomCallBacksActions(func_name="done_callback_airdrop_done", action="airdrop_task_done").pack())]
                                                    ]
                                                )
                                                )
    except Exception as e:
        await callback_query.message.reply("⚠️ Cannot verify if you're a member. ⚠️")
        print(e)

@dp.callback_query(CustomCallBacksActions.filter((F.func_name == "done_callback_airdrop_done") & (F.action == "airdrop_task_done")))
async def share_link(callback_query: CallbackQuery, bot: Bot):
    try:
        if check_verification(callback_query.message.chat.id) is UserType.NO_USER:
            await callback_query.message.answer("<b>Please Verify You're Human First (Click the start Command or type '/start' to begin)</b>")
            return
        
        await callback_query.message.answer(layouts.share_twitter_link())
    except Exception as e:
        print(e)




    
@dp.callback_query(CustomCallBacksActions.filter((F.func_name == "validate_twitter_task") & (F.action == "twitter_task_done")))
async def callback_validate_twitter_task(callback_query: CallbackQuery, bot: Bot):
    try:
        verified = True

        await bot_helpers.twitter_task_verify_helper(callback_query.from_user.id, verified, callback_query.message)
    except Exception as e:
        print(e)


@dp.message(F.text.regexp("^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"))
async def validate_twitter_task(message: Message):
    try:
        verified = False
        if check_verification(message.chat.id) is UserType.NO_USER:
            await message.answer("<b>Please Verify You're Human First (Click the start Command or type '/start' to begin)</b>")
            return
        print(message.text)
        if "x.com" not in message.text and "twitter.com" not in message.text:
            await message.answer("⚠️ Wrong Link Sent ⚠️")
            return

        
        await message.answer("Validating Data, Kindly wait..")

        await bot_helpers.twitter_task_verify_helper(message.from_user.id, verified, message)
    except Exception as e:
        print(e)

@dp.message(F.text.startswith('admin/'))
async def admin_messages(message:Message, bot: Bot):
    try:
        admin = await bot.get_chat_member(chat_id=sparkz_store_channel_id, user_id=message.from_user.id)

        if admin.status is not ChatMemberStatus.ADMINISTRATOR and admin.status is not ChatMemberStatus.CREATOR:
            return
        
        data = message.text
        directives = data.replace("admin/", "")

        users = db.User.objects()

        for u in users:
            await bot.send_message(u.user_id, directives)
    except Exception as e:
        print(e)

@dp.message(Command("referral"))
async def referral_command(message: Message):
    if check_verification(message.chat.id) is UserType.NO_USER:
            await message.answer("""
<b>Please Verify You're Human First (Click the start Command or type '/start' to begin)</b>

And after Link your Solana address to get verified.                                
""")
            return
    await message.reply("Please provide the referral link below 👇")

@dp.message(F.text.regexp(r"referral:\d+"))
async def handle_referral(message: Message, bot: Bot):
    try:
        if check_verification(message.chat.id) is UserType.NO_USER:
            await message.answer("""
<b>Please Verify You're Human First (Click the start Command or type '/start' to begin)</b>

And after Link your Solana address to get verified.                                 
""")
            return
        ref_owner = db.User.objects(referral=message.text)
        user = db.User.objects(user_id=message.chat.id)

        if len(ref_owner) < 1:
            await message.answer("⚠️ Referal Code is not correct ⚠️")
            return
        
        if ref_owner[0].user_id == user[0].user_id:
            await message.answer("⚠️ Cannot use own referral link ⚠️")
            return
        
        if ref_owner[0].ref_used is True:
            await message.answer("⚠️ Referal Code already used ⚠️")
            return
        
        if user[0].ref_self is True:
            await message.answer("⚠️ Cannot supply referral code more than once ⚠️")
            return
        
        ref_owner.update(ref_used=True, token_balance=ref_owner[0].token_balance + 75)
        user.update(ref_self=True)

        await message.answer("Referral Linking Sucessful 🎯")
        await bot.send_message(chat_id=ref_owner[0].user_id, text="You have a new Referral bonus: 75 $SPARKZ")


    except Exception as e:
        print(e)

    


# @dp.message()
# async def echo_handler(message: types.Message) -> None:
#     """
#     Handler will forward receive a message back to the sender

#     By default, message handler will handle all message types (like a text, photo, sticker etc.)
#     """
#     try:
#         print("Invalid Message Passed")
#         await message.reply("⚠️ Invalid Message Passed ⚠️")
#     except TypeError:
#         await message.answer("Wrong!!!")


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())