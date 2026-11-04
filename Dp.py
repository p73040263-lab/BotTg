import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup
import db

TOKEN = "9280180788:AAEbFK93jbajnEFnL9NOuyOioxaCwQdykxk"
ADMIN_USERNAME = "@AdmHoney"
ADMIN_USERNAME_CLEAN = ADMIN_USERNAME.lstrip('@')

bot = Bot(token=TOKEN)
dp = Dispatcher()
db.init_db()

# ---------- Middleware для логирования входящих ----------
class LoggingMiddleware:
    async def __call__(self, handler, event, data):
        if isinstance(event, types.Message):
            user = event.from_user
            db.add_or_update_user(user.id, user.username, user.first_name, user.last_name)
            if event.text:
                db.log_message(user.id, 'in', event.text)
        return await handler(event, data)

dp.message.middleware(LoggingMiddleware())

# ---------- Категории и клавиатуры (без изменений) ----------
CATEGORY_NAMES = {
    "cat_gpu": "👧Девочки 9-17 лет👧",
    "cat_cpu": "👦Мальчики 5-16 лет👦",
    "cat_mb": "🔞Жесткое мальчики🔞",
    "cat_ram": "🔞Жесткое девочки🔞",
    "cat_storage": "👧👦Мальчики и девочки👧👦",
    "cat_psu": "👪С родителями👪",
    "cat_coolers": "🐶🐱С животными 🐶🐱",
    "cat_cases": "🔞БДСМ🔞",
    "cat_peripherals": "МАЛЬЧИКИ ВСЕ ВОЗРАСТА",
}

CATEGORY_PRICES = {
    "cat_gpu": {"200": "300 руб.", "500": "650 руб.", "1000": "850 руб.", "2000": "1000 руб."},
    "cat_cpu": {"200": "300 руб.", "500": "650 руб.", "1000": "850 руб.", "2000": "1000 руб."},
    "cat_mb": {"200": "300 руб.", "500": "650 руб.", "1000": "850 руб.", "2000": "1000 руб."},
    "cat_ram": {"200": "300 руб.", "500": "650 руб.", "1000": "850 руб.", "2000": "1000 руб."},
    "cat_storage": {"200": "300 руб.", "500": "650 руб.", "1000": "850 руб.", "2000": "1000 руб."},
    "cat_psu": {"200": "300 руб.", "500": "650 руб.", "1000": "850 руб.", "2000": "1000 руб."},
    "cat_coolers": {"200": "300 руб.", "500": "650 руб.", "1000": "850 руб.", "2000": "1000 руб."},
    "cat_cases": {"200": "300 руб.", "500": "650 руб.", "1000": "850 руб.", "2000": "1000 руб."},
    "cat_peripherals": {"200": "300 руб.", "500": "650 руб.", "1000": "850 руб.", "2000": "1000 руб."},
}

main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📦 Ассортимент 📦", callback_data="catalog")],
        [InlineKeyboardButton(text="🛡️ Доказательства наличия (Фото)", callback_data="proofs")],
    ]
)

categories_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👧Девочки 9-17 лет👧", callback_data="cat_gpu"),
            InlineKeyboardButton(text="👦Мальчики 5-16 лет👦", callback_data="cat_cpu"),
        ],
        [
            InlineKeyboardButton(text="🔞Жесткое мальчики🔞", callback_data="cat_mb"),
            InlineKeyboardButton(text="🔞Жесткое девочки🔞", callback_data="cat_ram"),
        ],
        [
            InlineKeyboardButton(text="👧👦Мальчики и девочки👧👦", callback_data="cat_storage"),
            InlineKeyboardButton(text="👪С родителями👪", callback_data="cat_psu"),
        ],
        [
            InlineKeyboardButton(text="🐶🐱С животными 🐶🐱", callback_data="cat_coolers"),
            InlineKeyboardButton(text="🔞БДСМ🔞", callback_data="cat_cases"),
        ],
        [
            InlineKeyboardButton(text="МАЛЬЧИКИ ВСЕ ВОЗРАСТА", callback_data="cat_peripherals")
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main")],
    ]
)

paid_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="confirm_pay")]
    ]
)

def get_quantity_keyboard(cat_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="200 ВИДЕО.", callback_data=f"buy_{cat_code}_200"),
                InlineKeyboardButton(text="500 ВИДЕО.", callback_data=f"buy_{cat_code}_500"),
                InlineKeyboardButton(text="1000 ВИДЕО.", callback_data=f"buy_{cat_code}_1000"),
                InlineKeyboardButton(text="2000 ВИДЕО(СКИДКА).", callback_data=f"buy_{cat_code}_2000"),
            ],
            [InlineKeyboardButton(text="⬅️ К категориям", callback_data="catalog")],
        ]
    )

# ---------- Обработчики ----------
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    db.add_or_update_user(message.from_user.id, message.from_user.username,
                          message.from_user.first_name, message.from_user.last_name)
    caption_text = (
        "Добро пожаловать! 👋\n"
        "Мой магазин называется Honey DP 🍯.\n"
        "У нас вы найдёте качественные каналы с ДП по отличным ценам."
        
    )
    photo_path = "startimage.jpg"
    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        sent = await message.answer_photo(photo=photo, caption=caption_text, reply_markup=main_keyboard)
        db.log_message(user_id, 'out', sent.caption or "Фото с подписью")
    else:
        sent = await message.answer(caption_text, parse_mode="Markdown", reply_markup=main_keyboard)
        db.log_message(user_id, 'out', sent.text)

