import os
import re
import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    Message,
    ReplyKeyboardRemove,
)

from catalog import (
    CATEGORIES,
    PRODUCTS,
    get_setup_products,
    calculate_total,
    format_setup_text,
)
from db import save_request
from keyboards import (
    buy_format_menu,
    games_menu,
    tasks_menu,
    budgets_menu,
    item_categories_menu,
    setup_confirm_menu,
    products_menu,
    quantity_menu,
    contact_share_kb,
    main_menu,
)
from states import BuyFlow, ItemFlow

logger = logging.getLogger(__name__)
router = Router(name="shop")

MEDIA_DIR = "/opt/kiberkot/media"


def digits_only(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def get_image_path(kind: str, code: str):
    """Путь к картинке, если файл существует, иначе None."""
    base = os.path.join(MEDIA_DIR, kind, code)
    for ext in (".jpg", ".jpeg", ".png"):
        path = base + ext
        if os.path.exists(path):
            return path
    return None


async def edit_or_answer(callback: CallbackQuery, text: str, reply_markup=None, photo_path=None, parse_mode=None):
    if photo_path:
        await callback.message.answer_photo(
            photo=FSInputFile(photo_path),
            caption=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
        return
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception:
        await callback.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)


async def finalize_order(message: Message, state: FSMContext, order_type: str):
    data = await state.get_data()

    payload = {}
    if order_type == "setup":
        payload = {
            "game": data.get("game"),
            "game_other": data.get("game_other"),
            "task": data.get("task"),
            "budget": data.get("budget"),
            "setup_items": data.get("setup_items", []),
            "total_price": data.get("total_price"),
        }
    elif order_type == "item":
        payload = {
            "product_id": data.get("product_id"),
            "quantity": data.get("quantity"),
            "total_price": data.get("total_price"),
        }

    order_id = await save_request(
        user_id=message.from_user.id,
        username=message.from_user.username,
        order_type=order_type,
        payload=payload,
        name=data.get("name"),
        phone=data.get("phone"),
        city=data.get("city"),
        comment=data.get("comment"),
    )

    await state.clear()

    await message.answer(
        f"Заявка №{order_id} принята.\n"
        "Менеджер свяжется с вами для подтверждения.",
        reply_markup=main_menu(),
    )


# ---------- Вход в покупку ----------

@router.callback_query(F.data == "menu:buy")
async def buy_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(BuyFlow.choose_format)

    await edit_or_answer(
        callback,
        "Что хотите сделать: подобрать готовый сетап или выбрать отдельное устройство?",
        reply_markup=buy_format_menu(),
    )
    await callback.answer()


# ---------- Подбор сетапа ----------

@router.callback_query(StateFilter(BuyFlow.choose_format), F.data == "buy:setup")
async def start_setup(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BuyFlow.choose_game)
    await edit_or_answer(
        callback,
        "Выберите игру, под которую подбираем сетап.",
        reply_markup=games_menu(),
    )
    await callback.answer()


@router.callback_query(StateFilter(BuyFlow.choose_game), F.data.startswith("buy:game:"))
async def choose_game(callback: CallbackQuery, state: FSMContext):
    game_code = callback.data.split(":")[-1]

    if game_code == "other":
        await state.set_state(BuyFlow.choose_game_other)
        await edit_or_answer(callback, "Напишите игру текстом.")
    else:
        await state.update_data(game=game_code)
        await state.set_state(BuyFlow.choose_task)
        await edit_or_answer(
            callback,
            "Какая задача для вас важнее всего?",
            reply_markup=tasks_menu(),
        )
    await callback.answer()


@router.message(StateFilter(BuyFlow.choose_game_other), F.text)
async def choose_game_other(message: Message, state: FSMContext):
    await state.update_data(game="other", game_other=message.text.strip())
    await state.set_state(BuyFlow.choose_task)
    await message.answer(
        "Какая задача для вас важнее всего?",
        reply_markup=tasks_menu(),
    )


@router.callback_query(StateFilter(BuyFlow.choose_task), F.data.startswith("buy:task:"))
async def choose_task(callback: CallbackQuery, state: FSMContext):
    task_code = callback.data.split(":")[-1]
    await state.update_data(task=task_code)
    await state.set_state(BuyFlow.choose_budget)
    await edit_or_answer(
        callback,
        "Выберите комфортный бюджет.",
        reply_markup=budgets_menu(),
    )
    await callback.answer()


@router.callback_query(StateFilter(BuyFlow.choose_budget), F.data.startswith("buy:budget:"))
async def choose_budget(callback: CallbackQuery, state: FSMContext):
    budget_code = callback.data.split(":")[-1]
    data = await state.get_data()
    task_code = data.get("task", "universal")

    setup_items = get_setup_products(task_code, budget_code)
    total_price = calculate_total(setup_items)

    await state.update_data(
        budget=budget_code,
        setup_items=setup_items,
        total_price=total_price,
    )
    await state.set_state(BuyFlow.review_setup)

    setup_text = format_setup_text(setup_items)

    await edit_or_answer(
        callback,
        "Под ваш запрос подходит следующий сетап:\n\n"
        f"{setup_text}\n\n"
        "Оформить заявку на этот сетап?",
        reply_markup=setup_confirm_menu(),
    )
    await callback.answer()


@router.callback_query(StateFilter(BuyFlow.review_setup), F.data == "setup:confirm")
async def confirm_setup(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BuyFlow.waiting_name)
    await edit_or_answer(callback, "Как к вам обращаться?")
    await callback.answer()


@router.callback_query(StateFilter(BuyFlow.review_setup), F.data == "setup:restart")
async def restart_setup(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BuyFlow.choose_game)
    await edit_or_answer(
        callback,
        "Выберите игру, под которую подбираем сетап.",
        reply_markup=games_menu(),
    )
    await callback.answer()


# ---------- Покупка отдельного товара ----------

@router.callback_query(StateFilter(BuyFlow.choose_format), F.data == "buy:item")
async def start_item(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ItemFlow.choose_category)
    await edit_or_answer(
        callback,
        "Выберите категорию устройства.",
        reply_markup=item_categories_menu(),
    )
    await callback.answer()


@router.callback_query(StateFilter(ItemFlow.choose_category), F.data.startswith("item:cat:"))
async def choose_item_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":")[-1]
    await state.update_data(category=category)
    await state.set_state(ItemFlow.choose_product)

    cat_title = CATEGORIES.get(category, category)
    cat_img = get_image_path("categories", category)

    await edit_or_answer(
        callback,
        f"{cat_title}\nВыберите устройство.",
        reply_markup=products_menu(category),
        photo_path=cat_img,
    )
    await callback.answer()


