import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from nlu import classify_intent
from states import BuyFlow, ReturnFlow, QuestionFlow
from keyboards import buy_format_menu, question_categories_menu

logger = logging.getLogger(__name__)
router = Router(name="nlu")


@router.message(StateFilter(None), F.text)
async def nlu_dispatcher(message: Message, state: FSMContext):
    """
    NLU-роутер: ловит свободный текст, когда юзер НЕ в FSM.
    Классифицирует через Gemini и перенаправляет на нужный сценарий.
    """
    text = message.text.strip()
    intent = await classify_intent(text)
    logger.info(f"NLU | user={message.from_user.id} | text='{text}' | intent={intent}")

    if intent == "buy":
        await state.set_state(BuyFlow.choose_format)
        await message.answer(
            "🛒 Понял, хочешь прикупить что-то из Razer!\n"
            "Выбирай — полный сетап или отдельный девайс:",
            reply_markup=buy_format_menu(),
        )

    elif intent == "return":
        await state.set_state(ReturnFlow.waiting_order)
        await message.answer(
            "🔄 Без проблем, давай оформим возврат.\n"
            "Напишите номер заказа или телефон, который использовался при покупке."
        )

    elif intent == "question":
        await state.set_state(QuestionFlow.choose_category)
        await message.answer(
            "❓ Конечно, отвечу на любой вопрос по девайсам!\n"
            "Выберите категорию товара.",
            reply_markup=question_categories_menu(),
        )

    # intent == "other" → ничего не делаем, сообщение пролетит в fallback
