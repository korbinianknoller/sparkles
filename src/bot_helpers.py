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

from callback_actions import CustomCallBacksActions

async def get_balance_helper(user: list[db.User], message: Message):
    try:
        user, *_ = user
        print(user)
        await message.answer(layouts.sparkz_balance(
                            token_balance=user.token_balance,
                            presale_balance=0,
                            mission_balance=0,
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
            
        user.update(verify_twitter_task=True, token_balance=user[0].token_balance + 1000)

        await get_balance_helper(user, message)
    except Exception as e:
        print(e)

async def get_referral_helper(user: list[db.User], message: Message):
    try:
        user, *_ = user
        await message.answer(f"""
Your referral link is:   <i>{user.referral}</i>

For address: <i>{user.solana_address}</i>
""")
    except Exception as e:
        print(e)