from contextlib import suppress

import requests
from aiogram import Bot, Dispatcher, types, executor
from aiogram.utils.exceptions import MessageNotModified
from bs4 import BeautifulSoup

from config import TOKEN, text, filters, emoji, commands_text, URL_SITE_WITH_JOKES
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import random

# initialisation dynamic libraries for keyboards
chat_data = {}
status_callback_data = CallbackData("number", "action")

# logging and returning status info in console
logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


# first keyboard initialisation
def get_keyboard_tab():
	buttons = [
		InlineKeyboardButton(text="Указать границы", callback_data=status_callback_data.new(action="set_brpoint")),
		InlineKeyboardButton(text="Сгенерировать", callback_data=status_callback_data.new(action="run")),
	]
	keyboard = InlineKeyboardMarkup(row_width=2)
	keyboard.add(*buttons)
	return keyboard


# second keyboard initialisation
def edit_number_tab_keyboard():
	buttons = [
		InlineKeyboardButton(text="Сохранить", callback_data=status_callback_data.new(action="save")),
		InlineKeyboardButton(text="Сбросить", callback_data=status_callback_data.new(action="reset")),
		InlineKeyboardButton(text="+1", callback_data=status_callback_data.new(action="increase_1")),
		InlineKeyboardButton(text="-1", callback_data=status_callback_data.new(action="decrease_1")),
		InlineKeyboardButton(text="+10", callback_data=status_callback_data.new(action="increase_10")),
		InlineKeyboardButton(text="-10", callback_data=status_callback_data.new(action="decrease_10")),
	]
	keyboard = InlineKeyboardMarkup(row_width=2)
	keyboard.add(*buttons)
	keyboard.add(InlineKeyboardButton(text="Назад", callback_data=status_callback_data.new(action="back")))
	return keyboard


# changing message with current value
async def update_random_number(message: types.Message, value: int):
	with suppress(MessageNotModified):
		# this context manager is used to exclude possible errors with modifying message
		await message.edit_text(text=f"Текущее значение границы: {value}", reply_markup=edit_number_tab_keyboard())


# changing message after click on first inline button
@dp.callback_query_handler(status_callback_data.filter(action=["set_brpoint"]))
async def set_keyboard(call: types.CallbackQuery):
	user_value = chat_data.get(call.from_user.id, 0)
	# for the first time we are setting up default value as 0
	if user_value != 0:
		# checking user value
		user_value = chat_data[call.from_user.id]
	await call.message.edit_text(f"Текущее значение границы: {user_value}", reply_markup=edit_number_tab_keyboard())


# callbacks which using for changing user value of range
@dp.callback_query_handler(status_callback_data.filter(action=filters))
async def callback_filter(call: types.CallbackQuery, callback_data: dict):
	user_value = chat_data.get(call.from_user.id, 0)
	action = callback_data["action"]
	# increasing the value on 1 unit
	if action == "increase_1":
		chat_data[call.from_user.id] = user_value + 1
		await update_random_number(call.message, user_value + 1)
	# setting up the value as 0
	elif action == "reset":
		chat_data[call.from_user.id] = 0
		await update_random_number(call.message, 0)
	# decreasing the value on 1 unit
	elif action == "decrease_1":
		if user_value - 1 <= 0:
			pass
		else:
			chat_data[call.from_user.id] = user_value - 1
			await update_random_number(call.message, user_value - 1)
	# increasing the value on 10 units
	if action == "increase_10":
		chat_data[call.from_user.id] = user_value + 10
		await update_random_number(call.message, user_value + 10)
	# decreasing the value on 10 units
	elif action == "decrease_10":
		if user_value - 10 <= 0:
			pass
		else:
			chat_data[call.from_user.id] = user_value - 10
			await update_random_number(call.message, user_value - 10)

	await call.answer()


# callbacks which using for saving or skipping editing number range
@dp.callback_query_handler(status_callback_data.filter(action=["save", "back"]))
async def callback_values(call: types.CallbackQuery, callback_data: dict):
	user_value = chat_data.get(call.from_user.id, 1)
	action = callback_data["action"]
	# saving current value
	if action == "save":
		await call.message.edit_text(f"Значение границы: {user_value}", reply_markup=get_keyboard_tab())
		chat_data.get(call.from_user.id, 0)
	# returning back on previous step
	elif action == "back":
		await call.message.edit_text(text="Я жду от тебя действий {emoji['Rocket']}", reply_markup=get_keyboard_tab())


# returning random number in chat
@dp.callback_query_handler(status_callback_data.filter(action=["run"]))
async def set_keyboard(call: types.CallbackQuery):
	user_value = chat_data.get(call.from_user.id, 1)
	rand_num = random.randint(0, user_value)
	await call.message.edit_text(f" Рандомное число: {emoji['Bomb']} <b>{rand_num}</b> {emoji['Bomb']}")


# sending welcome message
@dp.message_handler(commands=["start"])
async def welcome_mess(message: types.Message):
	await message.answer("\n".join(text))


# sending message with first inline keyboard
@dp.message_handler(commands=["number"])
async def num_mess(message: types.Message):
	await message.answer(f"Я жду от тебя действий {emoji['Rocket']}", reply_markup=get_keyboard_tab())


# sending commands list
@dp.message_handler(commands=["commands"])
async def commands_mess(message: types.Message):
	await message.answer("\n".join(commands_text))


# hidden command which returning random joke
@dp.callback_query_handler(text='joke')
async def get_random_joke(call: types.CallbackQuery):
	random_page_number = str(random.randint(1, 619))
	webpage = requests.get(URL_SITE_WITH_JOKES + random_page_number + '/').text
	tags = BeautifulSoup(webpage, 'html.parser').find_all('p')
	jokes = []
	for tag in tags:
		tag_text = tag.get_text()
		if tag_text == '\n':
			break
		jokes.append(tag_text)
	await call.message.answer(random.choice(jokes[1:-1]))
	await call.answer()


# bot pooling
if __name__ == "__main__":
	executor.start_polling(dp, skip_updates=True)
