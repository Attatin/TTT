import logging
import asyncpg
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import psycopg2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from psycopg2 import extensions

host = '10.40.240.85'
port = '5432'
user = 'student'
password = 'student-rtf-123'
database = 'fila'

TOKEN = '6055998098:AAEIhwECL5vI_PZBLvszTJh6tSMEUX2O3bA'
bot = Bot(token=TOKEN)

logging.basicConfig(level=logging.INFO)

dp = Dispatcher(bot, storage=MemoryStorage())

role_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
role_keyboard.add(KeyboardButton('Расписание мероприятий'))
role_keyboard.add(KeyboardButton('Информация о призерах конкурсов'))
role_keyboard.add(KeyboardButton('Узнать информацию о залах'))
role_keyboard.add(KeyboardButton('Деятельность артистов'))
role_keyboard.add(KeyboardButton('Статистика мероприятий организатора'))
role_keyboard.add(KeyboardButton('Импресарио и его артисты'))


######запуск бота######

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply('Привет, я бот филармонии. Что бы вы хотели сделать:', reply_markup=role_keyboard)


#########мероприятия###########


async def send_message_with_limit(chat_id, message_text):
    if len(message_text) <= 4096:
        await bot.send_message(chat_id, message_text)
    else:
        parts = [message_text[i:i + 4096] for i in range(0, len(message_text), 4096)]
        for part in parts:
            await bot.send_message(chat_id, part)


@dp.message_handler(lambda message: message.text == 'Расписание мероприятий')
async def handler_chose_mero(message: types.Message, state: FSMContext):
    await message.reply("Для начала список:", reply_markup=role_keyboard)
    conn = psycopg2.connect(database='fila', user='student', password='student-rtf-123',
                            host='10.40.240.85', port='5432')
    cursor = conn.cursor()
    try:
        cursor.execute('select * from fila.mero_view')
        rows = cursor.fetchall()

        response = 'Мероприятия и их расписание:\n\n'
        for row in rows:
            mero_str = f"Название: {row[0]}\nДата: {row[1]}\nТип: {row[2]}\nЗал: {row[3]}\n\n"
            response += mero_str

        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о мероприятиях.")

    cursor.close()
    conn.close()


####информация о призерах####


async def send_message_with_limit(chat_id, message_text):
    if len(message_text) <= 4096:
        await bot.send_message(chat_id, message_text)
    else:
        parts = [message_text[i:i + 4096] for i in range(0, len(message_text), 4096)]
        for part in parts:
            await bot.send_message(chat_id, part)


@dp.message_handler(lambda message: message.text == 'Информация о призерах конкурсов')
async def handler_chose_mero(message: types.Message, state: FSMContext):
    conn = psycopg2.connect(database='fila', user='student', password='student-rtf-123',
                            host='10.40.240.85', port='5432')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM fila.призеры_конкурсов')
        rows = cursor.fetchall()

        response = 'Конкурсы и их призеры:\n\n'
        for row in rows:
            priz_str = f"Конкурс: {row[1]}\nДата: {row[2]}\nАртист: {row[0]}\nМесто: {row[3]}\n\n"
            response += priz_str

        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о мероприятиях.")

    cursor.close()
    conn.close()


###########залы############


async def send_message_with_limit(chat_id, message_text):
    if len(message_text) <= 4096:
        await bot.send_message(chat_id, message_text)
    else:
        parts = [message_text[i:i + 4096] for i in range(0, len(message_text), 4096)]
        for part in parts:
            await bot.send_message(chat_id, part)


@dp.message_handler(lambda message: message.text == 'Узнать информацию о залах')
async def handler_chose_zal(message: types.Message, state: FSMContext):
    conn = psycopg2.connect(database='fila', user='student', password='student-rtf-123',
                            host='10.40.240.85', port='5432')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM fila.залы')
        rows = cursor.fetchall()

        response = 'Дополнительная информация о залах:\n\n'
        for row in rows:
            zal_str = f"Название зала: {row[1]}\nВместимость: {row[2]}\nХарактеристики: {row[3]}\n\n"
            response += zal_str

        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о мероприятиях.")

    cursor.close()
    conn.close()


###############информация о жанре артиста###############

@dp.message_handler(lambda message: message.text == "Деятельность артистов")
async def handle_do_artist_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Введите фамилию интересующего артиста:")
    await GetArtistDoState.LAST_NAME.set()
    await state.update_data(chat_id=chat_id)


class GetArtistDoState(StatesGroup):
    LAST_NAME = State()
    FIRST_NAME = State()


@dp.message_handler(state=GetArtistDoState.LAST_NAME)
async def handle_do_artist_id_last_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    last_name = message.text
    await state.update_data(last_name=last_name)
    await bot.send_message(chat_id, "Введите его имя:")
    await GetArtistDoState.FIRST_NAME.set()


