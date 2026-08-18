from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from catalog import PRODUCTS
from db import save_request
from keyboards import (
    main_menu,
    question_categories_menu,
    faq_menu,
)
from states import ReturnFlow, QuestionFlow


router = Router(name="support")


async def edit_or_answer(callback: CallbackQuery, text: str, reply_markup=None):
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except Exception:
        await callback.message.answer(text, reply_markup=reply_markup)


# ---------- Возврат ----------


@router.callback_query(F.data == "menu:return")
async def return_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ReturnFlow.waiting_order)

    await edit_or_answer(
        callback,
        "Напишите номер заказа или телефон, который использовался при покупке.",
    )

    await callback.answer()


@router.message(StateFilter(ReturnFlow.waiting_order), F.text)
async def return_order(message: Message, state: FSMContext):
    await state.update_data(order_ref=message.text.strip())
    await state.set_state(ReturnFlow.waiting_reason)

    await message.answer("Кратко опишите причину возврата.")


@router.message(StateFilter(ReturnFlow.waiting_reason), F.text)
async def return_reason(message: Message, state: FSMContext):
    await state.update_data(reason=message.text.strip())
    await state.set_state(ReturnFlow.waiting_contact)

    await message.answer("Оставьте имя и телефон, чтобы мы могли связаться с вами.")


@router.message(StateFilter(ReturnFlow.waiting_contact), F.text)
async def return_contact(message: Message, state: FSMContext):
    data = await state.get_data()

    payload = {
        "order_ref": data.get("order_ref"),
        "reason": data.get("reason"),
        "contact": message.text.strip(),
    }

    order_id = await save_request(
        user_id=message.from_user.id,
        username=message.from_user.username,
        order_type="return",
        payload=payload,
        comment=message.text.strip(),
    )

    await state.clear()

    await message.answer(
        f"Заявка №{order_id} принята.\n"
        "Мы свяжемся с вами по возврату.",
        reply_markup=main_menu()
    )


# ---------- Вопросы по товару ----------


@router.callback_query(F.data == "menu:question")
async def question_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(QuestionFlow.choose_category)

    await edit_or_answer(
        callback,
        "Выберите категорию товара.",
        reply_markup=question_categories_menu(),
    )

    await callback.answer()


@router.callback_query(
    StateFilter(QuestionFlow.choose_category),
    F.data.startswith("question:category:")
)
async def question_category(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.split(":")[-1]

    if product_id not in PRODUCTS:
        await callback.answer("Категория не найдена.")
        return

    product = PRODUCTS[product_id]

    await state.update_data(question_category=product_id)

    text = (
        f"{product['emoji']} {product['name']}\n"
        f"{product['short']}\n\n"
        "Если нужен вопрос менеджеру, нажмите кнопку ниже."
    )

    await edit_or_answer(callback, text, reply_markup=faq_menu(product_id))

    await callback.answer()


@router.callback_query(
    StateFilter(QuestionFlow.choose_category),
    F.data == "question:back"
)
async def question_back(callback: CallbackQuery, state: FSMContext):
    await edit_or_answer(
        callback,
        "Выберите категорию товара.",
        reply_markup=question_categories_menu(),
    )

    await callback.answer()


@router.callback_query(
    StateFilter(QuestionFlow.choose_category),
    F.data.startswith("question:ask:")
)
async def question_ask(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.split(":")[-1]

    if product_id not in PRODUCTS:
        await callback.answer("Категория не найдена.")
        return

    await state.update_data(question_category=product_id)
    await state.set_state(QuestionFlow.waiting_question)

    await edit_or_answer(
        callback,
        "Напишите ваш вопрос. Я передам его менеджеру.",
    )

    await callback.answer()


@router.message(StateFilter(QuestionFlow.waiting_question), F.text)
async def question_text(message: Message, state: FSMContext):
    data = await state.get_data()

    payload = {
        "category": data.get("question_category"),
        "question": message.text.strip(),
    }

    order_id = await save_request(
        user_id=message.from_user.id,
        username=message.from_user.username,
        order_type="question",
        payload=payload,
        comment=message.text.strip(),
    )

    await state.clear()

    await message.answer(
        f"Вопрос №{order_id} принят.\n"
        "Менеджер свяжется с вами.",
        reply_markup=main_menu()
    )
