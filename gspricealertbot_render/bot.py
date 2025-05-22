
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import asyncio
import config

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)
user_data = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Binance", callback_data='exchange_binance'),
        InlineKeyboardButton("MEXC", callback_data='exchange_mexc')
    )
    await message.answer("👋 Привіт! Обери біржу:", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith('exchange_'))
async def select_exchange(callback_query: types.CallbackQuery):
    exchange = callback_query.data.split('_')[1]
    user_data[callback_query.from_user.id] = {'exchange': exchange}
    markup = InlineKeyboardMarkup(row_width=2)
    for token in ['BTC', 'ETH', 'DOGE', 'SOL']:
        markup.insert(InlineKeyboardButton(token, callback_data=f"token_{token}"))
    await bot.send_message(callback_query.from_user.id, f"📊 Біржа {exchange.upper()} обрана. Тепер обери токен:", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith('token_'))
async def select_token(callback_query: types.CallbackQuery):
    token = callback_query.data.split('_')[1]
    user_data[callback_query.from_user.id]['token'] = token
    await bot.send_message(callback_query.from_user.id, "💰 Введи ціну, при досягненні якої надіслати алерт:")

@dp.message_handler(lambda message: message.text.replace('.', '', 1).isdigit())
async def set_price(message: types.Message):
    user_id = message.from_user.id
    price = float(message.text)
    user_data[user_id]['target_price'] = price
    await message.answer(f"✅ Алерт створено для {user_data[user_id]['token']} на {price} USDT")
    asyncio.create_task(check_price(user_id))

async def check_price(user_id):
    await asyncio.sleep(2)
    await bot.send_message(user_id, f"🚨 {user_data[user_id]['token']} досяг цільової ціни!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