@dp.message_handler(state=GetArtistDoState.FIRST_NAME)
async def handle_do_artist_id_first_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    first_name = message.text
    await state.update_data(first_name=first_name)

    data = await state.get_data()

    first_name = data.get('first_name')
    last_name = data.get('last_name')

    conn = psycopg2.connect(database='fila', user='student', password='student-rtf-123',
                            host='10.40.240.85', port='5432')
    cursor = conn.cursor()

    try:

        cursor.execute('select * from fila.жанр_view where имя_артиста = %s and фамилия_артиста = %s',
                       (first_name, last_name))
        rows = cursor.fetchall()
        ##result = cursor.fetchone()

        response = 'Жанры артиста:\n\n'
        for row in rows:
            жанр_str = f"{row[0]}\n\n"
            response += жанр_str


        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о жанрах артиста.")

        cursor.close()
        conn.close()


    await state.finish()

###############информация об организаторах###############

@dp.message_handler(lambda message: message.text == "Статистика мероприятий организатора")
async def handle_get_mero_org(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Введите имя интересующего организатора:")
    await GetMeroOrgState.FIRST_NAME.set()
    await state.update_data(chat_id=chat_id)


class GetMeroOrgState(StatesGroup):
    FIRST_NAME = State()
    LAST_NAME = State()


@dp.message_handler(state=GetMeroOrgState.FIRST_NAME)
async def handle_get_mero_org_first_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    first_name = message.text
    await state.update_data(first_name=first_name)
    await bot.send_message(chat_id, "Введите его фамилию:")
    await GetMeroOrgState.LAST_NAME.set()


@dp.message_handler(state=GetMeroOrgState.LAST_NAME)
async def handle_get_mero_org_last_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    last_name = message.text
    await state.update_data(last_name=last_name)

    data = await state.get_data()

    first_name = data.get('first_name')
    last_name = data.get('last_name')

    try:
        conn = psycopg2.connect(database='fila', user='student', password='student-rtf-123',
                                host='10.40.240.85', port='5432')

        cursor = conn.cursor()

        cursor.execute('SELECT прошедшие_меро, текущие_меро, предстоящие_меро FROM fila.организаторы WHERE имя_организатора = %s AND фамилия_организатора = %s',
                       (first_name, last_name))
        result = cursor.fetchone()

        if result:
            прошедшие_меро = result[0]
            текущие_меро = result[1]
            предстоящие_меро = result[2]
            await bot.send_message(chat_id, f"Кол-во прошедших меро: {прошедшие_меро}\nКол-во текущих меро: {текущие_меро}\n"
                                            f"Кол-во предстоящих меро: {предстоящие_меро}\n")
        else:
            await bot.send_message(chat_id, "Организатор не найден.")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при получении инфо об организаторе.")

    await state.finish()


###############информация об артистах импресарио###############

@dp.message_handler(lambda message: message.text == "Импресарио и его артисты")
async def handle_get_imp_art(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Введите имя интересующего импресарио:")
    await GetImpArtState.FIRST_NAME.set()
    await state.update_data(chat_id=chat_id)


class GetImpArtState(StatesGroup):
    FIRST_NAME = State()
    LAST_NAME = State()


@dp.message_handler(state=GetImpArtState.FIRST_NAME)
async def handle_get_imp_art_first_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    first_name = message.text
    await state.update_data(first_name=first_name)
    await bot.send_message(chat_id, "Введите его фамилию:")
    await GetImpArtState.LAST_NAME.set()


@dp.message_handler(state=GetImpArtState.LAST_NAME)
async def handle_get_imp_art_last_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    last_name = message.text
    await state.update_data(last_name=last_name)

    data = await state.get_data()

    first_name = data.get('first_name')
    last_name = data.get('last_name')

    try:
        conn = psycopg2.connect(database='fila', user='student', password='student-rtf-123',
                                host='10.40.240.85', port='5432')

        cursor = conn.cursor()

        cursor.execute('SELECT артист_2, артист_1, жанры FROM fila.импр_view WHERE имя = %s AND фамилия = %s',
                       (first_name, last_name))
        rows = cursor.fetchall()
        ##result = cursor.fetchone()

        response = 'Его артисты:\n\n'
        for row in rows:
            арт_а_str = f"Артист: {row[0]} {row[1]}\nЖанры: {row[2]}\n\n"
            response += арт_а_str

        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о жанрах артиста.")

        cursor.close()
        conn.close()

    await state.finish()


if __name__ == '__main__':
    logging.info("Бот запущен!")
    executor.start_polling(dp)
