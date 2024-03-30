import asyncio
import db
from aiogram.types import Message
import layouts
from aiogram.types import (
    Message, 
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram import Bot

from callback_actions import CustomCallBacksActions

async def get_balance_helper(user: list[db.User], message: Message):
    try:
        user, *_ = user
        print(user)
        await message.answer(layouts.sparkz_balance(
                            token_balance=user.token_balance,
                            presale_balance=user.presale_balance,
                            mission_balance=user.mission_balance,
                            address=user.solana_address))
    except Exception as e:
        print(e)


async def twitter_task_verify_helper(id: int, verified: bool, message: Message):
    try:
        if verified is False:
            await message.answer(layouts.not_done_twitter_task(), 
                                    reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text="✅ DONE", callback_data=CustomCallBacksActions(func_name="validate_twitter_task", action="twitter_task_done").pack())]
                                        ]
                                    ))
            return
            
        user = db.User.objects(from_user_id=id)
            
        if user[0].verify_twitter_task is True:
            await message.answer("Twitter task already verified")
            return
            
        user.update(verify_twitter_task=True, mission_balance=user[0].mission_balance + 100)
        await message.answer("📝 Task submitted, and your point is added. Every mission will be reverified before claim after launch")
        await get_balance_helper(user, message)
    except Exception as e:
        print(e)

async def get_referral_helper(user: list[db.User], message: Message):
    try:
        user, *_ = user
        await message.answer(f"""
Your referral link is:   <i>https://t.me/SparkzStoreBot?start={user.referral}</i>

For address: <i>{user.solana_address}</i>
""")
    except Exception as e:
        print(e)

async def handle_ref(message: Message, bot: Bot, ref: str):
    try:
        ref_owner = db.User.objects(referral=ref)
        user = db.User.objects(user_id=message.chat.id)

        if len(ref_owner) < 1:
            await message.answer("⚠️ Referal Code is not correct ⚠️")
            return
        
        if ref_owner[0].user_id == user[0].user_id:
            await message.answer("⚠️ Cannot use own referral link ⚠️")
            return
        
        if user[0].ref_self is True:
            await message.answer("⚠️ Cannot use referral code more than once ⚠️")
            return
        
        ref_owner.update(ref_count=ref_owner[0].ref_count + 1, token_balance=ref_owner[0].token_balance + 75)
        user.update(ref_self=True)

        await message.answer("Referral Linking Sucessful 🎯")
        await bot.send_message(chat_id=ref_owner[0].user_id, text="You have a new Referral bonus: 75 $SPARKZ")

    except Exception as e:
        print(e)