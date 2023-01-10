
from aiogram.types import ReplyKeyboardRemove,ReplyKeyboardMarkup, KeyboardButton
from aiogram import Bot, Dispatcher, executor, types




TOKEN = '5653486266:AAEXoa-iM1pAY5N9eDEwbXJ6-aLGCyEgR5k'
CHAT = '624736798'
bot = Bot(TOKEN)
dp = Dispatcher(bot)

kb = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
b1=KeyboardButton('graphic')
b2=KeyboardButton('procent')
b3=KeyboardButton('price')
b4=KeyboardButton('balance')
b5=KeyboardButton('close_pos')
b6=KeyboardButton('hello')
b7=KeyboardButton('help')
b8=KeyboardButton('quit')
kb.add(b1).insert(b2).add(b3).insert(b4).add(b5).insert(b6).add(b7).insert(b8)

@dp.message_handler(commands=['start'])
async def startcom(message: types.Message):
    await message.answer(text='hi',
                         reply_markup=kb)

if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)