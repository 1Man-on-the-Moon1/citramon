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
from i18n import t, set_user_lang, get_user_lang, get_back_text

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
    choosing_language = State()
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
    edit_name = State()
    edit_age = State()
    edit_city = State()
    edit_bio = State()
    edit_photo = State()
    edit_interests = State()
    date_choose_type = State()

# ===== Keyboards =====

def get_back_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=get_back_text(user_id))
    return builder.as_markup(resize_keyboard=True)

def get_language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.button(text="🇬🇧 English", callback_data="lang_en")
    builder.adjust(2)
    return builder.as_markup()

def get_gender_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=t(user_id, 'gender_male'))
    builder.button(text=t(user_id, 'gender_female'))
    builder.button(text=get_back_text(user_id))
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

def get_cities_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for city in BELARUS_CITIES:
        builder.button(text=city)
    builder.button(text=get_back_text(user_id))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_interests_keyboard(user_id: int, selected: list = None) -> InlineKeyboardMarkup:
    if selected is None:
        selected = []
    builder = InlineKeyboardBuilder()
    for interest in INTERESTS:
        checked = "✓" if interest in selected else ""
        builder.button(text=f"{checked} {interest}", callback_data=f"interest_{interest}")
    builder.adjust(2)
    if len(selected) > 0:
        builder.button(text=t(user_id, 'interests_done'), callback_data="interests_done")
    builder.button(text=get_back_text(user_id), callback_data="interests_back")
    builder.adjust(1)
    return builder.as_markup()

def get_main_menu_keyboard(user_id: int = None) -> ReplyKeyboardMarkup:
    uid = user_id or 0
    builder = ReplyKeyboardBuilder()
    builder.button(text=t(uid, 'menu_feed'))
    builder.button(text=t(uid, 'menu_matches'))
    builder.button(text=t(uid, 'menu_profile'))
    builder.button(text=t(uid, 'menu_photos'))
    builder.button(text=t(uid, 'menu_edit'))
    builder.button(text=t(uid, 'menu_support'))
    builder.button(text=t(uid, 'menu_delete'))
    builder.button(text=t(uid, 'menu_language'))
    if user_id and user_id == ADMIN_ID:
        builder.button(text=t(uid, 'menu_admin'))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="📋 Жалобы")
    builder.button(text="👥 Управление пользователями")
    builder.button(text="📊 Статистика")
    builder.button(text="📢 Рассылка")
    builder.button(text="◀️ Назад")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# Feed keyboard: embed profile_user_id in callback_data for state-independent operation
def get_feed_keyboard(user_id: int, profile_user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'feed_like'), callback_data=f"like_{profile_user_id}")
    builder.button(text=t(user_id, 'feed_skip'), callback_data=f"skip_{profile_user_id}")
    builder.button(text=t(user_id, 'match_reviews'), callback_data=f"reviews_{profile_user_id}")
    builder.button(text=t(user_id, 'feed_report'), callback_data=f"report_{profile_user_id}")
    builder.button(text=get_back_text(user_id), callback_data="feed_back")
    builder.adjust(2, 1, 1, 1)
    return builder.as_markup()

def get_match_keyboard(user_id: int, match_id: int, partner_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'match_chat'), callback_data=f"chat_{match_id}")
    builder.button(text=t(user_id, 'match_date'), callback_data=f"date_{match_id}")
    builder.button(text=t(user_id, 'match_reviews'), callback_data=f"reviews_{partner_id}")
    builder.adjust(2, 1)
    return builder.as_markup()

def get_date_type_keyboard(user_id: int, match_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'date_online'), callback_data=f"datetype_online_{match_id}")
    builder.button(text=t(user_id, 'date_offline'), callback_data=f"datetype_offline_{match_id}")
    builder.button(text=get_back_text(user_id), callback_data="datetype_back")
    builder.adjust(2, 1)
    return builder.as_markup()

