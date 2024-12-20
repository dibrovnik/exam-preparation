import os
import requests
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# URL и токены API
APP_API_URL = os.getenv("APP_API_URL", "http://localhost:8000/api")
APP_API_TOKEN = os.getenv("APP_API_TOKEN", "iqO0M6kDsEtMQt0OMV65xJf0lDrdWB4p1zCkkak75f977bca")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7722830157:AAFaHc4CmkiXytXtjqYL1eeX3dX6-xFhsoM")

# Состояние пользователя
user_states = {}


# Функция для получения списка экзаменов
def fetch_exams():
    headers = {"Authorization": f"Bearer {APP_API_TOKEN}", "Accept": "application/json"}
    response = requests.get(f"{APP_API_URL}/exams", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Ошибка получения экзаменов: {response.text}")
        return []
    
# Функция для получения вопросов экзамена
def fetch_exam_questions(exam_id):
    headers = {"Authorization": f"Bearer {APP_API_TOKEN}", "Accept": "application/json"}
    response = requests.get(f"{APP_API_URL}/exams/{exam_id}", headers=headers)
    if response.status_code == 200:
        return response.json().get("questions", [])
    return []

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение с описанием всех команд."""
    welcome_message = (
        "Добро пожаловать в бота для подготовки к экзаменам!\n\n"
        "Доступные команды:\n"
        "/prepare - Начать подготовку к экзамену\n"
        "/upload - Загрузить вопросы в экзамен\n"
        "/addexam - Создать новый экзамен\n"
        "/help - Показать это сообщение\n"
    )

    # Клавиатура с командами
    keyboard = [
        [KeyboardButton("/prepare")],
        [KeyboardButton("/addexam")],
        [KeyboardButton("/upload")],
        [KeyboardButton("/help")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


# Команда /start
async def start_preparing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение и выбор экзамена."""
    exams = fetch_exams()
    if not exams:
        await update.message.reply_text("Нет доступных экзаменов.")
        return

    # Генерация кнопок для выбора экзамена
    keyboard = [
        [InlineKeyboardButton(exam["name"], callback_data=f"exam_{exam['id']}")]
        for exam in exams
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Добро пожаловать! Выберите экзамен из списка:", reply_markup=reply_markup
    )


# Обработка выбора экзамена
async def exam_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора экзамена и отображение первого вопроса."""
    query = update.callback_query
    await query.answer()

    exam_id = query.data.split("_")[1]
    questions = fetch_exam_questions(exam_id)

    if not questions:
        await query.edit_message_text("В этом экзамене нет вопросов.")
        return

    # Сохранение состояния пользователя
    user_states[query.from_user.id] = {
        "exam_id": exam_id,
        "questions": questions,
        "current_index": 0,
    }

    # Показ первого вопроса
    await show_question(query, context)


# Показ текущего вопроса
async def show_question(query, context: ContextTypes.DEFAULT_TYPE):
    """Отображение текущего вопроса с кнопками навигации."""
    user_id = query.from_user.id
    state = user_states.get(user_id)

    if not state:
        await query.edit_message_text("Сессия истекла. Используйте /start для начала.")
        return

    current_index = state["current_index"]
    question = state["questions"][current_index]

    # Формирование текста вопроса
    text = f"Вопрос {current_index + 1} из {len(state['questions'])}:\n\n{question['question']}\n\nОтвет: {question['answer']}"

    # Кнопки навигации
    buttons = []
    if current_index > 0:
        buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data="prev"))
    if current_index < len(state["questions"]) - 1:
        buttons.append(InlineKeyboardButton("➡️ Вперед", callback_data="next"))

    reply_markup = InlineKeyboardMarkup([buttons])

    await query.edit_message_text(text, reply_markup=reply_markup)


# Обработка кнопок "Вперед" и "Назад"
async def navigate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка навигации между вопросами."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    state = user_states.get(user_id)

    if not state:
        await query.edit_message_text("Сессия истекла. Используйте /start для начала.")
        return

    # Изменение текущего индекса
    if query.data == "prev" and state["current_index"] > 0:
        state["current_index"] -= 1
    elif query.data == "next" and state["current_index"] < len(state["questions"]) - 1:
        state["current_index"] += 1

    # Показ текущего вопроса
    await show_question(query, context)

# Команда /upload
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос выбора экзамена перед загрузкой вопросов."""
    logger.info(f"Пользователь {update.effective_user.id} вызвал команду /upload.")
    exams = fetch_exams()
    if not exams:
        await update.message.reply_text("Нет доступных экзаменов.")
        return

    keyboard = [
        [InlineKeyboardButton(exam["name"], callback_data=f"upload_exam_{exam['id']}")]
        for exam in exams
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите экзамен для загрузки вопросов:", reply_markup=reply_markup)



# Обработка выбора экзамена для загрузки вопросов
async def select_exam_for_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    exam_id = query.data.split("_")[-1]
    logger.info(f"Пользователь {query.from_user.id} выбрал экзамен ID {exam_id} для загрузки вопросов.")

    # Сохраняем ID выбранного экзамена
    user_states[query.from_user.id] = {"exam_id": exam_id}

    await query.edit_message_text("Теперь отправьте файл .xlsx с вопросами.")


# Обработка загруженного файла
async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка файла и отправка на сервер."""
    logger.info(f"Пользователь {update.effective_user.id} загрузил файл.")

    state = user_states.get(update.effective_user.id)
    if not state or "exam_id" not in state:
        await update.message.reply_text("Сначала выберите экзамен с помощью команды /upload.")
        return

    file = await context.bot.get_file(update.message.document.file_id)
    file_path = f"/tmp/{update.message.document.file_name}"
    await file.download_to_drive(file_path)
    logger.info(f"Файл сохранён во временной директории: {file_path}")

    # Отправляем файл на API
    exam_id = state["exam_id"]
    endpoint_url = f"{APP_API_URL}/exams/{exam_id}/import-questions"
    headers = {"Authorization": f"Bearer {APP_API_TOKEN}"}
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(endpoint_url, files=files, headers=headers)

    if response.status_code == 200:
        logger.info(f"Файл успешно загружен для экзамена ID {exam_id}.")
        await update.message.reply_text("Файл успешно загружен!")
    else:
        logger.error(f"Ошибка загрузки файла: {response.text}")
        await update.message.reply_text("Ошибка при загрузке файла. Попробуйте позже.")

# Команда /addexam
async def add_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос на добавление нового экзамена."""
    logger.info(f"Пользователь {update.effective_user.id} вызвал команду /addexam.")
    await update.message.reply_text(
        "Введите имя и дату экзамена в формате:\n\n<имя экзамена>\n<дата (YYYY-MM-DD)>"
    )
# Обработка текста после /addexam
async def handle_add_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает добавление экзамена."""
    logger.info(f"Пользователь {update.effective_user.id} вводит данные для нового экзамена.")
    try:
        text = update.message.text.strip()
        name, date = text.split("\n")

        # Отправляем запрос на создание экзамена
        payload = {"name": name.strip(), "date": date.strip()}
        headers = {"Authorization": f"Bearer {APP_API_TOKEN}", "Accept": "application/json"}
        response = requests.post(f"{APP_API_URL}/exams", json=payload, headers=headers)

        if response.status_code == 201:
            logger.info(f"Экзамен '{name}' успешно создан.")
            await update.message.reply_text(f"Экзамен '{name}' успешно создан.")
        else:
            logger.error(f"Ошибка создания экзамена: {response.text}")
            await update.message.reply_text("Ошибка при создании экзамена. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Ошибка обработки команды /addexam: {e}")
        await update.message.reply_text(
            "Неверный формат. Введите имя и дату экзамена в формате:\n\n<имя экзамена>\n<дата (YYYY-MM-DD)>"
        )


# Запуск приложения
if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("prepare", start_preparing))
    application.add_handler(CommandHandler("addexam", add_exam))
    application.add_handler(CallbackQueryHandler(exam_selection, pattern="^exam_"))
    application.add_handler(CallbackQueryHandler(navigate, pattern="^(prev|next)$"))
    application.add_handler(CommandHandler("upload", upload))
    application.add_handler(CommandHandler("addexam", add_exam))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_exam))
    application.add_handler(CallbackQueryHandler(select_exam_for_upload, pattern="^upload_exam_"))
    application.add_handler(MessageHandler(filters.Document.FileExtension("xlsx"), handle_file_upload))

    # Запуск
    logger.info("Запуск Telegram-бота.")
    application.run_polling()
