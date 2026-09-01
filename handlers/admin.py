from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import database as db
from config import ADMIN_IDS
from keyboards import admin_withdrawal_keyboard
from utils import anti_flood, logger

router = Router()

def is_admin(message: Message) -> bool:
    return message.from_user.id in ADMIN_IDS

@router.message(Command("stats"), is_admin)
async def admin_stats(message: Message):
    user_count = db.get_user_count()
    total_balance = db.get_total_balance()
    await message.answer(
        f"📊 <b>USDT Repay Bot Statistics</b>\n\n"
        f"👥 Registered users: {user_count}\n"
        f"💰 Total balance: {total_balance:.2f} USDT\n"
        f"📬 Pending withdrawals: use /pending",
        parse_mode="HTML"
    )

@router.message(Command("users"), is_admin)
async def admin_users(message: Message):
    users = db.get_all_users()
    if not users:
        await message.answer("No registered users yet.")
        return
    user_list = "\n".join([f"<code>{uid}</code>" for uid in users[:50]])
    await message.answer(f"👥 <b>Registered Users (first 50)</b>:\n{user_list}", parse_mode="HTML")

@router.message(Command("pending"), is_admin)
async def admin_pending(message: Message):
    pending = db.get_pending_withdrawals()
    if not pending:
        await message.answer("No pending withdrawals.")
        return

    for w in pending:
        user = db.get_user(w['user_id'])
        if user:
            text = (
                f"🔔 <b>Withdrawal #{w['id']}</b>\n"
                f"👤 User: {user['first_name']} (ID: {w['user_id']})\n"
                f"💵 Amount: {w['amount']} USDT\n"
                f"🔗 Wallet: {w['wallet'][:15]}...\n"
                f"📅 Date: {w['request_date']}\n"
            )
            await message.answer(text, parse_mode="HTML", reply_markup=admin_withdrawal_keyboard(w['id']))

@router.callback_query(F.data.startswith("approve_"), is_admin)
async def approve_withdrawal(callback: CallbackQuery):
    withdrawal_id = int(callback.data.split("_")[1])
    db.update_withdrawal_status(withdrawal_id, "approved")
    await callback.message.edit_text(f"✅ Withdrawal #{withdrawal_id} approved.")
    await callback.answer("Approved.")

@router.callback_query(F.data.startswith("reject_"), is_admin)
async def reject_withdrawal(callback: CallbackQuery):
    withdrawal_id = int(callback.data.split("_")[1])
    # টাকা ফেরত দিন
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, amount FROM withdrawals WHERE id = ?", (withdrawal_id,))
    w = cur.fetchone()
    conn.close()
    if w:
        db.add_balance(w['user_id'], w['amount'])
    db.update_withdrawal_status(withdrawal_id, "rejected")
    await callback.message.edit_text(f"❌ Withdrawal #{withdrawal_id} rejected. Balance refunded.")
    await callback.answer("Rejected.")
