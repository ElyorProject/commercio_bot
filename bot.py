import asyncio
import logging
import sys
import re
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import WebAppInfo, CallbackQuery, KeyboardButton, ReplyKeyboardRemove, FSInputFile

# Ваш токен от BotFather
TOKEN = "8371967950:AAGJf0pHoV8bHSR9RutG8zvdLa8UdEO8jvc"

# ID менеджера - ЗАМЕНИТЕ НА ВАШ TELEGRAM ID
# Чтобы узнать свой ID, напишите @userinfobot в Telegram
MANAGER_ID = 5107584493  # ← ВСТАВЬТЕ СЮДА ВАШ ID

# Путь к папке с фотографиями товаров
PHOTOS_PATH = r"c:\Users\elyor\OneDrive\Рабочий стол\commercio\bot-products"

# Словарь для хранения товаров (артикул: данные)
PRODUCTS = {
    "60001": {
        "name": "Rolex Datejust",
        "price": 1200,
        "stock": {"One Size": 2}
    },
    "30001": {
        "name": "Peter Millar Oxford",
        "price": 280,
        "stock": {"40": 1, "41": 2, "42": 1, "43": 1}
    },
    "50001": {
        "name": "Classic Suit Premium",
        "price": 450,
        "stock": {"S": 3, "M": 4, "L": 2, "XL": 1}
    },
    "70001": {
        "name": "Designer Handbag",
        "price": 320,
        "stock": {"One Size": 1}
    },
    "20001": {
        "name": "Elegant Evening Dress",
        "price": 180,
        "stock": {"XS": 1, "S": 2, "M": 2, "L": 1}
    },
    "50002": {
        "name": "Vintage Leather Coat",
        "price": 380,
        "stock": {"S": 2, "M": 3, "L": 2, "XL": 1}
    },
    "60002": {
        "name": "Apple Watch Series",
        "price": 420,
        "stock": {"38mm": 2, "42mm": 3}
    },
    "80001": {
        "name": "Nike Running Jacket",
        "price": 150,
        "stock": {"S": 1, "M": 2, "L": 2, "XL": 1}
    },
    "70002": {
        "name": "Premium Leather Wallet",
        "price": 95,
        "stock": {"One Size": 5}
    },
    "30002": {
        "name": "Designer Sneakers",
        "price": 220,
        "stock": {"38": 1, "39": 2, "40": 2, "41": 2, "42": 1, "43": 1}
    },
    "20002": {
        "name": "Cashmere Sweater",
        "price": 160,
        "stock": {"XS": 1, "S": 2, "M": 2, "L": 1}
    },
    "50003": {
        "name": "Classic Formal Dress",
        "price": 280,
        "stock": {"XS": 1, "S": 2, "M": 3, "L": 2}
    },
    "10001": {
        "name": "Casual T-Shirt",
        "price": 35,
        "stock": {"S": 5, "M": 8, "L": 6, "XL": 3}
    },
    "10002": {
        "name": "Denim Jeans",
        "price": 85,
        "stock": {"30": 3, "32": 4, "34": 3, "36": 2}
    },
    "30003": {
        "name": "Women Heels",
        "price": 140,
        "stock": {"36": 2, "37": 3, "38": 2, "39": 2, "40": 1}
    },
    "80002": {
        "name": "Sports Bag",
        "price": 65,
        "stock": {"One Size": 4}
    },
    "60003": {
        "name": "Wireless Headphones",
        "price": 180,
        "stock": {"One Size": 3}
    },
    "70003": {
        "name": "Business Wallet",
        "price": 75,
        "stock": {"One Size": 6}
    }
}

# Словарь для отслеживания пользователей в ручном режиме
manual_mode_users = set()

# Список всех пользователей для рассылки
all_users = set()

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    all_users.add(message.from_user.id)
    
    builder = InlineKeyboardBuilder()
    
    builder.row(types.InlineKeyboardButton(
        text="Витрина Commercio", 
        web_app=WebAppInfo(url="https://commercio-showcase.vercel.app")
    ))

    await message.answer(
        "👋🏼 Добро пожаловать в Commercio 🌟\n\nСтильные отобранные товары, частые дропы и тренды сезонов!\n\nВ commercio вы всегда найдёте подходящую одежду для вашего стиля.\n\nГотовы начать покупки? Открывайте витрину и начинайте поиск идеального товара!\n\n"
        "Для поиска товара введите артикул (например: 60001)",
        reply_markup=builder.as_markup()
    )

