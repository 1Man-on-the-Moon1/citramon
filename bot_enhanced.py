import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional
import json
import re

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from config import *
from database import Database, init_db

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()
db = Database()

# Bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# FSM States
class RegistrationState(StatesGroup):
    waiting_for_name = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_city = State()
    waiting_for_photos = State()
    waiting_for_bio = State()
    waiting_for_interests = State()
    registration_complete = State()

class MainMenuState(StatesGroup):
    main_menu = State()
    viewing_profile = State()
    browsing_feed = State()
    in_chat = State()
    rating_user = State()
    in_admin = State()
    admin_search_user = State()
    admin_broadcast = State()
    viewing_photos = State()
    editing_profile = State()

# ===== Keyboards =====

BACK_TEXT = "◀️ Назад"

def get_back_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=BACK_TEXT)
    return builder.as_markup(resize_keyboard=True)

def get_gender_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="👨 Мужской")
    builder.button(text="👩 Женский")
    builder.button(text=BACK_TEXT)
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

def get_cities_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for city in BELARUS_CITIES:
        builder.button(text=city)
    builder.button(text=BACK_TEXT)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_interests_keyboard(selected: list = None) -> InlineKeyboardMarkup:
    if selected is None:
        selected = []
    builder = InlineKeyboardBuilder()
    for interest in INTERESTS:
        checked = "✓" if interest in selected else ""
        builder.button(text=f"{checked} {interest}", callback_data=f"interest_{interest}")
    builder.adjust(2)
    if len(selected) > 0:
        builder.button(text="✅ Готово", callback_data="interests_done")
    builder.button(text=BACK_TEXT, callback_data="interests_back")
    builder.adjust(1)
    return builder.as_markup()

def get_main_menu_keyboard(user_id: int = None) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="❤️ Лента анкет")
    builder.button(text="💬 Мои мэтчи")
    builder.button(text="👤 Мой профиль")
    builder.button(text="🔍 Просмотр фото")
    builder.button(text="✏️ Отредактировать")
    builder.button(text="📞 Поддержка")
    builder.button(text="🗑 Удалить анкету")
    if user_id and user_id == ADMIN_ID:
        builder.button(text="🔧 Админ")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="📋 Жалобы")
    builder.button(text="👥 Управление пользователями")
    builder.button(text="📊 Статистика")
    builder.button(text="📢 Рассылка")
    builder.button(text=BACK_TEXT)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_feed_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❤️ Лайк", callback_data="like_profile")
    builder.button(text="👎 Пропустить", callback_data="skip_profile")
    builder.button(text="🚨 Пожаловаться", callback_data="report_profile")
    builder.button(text=BACK_TEXT, callback_data="feed_back")
    builder.adjust(1)
    return builder.as_markup()

