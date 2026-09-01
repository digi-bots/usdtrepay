from aiogram.fsm.state import StatesGroup, State

class Registration(StatesGroup):
    waiting_for_email = State()
    waiting_for_wallet_network = State()
    waiting_for_wallet_address = State()

class BroadcastStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_text = State()
    waiting_for_media = State()
    waiting_for_buttons = State()
    confirm_broadcast = State()
