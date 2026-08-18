from aiogram.fsm.state import StatesGroup, State


class BuyFlow(StatesGroup):
    choose_format = State()       # сетап или отдельный товар
    choose_game = State()
    choose_game_other = State()
    choose_task = State()
    choose_budget = State()
    review_setup = State()

    waiting_name = State()
    waiting_phone = State()
    waiting_city = State()
    waiting_comment = State()


class ItemFlow(StatesGroup):
    choose_category = State()     # НОВОЕ: выбор категории
    choose_product = State()
    choose_quantity = State()

    waiting_name = State()
    waiting_phone = State()
    waiting_city = State()
    waiting_comment = State()


class ReturnFlow(StatesGroup):
    waiting_order = State()
    waiting_reason = State()
    waiting_contact = State()


class QuestionFlow(StatesGroup):
    choose_category = State()
    waiting_question = State()
