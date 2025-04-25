import asyncio
import random
from aiogram import Bot, Dispatcher, types, filters
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage


TOKEN = "7247194448:AAFIINumA5xA9QU2jv8afaMvUmQeTJaPHrA"
bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class FeedbackState(StatesGroup):
    complaint = State()
    suggestion = State()

class AuthState(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()

# === ПЕРЕМЕННЫЕ === #
present_teachers = set()
fake_users = {
    "STUDENT-1234": {"password": "1234", "role": "Студент", "direction": "IT"},
    "PARENT-5678": {"password": "5678", "role": "Родитель", "direction": "Юриспруденция"},
    "TEACHER-9999": {"password": "9999", "role": "Учитель", "direction": "Маркетинг"},
}

# === УТИЛИТЫ === #
def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ℹ️ Information", callback_data="category:Information")],
        [InlineKeyboardButton(text="📅 Registration", callback_data="category:Registration")],
        [InlineKeyboardButton(text="🔑 User", callback_data="category:User")],
        [InlineKeyboardButton(text="🔐 Профиль", callback_data="category:profile")],
        [InlineKeyboardButton(text="🔍 Search", callback_data="category:Search")],
        [InlineKeyboardButton(text="📣 Complaints & Suggestions", callback_data="category:complaints")],
        [InlineKeyboardButton(text="🔗 TGK Nomad", callback_data="category:TGKNomad")],
    ])

# === ОБРАБОТЧИКИ === #
@dp.message(filters.Command('start'))
async def start(message: types.Message):
    await message.answer(f"Hello, {message.from_user.username}!\n\nPlease choose a category:", reply_markup=get_main_menu())

@dp.callback_query(lambda call: call.data.startswith('category:'))
async def handle_category(call: CallbackQuery, state: FSMContext):
    category = call.data.split(':')[1]

    match category:
        case "Information":
            await call.message.answer("ℹ️ Выберите информацию:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Колледж", callback_data="info:college")],
                [InlineKeyboardButton(text="Специальности", callback_data="info:specialties")]
            ]))
        case "Registration":
            await call.message.answer("📅 Выберите тип регистрации:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Гость", callback_data="reg:guest")],
                [InlineKeyboardButton(text="Студент", callback_data="reg:student")],
                [InlineKeyboardButton(text="Родитель", callback_data="reg:parent")],
                [InlineKeyboardButton(text="Учитель", callback_data="reg:teacher")]
            ]))
        case "User":
            await call.message.answer("🔑 Вход в систему.\n\nПолучите логин и пароль при регистрации.", parse_mode="Markdown")
        case "Search":
            present = '\n'.join(present_teachers) if present_teachers else '❌ Учителей в колледже сейчас нет.'
            await call.message.answer(f"👨‍🏫 Учителя в колледже:\n{present}")
            await call.message.answer("🔍 Отметка присутствия:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Я в колледже", callback_data="teacher:in")],
                [InlineKeyboardButton(text="❌ Я ушел", callback_data="teacher:out")]
            ]))
        case "complaints":
            await call.message.answer("📣 Выберите, что хотите отправить:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📣 Жалоба", callback_data="complaint:file")],
                [InlineKeyboardButton(text="✨ Предложение", callback_data="suggestion:file")]
            ]))
        case "TGKNomad":
            await call.message.answer("🔗 Наш Telegram Канал:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Перейти в канал", url="https://t.me/+6HRrYRj2bm9kNTYy")]
            ]))
        case "profile":
            await call.message.answer("🔐 Введите ваш *логин*:", parse_mode="Markdown")
            await state.set_state(AuthState.waiting_for_login)

@dp.callback_query(lambda c: c.data.startswith("info:"))
async def info_handler(call: CallbackQuery):
    key = call.data.split(":")[1]
    if key == "college":
        await call.message.answer("🏫 Колледж находится в 7-апреля 4/3. Видео:https://www.instagram.com/reel/C9MwjNWoaR1/?igsh=MXZwdWZlYTQ3cWEwNw==")
    elif key == "specialties":
        specialties = [
            ("IT", "it"), ("Дизайнер", "design"), ("Юриспруденция", "law"),
            ("Маркетолог", "marketing"), ("Переводчики", "translation"),
            ("Менеджмент", "management"), ("Бизнес", "business")
        ]
        await call.message.answer("📚 Выберите специальность:", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=name, callback_data=f"spec:{key}")] for name, key in specialties]
        ))

@dp.callback_query(lambda c: c.data.startswith("spec:"))
async def spec_info(call: CallbackQuery):
    prices = {
        "it": "💻 IT — 270,000 сом",
        "design": "🎨 Дизайнер — 200,000 сом",
        "law": "⚖️ Юриспруденция — 200,000 сом",
        "marketing": "📊 Маркетинг — 200,000 сом",
        "translation": "🌐 Переводческое дело — 200,000 сом",
        "management": "📋 Менеджмент — 270,000 сом",
        "business": "💼 Финансы — 200,000 сом",
    }
    await call.message.answer(prices.get(call.data.split(":")[1], "Информация не найдена."))

