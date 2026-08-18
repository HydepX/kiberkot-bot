import json
import logging

from aiogram import Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from html import escape

from config import ADMIN_ID
from database import create_order, update_order_status, get_order_by_id

logger = logging.getLogger(__name__)

ORDER_TYPES = {
    "buy": "🛒 Покупка",
    "return": "🔄 Возврат",
    "question": "❓ Вопрос",
    "handover": "🆘 Связь с менеджером",
}

STATUS_TEXT = {
    "completed": "✅ Подтверждено",
    "cancelled": "❌ Отклонено",
    "processing": "🛠 В работе",
}


async def process_new_order(
    bot: Bot,
    user_id: int,
    username: str,
    order_type: str,
    data_dict: dict,
    phone: str = None,
) -> int:
    """
    Единая точка входа: сохраняем заявку и шлём уведомление админу.
    """
    data_json = json.dumps(data_dict, ensure_ascii=False)
    order_id = await create_order(user_id, order_type, data_json, phone)

    type_text = ORDER_TYPES.get(order_type, order_type)

    text = (
        f"🚨 <b>Новая заявка #{order_id}!</b>\n\n"
        f"👤 <b>Клиент:</b> @{escape(username or 'без_ника')} (ID: <code>{user_id}</code>)\n"
        f"📞 <b>Телефон:</b> {escape(phone or 'не указан')}\n"
        f"📦 <b>Тип:</b> {type_text}\n\n"
        f"📝 <b>Детали:</b>\n"
    )
    for key, value in data_dict.items():
        text += f"  • <i>{escape(str(key))}:</i> {escape(str(value))}\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"adm_ok_{order_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"adm_no_{order_id}"),
        ],
        [InlineKeyboardButton(text="🛠 В работу", callback_data=f"adm_proc_{order_id}")],
    ])

    try:
        await bot.send_message(ADMIN_ID, text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления админу: {e}")

    return order_id


async def process_admin_action(bot: Bot, callback: CallbackQuery):
    """
    Обработка кнопок админа: обновляет статус, пишет клиенту, правит сообщение.
    """
    action, order_id_str = callback.data.rsplit("_", 1)
    order_id = int(order_id_str)

    actions_map = {
        "adm_ok": ("completed", "✅ Ваша заявка #{id} подтверждена! Менеджер скоро свяжется с вами."),
        "adm_no": ("cancelled", "❌ К сожалению, заявка #{id} отклонена. Попробуйте обратиться позже."),
        "adm_proc": ("processing", "🛠 Ваша заявка #{id} взята в работу! Ожидайте."),
    }

    if action not in actions_map:
        return

    new_status, template = actions_map[action]

    await update_order_status(order_id, new_status)

    order = await get_order_by_id(order_id)
    if order:
        user_id = order[1]
        try:
            await bot.send_message(user_id, template.format(id=order_id))
        except Exception:
            pass  # пользователь мог заблокировать бота

    try:
        await bot.edit_message_text(
            text=f"Заявка #{order_id}: <b>{STATUS_TEXT[new_status]}</b>",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            parse_mode="HTML",
        )
    except Exception:
        pass