def get_match_keyboard(match_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Написать сообщение", callback_data=f"chat_{match_id}")
    builder.button(text="🎉 ПРИГЛАСИТЬ НА СВИДАНИЕ", callback_data=f"invite_{match_id}")
    builder.button(text="📅 Назначить свидание", callback_data=f"date_{match_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_date_accept_keyboard(date_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить свидание", callback_data=f"accept_date_{date_id}")
    builder.button(text="❌ Отклонить", callback_data=f"decline_date_{date_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_date_arrival_keyboard(date_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Я на месте", callback_data=f"arrived_date_{date_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_rating_keyboard(date_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for stars in range(1, 6):
        builder.button(text="⭐" * stars, callback_data=f"rate_{date_id}_{stars}")
    builder.adjust(1)
    return builder.as_markup()

def get_positive_tags_keyboard(date_id: int, stars: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for tag in POSITIVE_TAGS:
        builder.button(text=tag, callback_data=f"pos_tag_{date_id}_{stars}_{tag}")
    builder.button(text="✅ Готово", callback_data=f"done_pos_tags_{date_id}_{stars}")
    builder.adjust(1)
    return builder.as_markup()

def get_negative_tags_keyboard(date_id: int, stars: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for tag in NEGATIVE_TAGS:
        builder.button(text=tag, callback_data=f"neg_tag_{date_id}_{stars}_{tag}")
    builder.button(text="✅ Готово", callback_data=f"done_neg_tags_{date_id}_{stars}")
    builder.adjust(1)
    return builder.as_markup()

def get_complaint_types_keyboard(to_user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for complaint_type in COMPLAINT_TYPES:
        builder.button(text=complaint_type, callback_data=f"complaint_{to_user_id}_{complaint_type}")
    builder.adjust(1)
    return builder.as_markup()

# ===== Helper functions =====

def extract_gender_from_text(text: str) -> Optional[str]:
    if "Мужской" in text:
        return "M"
    elif "Женский" in text:
        return "F"
    return None

def get_opposite_gender(gender: str) -> str:
    return "F" if gender == "M" else "M"

def get_next_profile_to_show(user_id: int) -> Optional[dict]:
    user = db.get_user(user_id)
    if not user:
        return None
    
    all_users = db.get_all_users()
    
    candidates = []
    for u in all_users:
        if u['user_id'] == user_id:
            continue
        user_obj = db.get_user(u['user_id'])
        if not user_obj:
            continue
        if user_obj['is_banned'] or user_obj['is_shadow_banned']:
            continue
        if user_obj['gender'] == user['gender']:
            continue
        if db.has_liked(user_id, u['user_id']) or db.has_skipped(user_id, u['user_id']):
            continue
        candidates.append(u)
    
    if not candidates:
        return None
    
    def score_profile(profile):
        score = 0
        if profile['rating'] >= 4.5:
            score += 1000
        if profile['city'] == user['city']:
            score += 500
        user_obj = db.get_user(profile['user_id'])
        created = datetime.fromisoformat(user_obj['created_at'])
        if datetime.now() - created < timedelta(hours=NEWBIE_BOOST_HOURS):
            score += 300
        if user_obj['last_seen']:
            last_seen = datetime.fromisoformat(user_obj['last_seen'])
            hours_ago = (datetime.now() - last_seen).total_seconds() / 3600
            if hours_ago < 24:
                score += 200
        score += profile['rating'] * 10
        return score
    
    candidates.sort(key=score_profile, reverse=True)
    return db.get_user(candidates[0]['user_id'])

# ===== Command handlers =====

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if user and user['registration_complete']:
        await message.answer(
            "👋 Добро пожаловать в ЦИТРАМОН!\n\n"
            "Выберите действие:",
            reply_markup=get_main_menu_keyboard(user_id)
        )
        await state.set_state(MainMenuState.main_menu)
    else:
        await message.answer(
            "👋 Добро пожаловать в ЦИТРАМОН - приложение для знакомств в Беларуси!\n\n"
            "Давайте создадим вашу анкету. Как вас зовут? (максимум 20 символов)\n\n"
            "Для отмены нажмите ◀️ Назад",
            reply_markup=get_back_keyboard()
        )
        await state.set_state(RegistrationState.waiting_for_name)

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к админ-панели")
        return
    
    await message.answer(
        "🔧 Админ-панель",
        reply_markup=get_admin_keyboard()
    )
    await state.set_state(MainMenuState.in_admin)

# ===== Registration handlers with BACK buttons =====

@dp.message(RegistrationState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    if message.text == BACK_TEXT:
        await state.clear()
        user = db.get_user(message.from_user.id)
        if user and user['registration_complete']:
            await message.answer("Выберите действие:", reply_markup=get_main_menu_keyboard(message.from_user.id))
            await state.set_state(MainMenuState.main_menu)
        else:
            await message.answer("Регистрация отменена. Напишите /start чтобы начать заново.", reply_markup=types.ReplyKeyboardRemove())
        return
    
    try:
        if not message.text or message.text.startswith('/'):
            await message.answer("❌ Пожалуйста, введите ваше имя (текст без команд).")
            return
        
        name = message.text.strip()
        if not name:
            await message.answer("❌ Имя не может быть пустым.")
            return
        if len(name) > MAX_NAME_LENGTH:
            await message.answer(f"❌ Имя слишком длинное. Максимум {MAX_NAME_LENGTH} символов.")
            return
        if len(name) < 2:
            await message.answer("❌ Имя слишком короткое. Минимум 2 символа.")
            return
        
        await state.update_data(name=name)
        await message.answer(
            "Выберите ваш пол:",
            reply_markup=get_gender_keyboard()
        )
        await state.set_state(RegistrationState.waiting_for_gender)
    except Exception as e:
        logger.error(f"Error in process_name: {e}")
        await message.answer("❌ Ошибка при обработке имени. Попробуйте снова.")

@dp.message(RegistrationState.waiting_for_gender)
async def process_gender(message: types.Message, state: FSMContext):
    if message.text == BACK_TEXT:
        await message.answer(
            "Как вас зовут? (максимум 20 символов)",
            reply_markup=get_back_keyboard()
        )
        await state.set_state(RegistrationState.waiting_for_name)
        return
    
    try:
        if not message.text or message.text.startswith('/'):
            await message.answer("❌ Пожалуйста, выберите пол из кнопок.")
            return
        
        gender = extract_gender_from_text(message.text)
        if not gender:
            await message.answer("❌ Пожалуйста, выберите пол из предложенных вариантов.")
            return
    except Exception as e:
        logger.error(f"Error in process_gender: {e}")
        await message.answer("❌ Ошибка при обработке пола. Попробуйте снова.")
        return
    
    await state.update_data(gender=gender)
    await message.answer(
        "Сколько вам лет? (введите число, минимум 18)",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(RegistrationState.waiting_for_age)

@dp.message(RegistrationState.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    if message.text == BACK_TEXT:
        await message.answer("Выберите ваш пол:", reply_markup=get_gender_keyboard())
        await state.set_state(RegistrationState.waiting_for_gender)
        return
    
    try:
        if not message.text or message.text.startswith('/'):
            await message.answer("❌ Пожалуйста, введите число.")
            return
        
        age = int(message.text.strip())
        if age < MIN_AGE or age > MAX_AGE:
            await message.answer(f"❌ Возраст должен быть от {MIN_AGE} до {MAX_AGE} лет.")
            return
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректный возраст (число).")
        return
    except Exception as e:
        logger.error(f"Error in process_age: {e}")
        await message.answer("❌ Ошибка при обработке возраста. Попробуйте снова.")
        return
    
    await state.update_data(age=age)
    await message.answer(
        "Выберите ваш город:",
        reply_markup=get_cities_keyboard()
    )
    await state.set_state(RegistrationState.waiting_for_city)

@dp.message(RegistrationState.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    if message.text == BACK_TEXT:
        await message.answer("Сколько вам лет? (введите число, минимум 18)", reply_markup=get_back_keyboard())
        await state.set_state(RegistrationState.waiting_for_age)
        return
    
    city = message.text.strip()
    if city not in BELARUS_CITIES:
        await message.answer("❌ Пожалуйста, выберите город из предложенных вариантов.")
        return
    
    await state.update_data(city=city)
    await message.answer(
        "Загрузите фотографию вашего профиля.",
        reply_markup=get_back_keyboard()
    )
    await state.update_data(photos=[])
    await state.set_state(RegistrationState.waiting_for_photos)

@dp.message(RegistrationState.waiting_for_photos)
async def process_photos(message: types.Message, state: FSMContext):
    if message.text == BACK_TEXT:
        await message.answer("Выберите ваш город:", reply_markup=get_cities_keyboard())
        await state.set_state(RegistrationState.waiting_for_city)
        return
    
    data = await state.get_data()
    photos = data.get('photos', [])
    
    if message.photo:
        if len(photos) >= MAX_PHOTOS:
            await message.answer(f"❌ Максимум {MAX_PHOTOS} фотография.")
            return
        
        photo = message.photo[-1]
        photos.append(photo.file_id)
        await state.update_data(photos=photos)
        
        # With MAX_PHOTOS=1, auto-advance to bio step
        await message.answer(
            "✅ Фотография загружена!\n\nНапишите о себе (максимум 200 символов):",
            reply_markup=get_back_keyboard()
        )
        await state.set_state(RegistrationState.waiting_for_bio)
        return
    
    await message.answer("❌ Пожалуйста, отправьте фотографию.")

@dp.message(RegistrationState.waiting_for_bio)
async def process_bio(message: types.Message, state: FSMContext):
    if message.text == BACK_TEXT:
        await state.update_data(photos=[])
        await message.answer("Загрузите фотографию вашего профиля.", reply_markup=get_back_keyboard())
        await state.set_state(RegistrationState.waiting_for_photos)
        return
    
    if not message.text:
        await message.answer("❌ Пожалуйста, введите текст о себе.")
        return
    
    bio = message.text.strip()
    if len(bio) > MAX_BIO_LENGTH:
        await message.answer(f"❌ Описание слишком длинное. Максимум {MAX_BIO_LENGTH} символов.")
        return
    
    await state.update_data(bio=bio)
    await message.answer(
        "Выберите ваши интересы (максимум 5). Нажимайте на кнопки для выбора:",
        reply_markup=get_interests_keyboard()
    )
    await state.update_data(interests=[])
    await state.set_state(RegistrationState.waiting_for_interests)

@dp.callback_query(RegistrationState.waiting_for_interests)
async def process_interests(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    interests = data.get('interests', [])
    
    if query.data == "interests_back":
        await query.message.answer(
            "Напишите о себе (максимум 200 символов):",
            reply_markup=get_back_keyboard()
        )
        await state.set_state(RegistrationState.waiting_for_bio)
        return
    
    if query.data == "interests_done":
        if len(interests) == 0:
            await query.answer("❌ Выберите хотя бы один интерес")
            return
        
        user_data = await state.get_data()
        user_id = query.from_user.id
        
        db.create_user(
            user_id=user_id,
            name=user_data['name'],
            gender=user_data['gender'],
            age=user_data['age'],
            city=user_data['city']
        )
        
        for photo_id in user_data['photos']:
            db.add_photo(user_id, photo_id)
        
        db.update_user(
            user_id,
            bio=user_data['bio'],
            interests=json.dumps(interests),
            registration_complete=True,
            last_seen=datetime.now().isoformat()
        )
        
        await query.message.answer(
            "✅ Ваша анкета создана!\n\n"
            "Добро пожаловать в ЦИТРАМОН! 🎉",
            reply_markup=get_main_menu_keyboard(user_id)
        )
        await state.set_state(MainMenuState.main_menu)
        return
    
    if query.data.startswith("interest_"):
        interest = query.data.replace("interest_", "")
        if interest in interests:
            interests.remove(interest)
        else:
            if len(interests) >= MAX_INTERESTS:
                await query.answer(f"❌ Максимум {MAX_INTERESTS} интересов")
                return
            interests.append(interest)
        
        await state.update_data(interests=interests)
        await query.message.edit_reply_markup(
            reply_markup=get_interests_keyboard(interests)
        )

# ===== Main menu handlers =====

@dp.message(MainMenuState.main_menu, F.text == "❤️ Лента анкет")
async def show_feed(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if user['is_banned']:
        await message.answer("❌ Ваш аккаунт заблокирован")
        return
    
    profile = get_next_profile_to_show(user_id)
    
    if not profile:
        await message.answer("😔 Больше нет анкет для просмотра")
        return
    
    await state.update_data(current_profile_id=profile['user_id'])
    
    photos = db.get_user_photos(profile['user_id'])
    interests = json.loads(profile['interests']) if profile['interests'] else []
    
    caption = f"👤 {profile['name']}, {profile['age']}\n"
    caption += f"📍 {profile['city']}\n"
    caption += f"⭐ Рейтинг: {profile['rating']:.1f}\n\n"
    caption += f"📝 {profile['bio']}\n\n"
    caption += f"💫 Интересы: {', '.join(interests)}"
    
    ratings = db.get_user_ratings(profile['user_id'])
    if ratings:
        caption += "\n\n📝 Отзывы:\n"
        for rating in ratings[:3]:
            caption += f"⭐ {rating['stars']} звёзд\n"
            if rating['positive_tags']:
                pos_tags = json.loads(rating['positive_tags'])
                caption += f"✅ {', '.join(pos_tags)}\n"
            if rating['negative_tags']:
                neg_tags = json.loads(rating['negative_tags'])
                caption += f"❌ {', '.join(neg_tags)}\n"
    
    if photos:
        await message.answer_photo(
            photo=photos[0]['file_id'],
            caption=caption,
            reply_markup=get_feed_keyboard()
        )
    else:
        await message.answer(caption, reply_markup=get_feed_keyboard())
    
    await state.set_state(MainMenuState.browsing_feed)

# Feed: Back button
@dp.callback_query(MainMenuState.browsing_feed, F.data == "feed_back")
async def feed_back(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer("Выберите действие:", reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(MainMenuState.browsing_feed, F.data == "like_profile")
async def like_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    data = await state.get_data()
    to_user_id = data.get('current_profile_id')
    
    if not to_user_id:
        await query.answer("❌ Ошибка")
        return
    
    db.add_like(user_id, to_user_id)
    
    if db.check_mutual_like(user_id, to_user_id):
        match_id = db.create_match(user_id, to_user_id)
        
        await bot.send_message(
            user_id,
            f"❤️ Взаимный лайк! Вы мэтчились!\n\n"
            f"Теперь вы можете общаться с этим пользователем.",
            reply_markup=get_main_menu_keyboard(user_id)
        )
        
        from_user = db.get_user(user_id)
        await bot.send_message(
            to_user_id,
            f"❤️ Взаимный лайк! Вы мэтчились с {from_user['name']}!\n\n"
            f"Теперь вы можете общаться.",
            reply_markup=get_main_menu_keyboard(to_user_id)
        )
    else:
        await query.answer("❤️ Лайк отправлен!")
    
    # Show next profile
    profile = get_next_profile_to_show(user_id)
    if profile:
        await state.update_data(current_profile_id=profile['user_id'])
        photos = db.get_user_photos(profile['user_id'])
        interests = json.loads(profile['interests']) if profile['interests'] else []
        
        caption = f"👤 {profile['name']}, {profile['age']}\n"
        caption += f"📍 {profile['city']}\n"
        caption += f"⭐ Рейтинг: {profile['rating']:.1f}\n\n"
        caption += f"📝 {profile['bio']}\n\n"
        caption += f"💫 Интересы: {', '.join(interests)}"
        
        if photos:
            await query.message.answer_photo(
                photo=photos[0]['file_id'],
                caption=caption,
                reply_markup=get_feed_keyboard()
            )
        else:
            await query.message.answer(caption, reply_markup=get_feed_keyboard())
    else:
        await query.message.answer("😔 Больше нет анкет для просмотра", reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu)

@dp.callback_query(MainMenuState.browsing_feed, F.data == "skip_profile")
async def skip_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    data = await state.get_data()
    to_user_id = data.get('current_profile_id')
    
    if to_user_id:
        db.add_skip(user_id, to_user_id)
    
    profile = get_next_profile_to_show(user_id)
    if profile:
        await state.update_data(current_profile_id=profile['user_id'])
        photos = db.get_user_photos(profile['user_id'])
        interests = json.loads(profile['interests']) if profile['interests'] else []
        
        caption = f"👤 {profile['name']}, {profile['age']}\n"
        caption += f"📍 {profile['city']}\n"
        caption += f"⭐ Рейтинг: {profile['rating']:.1f}\n\n"
        caption += f"📝 {profile['bio']}\n\n"
        caption += f"💫 Интересы: {', '.join(interests)}"
        
        if photos:
            await query.message.answer_photo(
                photo=photos[0]['file_id'],
                caption=caption,
                reply_markup=get_feed_keyboard()
            )
        else:
            await query.message.answer(caption, reply_markup=get_feed_keyboard())
    else:
        await query.message.answer("😔 Больше нет анкет для просмотра", reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu)

@dp.callback_query(MainMenuState.browsing_feed, F.data == "report_profile")
async def report_profile(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    to_user_id = data.get('current_profile_id')
    
    if not to_user_id:
        await query.answer("❌ Ошибка")
        return
    
    await state.update_data(report_user_id=to_user_id)
    await query.message.answer(
        "Выберите тип жалобы:",
        reply_markup=get_complaint_types_keyboard(to_user_id)
    )

@dp.callback_query(F.data.startswith("complaint_"))
async def process_complaint(query: types.CallbackQuery, state: FSMContext):
    parts = query.data.split("_", 2)
    to_user_id = int(parts[1])
    complaint_type = parts[2]
    
    user_id = query.from_user.id
    db.add_complaint(user_id, to_user_id, complaint_type)
    
    await query.message.answer(
        "✅ Жалоба отправлена. Спасибо за помощь в модерации!",
        reply_markup=get_main_menu_keyboard(user_id)
    )
    await state.set_state(MainMenuState.main_menu)

@dp.message(MainMenuState.main_menu, F.text == "💬 Мои мэтчи")
async def show_matches(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    matches = db.get_user_matches(user_id)
    
    if not matches:
        await message.answer("😔 У вас пока нет мэтчей")
        return
    
    for match in matches:
        partner_id = match['user2_id'] if match['user1_id'] == user_id else match['user1_id']
        partner = db.get_user(partner_id)
        
        text = f"👤 {partner['name']}, {partner['age']}\n"
        text += f"📍 {partner['city']}\n"
        text += f"⭐ Рейтинг: {partner['rating']:.1f}\n\n"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="💬 Чат", callback_data=f"chat_{match['match_id']}")
        builder.button(text="📅 Свидание", callback_data=f"date_{match['match_id']}")
        builder.button(text="⭐ Оценить", callback_data=f"rate_{match['match_id']}")
        builder.adjust(2)
        
        await message.answer(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("chat_"))
async def enter_chat(query: types.CallbackQuery, state: FSMContext):
    match_id = int(query.data.split("_")[1])
    partner_id = db.get_match_partner(match_id, query.from_user.id)
    
    if not partner_id:
        await query.answer("❌ Ошибка")
        return
    
    messages = db.get_match_messages(match_id)
    
    text = "💬 История сообщений:\n\n"
    if messages:
        for msg in messages:
            sender_name = db.get_user(msg['from_user_id'])['name']
            text += f"{sender_name}: {msg['content']}\n"
    else:
        text = "💬 Нет сообщений. Начните разговор!\n\n"
    
    text += "\nОтправьте сообщение (или нажмите ◀️ Назад):"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ СВИДАНИЕ СОСТОЯЛОСЬ", callback_data=f"confirm_dating_{match_id}")
    builder.adjust(1)
    
    await query.message.answer(text, reply_markup=builder.as_markup())
    await state.update_data(current_match_id=match_id)
    await state.set_state(MainMenuState.in_chat)

@dp.message(MainMenuState.in_chat)
async def send_message(message: types.Message, state: FSMContext):
    # Back button in chat
    if message.text == BACK_TEXT:
        await message.answer("Выберите действие:", reply_markup=get_main_menu_keyboard(message.from_user.id))
        await state.set_state(MainMenuState.main_menu)
        return
    
    data = await state.get_data()
    match_id = data.get('current_match_id')
    
    if not match_id:
        await message.answer("❌ Ошибка")
        return
    
    to_user_id = db.get_match_partner(match_id, message.from_user.id)
    
    if not to_user_id:
        await message.answer("❌ Ошибка")
        return
    
    db.send_message(match_id, message.from_user.id, to_user_id, message.text)
    
    sender = db.get_user(message.from_user.id)
    await bot.send_message(
        to_user_id,
        f"💬 Новое сообщение от {sender['name']}:\n\n{message.text}"
    )
    
    await message.answer("✅ Сообщение отправлено!")
    await message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard(message.from_user.id)
    )
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(F.data.startswith("confirm_dating_"))
async def confirm_dating(query: types.CallbackQuery, state: FSMContext):
    match_id = int(query.data.split("_")[2])
    user_id = query.from_user.id
    
    db.confirm_dating_occurred(match_id, user_id)
    
    status = db.get_match_confirmation_status(match_id)
    partner_id = status['user2_id'] if status['user1_id'] == user_id else status['user1_id']
    
    if status['both_confirmed']:
        await query.answer("✅ Оба пользователя подтвердили свидание!")
        await query.message.answer(
            "🎉 Оба пользователя подтвердили, что свидание состоялось!\n\nТеперь вы можете оставить отзыв."
        )
        await bot.send_message(
            partner_id,
            "🎉 Оба пользователя подтвердили, что свидание состоялось!\n\nТеперь вы можете оставить отзыв."
        )
    else:
        await query.answer("✅ Вы подтвердили свидание")
        await query.message.answer("⏳ Ожидание подтверждения от партнёра...")
        await bot.send_message(
            partner_id,
            "📄 Ваш партнёр подтвердил, что свидание состоялось. Подтвердите и вы."
        )

@dp.callback_query(F.data.startswith("rate_"))
async def rate_match(query: types.CallbackQuery, state: FSMContext):
    parts = query.data.split("_")
    if len(parts) == 2:  # rate_{match_id}
        match_id = int(parts[1])
        
        if not db.is_dating_confirmed_by_both(match_id):
            await query.answer(
                "❌ Оба пользователя должны подтвердить свидание в чате!",
                show_alert=True
            )
            return
        
        await query.message.answer(
            "🌟 Оцените вашего партнёра:",
            reply_markup=get_rating_keyboard(match_id)
        )
    elif len(parts) == 3:  # rate_{match_id}_{stars}
        match_id = int(parts[1])
        stars = int(parts[2])
        await state.update_data(rating_match_id=match_id, rating_stars=stars)
        await query.message.answer(
            "😊 Выберите положительные качества:",
            reply_markup=get_positive_tags_keyboard(match_id, stars)
        )

@dp.callback_query(F.data.startswith("pos_tag_"))
async def select_positive_tag(query: types.CallbackQuery, state: FSMContext):
    parts = query.data.split("_", 3)
    match_id = int(parts[2])
    stars = int(parts[3])
    
    data = await state.get_data()
    pos_tags = data.get('pos_tags', [])
    tag = query.data.replace(f"pos_tag_{match_id}_{stars}_", "")
    
    if tag not in pos_tags:
        pos_tags.append(tag)
    
    await state.update_data(pos_tags=pos_tags)
    await query.answer(f"✅ {tag} добавлен")

@dp.callback_query(F.data.startswith("done_pos_tags_"))
async def done_positive_tags(query: types.CallbackQuery, state: FSMContext):
    parts = query.data.split("_")
    match_id = int(parts[3])
    stars = int(parts[4])
    
    await query.message.answer(
        "😮 Выберите отрицательные качества:",
        reply_markup=get_negative_tags_keyboard(match_id, stars)
    )

@dp.callback_query(F.data.startswith("neg_tag_"))
async def select_negative_tag(query: types.CallbackQuery, state: FSMContext):
    parts = query.data.split("_", 3)
    match_id = int(parts[2])
    stars = int(parts[3])
    
    data = await state.get_data()
    neg_tags = data.get('neg_tags', [])
    tag = query.data.replace(f"neg_tag_{match_id}_{stars}_", "")
    
    if tag not in neg_tags:
        neg_tags.append(tag)
    
    await state.update_data(neg_tags=neg_tags)
    await query.answer(f"✅ {tag} добавлен")

@dp.callback_query(F.data.startswith("done_neg_tags_"))
async def done_negative_tags(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    parts = query.data.split("_")
    match_id = int(parts[3])
    stars = int(parts[4])
    
    user_id = query.from_user.id
    pos_tags = data.get('pos_tags', [])
    neg_tags = data.get('neg_tags', [])
    
    db.add_rating(
        match_id,
        user_id,
        stars,
        json.dumps(pos_tags),
        json.dumps(neg_tags)
    )
    
    await query.message.answer("✅ Оценка сохранена!")
    await query.message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard(user_id)
    )
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(F.data.startswith("invite_"))
async def invite_to_date(query: types.CallbackQuery, state: FSMContext):
    match_id = int(query.data.split("_")[1])
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📱 ОНЛАЙН", callback_data=f"invite_online_{match_id}")
    builder.button(text="🌟 ОФЛАЙН", callback_data=f"invite_offline_{match_id}")
    builder.adjust(1)
    
    await query.message.answer(
        "🎉 Выберите тип свидания:",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data.startswith("invite_online_"))
async def invite_online(query: types.CallbackQuery, state: FSMContext):
    match_id = int(query.data.split("_")[2])
    user_id = query.from_user.id
    partner_id = db.get_match_partner(match_id, user_id)
    user = db.get_user(user_id)
    
    await bot.send_message(
        partner_id,
        f"🎉 {user['name']} приглашает вас на ОНЛАЙН свидание!\n\nПодтвердите или отклоните приглашение."
    )
    
    await query.message.answer("✅ Приглашение отправлено!")

@dp.callback_query(F.data.startswith("invite_offline_"))
async def invite_offline(query: types.CallbackQuery, state: FSMContext):
    match_id = int(query.data.split("_")[2])
    user_id = query.from_user.id
    partner_id = db.get_match_partner(match_id, user_id)
    user = db.get_user(user_id)
    
    await bot.send_message(
        partner_id,
        f"🎉 {user['name']} приглашает вас на ОФЛАЙН свидание!\n\nПодтвердите или отклоните приглашение."
    )
    
    await query.message.answer("✅ Приглашение отправлено!")

# ===== Simplified date flow: propose → accept → both arrive =====

@dp.callback_query(F.data.startswith("date_"))
async def propose_date(query: types.CallbackQuery, state: FSMContext):
    match_id = int(query.data.split("_")[1])
    user_id = query.from_user.id
    partner_id = db.get_match_partner(match_id, user_id)
    proposer = db.get_user(user_id)
    
    date_id = db.propose_date(match_id, user_id)
    
    await bot.send_message(
        partner_id,
        f"📅 {proposer['name']} назначает свидание!\n\nПодтвердите или отклоните.",
        reply_markup=get_date_accept_keyboard(date_id)
    )
    
    await query.message.answer(
        "✅ Свидание предложено! Ожидаем подтверждения от партнёра.",
        reply_markup=get_main_menu_keyboard(user_id)
    )
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(F.data.startswith("accept_date_"))
async def accept_date(query: types.CallbackQuery, state: FSMContext):
    date_id = int(query.data.split("_")[2])
    date_record = db.get_date(date_id)
    
    if not date_record:
        await query.answer("❌ Свидание не найдено")
        return
    
    db.accept_date(date_id)
    
    user_id = query.from_user.id
    proposer_id = date_record['proposer_id']
    
    # Send arrival buttons to both
    await query.message.answer(
        "✅ Свидание подтверждено! Когда будете на месте, нажмите кнопку.",
        reply_markup=get_date_arrival_keyboard(date_id)
    )
    
    await bot.send_message(
        proposer_id,
        "✅ Партнёр подтвердил свидание! Когда будете на месте, нажмите кнопку.",
        reply_markup=get_date_arrival_keyboard(date_id)
    )

@dp.callback_query(F.data.startswith("decline_date_"))
async def decline_date(query: types.CallbackQuery, state: FSMContext):
    date_id = int(query.data.split("_")[2])
    date_record = db.get_date(date_id)
    
    if not date_record:
        await query.answer("❌ Свидание не найдено")
        return
    
    proposer_id = date_record['proposer_id']
    
    await query.message.answer("❌ Вы отклонили свидание.")
    await bot.send_message(proposer_id, "😔 Партнёр отклонил свидание.")

@dp.callback_query(F.data.startswith("arrived_date_"))
async def arrived_at_date(query: types.CallbackQuery, state: FSMContext):
    date_id = int(query.data.split("_")[2])
    user_id = query.from_user.id
    
    date_record = db.get_date(date_id)
    if not date_record:
        await query.answer("❌ Свидание не найдено")
        return
    
    db.confirm_arrival(date_id, user_id)
    
    updated = db.get_date(date_id)
    match = db.get_match_by_id(date_record['match_id'])
    partner_id = match['user2_id'] if match['user1_id'] == user_id else match['user1_id']
    
    if updated['status'] == 'completed':
        await query.message.answer("🎉 Оба на месте! Свидание состоялось! Приятного времяпровождения!")
        await bot.send_message(partner_id, "🎉 Оба на месте! Свидание состоялось! Приятного времяпровождения!")
    else:
        await query.answer("✅ Вы отметились! Ожидаем партнёра.")
        await bot.send_message(partner_id, "📍 Ваш партнёр уже на месте! Отметьтесь, когда придёте.", reply_markup=get_date_arrival_keyboard(date_id))

# ===== Profile, Support, Delete =====

@dp.message(MainMenuState.main_menu, F.text == "👤 Мой профиль")
async def show_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        await message.answer("❌ Профиль не найден")
        return
    
    interests = json.loads(user['interests']) if user['interests'] else []
    
    text = f"👤 Ваш профиль\n\n"
    text += f"Имя: {user['name']}\n"
    text += f"Возраст: {user['age']}\n"
    text += f"Город: {user['city']}\n"
    text += f"⭐ Рейтинг: {user['rating']:.1f}\n\n"
    text += f"📝 О себе: {user['bio']}\n\n"
    text += f"💫 Интересы: {', '.join(interests)}"
    
    await message.answer(text)

@dp.message(MainMenuState.main_menu, F.text == "🔍 Просмотр фото")
async def view_photos(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    photos = db.get_user_photos(user_id)
    
    if not photos:
        await message.answer("❌ У вас нет фото")
        return
    
    for photo in photos:
        await message.answer_photo(photo['file_id'])
    
    await message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard(user_id)
    )
    await state.set_state(MainMenuState.main_menu)

@dp.message(MainMenuState.main_menu, F.text == "✏️ Отредактировать")
async def edit_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    text = "📄 Редактирование профиля\n\n"
    text += f"👤 Имя: {user['name']}\n"
    text += f"👨 Пол: {user['gender']}\n"
    text += f"🎂 Возраст: {user['age']}\n"
    text += f"📍 Город: {user['city']}\n"
    text += f"📝 О себе: {user['bio']}\n\n"
    text += "Какие данные вы хотите изменить? (текущая версия поддерживает редактирование био и интересов)"
    
    await message.answer(text)
    await message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard(user_id)
    )
    await state.set_state(MainMenuState.main_menu)

# Support — просто ссылка на диалог с админом
@dp.message(MainMenuState.main_menu, F.text == "📞 Поддержка")
async def support(message: types.Message, state: FSMContext):
    await message.answer(
        f"📞 Поддержка\n\n"
        f"Для связи с администратором нажмите на ссылку ниже:\n"
        f"👉 [Написать админу](tg://user?id={ADMIN_ID})",
        parse_mode="Markdown"
    )

# Удаление анкеты
@dp.message(MainMenuState.main_menu, F.text == "🗑 Удалить анкету")
async def delete_profile_prompt(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, удалить", callback_data="confirm_delete_profile")
    builder.button(text="❌ Отмена", callback_data="cancel_delete_profile")
    builder.adjust(2)
    
    await message.answer(
        "⚠️ Вы уверены, что хотите удалить свою анкету?\n\n"
        "Это действие необратимо. Все ваши данные, мэтчи, сообщения и оценки будут удалены.",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "confirm_delete_profile")
async def confirm_delete_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    success = db.delete_user(user_id)
    
    if success:
        await state.clear()
        await query.message.answer(
            "✅ Ваша анкета удалена. Спасибо, что пользовались ЦИТРАМОН!\n\n"
            "Чтобы создать новую анкету, напишите /start",
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await query.message.answer("❌ Ошибка при удалении. Попробуйте позже.")

@dp.callback_query(F.data == "cancel_delete_profile")
async def cancel_delete_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(
        "✅ Удаление отменено.",
        reply_markup=get_main_menu_keyboard(user_id)
    )

# ===== Admin handlers =====

@dp.message(MainMenuState.main_menu, F.text == "🔧 Админ")
async def admin_button(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к админ-панели")
        return
    
    await message.answer(
        "🔧 Админ-панель",
        reply_markup=get_admin_keyboard()
    )
    await state.set_state(MainMenuState.in_admin)

@dp.message(MainMenuState.in_admin, F.text == "📋 Жалобы")
async def show_complaints(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа")
        return
    
    complaints = db.get_pending_complaints()
    
    if not complaints:
        await message.answer("✅ Нет новых жалоб")
        return
    
    for complaint in complaints:
        from_user = db.get_user(complaint['from_user_id'])
        to_user = db.get_user(complaint['to_user_id'])
        
        text = f"📋 Жалоба #{complaint['complaint_id']}\n\n"
        text += f"От: {from_user['name']}\n"
        text += f"На: {to_user['name']}\n"
        text += f"Тип: {complaint['complaint_type']}\n"
        text += f"Описание: {complaint['description']}\n"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Одобрить", callback_data=f"resolve_complaint_{complaint['complaint_id']}_approved")
        builder.button(text="❌ Отклонить", callback_data=f"resolve_complaint_{complaint['complaint_id']}_rejected")
        builder.adjust(2)
        
        await message.answer(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("resolve_complaint_"))
async def resolve_complaint(query: types.CallbackQuery):
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа")
        return
    
    parts = query.data.split("_")
    complaint_id = int(parts[2])
    status = parts[3]
    
    db.resolve_complaint(complaint_id, status)
    
    if status == "approved":
        complaint = db.get_complaint(complaint_id)
        db.ban_user(complaint['to_user_id'], shadow_ban=True)
        await query.answer("✅ Жалоба одобрена, пользователь теневой бан")
    else:
        await query.answer("✅ Жалоба отклонена")

@dp.message(MainMenuState.in_admin, F.text == "👥 Управление пользователями")
async def manage_users(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа")
        return
    
    await message.answer("Введите ID пользователя для поиска:")
    await state.set_state(MainMenuState.admin_search_user)

@dp.message(MainMenuState.admin_search_user)
async def search_user(message: types.Message, state: FSMContext):
    if message.text == BACK_TEXT:
        await message.answer("🔧 Админ-панель", reply_markup=get_admin_keyboard())
        await state.set_state(MainMenuState.in_admin)
        return
    
    try:
        user_id = int(message.text.strip())
        user = db.get_user(user_id)
        
        if not user:
            await message.answer("❌ Пользователь не найден")
            return
        
        text = f"👤 {user['name']}\n"
        text += f"ID: {user['user_id']}\n"
        text += f"Возраст: {user['age']}\n"
        text += f"Город: {user['city']}\n"
        text += f"⭐ Рейтинг: {user['rating']:.1f}\n"
        text += f"Заблокирован: {'Да' if user['is_banned'] else 'Нет'}\n"
        text += f"Теневой бан: {'Да' if user['is_shadow_banned'] else 'Нет'}\n"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🚫 Заблокировать", callback_data=f"admin_ban_{user_id}")
        builder.button(text="👻 Теневой бан", callback_data=f"admin_shadow_ban_{user_id}")
        builder.button(text="⭐ Обнулить рейтинг", callback_data=f"admin_reset_rating_{user_id}")
        builder.adjust(1)
        
        await message.answer(text, reply_markup=builder.as_markup())
        await state.set_state(MainMenuState.in_admin)
    except ValueError:
        await message.answer("❌ Введите корректный ID")

@dp.callback_query(F.data.startswith("admin_ban_"))
async def admin_ban_user(query: types.CallbackQuery):
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа")
        return
    
    user_id = int(query.data.split("_")[2])
    db.ban_user(user_id, shadow_ban=False)
    await query.answer("✅ Пользователь заблокирован")

@dp.callback_query(F.data.startswith("admin_shadow_ban_"))
async def admin_shadow_ban_user(query: types.CallbackQuery):
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа")
        return
    
    user_id = int(query.data.split("_")[3])
    db.ban_user(user_id, shadow_ban=True)
    await query.answer("✅ Пользователь получил теневой бан")

@dp.callback_query(F.data.startswith("admin_reset_rating_"))
async def admin_reset_rating(query: types.CallbackQuery):
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа")
        return
    
    user_id = int(query.data.split("_")[3])
    db.reset_user_rating(user_id)
    await query.answer("✅ Рейтинг пользователя обнулен")

@dp.message(MainMenuState.in_admin, F.text == "📊 Статистика")
async def show_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа")
        return
    
    stats = db.get_stats()
    
    text = "📊 Статистика:\n\n"
    text += f"👥 Всего пользователей: {stats['total_users']}\n"
    text += f"❤️ Всего мэтчей: {stats['total_matches']}\n"
    text += f"✅ Подтверждённых свиданий: {stats['confirmed_dates']}\n\n"
    text += "📍 По городам:\n"
    for city, count in stats['city_stats'].items():
        text += f"  {city}: {count}\n"
    
    await message.answer(text)

@dp.message(MainMenuState.in_admin, F.text == "📢 Рассылка")
async def broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа")
        return
    
    await message.answer("Введите текст рассылки (или ◀️ Назад для отмены):")
    await state.set_state(MainMenuState.admin_broadcast)

@dp.message(MainMenuState.admin_broadcast)
async def send_broadcast(message: types.Message, state: FSMContext):
    if message.text == BACK_TEXT:
        await message.answer("🔧 Админ-панель", reply_markup=get_admin_keyboard())
        await state.set_state(MainMenuState.in_admin)
        return
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа")
        return
    
    users = db.get_all_users()
    sent_count = 0
    
    for user in users:
        try:
            await bot.send_message(user['user_id'], message.text)
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send broadcast to {user['user_id']}: {e}")
    
    await message.answer(f"✅ Рассылка отправлена {sent_count} пользователям")
    await message.answer(
        "Выберите действие:",
        reply_markup=get_admin_keyboard()
    )
    await state.set_state(MainMenuState.in_admin)

@dp.message(MainMenuState.in_admin, F.text == BACK_TEXT)
async def admin_back(message: types.Message, state: FSMContext):
    await message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard(message.from_user.id)
    )
    await state.set_state(MainMenuState.main_menu)

# ===== Background tasks =====

async def publish_ratings():
    """Publish ratings that are 24 hours old"""
    while True:
        try:
            db.publish_pending_ratings()
        except Exception as e:
            logger.error(f"Error in publish_ratings: {e}")
        
        await asyncio.sleep(3600)

async def main():
    """Main entry point"""
    logger.info(f"Starting {BOT_NAME} bot...")
    
    try:
        asyncio.create_task(publish_ratings())
        
        logger.info("Bot started successfully, polling for updates...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        raise
    finally:
        await bot.session.close()
        logger.info("Bot session closed")

if __name__ == "__main__":
    asyncio.run(main())