@dp.callback_query(lambda c: c.data.startswith("reg:"))
async def registration_handler(call: CallbackQuery):
    role = call.data.split(":")[1]
    if role == "guest":
        await call.message.answer("👋 Как гость вы можете просто ознакомиться с информацией.")
    else:
        number = random.randint(1000, 9999)
        login = f"{role.upper()}-{number}"
        await call.message.answer(f"✍️ Регистрация завершена как {role.title()}!\n🔐 Логин: {login}\n🔑 Пароль: {number}")

@dp.callback_query(lambda c: c.data.startswith("teacher:"))
async def teacher_presence(call: CallbackQuery):
    user = call.from_user.full_name
    status = call.data.split(":")[1]
    if status == "in":
        present_teachers.add(user)
        await call.message.answer("✅ Вы отметились как *в колледже*", parse_mode="Markdown")
    else:
        present_teachers.discard(user)
        await call.message.answer("❌ Вы отметились как *ушли*", parse_mode="Markdown")

@dp.callback_query(lambda c: c.data.endswith(":file"))
async def feedback_handler(call: CallbackQuery, state: FSMContext):
    action = call.data.split(":")[0]
    state_map = {
        "complaint": FeedbackState.complaint,
        "suggestion": FeedbackState.suggestion
    }
    prompts = {
        "complaint": "Пожалуйста, опишите вашу *жалобу*:",
        "suggestion": "Пожалуйста, напишите ваше *предложение*:"
    }
    await call.message.answer(prompts[action], parse_mode="Markdown")
    await state.set_state(state_map[action])

@dp.message(FeedbackState.complaint)
async def save_complaint(message: types.Message, state: FSMContext):
    await message.answer("📣 Ваша жалоба сохранена. Спасибо!")
    await state.clear()

@dp.message(FeedbackState.suggestion)
async def save_suggestion(message: types.Message, state: FSMContext):
    await message.answer("✨ Ваше предложение сохранено. Спасибо!")
    await state.clear()

@dp.message(AuthState.waiting_for_login)
async def auth_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text.strip().upper())
    await message.answer("🔑 Введите ваш *пароль*:", parse_mode="Markdown")
    await state.set_state(AuthState.waiting_for_password)

@dp.message(AuthState.waiting_for_password)
async def auth_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    login = data.get("login")
    password = message.text.strip()

    # Проверка логина и пароля
    if login in fake_users and fake_users[login]["password"] == password:
        # Успешная авторизация, выводим данные
        user_info = fake_users[login]
        role = user_info["role"]
        direction = user_info["direction"]
        await message.answer(f"✅ Вы успешно вошли в систему!\n\n*Роль:* {role}\n*Направление:* {direction}")
    else:
        # Ошибка при авторизации
        await message.answer("❌ Неверный логин или пароль. Пожалуйста, попробуйте снова.")
        await state.set_state(AuthState.waiting_for_login)

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot)) 
@dp.callback_query(lambda c: c.data == "reg:parent")
async def register_parent(call: CallbackQuery):
    number = random.randint(1000, 9999)
    login = f"PARENT-{number}"
    password = str(number)

    fake_users[login] = {
        "password": password,
        "role": "Родитель",
        "direction": "Юриспруденция"
    }

    await call.message.answer(
        f"👨‍👩‍👧 Регистрация завершена как Родитель!\n\n"
        f"🔐 *Логин:* `{login}`\n"
        f"🔑 *Пароль:* `{password}`\n\n"
        f"Сохраните эти данные для входа в профиль.",
        parse_mode="Markdown"
    )
    @dp.callback_query(lambda c: c.data == "reg:teacher")
    async def register_teacher(call: CallbackQuery):
        number = random.randint(1000, 9999)
    login = f"TEACHER-{number}"
    password = str(number)

    fake_users[login] = {
        "password": password,
        "role": "Учитель",
        "direction": "Маркетинг"
    }

    await call.message.answer(
        f"👨‍🏫 Регистрация завершена как Учитель!\n\n"
        f"🔐 *Логин:* `{login}`\n"
        f"🔑 *Пароль:* `{password}`\n\n"
        f"Сохраните эти данные для входа в профиль.",
        parse_mode="Markdown"
    )

import mysql.connector
from mysql.connector import Error

# Подключение к базе данных
def connect():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='college_bot',
            user='root',
            password='your_password_here'  # ❗️замени на свой пароль
        )
        return connection
    except Error as e:
        print("Ошибка подключения к MySQL", e)
        return None


