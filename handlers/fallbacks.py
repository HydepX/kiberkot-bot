from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from keyboards import main_menu


router = Router(name="fallbacks")


@router.callback_query()
async def unknown_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.answer("Неизвестная кнопка.")

    await callback.message.answer(
        "Я не распознал выбор. Возвращаю в главное меню.",
        reply_markup=main_menu()
    )


@router.message()
async def unknown_message(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Я не распознал ввод. Возврат в главное меню.",
        reply_markup=ReplyKeyboardRemove()
    )

    await message.answer(
        "Главное меню.",
        reply_markup=main_menu()
    )
