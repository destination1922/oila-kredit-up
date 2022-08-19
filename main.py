import logging
import requests
from config import *
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands='start')
async def start(message: types.Message):
    telegram_id = message.from_user.id
    with open('users.txt') as rfile:
        lines = rfile.readlines()
    ids = []
    for i in lines:
        ids.append(i.rstrip('\n'))

    if str(telegram_id) in ids:
        main_btn = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [types.KeyboardButton(text=CHECK_APPLICATION)],
                [types.KeyboardButton(text=ALLOCATED_APPLICATIONS)]
            ]
        )
        await message.answer(text=START_TEXT, reply_markup=main_btn)
    else:
        await message.answer("Кечирасиз ботдан фойдаланиш ҳуқуқи сизда мавжуд эмас!")

@dp.callback_query_handler()
async def app_function(query: types.CallbackQuery):
    telegram_id = query.from_user.id
    app_id = query.data

    r = requests.get(f"{BASIC_API}by_app?param={app_id}")
    r_data = r.json()
    data = r_data['data'][0]
    await bot.send_message(chat_id=telegram_id, text=notify(data), parse_mode='HTML')

@dp.message_handler()
async def reply_function(message: types.Message):
    msg = message.text

    if msg == CHECK_APPLICATION:
        await message.answer(text=CHECK_TEXT)

    elif msg == ALLOCATED_APPLICATIONS:
        keyboard_markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = (types.InlineKeyboardButton(
            text, url=f'{FORM_LINK}?button={get_export(count)}&header={get_header(count)}')
            for count, text in enumerate(buttons_array)
        )
        keyboard_markup.add(*buttons)
        await message.answer(text="Қуйидагилардан бирини танланг:", reply_markup=keyboard_markup)

    elif check_message(msg) != 'error':
        r = requests.get(f"{BASIC_API}by_{check_message(msg)}?param={msg}")
        r_data = r.json()
        data = r_data['data']

        if len(data) == 1:
            for child in data: await message.answer(text=notify(child), parse_mode='HTML')

        elif len(data) > 1:
            app_array = []
            for child in data[1:]:
                ar_i = []
                id = child['app_id']
                text = f"Aриза рақами: {id}  {get_date(child['app_date'])}"
                ar_i.append(text)
                ar_i.append(str(id))
                app_array.append(ar_i)

            inline_app_markup = types.InlineKeyboardMarkup(row_width=1)
            btns_app = (types.InlineKeyboardButton(text, callback_data=data) for text, data in app_array)
            inline_app_markup.add(*btns_app)

            data0 = data[0]
            await message.answer(text=last_notify(data0), parse_mode='HTML', reply_markup=inline_app_markup)
        else:
            await message.answer("Ҳеч қандай ариза топилмади!")
    elif msg[:9] == 'new_user:':
        user_id = msg[9:]
        with open('users.txt', 'a') as file:
            file.write(f'\n{user_id}')
        await message.answer('Successfully added! :)')
    else:
        await message.answer(text="Илтимос ноўрин хабар юборманг!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)