from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import database as db
from config import MIN_WITHDRAWAL
from utils import anti_flood

router = Router()

@router.message(F.text == "💰 Balance")
async def show_balance(message: Message):
    user_id = message.from_user.id
    if not await anti_flood(user_id):
        await message.answer("⏳ Wait a moment.")
        return

    user = db.get_user(user_id)
    if not user or user['registered'] != 1:
        await message.answer("⚠️ Please complete registration first. Use /start.")
        return

    await message.answer(
        f"💰 <b>Your Balance</b>\n\n"
        f"<code>{user['balance']:.2f}</code> USDT\n\n"
        f"🔹 Referrals: {user['referral_count']}\n"
        f"🔹 Wallet: {user['wallet_network']} - <code>{user['wallet'][:10]}...</code>",
        parse_mode="HTML"
    )

@router.message(F.text == "🔗 Referral")
async def show_referral(message: Message):
    user_id = message.from_user.id
    if not await anti_flood(user_id):
        await message.answer("⏳ Wait.")
        return

    user = db.get_user(user_id)
    if not user or user['registered'] != 1:
        await message.answer("⚠️ Complete registration first.")
        return

    bot_username = (await message.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    await message.answer(
        f"🔗 <b>Your Referral Link</b>\n\n"
        f"<code>{referral_link}</code>\n\n"
        f"👥 Referrals: {user['referral_count']}\n"
        f"💵 Earn 2.0 USDT per friend who joins and completes registration!",
        parse_mode="HTML",
        disable_web_page_preview=True
    )

@router.message(F.text == "↘️ Withdraw")
async def withdraw_request(message: Message):
    user_id = message.from_user.id
    if not await anti_flood(user_id):
        await message.answer("⏳ Wait.")
        return

    user = db.get_user(user_id)
    if not user or user['registered'] != 1:
        await message.answer("⚠️ Complete registration first.")
        return

    balance = user['balance']
    if balance < MIN_WITHDRAWAL:
        await message.answer(
            f"❌ Minimum withdrawal is {MIN_WITHDRAWAL} USDT.\n"
            f"Your balance: {balance:.2f} USDT"
        )
        return

    # সম্পূর্ণ ব্যালেন্স উইথড্র রিকোয়েস্ট
    db.add_withdrawal(user_id, balance, user['wallet'])
    db.update_user(user_id, balance=0.0)
    await message.answer(
        f"✅ Withdrawal request of <b>{balance:.2f} USDT</b> submitted.\n"
        f"Wallet: <code>{user['wallet_network']} - {user['wallet'][:10]}...</code>\n\n"
        f"⏳ Your request is pending admin approval.",
        parse_mode="HTML"
    )
