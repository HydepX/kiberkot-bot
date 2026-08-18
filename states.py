from aiogram.fsm.state import StatesGroup, State


class BuyFlow(StatesGroup):
    choose_format = State()       # сетап или отдельный товар
    choose_game = State()         # выбор игры
    choose_game_other = State()   # ввод другой игры текстом
    choose_task = State()         # выбор задачи
    choose_budget = State()       # выбор бюджета
    review_setup = State()        # показ сетапа и подтверждение

    waiting_name = State()
    waiting_phone = State()
    waiting_city = State()
    waiting_comment = State()


class ItemFlow(StatesGroup):
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