@dp.callback_query()
async def handle_size_selection(callback: CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    
    if data.startswith('size_'):
        parts = data.split('_')
        article = parts[1]
        size = parts[2]
        
        if article in PRODUCTS:
            product = PRODUCTS[article]
            if size in product['stock']:
                stock_count = product['stock'][size]
                response = f"{product['name']} размер {size} цена {product['price']} $ в наличии {stock_count} штук"
                
                # Переводим пользователя в ручной режим
                manual_mode_users.add(user_id)
                
                # Создаем клавиатуру с кнопкой выхода
                keyboard = ReplyKeyboardBuilder()
                keyboard.button(text="🚪 Выйти из диалога")
                keyboard.adjust(1)
                
                # Уведомляем менеджера
                if MANAGER_ID:
                    try:
                        bot = Bot(token=TOKEN)
                        await bot.send_message(
                            MANAGER_ID,
                            f"Новый клиент @{callback.from_user.username or callback.from_user.first_name} (ID: {user_id}) интересуется:\n{response}\n\nТеперь вы можете общаться с клиентом. Используйте /reply {user_id} для ответа."
                        )
                    except Exception as e:
                        print(f"Ошибка уведомления менеджера: {e}")
                
                try:
                    await callback.message.edit_text(response + "\n\nМенеджер подключился к разговору и скоро ответит на ваши вопросы.", reply_markup=None)
                except:
                    await callback.message.answer(response + "\n\nМенеджер подключился к разговору и скоро ответит на ваши вопросы.")
                
                await callback.message.answer("Вы можете задать любые вопросы менеджеру:", reply_markup=keyboard.as_markup(resize_keyboard=True))
        
        await callback.answer()

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    
    print(f"Получено сообщение: '{text}' от пользователя {user_id}")
    
    # Проверяем команду выхода из диалога
    if text == "🚪 Выйти из диалога" and user_id in manual_mode_users:
        manual_mode_users.remove(user_id)
        
        # Уведомляем менеджера о выходе клиента
        if MANAGER_ID:
            try:
                bot = Bot(token=TOKEN)
                await bot.send_message(
                    MANAGER_ID,
                    f"❌ Клиент @{message.from_user.username or message.from_user.first_name} (ID: {user_id}) вышел из диалога"
                )
            except Exception as e:
                print(f"Ошибка уведомления менеджера: {e}")
        
        await message.answer(
            "Вы вышли из диалога с менеджером. Теперь можете снова искать товары по артикулу.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Если пользователь в ручном режиме, пересылаем сообщение менеджеру
    if user_id in manual_mode_users and MANAGER_ID:
        try:
            bot = Bot(token=TOKEN)
            await bot.send_message(
                MANAGER_ID,
                f"Сообщение от @{message.from_user.username or message.from_user.first_name} (ID: {user_id}):\n{text}"
            )
        except Exception as e:
            print(f"Ошибка отправки менеджеру: {e}")
        return
    
    # Проверяем, является ли отправитель менеджером
    if MANAGER_ID and user_id == MANAGER_ID:
        # Команда для ответа клиенту: /reply USER_ID текст сообщения
        if text.startswith('/reply '):
            parts = text.split(' ', 2)
            if len(parts) >= 3:
                try:
                    client_id = int(parts[1])
                    reply_text = parts[2]
                    bot = Bot(token=TOKEN)
                    await bot.send_message(client_id, reply_text)
                    await message.answer(f"Сообщение отправлено пользователю {client_id}")
                except ValueError:
                    await message.answer("Неверный формат. Используйте: /reply USER_ID текст")
                except Exception as e:
                    await message.answer(f"Ошибка отправки: {e}")
            else:
                await message.answer("Используйте: /reply USER_ID текст сообщения")
            return
        
        # Команда рассылки: /ad текст сообщения
        if text.startswith('/ad '):
            ad_text = text[4:]  # Убираем '/ad '
            bot = Bot(token=TOKEN)
            sent_count = 0
            
            for user_id_to_send in all_users:
                try:
                    await bot.send_message(user_id_to_send, ad_text)
                    sent_count += 1
                except Exception:
                    pass  # Пропускаем ошибки (например, заблокированные пользователи)
            
            await message.answer(f"Рассылка завершена. Отправлено: {sent_count} сообщений")
            return
    
    # Проверяем, является ли это артикулом товара
    if text.isdigit() and text in PRODUCTS:
        all_users.add(user_id)
        product = PRODUCTS[text]
        
        # Ищем фото товара
        photo_path = None
        for ext in ['.jpg', '.png', '.jpeg']:
            potential_path = os.path.join(PHOTOS_PATH, f"{text}{ext}")
            if os.path.exists(potential_path):
                photo_path = potential_path
                break
        
        builder = InlineKeyboardBuilder()
        
        # Создаем кнопки для каждого доступного размера
        for size, stock in product['stock'].items():
            if stock > 0:  # Показываем только размеры в наличии
                builder.button(
                    text=f"{size} ({stock} шт)",
                    callback_data=f"size_{text}_{size}"
                )
        
        builder.adjust(2)  # По 2 кнопки в ряд
        
        caption = f"{product['name']} - {product['price']}$\nВыберите размер:"
        
        if photo_path:
            photo = FSInputFile(photo_path)
            await message.answer_photo(
                photo=photo,
                caption=caption,
                reply_markup=builder.as_markup()
            )
        else:
            await message.answer(
                caption,
                reply_markup=builder.as_markup()
            )
        return
    
    # Если артикул не найден
    if text.isdigit():
        await message.answer(f"Товар с артикулом {text} не найден")
        return
    
    await message.answer("Для поиска товара введите артикул (например: 60001)")

async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())