@dp.callback_query(F.data == "proofs")
async def send_proofs(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    photo1_path = "dokv1.jpg"
    photo2_path = "dokv2.jpg"
    if os.path.exists(photo1_path):
        await callback.message.answer_photo(photo=FSInputFile(photo1_path), caption="🛡️ Доказательство наличия товара (Фото 1)")
        db.log_message(user_id, 'out', "🛡️ Доказательство наличия товара (Фото 1)")
    else:
        sent = await callback.message.answer("🛡️ [Фото 1 не найдено] Доказательство наличия товара")
        db.log_message(user_id, 'out', sent.text)
    if os.path.exists(photo2_path):
        await callback.message.answer_photo(photo=FSInputFile(photo2_path), caption="🛡️ Фото канала (Фото 2)")
        db.log_message(user_id, 'out', "🛡️ Фото канала (Фото 2)")
    else:
        sent = await callback.message.answer("🛡️ [Фото 2 не найдено] Фото канала")
        db.log_message(user_id, 'out', sent.text)
    await callback.answer()

@dp.callback_query(F.data == "catalog")
async def show_catalog(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    sent = await callback.message.answer("Выберите интересующую вас категорию:", reply_markup=categories_keyboard)
    db.log_message(user_id, 'out', sent.text)
    await callback.answer()

@dp.callback_query(F.data == "to_main")
async def back_to_main(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await start_handler(callback.message)
    await callback.answer()

@dp.callback_query(F.data.startswith("cat_"))
async def category_select(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cat_code = callback.data
    cat_name = CATEGORY_NAMES.get(cat_code, "Запчасти")
    sent = await callback.message.answer(
        f"Вы выбрали категорию **{cat_name}**.\nУкажите необходимое количество:",
        parse_mode="Markdown",
        reply_markup=get_quantity_keyboard(cat_code),
    )
    db.log_message(user_id, 'out', sent.text)
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def process_payment(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data[4:]
    parts = data.split("_")
    count = parts[-1]
    cat_code = "_".join(parts[:-1])
    cat_name = CATEGORY_NAMES.get(cat_code, "Товар")
    price = CATEGORY_PRICES.get(cat_code, {}).get(count, "По запросу")
    pay_text = (
        f"💳 **Оплата заказа**\n\n"
        f"Товар: **{cat_name}** ({count} видео.)\n"
        f"Сумма к оплате: **{price}**\n\n"
        f"**Реквизиты для перевода:**\n"
        f"🏦 Карта: `2200 7020 8324 9263` (T-Банк)\n"
        f"После перевода нажмите кнопку «Я оплатил» ниже."
    )
    sent = await callback.message.answer(pay_text, parse_mode="Markdown", reply_markup=paid_keyboard)
    db.log_message(user_id, 'out', sent.text)
    await callback.answer()

@dp.callback_query(F.data == "confirm_pay")
async def confirm_payment(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    msg_text = (
        f"Спасибо! Пожалуйста, отправьте чек об оплате в личные сообщения администратору:\n"
        f"👉 {ADMIN_USERNAME}\n\n"
        f"Мы проверим платеж и сразу начнем сборку вашего заказа!"
    )
    sent = await callback.message.answer(msg_text)
    db.log_message(user_id, 'out', sent.text)
    await callback.answer()

# ---------- Админ-панель (только статистика и рассылка) ----------
class BroadcastStates(StatesGroup):
    waiting_for_text = State()

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.username != ADMIN_USERNAME_CLEAN:
        await message.answer("У вас нет доступа к админ-панели.")
        return
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📨 Рассылка", callback_data="admin_broadcast")],
        ]
    )
    sent = await message.answer("Админ-панель:", reply_markup=keyboard)
    db.log_message(message.from_user.id, 'out', sent.text)

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    if callback.from_user.username != ADMIN_USERNAME_CLEAN:
        await callback.answer("Нет доступа", show_alert=True)
        return
    new_users = db.get_new_users_since(1)          # за последние сутки
    inactive_users = db.get_inactive_users_since(1) # неактивные за сутки
    total_users = db.get_total_users()
    stats_text = (
        f"📊 **Статистика**\n\n"
        f"⏫ Новых за 24ч: {new_users}\n"
        f"⏬ Неактивных за 24ч: {inactive_users}\n"
        f"👥 Всего пользователей: {total_users}"
    )
    sent = await callback.message.answer(stats_text, parse_mode="Markdown")
    db.log_message(callback.from_user.id, 'out', sent.text)
    await callback.answer()

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.username != ADMIN_USERNAME_CLEAN:
        await callback.answer("Нет доступа", show_alert=True)
        return
    sent = await callback.message.answer("✏️ Введите текст сообщения для рассылки (всем пользователям).")
    db.log_message(callback.from_user.id, 'out', sent.text)
    await state.set_state(BroadcastStates.waiting_for_text)
    await callback.answer()

@dp.message(StateFilter(BroadcastStates.waiting_for_text))
async def broadcast_send(message: types.Message, state: FSMContext):
    if message.from_user.username != ADMIN_USERNAME_CLEAN:
        await message.answer("Нет доступа.")
        return
    text = message.text
    if not text:
        await message.answer("Текст не может быть пустым. Попробуйте снова.")
        return
    users = db.get_all_users()
    count = 0
    for user in users:
        try:
            await bot.send_message(user['id'], text)
            db.log_message(user['id'], 'out', text)
            count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            print(f"Ошибка отправки пользователю {user['id']}: {e}")
    sent = await message.answer(f"✅ Рассылка завершена. Отправлено {count} сообщений.")
    db.log_message(message.from_user.id, 'out', sent.text)
    await state.clear()

# ---------- Запуск ----------
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