def get_date_accept_keyboard(user_id: int, date_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'date_accept'), callback_data=f"accept_date_{date_id}")
    builder.button(text=t(user_id, 'date_decline'), callback_data=f"decline_date_{date_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_date_arrival_keyboard(user_id: int, date_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'date_arrived'), callback_data=f"arrived_date_{date_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_rating_keyboard(user_id: int, date_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for stars in range(1, 6):
        builder.button(text="⭐" * stars, callback_data=f"ratestars_{date_id}_{stars}")
    builder.adjust(1)
    return builder.as_markup()

def get_positive_tags_keyboard(date_id: int, stars: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for tag in POSITIVE_TAGS:
        builder.button(text=tag, callback_data=f"pos_tag_{date_id}_{stars}_{tag}")
    builder.button(text="✅ Готово / Done", callback_data=f"done_pos_tags_{date_id}_{stars}")
    builder.adjust(1)
    return builder.as_markup()

def get_negative_tags_keyboard(date_id: int, stars: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for tag in NEGATIVE_TAGS:
        builder.button(text=tag, callback_data=f"neg_tag_{date_id}_{stars}_{tag}")
    builder.button(text="✅ Готово / Done", callback_data=f"done_neg_tags_{date_id}_{stars}")
    builder.adjust(1)
    return builder.as_markup()

def get_complaint_types_keyboard(from_user_id: int, to_user_id: int) -> InlineKeyboardMarkup:
    """Build complaint keyboard. 'Не пришёл на встречу' only shown if there was a completed date."""
    builder = InlineKeyboardBuilder()
    has_date = db.has_completed_date_between(from_user_id, to_user_id)
    for complaint_type in COMPLAINT_TYPES:
        # Only show "Не пришёл на встречу" if there was a completed date
        if complaint_type == 'Не пришёл на встречу' and not has_date:
            continue
        builder.button(text=complaint_type, callback_data=f"complaint_{to_user_id}_{complaint_type}")
    builder.adjust(1)
    return builder.as_markup()

def get_reply_keyboard(user_id: int, match_id: int) -> InlineKeyboardMarkup:
    """Inline keyboard with Reply button under incoming messages."""
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'chat_reply'), callback_data=f"chat_{match_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_edit_profile_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'edit_name'), callback_data="edit_name")
    builder.button(text=t(user_id, 'edit_age'), callback_data="edit_age")
    builder.button(text=t(user_id, 'edit_city'), callback_data="edit_city")
    builder.button(text=t(user_id, 'edit_bio'), callback_data="edit_bio")
    builder.button(text=t(user_id, 'edit_photo'), callback_data="edit_photo")
    builder.button(text=t(user_id, 'edit_interests'), callback_data="edit_interests")
    builder.button(text=get_back_text(user_id), callback_data="edit_back")
    builder.adjust(2)
    return builder.as_markup()

# ===== Helper functions =====

def extract_gender_from_text(text: str) -> Optional[str]:
    if "Мужской" in text or "Male" in text:
        return "M"
    elif "Женский" in text or "Female" in text:
        return "F"
    return None

def get_opposite_gender(gender: str) -> str:
    return "F" if gender == "M" else "M"

def is_back(user_id: int, text: str) -> bool:
    """Check if the text is a back button in any language."""
    return text in ("◀️ Назад", "◀️ Back")

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

def is_menu_button(user_id: int, text: str) -> bool:
    """Check if text matches any main menu button."""
    menu_keys = ['menu_feed', 'menu_matches', 'menu_profile', 'menu_photos',
                 'menu_edit', 'menu_support', 'menu_delete', 'menu_admin', 'menu_language']
    for key in menu_keys:
        if text == t(user_id, key):
            return True
    return False

def build_profile_caption(profile: dict, user_id: int) -> str:
    """Build profile caption text for feed display."""
    interests = json.loads(profile['interests']) if profile['interests'] else []
    
    caption = f"👤 {profile['name']}, {profile['age']}\n"
    caption += f"📍 {profile['city']}\n"
    caption += f"⭐ {profile['rating']:.1f} ({profile['rating_count']} "
    caption += ("отзывов" if get_user_lang(user_id) == 'ru' else "reviews") + ")\n\n"
    caption += f"📝 {profile['bio']}\n\n"
    caption += f"💫 {', '.join(interests)}"
    
    return caption

# ===== Command handlers =====

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if user and user['registration_complete']:
        lang = user.get('language', 'ru')
        set_user_lang(user_id, lang)
        await message.answer(
            t(user_id, 'welcome_back'),
            reply_markup=get_main_menu_keyboard(user_id)
        )
        await state.set_state(MainMenuState.main_menu)
    else:
        await message.answer(
            "🌐 Выберите язык / Choose language:",
            reply_markup=get_language_keyboard()
        )
        await state.set_state(RegistrationState.choosing_language)

@dp.callback_query(RegistrationState.choosing_language)
async def choose_language_reg(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    if query.data == "lang_ru":
        set_user_lang(user_id, 'ru')
        await state.update_data(language='ru')
    elif query.data == "lang_en":
        set_user_lang(user_id, 'en')
        await state.update_data(language='en')
    else:
        return
    
    await query.message.answer(
        t(user_id, 'welcome_new'),
        reply_markup=get_back_keyboard(user_id)
    )
    await state.set_state(RegistrationState.waiting_for_name)

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer(t(message.from_user.id, 'admin_no_access'))
        return
    
    await message.answer(
        t(message.from_user.id, 'admin_title'),
        reply_markup=get_admin_keyboard()
    )
    await state.set_state(MainMenuState.in_admin)

# ===== Registration handlers with BACK buttons =====

@dp.message(RegistrationState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        await state.clear()
        user = db.get_user(user_id)
        if user and user['registration_complete']:
            await message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
            await state.set_state(MainMenuState.main_menu)
        else:
            await message.answer(t(user_id, 'reg_cancelled'), reply_markup=types.ReplyKeyboardRemove())
        return
    
    try:
        if not message.text or message.text.startswith('/'):
            await message.answer(t(user_id, 'name_no_commands'))
            return
        
        name = message.text.strip()
        if not name:
            await message.answer(t(user_id, 'name_empty'))
            return
        if len(name) > MAX_NAME_LENGTH:
            await message.answer(t(user_id, 'name_too_long', max=MAX_NAME_LENGTH))
            return
        if len(name) < 2:
            await message.answer(t(user_id, 'name_too_short'))
            return
        
        await state.update_data(name=name)
        await message.answer(
            t(user_id, 'choose_gender'),
            reply_markup=get_gender_keyboard(user_id)
        )
        await state.set_state(RegistrationState.waiting_for_gender)
    except Exception as e:
        logger.error(f"Error in process_name: {e}")
        await message.answer(t(user_id, 'name_error'))

@dp.message(RegistrationState.waiting_for_gender)
async def process_gender(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        await message.answer(
            t(user_id, 'enter_name'),
            reply_markup=get_back_keyboard(user_id)
        )
        await state.set_state(RegistrationState.waiting_for_name)
        return
    
    try:
        if not message.text or message.text.startswith('/'):
            await message.answer(t(user_id, 'gender_no_commands'))
            return
        
        gender = extract_gender_from_text(message.text)
        if not gender:
            await message.answer(t(user_id, 'gender_invalid'))
            return
    except Exception as e:
        logger.error(f"Error in process_gender: {e}")
        await message.answer(t(user_id, 'gender_error'))
        return
    
    await state.update_data(gender=gender)
    await message.answer(
        t(user_id, 'enter_age'),
        reply_markup=get_back_keyboard(user_id)
    )
    await state.set_state(RegistrationState.waiting_for_age)

@dp.message(RegistrationState.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        await message.answer(t(user_id, 'choose_gender'), reply_markup=get_gender_keyboard(user_id))
        await state.set_state(RegistrationState.waiting_for_gender)
        return
    
    try:
        if not message.text or message.text.startswith('/'):
            await message.answer(t(user_id, 'age_no_commands'))
            return
        
        age = int(message.text.strip())
        if age < MIN_AGE or age > MAX_AGE:
            await message.answer(t(user_id, 'age_invalid_range', min=MIN_AGE, max=MAX_AGE))
            return
    except ValueError:
        await message.answer(t(user_id, 'age_invalid'))
        return
    except Exception as e:
        logger.error(f"Error in process_age: {e}")
        await message.answer(t(user_id, 'age_error'))
        return
    
    await state.update_data(age=age)
    await message.answer(
        t(user_id, 'choose_city'),
        reply_markup=get_cities_keyboard(user_id)
    )
    await state.set_state(RegistrationState.waiting_for_city)

@dp.message(RegistrationState.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        await message.answer(t(user_id, 'enter_age'), reply_markup=get_back_keyboard(user_id))
        await state.set_state(RegistrationState.waiting_for_age)
        return
    
    city = message.text.strip()
    if city not in BELARUS_CITIES:
        await message.answer(t(user_id, 'city_invalid'))
        return
    
    await state.update_data(city=city)
    await message.answer(
        t(user_id, 'upload_photo'),
        reply_markup=get_back_keyboard(user_id)
    )
    await state.update_data(photos=[])
    await state.set_state(RegistrationState.waiting_for_photos)

@dp.message(RegistrationState.waiting_for_photos)
async def process_photos(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text and is_back(user_id, message.text):
        await message.answer(t(user_id, 'choose_city'), reply_markup=get_cities_keyboard(user_id))
        await state.set_state(RegistrationState.waiting_for_city)
        return
    
    data = await state.get_data()
    photos = data.get('photos', [])
    
    if message.photo:
        if len(photos) >= MAX_PHOTOS:
            await message.answer(t(user_id, 'photo_max', max=MAX_PHOTOS))
            return
        
        photo = message.photo[-1]
        photos.append(photo.file_id)
        await state.update_data(photos=photos)
        
        await message.answer(
            t(user_id, 'photo_uploaded'),
            reply_markup=get_back_keyboard(user_id)
        )
        await state.set_state(RegistrationState.waiting_for_bio)
        return
    
    await message.answer(t(user_id, 'photo_invalid'))

@dp.message(RegistrationState.waiting_for_bio)
async def process_bio(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        await state.update_data(photos=[])
        await message.answer(t(user_id, 'upload_photo'), reply_markup=get_back_keyboard(user_id))
        await state.set_state(RegistrationState.waiting_for_photos)
        return
    
    if not message.text:
        await message.answer(t(user_id, 'bio_text_only'))
        return
    
    bio = message.text.strip()
    if len(bio) > MAX_BIO_LENGTH:
        await message.answer(t(user_id, 'bio_too_long', max=MAX_BIO_LENGTH))
        return
    
    await state.update_data(bio=bio)
    await message.answer(
        t(user_id, 'choose_interests'),
        reply_markup=get_interests_keyboard(user_id)
    )
    await state.update_data(interests=[])
    await state.set_state(RegistrationState.waiting_for_interests)

@dp.callback_query(RegistrationState.waiting_for_interests)
async def process_interests(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    data = await state.get_data()
    interests = data.get('interests', [])
    
    if query.data == "interests_back":
        await query.message.answer(
            t(user_id, 'enter_bio'),
            reply_markup=get_back_keyboard(user_id)
        )
        await state.set_state(RegistrationState.waiting_for_bio)
        return
    
    if query.data == "interests_done":
        if len(interests) == 0:
            await query.answer(t(user_id, 'interests_min'))
            return
        
        user_data = await state.get_data()
        language = user_data.get('language', 'ru')
        
        db.create_user(
            user_id=user_id,
            name=user_data['name'],
            gender=user_data['gender'],
            age=user_data['age'],
            city=user_data['city'],
            language=language
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
            t(user_id, 'reg_complete'),
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
                await query.answer(t(user_id, 'interests_max', max=MAX_INTERESTS))
                return
            interests.append(interest)
        
        await state.update_data(interests=interests)
        await query.message.edit_reply_markup(
            reply_markup=get_interests_keyboard(user_id, interests)
        )

# ===== Main menu handlers =====

def menu_filter(key: str):
    """Create a filter that matches the menu button text for the user's language."""
    async def _filter(message: types.Message):
        user_id = message.from_user.id
        return message.text == t(user_id, key)
    return _filter

@dp.message(MainMenuState.main_menu, lambda m: m.text and any(
    m.text == t(m.from_user.id, k) for k in ['menu_feed']
))
async def show_feed(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if user['is_banned']:
        await message.answer(t(user_id, 'feed_banned'))
        return
    
    profile = get_next_profile_to_show(user_id)
    
    if not profile:
        await message.answer(t(user_id, 'feed_no_more'))
        return
    
    await state.update_data(current_profile_id=profile['user_id'])
    
    photos = db.get_user_photos(profile['user_id'])
    caption = build_profile_caption(profile, user_id)
    
    if photos:
        await message.answer_photo(
            photo=photos[0]['file_id'],
            caption=caption,
            reply_markup=get_feed_keyboard(user_id, profile['user_id'])
        )
    else:
        await message.answer(caption, reply_markup=get_feed_keyboard(user_id, profile['user_id']))
    
    await state.set_state(MainMenuState.browsing_feed)

# Feed: Back button (state-independent)
@dp.callback_query(F.data == "feed_back")
async def feed_back(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

# Like profile (state-independent - works even after new messages)
@dp.callback_query(F.data.regexp(r'^like_\d+$'))
async def like_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    to_user_id = int(query.data.split("_")[1])
    
    # Prevent double-like
    if db.has_liked(user_id, to_user_id):
        await query.answer("Already liked!")
        return
    
    db.add_like(user_id, to_user_id)
    
    if db.check_mutual_like(user_id, to_user_id):
        match_id = db.create_match(user_id, to_user_id)
        
        await bot.send_message(
            user_id,
            t(user_id, 'feed_mutual'),
            reply_markup=get_main_menu_keyboard(user_id)
        )
        
        from_user = db.get_user(user_id)
        await bot.send_message(
            to_user_id,
            t(to_user_id, 'feed_mutual_partner', name=from_user['name']),
            reply_markup=get_main_menu_keyboard(to_user_id)
        )
    else:
        await query.answer(t(user_id, 'feed_like_sent'))
    
    # Show next profile
    profile = get_next_profile_to_show(user_id)
    if profile:
        await state.update_data(current_profile_id=profile['user_id'])
        photos = db.get_user_photos(profile['user_id'])
        caption = build_profile_caption(profile, user_id)
        
        if photos:
            await query.message.answer_photo(
                photo=photos[0]['file_id'],
                caption=caption,
                reply_markup=get_feed_keyboard(user_id, profile['user_id'])
            )
        else:
            await query.message.answer(caption, reply_markup=get_feed_keyboard(user_id, profile['user_id']))
    else:
        await query.message.answer(t(user_id, 'feed_no_more'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu)

# Skip profile (state-independent)
@dp.callback_query(F.data.regexp(r'^skip_\d+$'))
async def skip_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    to_user_id = int(query.data.split("_")[1])
    
    db.add_skip(user_id, to_user_id)
    
    profile = get_next_profile_to_show(user_id)
    if profile:
        await state.update_data(current_profile_id=profile['user_id'])
        photos = db.get_user_photos(profile['user_id'])
        caption = build_profile_caption(profile, user_id)
        
        if photos:
            await query.message.answer_photo(
                photo=photos[0]['file_id'],
                caption=caption,
                reply_markup=get_feed_keyboard(user_id, profile['user_id'])
            )
        else:
            await query.message.answer(caption, reply_markup=get_feed_keyboard(user_id, profile['user_id']))
    else:
        await query.message.answer(t(user_id, 'feed_no_more'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu)

# Report profile (state-independent)
@dp.callback_query(F.data.regexp(r'^report_\d+$'))
async def report_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    to_user_id = int(query.data.split("_")[1])
    
    await state.update_data(report_user_id=to_user_id)
    await query.message.answer(
        t(user_id, 'complaint_choose'),
        reply_markup=get_complaint_types_keyboard(user_id, to_user_id)
    )

@dp.callback_query(F.data.startswith("complaint_"))
async def process_complaint(query: types.CallbackQuery, state: FSMContext):
    parts = query.data.split("_", 2)
    to_user_id = int(parts[1])
    complaint_type = parts[2]
    
    user_id = query.from_user.id
    db.add_complaint(user_id, to_user_id, complaint_type)
    
    await query.message.answer(
        t(user_id, 'complaint_sent'),
        reply_markup=get_main_menu_keyboard(user_id)
    )
    await state.set_state(MainMenuState.main_menu)

# ===== Reviews handler (works from ANY state - state-independent) =====

@dp.callback_query(F.data.startswith("reviews_"))
async def show_reviews(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    target_user_id = int(query.data.split("_")[1])
    target_user = db.get_user(target_user_id)
    
    if not target_user:
        await query.answer(t(user_id, 'error'))
        return
    
    summary = db.get_user_reviews_summary(target_user_id)
    
    if summary['count'] == 0:
        await query.message.answer(t(user_id, 'reviews_empty'))
        return
    
    text = t(user_id, 'reviews_title', name=target_user['name'])
    text += t(user_id, 'reviews_summary', rating=summary['avg'], count=summary['count'])
    
    # Show aggregated positive tags
    if summary['positive_tags']:
        tags_str = ', '.join([f"{tag} ({count})" for tag, count in summary['positive_tags']])
        text += t(user_id, 'reviews_positive_summary', tags=tags_str)
    
    # Show aggregated negative tags
    if summary['negative_tags']:
        tags_str = ', '.join([f"{tag} ({count})" for tag, count in summary['negative_tags']])
        text += t(user_id, 'reviews_negative_summary', tags=tags_str)
    
    text += "\n"
    
    # Show individual reviews (last 5)
    for r in summary['ratings'][:5]:
        reviewer_name = r.get('reviewer_name', '?')
        positive = ""
        negative = ""
        if r['positive_tags']:
            try:
                tags = json.loads(r['positive_tags'])
                if isinstance(tags, str):
                    tags = json.loads(tags)
                positive = "✅ " + ', '.join(tags) + " "
            except:
                pass
        if r['negative_tags']:
            try:
                tags = json.loads(r['negative_tags'])
                if isinstance(tags, str):
                    tags = json.loads(tags)
                negative = "❌ " + ', '.join(tags)
            except:
                pass
        text += f"{'⭐' * r['stars']} от {reviewer_name}: {positive}{negative}\n"
    
    await query.message.answer(text)

# ===== Matches =====

@dp.message(MainMenuState.main_menu, lambda m: m.text and any(
    m.text == t(m.from_user.id, k) for k in ['menu_matches']
))
async def show_matches(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    matches = db.get_user_matches(user_id)
    
    if not matches:
        await message.answer(t(user_id, 'no_matches'))
        return
    
    for match in matches:
        partner_id = match['user2_id'] if match['user1_id'] == user_id else match['user1_id']
        partner = db.get_user(partner_id)
        
        if not partner:
            continue
        
        text = f"👤 {partner['name']}, {partner['age']}\n"
        text += f"📍 {partner['city']}\n"
        text += f"⭐ {partner['rating']:.1f} ({partner['rating_count']} "
        text += ("отзывов" if get_user_lang(user_id) == 'ru' else "reviews") + ")\n\n"
        
        await message.answer(text, reply_markup=get_match_keyboard(user_id, match['match_id'], partner_id))

# ===== Chat with BACK button + Reply button on incoming messages =====

@dp.callback_query(F.data.startswith("chat_"))
async def enter_chat(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    match_id = int(query.data.split("_")[1])
    partner_id = db.get_match_partner(match_id, user_id)
    
    if not partner_id:
        await query.answer(t(user_id, 'error'))
        return
    
    messages = db.get_match_messages(match_id)
    
    text = t(user_id, 'chat_history') if messages else t(user_id, 'chat_empty')
    if messages:
        for msg in messages[-10:]:  # Show last 10 messages
            sender = db.get_user(msg['from_user_id'])
            sender_name = sender['name'] if sender else '?'
            text += f"{sender_name}: {msg['content']}\n"
    
    text += t(user_id, 'chat_send_prompt')
    
    await query.message.answer(text, reply_markup=get_back_keyboard(user_id))
    await state.update_data(current_match_id=match_id)
    await state.set_state(MainMenuState.in_chat)

@dp.message(MainMenuState.in_chat)
async def send_chat_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Back button — return to main menu
    if message.text and is_back(user_id, message.text):
        await message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu)
        return
    
    data = await state.get_data()
    match_id = data.get('current_match_id')
    
    if not match_id:
        await message.answer(t(user_id, 'error'))
        return
    
    to_user_id = db.get_match_partner(match_id, user_id)
    
    if not to_user_id:
        await message.answer(t(user_id, 'error'))
        return
    
    db.send_message(match_id, user_id, to_user_id, message.text)
    
    sender = db.get_user(user_id)
    # Send message to partner WITH Reply button
    await bot.send_message(
        to_user_id,
        t(to_user_id, 'chat_new_msg', name=sender['name'], text=message.text),
        reply_markup=get_reply_keyboard(to_user_id, match_id)
    )
    
    # Stay in chat — show confirmation with back button
    await message.answer(
        t(user_id, 'chat_msg_sent'),
        reply_markup=get_back_keyboard(user_id)
    )
    # Remain in chat state — user can keep sending messages

# ===== Date flow: Propose → Choose type → Notify partner (ONCE) =====

@dp.callback_query(F.data.regexp(r'^date_\d+$'))
async def propose_date(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    match_id = int(query.data.split("_")[1])
    
    # Check if there's already a pending/accepted date
    if db.has_pending_date(match_id):
        await query.answer(t(user_id, 'date_already_pending'), show_alert=True)
        return
    
    # Show type selection: Online / Offline
    await query.message.answer(
        t(user_id, 'date_choose_type'),
        reply_markup=get_date_type_keyboard(user_id, match_id)
    )

@dp.callback_query(F.data == "datetype_back")
async def datetype_back(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(F.data.startswith("datetype_online_"))
async def datetype_online(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    match_id = int(query.data.split("_")[2])
    
    # Double-check no pending date
    if db.has_pending_date(match_id):
        await query.answer(t(user_id, 'date_already_pending'), show_alert=True)
        return
    
    partner_id = db.get_match_partner(match_id, user_id)
    user = db.get_user(user_id)
    
    date_id = db.propose_date(match_id, user_id, date_type='online')
    
    await bot.send_message(
        partner_id,
        t(partner_id, 'date_proposed_online', name=user['name']),
        reply_markup=get_date_accept_keyboard(partner_id, date_id)
    )
    
    await query.message.answer(
        t(user_id, 'date_sent'),
        reply_markup=get_main_menu_keyboard(user_id)
    )
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(F.data.startswith("datetype_offline_"))
async def datetype_offline(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    match_id = int(query.data.split("_")[2])
    
    if db.has_pending_date(match_id):
        await query.answer(t(user_id, 'date_already_pending'), show_alert=True)
        return
    
    partner_id = db.get_match_partner(match_id, user_id)
    user = db.get_user(user_id)
    
    date_id = db.propose_date(match_id, user_id, date_type='offline')
    
    await bot.send_message(
        partner_id,
        t(partner_id, 'date_proposed_offline', name=user['name']),
        reply_markup=get_date_accept_keyboard(partner_id, date_id)
    )
    
    await query.message.answer(
        t(user_id, 'date_sent'),
        reply_markup=get_main_menu_keyboard(user_id)
    )
    await state.set_state(MainMenuState.main_menu)

# Accept / Decline / Arrival (state-independent)

@dp.callback_query(F.data.startswith("accept_date_"))
async def accept_date(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    date_id = int(query.data.split("_")[2])
    date_record = db.get_date(date_id)
    
    if not date_record:
        await query.answer(t(user_id, 'date_not_found'))
        return
    
    db.accept_date(date_id)
    
    proposer_id = date_record['proposer_id']
    date_type = date_record.get('date_type', 'offline')
    
    if date_type == 'online':
        # Online date: prompt to share video call link
        await query.message.answer(
            t(user_id, 'date_confirmed_online'),
            reply_markup=get_date_arrival_keyboard(user_id, date_id)
        )
        await bot.send_message(
            proposer_id,
            t(proposer_id, 'date_confirmed_online_proposer'),
            reply_markup=get_date_arrival_keyboard(proposer_id, date_id)
        )
    else:
        # Offline date: standard flow
        await query.message.answer(
            t(user_id, 'date_confirmed'),
            reply_markup=get_date_arrival_keyboard(user_id, date_id)
        )
        await bot.send_message(
            proposer_id,
            t(proposer_id, 'date_confirmed_proposer'),
            reply_markup=get_date_arrival_keyboard(proposer_id, date_id)
        )

@dp.callback_query(F.data.startswith("decline_date_"))
async def decline_date(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    date_id = int(query.data.split("_")[2])
    date_record = db.get_date(date_id)
    
    if not date_record:
        await query.answer(t(user_id, 'date_not_found'))
        return
    
    # Mark as declined
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE dates SET status = 'declined' WHERE date_id = ?", (date_id,))
    conn.commit()
    conn.close()
    
    proposer_id = date_record['proposer_id']
    
    await query.message.answer(t(user_id, 'date_declined_you'))
    await bot.send_message(proposer_id, t(proposer_id, 'date_declined_partner'))

@dp.callback_query(F.data.startswith("arrived_date_"))
async def arrived_at_date(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    date_id = int(query.data.split("_")[2])
    
    date_record = db.get_date(date_id)
    if not date_record:
        await query.answer(t(user_id, 'date_not_found'))
        return
    
    db.confirm_arrival(date_id, user_id)
    
    updated = db.get_date(date_id)
    match = db.get_match_by_id(date_record['match_id'])
    partner_id = match['user2_id'] if match['user1_id'] == user_id else match['user1_id']
    
    if updated['status'] == 'completed':
        # Both arrived! Show rating buttons
        rating_kb = get_rating_keyboard(user_id, date_id)
        partner_rating_kb = get_rating_keyboard(partner_id, date_id)
        
        await query.message.answer(
            t(user_id, 'date_both_arrived'),
            reply_markup=rating_kb
        )
        await bot.send_message(
            partner_id,
            t(partner_id, 'date_both_arrived'),
            reply_markup=partner_rating_kb
        )
    else:
        await query.answer(t(user_id, 'date_arrived_ok'))
        await bot.send_message(
            partner_id,
            t(partner_id, 'date_partner_arrived'),
            reply_markup=get_date_arrival_keyboard(partner_id, date_id)
        )

# ===== Rating (only after date completion) =====

@dp.callback_query(F.data.startswith("ratestars_"))
async def rate_stars_selected(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    parts = query.data.split("_")
    date_id = int(parts[1])
    stars = int(parts[2])
    
    await state.update_data(rating_date_id=date_id, rating_stars=stars)
    await query.message.answer(
        t(user_id, 'rate_positive'),
        reply_markup=get_positive_tags_keyboard(date_id, stars)
    )

@dp.callback_query(F.data.startswith("pos_tag_"))
async def select_positive_tag(query: types.CallbackQuery, state: FSMContext):
    parts = query.data.split("_", 3)
    date_id = int(parts[2])
    rest = parts[3]
    first_underscore = rest.index("_")
    stars = int(rest[:first_underscore])
    tag = rest[first_underscore+1:]
    
    data = await state.get_data()
    pos_tags = data.get('pos_tags', [])
    
    if tag not in pos_tags:
        pos_tags.append(tag)
    
    await state.update_data(pos_tags=pos_tags)
    await query.answer(f"✅ {tag}")

@dp.callback_query(F.data.startswith("done_pos_tags_"))
async def done_positive_tags(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    parts = query.data.split("_")
    date_id = int(parts[3])
    stars = int(parts[4])
    
    await query.message.answer(
        t(user_id, 'rate_negative'),
        reply_markup=get_negative_tags_keyboard(date_id, stars)
    )

@dp.callback_query(F.data.startswith("neg_tag_"))
async def select_negative_tag(query: types.CallbackQuery, state: FSMContext):
    parts = query.data.split("_", 3)
    date_id = int(parts[2])
    rest = parts[3]
    first_underscore = rest.index("_")
    stars = int(rest[:first_underscore])
    tag = rest[first_underscore+1:]
    
    data = await state.get_data()
    neg_tags = data.get('neg_tags', [])
    
    if tag not in neg_tags:
        neg_tags.append(tag)
    
    await state.update_data(neg_tags=neg_tags)
    await query.answer(f"✅ {tag}")

@dp.callback_query(F.data.startswith("done_neg_tags_"))
async def done_negative_tags(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    data = await state.get_data()
    parts = query.data.split("_")
    date_id = int(parts[3])
    stars = int(parts[4])
    
    pos_tags = data.get('pos_tags', [])
    neg_tags = data.get('neg_tags', [])
    
    # Get the date to find partner
    date_record = db.get_date(date_id)
    if date_record:
        match = db.get_match_by_id(date_record['match_id'])
        partner_id = match['user2_id'] if match['user1_id'] == user_id else match['user1_id']
        
        db.add_rating(
            date_id,
            user_id,
            partner_id,
            stars,
            json.dumps(pos_tags),
            json.dumps(neg_tags)
        )
    
    await query.message.answer(t(user_id, 'rate_saved'))
    await query.message.answer(
        t(user_id, 'action_choose'),
        reply_markup=get_main_menu_keyboard(user_id)
    )
    await state.update_data(pos_tags=[], neg_tags=[])
    await state.set_state(MainMenuState.main_menu)

# ===== Profile, Edit, Support, Delete =====

@dp.message(MainMenuState.main_menu, lambda m: m.text and any(
    m.text == t(m.from_user.id, k) for k in ['menu_profile']
))
async def show_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        await message.answer(t(user_id, 'profile_not_found'))
        return
    
    interests = json.loads(user['interests']) if user['interests'] else []
    
    text = t(user_id, 'profile_title')
    text += t(user_id, 'profile_name', name=user['name'])
    text += t(user_id, 'profile_age', age=user['age'])
    text += t(user_id, 'profile_city', city=user['city'])
    text += t(user_id, 'profile_rating', rating=user['rating'], count=user['rating_count'])
    text += t(user_id, 'profile_bio', bio=user['bio'])
    text += t(user_id, 'profile_interests', interests=', '.join(interests))
    
    await message.answer(text)

@dp.message(MainMenuState.main_menu, lambda m: m.text and any(
    m.text == t(m.from_user.id, k) for k in ['menu_photos']
))
async def view_photos(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    photos = db.get_user_photos(user_id)
    
    if not photos:
        await message.answer(t(user_id, 'no_photos'))
        return
    
    for photo in photos:
        await message.answer_photo(photo['file_id'])
    
    await message.answer(
        t(user_id, 'action_choose'),
        reply_markup=get_main_menu_keyboard(user_id)
    )
    await state.set_state(MainMenuState.main_menu)

# ===== Edit Profile =====

@dp.message(MainMenuState.main_menu, lambda m: m.text and any(
    m.text == t(m.from_user.id, k) for k in ['menu_edit']
))
async def edit_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    text = f"👤 {user['name']} | 🎂 {user['age']} | 📍 {user['city']}\n"
    text += f"📝 {user['bio']}\n\n"
    text += t(user_id, 'edit_title')
    
    await message.answer(text, reply_markup=get_edit_profile_keyboard(user_id))
    await state.set_state(MainMenuState.editing_profile)

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_back")
async def edit_back(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_name")
async def edit_name_start(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'edit_enter_name'), reply_markup=get_back_keyboard(user_id))
    await state.set_state(MainMenuState.edit_name)

@dp.message(MainMenuState.edit_name)
async def edit_name_process(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        user = db.get_user(user_id)
        text = t(user_id, 'edit_title')
        await message.answer(text, reply_markup=get_edit_profile_keyboard(user_id))
        await state.set_state(MainMenuState.editing_profile)
        return
    
    name = message.text.strip()
    if len(name) > MAX_NAME_LENGTH:
        await message.answer(t(user_id, 'name_too_long', max=MAX_NAME_LENGTH))
        return
    if len(name) < 2:
        await message.answer(t(user_id, 'name_too_short'))
        return
    
    db.update_user(user_id, name=name)
    await message.answer(t(user_id, 'edit_saved'))
    await message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_age")
async def edit_age_start(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'edit_enter_age'), reply_markup=get_back_keyboard(user_id))
    await state.set_state(MainMenuState.edit_age)

@dp.message(MainMenuState.edit_age)
async def edit_age_process(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        await message.answer(t(user_id, 'edit_title'), reply_markup=get_edit_profile_keyboard(user_id))
        await state.set_state(MainMenuState.editing_profile)
        return
    
    try:
        age = int(message.text.strip())
        if age < MIN_AGE or age > MAX_AGE:
            await message.answer(t(user_id, 'age_invalid_range', min=MIN_AGE, max=MAX_AGE))
            return
    except ValueError:
        await message.answer(t(user_id, 'age_invalid'))
        return
    
    db.update_user(user_id, age=age)
    await message.answer(t(user_id, 'edit_saved'))
    await message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_city")
async def edit_city_start(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'edit_choose_city'), reply_markup=get_cities_keyboard(user_id))
    await state.set_state(MainMenuState.edit_city)

@dp.message(MainMenuState.edit_city)
async def edit_city_process(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        await message.answer(t(user_id, 'edit_title'), reply_markup=get_edit_profile_keyboard(user_id))
        await state.set_state(MainMenuState.editing_profile)
        return
    
    city = message.text.strip()
    if city not in BELARUS_CITIES:
        await message.answer(t(user_id, 'city_invalid'))
        return
    
    db.update_user(user_id, city=city)
    await message.answer(t(user_id, 'edit_saved'))
    await message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_bio")
async def edit_bio_start(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'edit_enter_bio'), reply_markup=get_back_keyboard(user_id))
    await state.set_state(MainMenuState.edit_bio)

@dp.message(MainMenuState.edit_bio)
async def edit_bio_process(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        await message.answer(t(user_id, 'edit_title'), reply_markup=get_edit_profile_keyboard(user_id))
        await state.set_state(MainMenuState.editing_profile)
        return
    
    bio = message.text.strip()
    if len(bio) > MAX_BIO_LENGTH:
        await message.answer(t(user_id, 'bio_too_long', max=MAX_BIO_LENGTH))
        return
    
    db.update_user(user_id, bio=bio)
    await message.answer(t(user_id, 'edit_saved'))
    await message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_photo")
async def edit_photo_start(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'edit_upload_photo'), reply_markup=get_back_keyboard(user_id))
    await state.set_state(MainMenuState.edit_photo)

@dp.message(MainMenuState.edit_photo)
async def edit_photo_process(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text and is_back(user_id, message.text):
        await message.answer(t(user_id, 'edit_title'), reply_markup=get_edit_profile_keyboard(user_id))
        await state.set_state(MainMenuState.editing_profile)
        return
    
    if message.photo:
        photo = message.photo[-1]
        db.delete_user_photos(user_id)
        db.add_photo(user_id, photo.file_id)
        await message.answer(t(user_id, 'edit_saved'))
        await message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu)
        return
    
    await message.answer(t(user_id, 'photo_invalid'))

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_interests")
async def edit_interests_start(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    user = db.get_user(user_id)
    current = json.loads(user['interests']) if user['interests'] else []
    await state.update_data(edit_interests=current)
    await query.message.answer(
        t(user_id, 'edit_choose_interests'),
        reply_markup=get_interests_keyboard(user_id, current)
    )
    await state.set_state(MainMenuState.edit_interests)

@dp.callback_query(MainMenuState.edit_interests)
async def edit_interests_process(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    data = await state.get_data()
    interests = data.get('edit_interests', [])
    
    if query.data == "interests_back":
        await query.message.answer(t(user_id, 'edit_title'), reply_markup=get_edit_profile_keyboard(user_id))
        await state.set_state(MainMenuState.editing_profile)
        return
    
    if query.data == "interests_done":
        if len(interests) == 0:
            await query.answer(t(user_id, 'interests_min'))
            return
        db.update_user(user_id, interests=json.dumps(interests))
        await query.message.answer(t(user_id, 'edit_saved'))
        await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu)
        return
    
    if query.data.startswith("interest_"):
        interest = query.data.replace("interest_", "")
        if interest in interests:
            interests.remove(interest)
        else:
            if len(interests) >= MAX_INTERESTS:
                await query.answer(t(user_id, 'interests_max', max=MAX_INTERESTS))
                return
            interests.append(interest)
        
        await state.update_data(edit_interests=interests)
        await query.message.edit_reply_markup(
            reply_markup=get_interests_keyboard(user_id, interests)
        )

# Support
@dp.message(MainMenuState.main_menu, lambda m: m.text and any(
    m.text == t(m.from_user.id, k) for k in ['menu_support']
))
async def support(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer(
        t(user_id, 'support_text', admin_id=ADMIN_ID),
        parse_mode="Markdown"
    )

# Language change
@dp.message(MainMenuState.main_menu, lambda m: m.text and any(
    m.text == t(m.from_user.id, k) for k in ['menu_language']
))
async def change_language(message: types.Message, state: FSMContext):
    await message.answer(
        "🌐 Выберите язык / Choose language:",
        reply_markup=get_language_keyboard()
    )

@dp.callback_query(F.data.in_({"lang_ru", "lang_en"}))
async def language_selected(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = 'ru' if query.data == 'lang_ru' else 'en'
    set_user_lang(user_id, lang)
    db.update_user(user_id, language=lang)
    await query.message.answer(t(user_id, 'language_changed'))
    await query.message.answer(
        t(user_id, 'action_choose'),
        reply_markup=get_main_menu_keyboard(user_id)
    )
    await state.set_state(MainMenuState.main_menu)

# Delete profile
@dp.message(MainMenuState.main_menu, lambda m: m.text and any(
    m.text == t(m.from_user.id, k) for k in ['menu_delete']
))
async def delete_profile_prompt(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'delete_yes'), callback_data="confirm_delete_profile")
    builder.button(text=t(user_id, 'delete_no'), callback_data="cancel_delete_profile")
    builder.adjust(2)
    
    await message.answer(
        t(user_id, 'delete_confirm'),
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "confirm_delete_profile")
async def confirm_delete_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    success = db.delete_user(user_id)
    
    if success:
        await state.clear()
        await query.message.answer(
            t(user_id, 'delete_done'),
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await query.message.answer(t(user_id, 'delete_error'))

@dp.callback_query(F.data == "cancel_delete_profile")
async def cancel_delete_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(
        t(user_id, 'delete_cancelled'),
        reply_markup=get_main_menu_keyboard(user_id)
    )

# ===== Admin handlers =====

@dp.message(MainMenuState.main_menu, lambda m: m.text and any(
    m.text == t(m.from_user.id, k) for k in ['menu_admin']
))
async def admin_button(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer(t(message.from_user.id, 'admin_no_access'))
        return
    
    await message.answer(
        t(message.from_user.id, 'admin_title'),
        reply_markup=get_admin_keyboard()
    )
    await state.set_state(MainMenuState.in_admin)

@dp.message(MainMenuState.in_admin, F.text == "📋 Жалобы")
async def show_complaints(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    complaints = db.get_pending_complaints()
    
    if not complaints:
        await message.answer("✅ Нет новых жалоб")
        return
    
    for complaint in complaints:
        from_user = db.get_user(complaint['from_user_id'])
        to_user = db.get_user(complaint['to_user_id'])
        
        text = f"📋 Жалоба #{complaint['complaint_id']}\n\n"
        text += f"От: {from_user['name'] if from_user else 'Удалён'}\n"
        text += f"На: {to_user['name'] if to_user else 'Удалён'}\n"
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
        return
    
    parts = query.data.split("_")
    complaint_id = int(parts[2])
    status = parts[3]
    
    db.resolve_complaint(complaint_id, status)
    
    if status == "approved":
        complaint = db.get_complaint(complaint_id)
        db.ban_user(complaint['to_user_id'], shadow_ban=True)
        await query.answer("✅ Жалоба одобрена, теневой бан")
    else:
        await query.answer("✅ Жалоба отклонена")

@dp.message(MainMenuState.in_admin, F.text == "👥 Управление пользователями")
async def manage_users(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer("Введите ID пользователя для поиска:")
    await state.set_state(MainMenuState.admin_search_user)

@dp.message(MainMenuState.admin_search_user)
async def search_user(message: types.Message, state: FSMContext):
    if message.text == "◀️ Назад":
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
        text += f"⭐ Рейтинг: {user['rating']:.1f} ({user['rating_count']} оценок)\n"
        text += f"Язык: {user.get('language', 'ru')}\n"
        text += f"Заблокирован: {'Да' if user['is_banned'] else 'Нет'}\n"
        text += f"Теневой бан: {'Да' if user['is_shadow_banned'] else 'Нет'}\n"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🚫 Заблокировать", callback_data=f"admin_ban_{user_id}")
        builder.button(text="👻 Теневой бан", callback_data=f"admin_shadow_ban_{user_id}")
        builder.button(text="⭐ Обнулить рейтинг", callback_data=f"admin_reset_rating_{user_id}")
        builder.button(text="🔄 Обнулить анкету", callback_data=f"admin_full_reset_{user_id}")
        builder.button(text="🔓 Разблокировать", callback_data=f"admin_unban_{user_id}")
        builder.adjust(1)
        
        await message.answer(text, reply_markup=builder.as_markup())
        await state.set_state(MainMenuState.in_admin)
    except ValueError:
        await message.answer("❌ Введите корректный ID")

@dp.callback_query(F.data.startswith("admin_ban_"))
async def admin_ban_user(query: types.CallbackQuery):
    if query.from_user.id != ADMIN_ID:
        return
    
    user_id = int(query.data.split("_")[2])
    db.ban_user(user_id, shadow_ban=False)
    await query.answer("✅ Пользователь заблокирован")

@dp.callback_query(F.data.startswith("admin_shadow_ban_"))
async def admin_shadow_ban_user(query: types.CallbackQuery):
    if query.from_user.id != ADMIN_ID:
        return
    
    user_id = int(query.data.split("_")[3])
    db.ban_user(user_id, shadow_ban=True)
    await query.answer("✅ Теневой бан")

@dp.callback_query(F.data.startswith("admin_reset_rating_"))
async def admin_reset_rating(query: types.CallbackQuery):
    if query.from_user.id != ADMIN_ID:
        return
    
    user_id = int(query.data.split("_")[3])
    db.reset_user_rating(user_id)
    await query.answer("✅ Рейтинг обнулен")

@dp.callback_query(F.data.startswith("admin_full_reset_"))
async def admin_full_reset(query: types.CallbackQuery):
    """Full profile reset: delete all ratings/reviews and reset rating to default."""
    if query.from_user.id != ADMIN_ID:
        return
    
    user_id = int(query.data.split("_")[3])
    success = db.full_reset_user_profile(user_id)
    if success:
        await query.answer("✅ Анкета обнулена: рейтинг сброшен, все отзывы удалены")
    else:
        await query.answer("❌ Ошибка при обнулении анкеты")

@dp.callback_query(F.data.startswith("admin_unban_"))
async def admin_unban_user(query: types.CallbackQuery):
    """Unban user (remove regular and shadow ban)."""
    if query.from_user.id != ADMIN_ID:
        return
    
    user_id = int(query.data.split("_")[2])
    db.unban_user(user_id)
    await query.answer("✅ Пользователь разблокирован")

@dp.message(MainMenuState.in_admin, F.text == "📊 Статистика")
async def show_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
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
        return
    
    await message.answer("Введите текст рассылки (или ◀️ Назад для отмены):")
    await state.set_state(MainMenuState.admin_broadcast)

@dp.message(MainMenuState.admin_broadcast)
async def send_broadcast(message: types.Message, state: FSMContext):
    if message.text == "◀️ Назад":
        await message.answer("🔧 Админ-панель", reply_markup=get_admin_keyboard())
        await state.set_state(MainMenuState.in_admin)
        return
    
    if message.from_user.id != ADMIN_ID:
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

@dp.message(MainMenuState.in_admin, F.text == "◀️ Назад")
async def admin_back(message: types.Message, state: FSMContext):
    await message.answer(
        t(message.from_user.id, 'action_choose'),
        reply_markup=get_main_menu_keyboard(message.from_user.id)
    )
    await state.set_state(MainMenuState.main_menu)

# ===== Background tasks =====

async def publish_ratings():
    """Publish any legacy unpublished ratings"""
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