# Добавить пользователя (регистрация)
def add_user(login, password, role, direction):
    conn = connect()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (login, password, role, direction)
                VALUES (%s, %s, %s, %s)
            """, (login, password, role, direction))
            conn.commit()
            print(f"✅ Пользователь {login} добавлен")
        except Error as e:
            print("❌ Ошибка при добавлении пользователя:", e)
        finally:
            conn.close()


# Проверка авторизации
def authenticate_user(login, password):
    conn = connect()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM users WHERE login = %s AND password = %s
            """, (login, password))
            user = cursor.fetchone()
            return user
        except Error as e:
            print("❌ Ошибка при авторизации:", e)
            return None
        finally:
            conn.close()

# Добавление нового родителя
add_user("PARENT-1111", "1111", "Родитель", "Юриспруденция")

# Авторизация
user = authenticate_user("PARENT-1111", "1111")
if user:
    print(f"Добро пожаловать, {user['role']}!")
    print(f"Направление: {user['direction']}")
else:
    print("❌ Неверный логин или пароль.")





#plgn
from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Состояния для сбора жалобы
class ComplaintState(StatesGroup):
    waiting_for_complaint = State()

# Обработчик на команду жалобы
@dp.callback_query(lambda c: c.data == "complaint:file")
async def complaint_handler(call: CallbackQuery, state: FSMContext):
    await call.message.answer("📣 Пожалуйста, опишите вашу *жалобу*:", parse_mode="Markdown")
    await state.set_state(ComplaintState.waiting_for_complaint)

# Обработчик текста жалобы
@dp.message(ComplaintState.waiting_for_complaint)
async def save_complaint(message: types.Message, state: FSMContext):
    complaint_text = message.text.strip()

    # Сохранение жалобы в базу данных
    user_id = message.from_user.id
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='college_bot'
    )
    cursor = connection.cursor()

    cursor.execute("INSERT INTO complaints (user_id, complaint_text) VALUES (%s, %s)", (user_id, complaint_text))
    connection.commit()

    cursor.close()
    connection.close()

    await message.answer("📣 Ваша жалоба сохранена. Спасибо за ваше обращение!")
    await state.clear()





#no2
# Состояния для сбора отзыва
class FeedbackState(StatesGroup):
    waiting_for_feedback = State()

# Обработчик на команду отзыва
@dp.callback_query(lambda c: c.data == "suggestion:file")
async def feedback_handler(call: CallbackQuery, state: FSMContext):
    await call.message.answer("✨ Пожалуйста, напишите ваш *отзыв*:", parse_mode="Markdown")
    await state.set_state(FeedbackState.waiting_for_feedback)

# Обработчик текста отзыва
@dp.message(FeedbackState.waiting_for_feedback)
async def save_feedback(message: types.Message, state: FSMContext):
    feedback_text = message.text.strip()

    # Сохранение отзыва в базу данных
    user_id = message.from_user.id
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='college_bot'
    )
    cursor = connection.cursor()

    cursor.execute("INSERT INTO feedback (user_id, feedback_text) VALUES (%s, %s)", (user_id, feedback_text))
    connection.commit()

    cursor.close()
    connection.close()

    await message.answer("✨ Ваш отзыв сохранен. Спасибо за ваше мнение!")
    await state.clear()



#no3
@dp.message(commands=["view_complaints"])
async def view_complaints(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав для просмотра жалоб.")
        return

    # Подключение к базе данных
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='college_bot'
    )
    cursor = connection.cursor()

    cursor.execute("SELECT user_id, complaint_text, created_at FROM complaints")
    complaints = cursor.fetchall()

    if complaints:
        response = "📣 Все жалобы:\n\n"
        for complaint in complaints:
            response += f"ID Пользователя: {complaint[0]}\nЖалоба: {complaint[1]}\nДата: {complaint[2]}\n\n"
    else:
        response = "❌ Нет жалоб."

    await message.answer(response)
    cursor.close()
    connection.close()





#no4
@dp.message(commands=["view_feedback"])
async def view_feedback(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав для просмотра отзывов.")
        return

    # Подключение к базе данных
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='college_bot'
    )
    cursor = connection.cursor()

    cursor.execute("SELECT user_id, feedback_text, created_at FROM feedback")
    feedback = cursor.fetchall()

    if feedback:
        response = "✨ Все отзывы:\n\n"
        for fb in feedback:
            response += f"ID Пользователя: {fb[0]}\nОтзыв: {fb[1]}\nДата: {fb[2]}\n\n"
    else:
        response = "❌ Нет отзывов."

    await message.answer(response)
    cursor.close()
    connection.close()




#5
# Пример добавления отзыва в базу данных
import mysql.connector

# Подключение к базе данных
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="college_bot"
)

cursor = db.cursor()