@router.callback_query(StateFilter(ItemFlow.choose_product), F.data == "item:cats")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ItemFlow.choose_category)
    await edit_or_answer(
        callback,
        "Выберите категорию устройства.",
        reply_markup=item_categories_menu(),
    )
    await callback.answer()


@router.callback_query(StateFilter(ItemFlow.choose_product), F.data.startswith("item:product:"))
async def choose_product(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.split(":")[-1]

    if product_id not in PRODUCTS:
        await callback.answer("Товар не найден.")
        return

    await state.update_data(product_id=product_id)
    await state.set_state(ItemFlow.choose_quantity)

    p = PRODUCTS[product_id]
    text = (
        f"{p['emoji']} <b>{p['name']}</b>\n"
        f"{p['short']}\n\n"
        f"💰 Цена: <b>{p['price']} ₽</b>\n\n"
        "Выберите количество."
    )

    await edit_or_answer(
        callback,
        text,
        reply_markup=quantity_menu(product_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(StateFilter(ItemFlow.choose_quantity), F.data == "item:back")
async def item_back(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category = data.get("category", "mice")
    await state.set_state(ItemFlow.choose_product)
    await edit_or_answer(
        callback,
        "Выберите устройство.",
        reply_markup=products_menu(category),
    )
    await callback.answer()


@router.callback_query(StateFilter(ItemFlow.choose_quantity), F.data.startswith("item:qty:"))
async def choose_quantity(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    if len(parts) != 4:
        await callback.answer("Не удалось распознать выбор.")
        return

    product_id = parts[2]
    quantity = int(parts[3])

    if product_id not in PRODUCTS:
        await callback.answer("Товар не найден.")
        return

    total_price = PRODUCTS[product_id]["price"] * quantity

    await state.update_data(quantity=quantity, total_price=total_price)
    await state.set_state(ItemFlow.waiting_name)

    await edit_or_answer(callback, "Как к вам обращаться?")
    await callback.answer()


# ---------- Общая цепочка контактов ----------

@router.message(StateFilter(BuyFlow.waiting_name, ItemFlow.waiting_name), F.text)
async def waiting_name(message: Message, state: FSMContext):
    current_state = await state.get_state()
    flow_name = current_state.split(":")[0]

    await state.update_data(name=message.text.strip())

    if flow_name == "BuyFlow":
        await state.set_state(BuyFlow.waiting_phone)
    else:
        await state.set_state(ItemFlow.waiting_phone)

    await message.answer(
        "Укажите номер телефона или нажмите кнопку ниже, чтобы поделиться контактом.",
        reply_markup=contact_share_kb(),
    )


@router.message(StateFilter(BuyFlow.waiting_phone, ItemFlow.waiting_phone), F.contact)
async def waiting_phone_contact(message: Message, state: FSMContext):
    current_state = await state.get_state()
    flow_name = current_state.split(":")[0]

    await state.update_data(phone=message.contact.phone_number)
    await message.answer("Спасибо, контакт получен.", reply_markup=ReplyKeyboardRemove())

    if flow_name == "BuyFlow":
        await state.set_state(BuyFlow.waiting_city)
    else:
        await state.set_state(ItemFlow.waiting_city)

    await message.answer("В каком городе находится получатель?")


@router.message(StateFilter(BuyFlow.waiting_phone, ItemFlow.waiting_phone), F.text == "✍️ Ввести вручную")
async def waiting_phone_manual_button(message: Message, state: FSMContext):
    await message.answer("Введите телефон текстом.", reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(BuyFlow.waiting_phone, ItemFlow.waiting_phone), F.text)
async def waiting_phone_text(message: Message, state: FSMContext):
    current_state = await state.get_state()
    flow_name = current_state.split(":")[0]

    digits = digits_only(message.text)

    if len(digits) < 10:
        await message.answer(
            "Не могу распознать номер. Попробуйте ещё раз или нажмите «Поделиться контактом».",
            reply_markup=contact_share_kb(),
        )
        return

    await state.update_data(phone=message.text.strip())
    await message.answer("Спасибо, контакт получен.", reply_markup=ReplyKeyboardRemove())

    if flow_name == "BuyFlow":
        await state.set_state(BuyFlow.waiting_city)
    else:
        await state.set_state(ItemFlow.waiting_city)

    await message.answer("В каком городе находится получатель?")


@router.message(StateFilter(BuyFlow.waiting_city, ItemFlow.waiting_city), F.text)
async def waiting_city(message: Message, state: FSMContext):
    current_state = await state.get_state()
    flow_name = current_state.split(":")[0]

    await state.update_data(city=message.text.strip())

    if flow_name == "BuyFlow":
        await state.set_state(BuyFlow.waiting_comment)
    else:
        await state.set_state(ItemFlow.waiting_comment)

    await message.answer("Есть ли комментарий к заказу? Если нет, отправьте «Нет».")


@router.message(StateFilter(BuyFlow.waiting_comment, ItemFlow.waiting_comment), F.text)
async def waiting_comment(message: Message, state: FSMContext):
    current_state = await state.get_state()
    flow_name = current_state.split(":")[0]

    comment_text = message.text.strip()

    if comment_text.lower() in {"нет", "-", "пропустить"}:
        comment_text = None

    await state.update_data(comment=comment_text)

    if flow_name == "BuyFlow":
        await finalize_order(message, state, "setup")
    else:
        await finalize_order(message, state, "item")
