from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from catalog import GAMES, TASKS, BUDGETS, PRODUCTS


def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 Купить", callback_data="menu:buy")
    builder.button(text="💸 Возврат", callback_data="menu:return")
    builder.button(text="❓ Вопрос по товару", callback_data="menu:question")
    builder.adjust(1)
    return builder.as_markup()


def buy_format_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 Подобрать сетап", callback_data="buy:setup")
    builder.button(text="📦 Купить отдельный девайс", callback_data="buy:item")
    builder.button(text="🔙 Главное меню", callback_data="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def games_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for code, title in GAMES.items():
        builder.button(text=title, callback_data=f"buy:game:{code}")

    builder.adjust(2)
    return builder.as_markup()


def tasks_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for code, title in TASKS.items():
        builder.button(text=title, callback_data=f"buy:task:{code}")

    builder.adjust(1)
    return builder.as_markup()


def budgets_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for code, title in BUDGETS.items():
        builder.button(text=title, callback_data=f"buy:budget:{code}")

    builder.adjust(1)
    return builder.as_markup()


def setup_confirm_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Беру", callback_data="setup:confirm")
    builder.button(text="🔄 Пересобрать", callback_data="setup:restart")
    builder.button(text="🔙 Главное меню", callback_data="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def products_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for product_id, product in PRODUCTS.items():
        text = f"{product['emoji']} {product['name']}"
        builder.button(text=text, callback_data=f"item:product:{product_id}")

    builder.button(text="🔙 Главное меню", callback_data="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def quantity_menu(product_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for qty in range(1, 6):
        builder.button(
            text=str(qty),
            callback_data=f"item:qty:{product_id}:{qty}"
        )

    builder.button(text="🔙 Назад", callback_data="item:back")
    builder.adjust(5, 1)
    return builder.as_markup()


def question_categories_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for product_id, product in PRODUCTS.items():
        text = f"{product['emoji']} {product['name']}"
        builder.button(text=text, callback_data=f"question:category:{product_id}")

    builder.button(text="🔙 Главное меню", callback_data="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def faq_menu(product_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❓ Задать вопрос менеджеру",
        callback_data=f"question:ask:{product_id}"
    )
    builder.button(text="🔙 Назад", callback_data="question:back")
    builder.button(text="🔙 Главное меню", callback_data="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def contact_share_kb() -> ReplyKeyboardMarkup:
    """
    Временная reply-клавиатура только для шага телефона.
    Нужна для кнопки 'Поделиться контактом'.
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text="📱 Поделиться контактом", request_contact=True)
    builder.button(text="✍️ Ввести вручную")
    builder.adjust(1)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )
