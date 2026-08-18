import json
import logging
from html import escape

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import ADMIN_ID
from database import get_all_orders, get_order_by_id
from services.order_service import ORDER_TYPES, process_new_order, process_admin_action

logger = logging.getLogger(__name__)

router = Router(name="admin")

STATUS_ICONS = {"new": "🆕", "processing": "🛠", "completed": "✅", "cancelled": "❌"}


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def build_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"adm_ok_{order_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"adm_no_{order_id}"),
        ],
        [InlineKeyboardButton(text="🛠 В работу", callback_data=f"adm_proc_{order_id}")],
        [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="adm_back_list")],
    ])


async def render_orders(message: Message):
    orders = await get_all_orders(limit=10)

    if not orders:
        await message.answer("📭 Заявок пока нет.")
        return

    text = "📋 <b>Последние 10 заявок:</b>\n\n"
    keyboard = []

    for order in orders:
        o_id, user_id, o_type, status, data_json, phone, created_at = order
        type_icon = ORDER_TYPES.get(o_type, "📦")
        s_icon = STATUS_ICONS.get(status, "⚪️")

        brief = "Нет деталей"
        try:
            data = json.loads(data_json or "{}")
            if data:
                brief = str(list(data.values())[0])
                if len(brief) > 30:
                    brief = brief[:30] + "..."
        except Exception:
            brief = "Ошибка данных"

        text += f"{s_icon} <b>#{o_id}</b> | {type_icon} | <i>{escape(brief)}</i>\n"
        keyboard.append([
            InlineKeyboardButton(text=f"👁 Заявка #{o_id}", callback_data=f"adm_view_{o_id}")
        ])

    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML",
    )


@router.message(Command("orders"))
async def cmd_orders(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔️ У вас нет прав администратора.")
    await render_orders(message)


@router.message(Command("testorder"))
async def cmd_testorder(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔️ У вас нет прав администратора.")

    order_id = await process_new_order(
        bot,
        user_id=message.from_user.id,
        username=message.from_user.username,
        order_type="buy",
        data_dict={"товар": "Razer Viper V4 Pro", "количество": 1, "тест": "да"},
        phone="+7 900 000-00-00",
    )
    await message.answer(f"🧪 Тестовая заявка #{order_id} создана. Уведомление ушло тебе в личку.")


@router.callback_query(F.data.startswith("adm_view_"))
async def process_admin_view(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("⛔️ Нет прав", show_alert=True)

    order_id = int(callback.data.split("_")[2])
    order = await get_order_by_id(order_id)

    if not order:
        return await callback.answer("Заявка не найдена", show_alert=True)

    o_id, user_id, o_type, status, data_json, phone, created_at = order

    text = (
        f"📋 <b>Заявка #{order_id}</b>\n"
        f"👤 ID клиента: <code>{user_id}</code>\n"
        f"📦 Тип: {ORDER_TYPES.get(o_type, o_type)}\n"
        f"📊 Статус: {status}\n"
        f"📞 Телефон: {escape(phone or 'не указан')}\n"
        f"🕒 Дата: {created_at}\n\n"
        f"📝 <b>Детали:</b>\n"
    )

    try:
        data = json.loads(data_json or "{}")
        for k, v in data.items():
            text += f"  • <i>{escape(str(k))}:</i> {escape(str(v))}\n"
    except Exception:
        text += "Нет данных\n"

    await callback.message.edit_text(
        text, reply_markup=build_order_keyboard(order_id), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "adm_back_list")
async def back_to_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("⛔️ Нет прав", show_alert=True)
    await render_orders(callback.message)
    await callback.answer()


@router.callback_query(F.data.startswith(("adm_ok_", "adm_no_", "adm_proc_")))
async def process_admin_actions(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        return await callback.answer("⛔️ Нет прав", show_alert=True)

    try:
        await process_admin_action(bot, callback)
        await callback.answer("Статус обновлен!")
    except Exception as e:
        logger.exception("Admin action failed")
        await callback.answer(f"Ошибка: {e}", show_alert=True)