def save_feedback(user_id, feedback_text):
    query = "INSERT INTO feedback (user_id, feedback_text, created_at) VALUES (%s, %s, NOW())"
    cursor.execute(query, (user_id, feedback_text))
    db.commit()
    print(f"Отзыв пользователя {user_id} добавлен.")


#6
def get_feedback():
    query = "SELECT * FROM feedback ORDER BY created_at DESC"
    cursor.execute(query)
    feedback = cursor.fetchall()

    for row in feedback:
        print(f"Отзыв от пользователя {row[1]}: {row[2]}")



#7
@dp.callback_query(lambda c: c.data == "view_feedback")
async def view_feedback(call: CallbackQuery):
    query = "SELECT * FROM feedback ORDER BY created_at DESC"
    cursor.execute(query)
    feedback = cursor.fetchall()
    
    if feedback:
        for row in feedback:
            await call.message.answer(f"Отзыв от пользователя {row[1]}: {row[2]}")
    else:
        await call.message.answer("Нет доступных отзывов.")



#8
from aiogram import types
from aiogram.types import CallbackQuery
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="college_bot"
)

cursor = db.cursor()

@dp.message()
async def handle_feedback(message: types.Message):
    feedback_text = message.text.strip()
    
    if feedback_text:
        user_id = message.from_user.id  # Получаем ID пользователя
        query = "INSERT INTO feedback (user_id, feedback_text, created_at) VALUES (%s, %s, NOW())"
        cursor.execute(query, (user_id, feedback_text))
        db.commit()
        
        await message.answer("Ваш отзыв был успешно добавлен! Спасибо!")
    else:
        await message.answer("Пожалуйста, напишите свой отзыв.")



#9
import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",  # Используйте ваш логин
        password="your_password",  # Используйте ваш пароль
        database="college_bot"  # Название вашей базы данных
    )
    cursor = db.cursor()
    print("Соединение установлено успешно!")
except mysql.connector.Error as err:
    print(f"Ошибка подключения: {err}")



#10
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",  # Ваш логин
    password="your_password",  # Ваш пароль
    database="college_bot"  # Название вашей базы данных
)

cursor = db.cursor()

def save_feedback(user_id, feedback_text):
    query = "INSERT INTO feedback (user_id, feedback_text, created_at) VALUES (%s, %s, NOW())"
    cursor.execute(query, (user_id, feedback_text))
    db.commit()
    print(f"Отзыв пользователя {user_id} добавлен.")

# Пример добавления отзыва
save_feedback(12345, "Отличное приложение!")






#register
import random
import string

# Генератор случайного логина и пароля
def generate_credentials():
    login = 'user' + ''.join(random.choices(string.digits, k=5))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return login, password



#register2
@dp.message_handler(commands=['register'])
async def register_user(message: types.Message):
    telegram_id = message.from_user.id

    # Проверка: зарегистрирован ли пользователь
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
    user = cursor.fetchone()

    if user:
        await message.answer("Вы уже зарегистрированы.")
        return

    # Запрос роли
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("студент"), KeyboardButton("родитель"), KeyboardButton("учитель"))
    await message.answer("Выберите вашу роль:", reply_markup=markup)
    await Registration.role.set()


@dp.message_handler(state=Registration.role)
async def process_role(message: types.Message, state: FSMContext):
    role = message.text.lower()
    if role not in ['студент', 'родитель', 'учитель']:
        await message.answer("Пожалуйста, выберите роль из списка.")
        return

    await state.update_data(role=role)
    await message.answer("Введите ваше имя:", reply_markup=ReplyKeyboardRemove())
    await Registration.next()


@dp.message_handler(state=Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    user_data = await state.get_data()
    role = user_data['role']
    telegram_id = message.from_user.id

    # Генерация логина и пароля
    login, password = generate_credentials()

    # Сохранение в БД
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (telegram_id, role, name, login, password) VALUES (%s, %s, %s, %s, %s)",
                   (telegram_id, role, name, login, password))
    conn.commit()
    cursor.close()
    conn.close()

    await message.answer(
        f"Регистрация прошла успешно!\n\n"
        f"🆔 Ваш логин: <code>{login}</code>\n"
        f"🔑 Пароль: <code>{password}</code>\n\n"
        f"Используйте эти данные для входа.",
        parse_mode="HTML"
    )
    await state.finish()



#register3
@dp.message_handler(commands=['login'])
async def login_start(message: types.Message):
    await message.answer("Введите ваш логин:")
    await Login.login.set()


@dp.message_handler(state=Login.login)
async def process_login_step(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Введите пароль:")
    await Login.next()


@dp.message_handler(state=Login.password)
async def process_password_step(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    login = user_data['login']
    password = message.text

    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE login = %s AND password = %s", (login, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        await message.answer(f"✅ Успешный вход. Ваша роль: {user[2]}")
        await state.finish()
    else:
        await message.answer("❌ Неверный логин или пароль. Попробуйте снова.")
        await state.finish()







