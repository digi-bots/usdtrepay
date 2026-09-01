from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import Registration
import database as db
from config import JOIN_BONUS, REFERRAL_BONUS
from keyboards import wallet_network_keyboard, main_menu_keyboard
from utils import anti_flood, logger

router = Router()

async def start_registration(message: Message, state: FSMContext):
    await message.answer("📧 Please enter your email address:")
    await state.set_state(Registration.waiting_for_email)

@router.message(Registration.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not await anti_flood(user_id):
        await message.answer("⏳ Slow down, please.")
        return

    email = message.text.strip()
    if "@" not in email or "." not in email:
        await message.answer("❌ Invalid email format. Please enter a valid email:")
        return

    await state.update_data(email=email)
    await message.answer("💼 Select your USDT wallet network:", reply_markup=wallet_network_keyboard())
    await state.set_state(Registration.waiting_for_wallet_network)

@router.callback_query(Registration.waiting_for_wallet_network, F.data.startswith("network_"))
async def process_wallet_network(callback: CallbackQuery, state: FSMContext):
    network = callback.data.split("_")[1]
    await state.update_data(wallet_network=network.upper())
    await callback.message.edit_text(f"📝 Enter your {network.upper()} wallet address:")
    await state.set_state(Registration.waiting_for_wallet_address)
    await callback.answer()

@router.message(Registration.waiting_for_wallet_address)
async def process_wallet_address(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not await anti_flood(user_id):
        await message.answer("⏳ Slow down.")
        return

    wallet = message.text.strip()
    if len(wallet) < 20:
        await message.answer("❌ That doesn't look like a valid wallet address. Try again:")
        return

    if db.is_wallet_used(wallet):
        await message.answer("⚠️ This wallet address is already registered. Use a different one:")
        return

    data = await state.get_data()
    email = data['email']
    network = data['wallet_network']

    db.update_user(user_id, email=email, wallet=wallet, wallet_network=network, registered=1)
    db.add_balance(user_id, JOIN_BONUS)

    user = db.get_user(user_id)
    if user and user['referred_by']:
        referrer_id = user['referred_by']
        referrer = db.get_user(referrer_id)
        if referrer:
            db.add_balance(referrer_id, REFERRAL_BONUS)
            db.increment_referral_count(referrer_id)
            logger.info(f"Referral bonus given: {referrer_id} from {user_id}")

    await state.clear()
    await message.answer(
        f"✅ Registration complete!\n\n"
        f"🎁 You received {JOIN_BONUS} USDT joining bonus.\n"
        f"💰 Your balance: {user['balance'] + JOIN_BONUS:.2f} USDT\n\n"
        f"Use the menu below to explore:",
        reply_markup=main_menu_keyboard()
    )
