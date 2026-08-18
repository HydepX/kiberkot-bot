from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from keyboards import main_menu


router = Router(name="common")


START_TEXT = (
    "Привет! Я КиберКот — бот для подбора периферии Razer.\n"
    "Выберите раздел."
)

HELP_TEXT = (
    "Разделы:\n\n"
    "🛒 Купить — подбор сетапа или покупка отдельного устройства.\n"
    "💸 Возврат — заявка на возврат.\n"
    "❓ Вопрос по товару — FAQ и вопрос менеджеру.\n\n"
    "Команды:\n"
    "/start — главное меню\n"
    "/help — справка\n"
    "/cancel — отменить текущее действие"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    # На всякий случай убираем возможную reply-клавиатуру.
    await message.answer("Возврат в главное меню.", reply_markup=ReplyKeyboardRemove())
    await message.answer(START_TEXT, reply_markup=main_menu())


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(HELP_TEXT, reply_markup=main_menu())


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Действие отменено.",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(START_TEXT, reply_markup=main_menu())


@router.callback_query(F.data == "nav:main")
async def nav_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    try:
        await callback.message.edit_text(
            START_TEXT,
            reply_markup=main_menu()
        )
    except Exception:
        await callback.message.answer(
            START_TEXT,
            reply_markup=main_menu()
        )

    await callback.answer()
