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
from i18n import (
    t,
    set_user_lang,
    get_user_lang,
    get_back_text,
    translate_interest,
    translate_positive_tag,
    translate_negative_tag,
    translate_complaint_type,
)
from city_i18n import get_city_display_name, get_city_ru_from_display

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

init_db()
db = Database()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

ZODIAC_RU_BY_KEY = {
    "aries": "Овен",
    "taurus": "Телец",
    "gemini": "Близнецы",
    "cancer": "Рак",
    "leo": "Лев",
    "virgo": "Дева",
    "libra": "Весы",
    "scorpio": "Скорпион",
    "sagittarius": "Стрелец",
    "capricorn": "Козерог",
    "aquarius": "Водолей",
    "pisces": "Рыбы",
}

# строки = Женщина, столбцы = Мужчина
ZODIAC_COMPAT_MATRIX = {
    "Овен":      {"Овен":45,"Телец":73,"Близнецы":46,"Рак":47,"Лев":59,"Дева":48,"Весы":66,"Скорпион":59,"Стрелец":67,"Козерог":43,"Водолей":89,"Рыбы":43},
    "Телец":     {"Овен":85,"Телец":89,"Близнецы":72,"Рак":79,"Лев":54,"Дева":76,"Весы":67,"Скорпион":89,"Стрелец":79,"Козерог":79,"Водолей":63,"Рыбы":91},
    "Близнецы":  {"Овен":51,"Телец":63,"Близнецы":75,"Рак":57,"Лев":48,"Дева":56,"Весы":73,"Скорпион":60,"Стрелец":66,"Козерог":86,"Водолей":89,"Рыбы":38},
    "Рак":       {"Овен":48,"Телец":92,"Близнецы":67,"Рак":51,"Лев":95,"Дева":87,"Весы":74,"Скорпион":79,"Стрелец":55,"Козерог":56,"Водолей":71,"Рыбы":73},
    "Лев":       {"Овен":49,"Телец":53,"Близнецы":43,"Рак":94,"Лев":45,"Дева":68,"Весы":69,"Скорпион":76,"Стрелец":88,"Козерог":79,"Водолей":68,"Рыбы":43},
    "Дева":      {"Овен":39,"Телец":55,"Близнецы":54,"Рак":90,"Лев":76,"Дева":62,"Весы":62,"Скорпион":78,"Стрелец":78,"Козерог":58,"Водолей":38,"Рыбы":53},
    "Весы":      {"Овен":58,"Телец":56,"Близнецы":66,"Рак":74,"Лев":89,"Дева":61,"Весы":69,"Скорпион":64,"Стрелец":87,"Козерог":49,"Водолей":90,"Рыбы":55},
    "Скорпион":  {"Овен":53,"Телец":84,"Близнецы":58,"Рак":68,"Лев":92,"Дева":72,"Весы":54,"Скорпион":38,"Стрелец":96,"Козерог":54,"Водолей":52,"Рыбы":87},
    "Стрелец":   {"Овен":61,"Телец":49,"Близнецы":71,"Рак":61,"Лев":93,"Дева":53,"Весы":85,"Скорпион":95,"Стрелец":91,"Козерог":66,"Водолей":89,"Рыбы":88},
    "Козерог":   {"Овен":58,"Телец":95,"Близнецы":72,"Рак":63,"Лев":88,"Дева":49,"Весы":45,"Скорпион":64,"Стрелец":40,"Козерог":84,"Водолей":78,"Рыбы":91},
    "Водолей":   {"Овен":72,"Телец":56,"Близнецы":78,"Рак":61,"Лев":78,"Дева":38,"Весы":89,"Скорпион":50,"Стрелец":75,"Козерог":67,"Водолей":76,"Рыбы":71},
    "Рыбы":      {"Овен":45,"Телец":92,"Близнецы":39,"Рак":72,"Лев":52,"Дева":63,"Весы":68,"Скорпион":65,"Стрелец":82,"Козерог":69,"Водолей":46,"Рыбы":76},
}

def _get_zodiac_ru_and_validity(user: Optional[dict]) -> tuple[Optional[str], bool]:
    """
    Returns (ru_name_or_none, is_valid).
    - None + True  => zodiac is NULL/empty (not chosen)
    - None + False => zodiac has invalid value (corrupted data)
    - "Овен" + True => valid mapped value
    """
    if not user:
        return None, False
    key = user.get("zodiac")
    if not key:
        return None, True
    ru = ZODIAC_RU_BY_KEY.get(key)
    if not ru:
        return None, False
    return ru, True

def _get_zodiac_ru(user: Optional[dict]) -> Optional[str]:
    ru, ok = _get_zodiac_ru_and_validity(user)
    return ru if ok else None

def _zodiac_matrix_get(female_ru: str, male_ru: str) -> Optional[int]:
    row = ZODIAC_COMPAT_MATRIX.get(female_ru)
    if not row:
        return None
    val = row.get(male_ru)
    return int(val) if isinstance(val, (int, float)) else None

def calc_zodiac_compat_percent(viewer: dict, target: dict) -> Optional[int]:
    """
    Возвращает percent (int) или None, если данные битые.
    Правила: таблица [женщина][мужчина]; при м/ж и ж/м ориентация по полу,
    иначе усреднение двух направлений.
    """
    a_sign = _get_zodiac_ru(viewer)
    b_sign = _get_zodiac_ru(target)
    if not a_sign or not b_sign:
        return None

    a_gender = viewer.get("gender")
    b_gender = target.get("gender")

    if a_gender == "M" and b_gender == "F":
        p = _zodiac_matrix_get(b_sign, a_sign)  # target female row, viewer male col
        return p
    if a_gender == "F" and b_gender == "M":
        p = _zodiac_matrix_get(a_sign, b_sign)  # viewer female row, target male col
        return p

    p1 = _zodiac_matrix_get(a_sign, b_sign)
    p2 = _zodiac_matrix_get(b_sign, a_sign)
    if p1 is None or p2 is None:
        return None
    return int(round((p1 + p2) / 2))

class RegistrationState(StatesGroup):
    choosing_language = State()
    viewing_welcome = State()
    choosing_country = State()
    waiting_for_name = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_zodiac = State()
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
    admin_welcome_lang = State()
    admin_welcome_text = State()
    viewing_photos = State()
    editing_profile = State()
    edit_name = State()
    edit_age = State()
    edit_city = State()
    edit_country = State()
    edit_bio = State()
    edit_photo = State()
    edit_interests = State()
    edit_zodiac = State()
    viewing_likes = State()
    date_choose_type = State()

# ===== Keyboards =====

def get_back_keyboard(user_id):
    builder = ReplyKeyboardBuilder()
    builder.button(text=get_back_text(user_id))
    return builder.as_markup(resize_keyboard=True)

def get_bio_keyboard(user_id):
    builder = ReplyKeyboardBuilder()
    builder.button(text=t(user_id, 'bio_skip'))
    builder.button(text=get_back_text(user_id))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_zodiac_keyboard(user_id, for_edit=False):
    builder = InlineKeyboardBuilder()
    for sign in ZODIAC_SIGNS:
        builder.button(text=t(user_id, f'zodiac_{sign}'), callback_data=f"zodiac_{sign}")
    builder.adjust(3)
    if for_edit:
        builder.row(
            InlineKeyboardButton(text=t(user_id, 'zodiac_remove'), callback_data="zodiac_remove"),
            InlineKeyboardButton(text=get_back_text(user_id), callback_data="zodiac_edit_back")
        )
    else:
        builder.row(
            InlineKeyboardButton(text=t(user_id, 'zodiac_skip'), callback_data="zodiac_skip"),
            InlineKeyboardButton(text=get_back_text(user_id), callback_data="zodiac_reg_back")
        )
    return builder.as_markup()

def get_language_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇬🇧 English", callback_data="lang_en")
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.button(text="🇬🇪 ქართული", callback_data="lang_ka")
    builder.button(text="🇪🇸 Español", callback_data="lang_es")
    builder.button(text="🇩🇪 Deutsch", callback_data="lang_de")
    builder.adjust(3, 2)
    return builder.as_markup()

def get_country_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    lang = get_user_lang(user_id)
    for key, country in COUNTRIES.items():
        label = country.get(lang, country['ru'])
        builder.button(text=label, callback_data=f"country_{key}")
    builder.button(text=get_back_text(user_id), callback_data="country_back")
    builder.adjust(2)
    return builder.as_markup()

def get_gender_keyboard(user_id):
    builder = ReplyKeyboardBuilder()
    builder.button(text=t(user_id, 'gender_male'))
    builder.button(text=t(user_id, 'gender_female'))
    builder.button(text=get_back_text(user_id))
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

def get_cities_keyboard(user_id, country=None):
    builder = ReplyKeyboardBuilder()
    lang = get_user_lang(user_id)
    if country and country in COUNTRIES:
        cities = COUNTRIES[country]['cities']
    else:
        cities = ALL_CITIES
    for city in cities:
        builder.button(text=get_city_display_name(city, lang))
    builder.button(text=get_back_text(user_id))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_interests_keyboard(user_id, selected=None, for_reg=False):
    if selected is None: selected = []
    builder = InlineKeyboardBuilder()
    for interest in INTERESTS:
        checked = "✅ " if interest in selected else ""
        label = translate_interest(user_id, interest)
        builder.button(text=f"{checked}{label}", callback_data=f"interest_{interest}")
    builder.adjust(2)
    row = []
    if len(selected) > 0:
        row.append(InlineKeyboardButton(text=t(user_id, 'interests_done'), callback_data="interests_done"))
    if for_reg:
        row.append(InlineKeyboardButton(text=t(user_id, 'interests_skip'), callback_data="interests_skip"))
    row.append(InlineKeyboardButton(text=get_back_text(user_id), callback_data="interests_back"))
    builder.row(*row)
    return builder.as_markup()

def get_main_menu_keyboard(user_id=None):
    uid = user_id or 0
    builder = ReplyKeyboardBuilder()
    builder.button(text=t(uid, 'menu_feed'))
    builder.button(text=t(uid, 'menu_likes'))
    builder.button(text=t(uid, 'menu_matches'))
    builder.button(text=t(uid, 'menu_profile'))
    builder.button(text=t(uid, 'menu_my_exes'))
    builder.button(text=t(uid, 'menu_support'))
    builder.button(text=t(uid, 'menu_psychologist'))
    if user_id and user_id == ADMIN_ID:
        builder.button(text=t(uid, 'menu_admin'))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_admin_keyboard():
    builder = ReplyKeyboardBuilder()
    # Админ-панель отображается только админу, поэтому ADMIN_ID
    uid = ADMIN_ID
    builder.button(text=t(uid, 'admin_menu_complaints'))
    builder.button(text=t(uid, 'admin_menu_users'))
    builder.button(text=t(uid, 'admin_menu_stats'))
    builder.button(text=t(uid, 'admin_menu_broadcast'))
    builder.button(text=t(uid, 'admin_menu_welcome'))
    builder.button(text=t(uid, 'admin_menu_back'))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_feed_keyboard(user_id, profile_user_id):
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'feed_like'), callback_data=f"like_{profile_user_id}")
    builder.button(text=t(user_id, 'feed_skip'), callback_data=f"skip_{profile_user_id}")
    builder.button(text=t(user_id, "compat_zodiac_btn"), callback_data=f"compat_zodiac:{profile_user_id}")
    builder.button(text=t(user_id, 'match_reviews'), callback_data=f"reviews_{profile_user_id}")
    builder.button(text=t(user_id, 'feed_report'), callback_data=f"report_{profile_user_id}")
    builder.button(text=get_back_text(user_id), callback_data="feed_back")
    builder.adjust(2, 1, 1, 1, 1)
    return builder.as_markup()

def get_match_keyboard(user_id, match_id, partner_id):
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'match_chat'), callback_data=f"chat_{match_id}")
    builder.button(text=t(user_id, 'match_date'), callback_data=f"date_{match_id}")
    builder.button(text=t(user_id, 'match_view_profile'), callback_data=f"viewprofile_{partner_id}")
    builder.button(text=t(user_id, 'match_reviews'), callback_data=f"reviews_{partner_id}")
    builder.adjust(2, 2)
    return builder.as_markup()

def get_date_type_keyboard(user_id, match_id):
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'date_online'), callback_data=f"datetype_online_{match_id}")
    builder.button(text=t(user_id, 'date_offline'), callback_data=f"datetype_offline_{match_id}")
    builder.button(text=get_back_text(user_id), callback_data="datetype_back")
    builder.adjust(2, 1)
    return builder.as_markup()

def get_date_accept_keyboard(user_id, date_id):
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'date_accept'), callback_data=f"accept_date_{date_id}")
    builder.button(text=t(user_id, 'date_decline'), callback_data=f"decline_date_{date_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_date_arrival_keyboard(user_id, date_id):
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'date_arrived'), callback_data=f"arrived_date_{date_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_rating_keyboard(user_id, date_id):
    builder = InlineKeyboardBuilder()
    for stars in range(1, 6):
        builder.button(text="⭐" * stars, callback_data=f"ratestars_{date_id}_{stars}")
    builder.adjust(1)
    return builder.as_markup()

def get_positive_tags_keyboard(user_id, date_id, stars, selected=None):
    if selected is None: selected = []
    builder = InlineKeyboardBuilder()
    for tag in POSITIVE_TAGS:
        prefix = "✅ " if tag in selected else ""
        label = translate_positive_tag(user_id, tag)
        builder.button(text=f"{prefix}{label}", callback_data=f"pos_tag_{date_id}_{stars}_{tag}")
    builder.button(text="✅ Готово / Done", callback_data=f"done_pos_tags_{date_id}_{stars}")
    builder.adjust(1)
    return builder.as_markup()

def get_negative_tags_keyboard(user_id, date_id, stars, selected=None):
    if selected is None: selected = []
    builder = InlineKeyboardBuilder()
    for tag in NEGATIVE_TAGS:
        prefix = "✅ " if tag in selected else ""
        label = translate_negative_tag(user_id, tag)
        builder.button(text=f"{prefix}{label}", callback_data=f"neg_tag_{date_id}_{stars}_{tag}")
    builder.button(text="✅ Готово / Done", callback_data=f"done_neg_tags_{date_id}_{stars}")
    builder.adjust(1)
    return builder.as_markup()

def get_anonymity_keyboard(user_id, date_id, stars):
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'rate_anonymous'), callback_data=f"review_anon_{date_id}_{stars}")
    builder.button(text=t(user_id, 'rate_with_name'), callback_data=f"review_named_{date_id}_{stars}")
    builder.adjust(1)
    return builder.as_markup()

def get_complaint_types_keyboard(from_user_id, to_user_id, from_feed=False):
    builder = InlineKeyboardBuilder()
    has_date = db.has_completed_date_between(from_user_id, to_user_id)
    for complaint_type in COMPLAINT_TYPES:
        if complaint_type == 'Не пришёл на встречу' and (not has_date or from_feed):
            continue
        label = translate_complaint_type(from_user_id, complaint_type)
        builder.button(text=label, callback_data=f"complaint_{to_user_id}_{complaint_type}")
    builder.adjust(1)
    return builder.as_markup()

def get_reply_keyboard(user_id, match_id):
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'chat_reply'), callback_data=f"chat_{match_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_edit_profile_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'edit_name'), callback_data="edit_name")
    builder.button(text=t(user_id, 'edit_age'), callback_data="edit_age")
    builder.button(text=t(user_id, 'edit_country'), callback_data="edit_country")
    builder.button(text=t(user_id, 'edit_city'), callback_data="edit_city")
    builder.button(text=t(user_id, 'edit_bio'), callback_data="edit_bio")
    builder.button(text=t(user_id, 'edit_photo'), callback_data="edit_photo")
    builder.button(text=t(user_id, 'edit_interests'), callback_data="edit_interests")
    builder.button(text=t(user_id, 'edit_zodiac'), callback_data="edit_zodiac")
    builder.button(text=t(user_id, 'menu_photos'), callback_data="edit_view_photos")
    builder.button(text=t(user_id, 'menu_delete'), callback_data="edit_delete_profile")
    builder.button(text=get_back_text(user_id), callback_data="edit_back")
    builder.adjust(2)
    return builder.as_markup()

# ===== Helpers =====

def extract_gender_from_text(text):
    if "Мужской" in text or "Male" in text or "მამრობითი" in text or "Masculino" in text or "Männlich" in text: return "M"
    elif "Женский" in text or "Female" in text or "მდედრობითი" in text or "Femenino" in text or "Weiblich" in text: return "F"
    return None

def get_opposite_gender(gender): return "F" if gender == "M" else "M"

def is_back(user_id, text): return text in ("◀️ Назад", "◀️ Back", "◀️ უკან", "◀️ Atrás", "◀️ Zurück")

def is_bio_skip(user_id, text): return text in ("⏩ Пропустить", "⏩ Skip", "⏩ გამოტოვება", "⏩ Saltar", "⏩ Überspringen")

def get_country_key_from_text(text: str) -> Optional[str]:
    if not text:
        return None
    normalized = text.strip().lower()
    normalized_no_emoji = re.sub(r'^[^\w]+', '', normalized, flags=re.UNICODE).strip()

    for country_key, country_data in COUNTRIES.items():
        candidates = {country_key.lower()}
        for value in country_data.values():
            if isinstance(value, str):
                value_norm = value.strip().lower()
                candidates.add(value_norm)
                candidates.add(re.sub(r'^[^\w]+', '', value_norm, flags=re.UNICODE).strip())
        if normalized in candidates or normalized_no_emoji in candidates:
            return country_key
    return None

def get_next_profile_to_show(user_id):
    user = db.get_user(user_id)
    if not user: return None
    all_users = db.get_all_users()
    candidates = []
    for u in all_users:
        if u['user_id'] == user_id: continue
        user_obj = db.get_user(u['user_id'])
        if not user_obj: continue
        if user_obj['is_banned']: continue
        if user_obj['gender'] == user['gender']: continue
        if db.has_liked(user_id, u['user_id']) or db.has_skipped(user_id, u['user_id']): continue
        candidates.append(u)
    if not candidates: return None
    def score_profile(profile):
        score = 0
        if profile['rating'] >= 4.5: score += 1000
        if profile['city'] == user['city']: score += 500
        user_obj = db.get_user(profile['user_id'])
        created = datetime.fromisoformat(user_obj['created_at'])
        if datetime.now() - created < timedelta(hours=NEWBIE_BOOST_HOURS): score += 300
        if user_obj['last_seen']:
            last_seen = datetime.fromisoformat(user_obj['last_seen'])
            hours_ago = (datetime.now() - last_seen).total_seconds() / 3600
            if hours_ago < 24: score += 200
        score += profile['rating'] * 10
        return score
    candidates.sort(key=score_profile, reverse=True)
    return db.get_user(candidates[0]['user_id'])

def is_menu_button(user_id, text):
    menu_keys = ['menu_feed', 'menu_likes', 'menu_matches', 'menu_profile',
                 'menu_support', 'menu_admin', 'menu_my_exes', 'menu_psychologist']
    for key in menu_keys:
        if text == t(user_id, key): return True
    return False

def build_profile_caption(profile, user_id):
    interests = json.loads(profile['interests']) if profile['interests'] else []
    lang = get_user_lang(user_id)
    city_display = get_city_display_name(profile['city'], lang)
    caption = f"👤 {profile['name']}, {profile['age']}\n📍 {city_display}\n"
    if profile.get('zodiac'):
        caption += t(user_id, 'profile_zodiac', zodiac=t(user_id, f"zodiac_{profile['zodiac']}"))
    caption += f"⭐ {profile['rating']:.1f} ({profile['rating_count']} "
    caption += {"ru": "отзывов", "ka": "შეფასება"}.get(lang, "reviews") + ")\n\n"
    if profile['bio']: caption += f"📝 {profile['bio']}\n\n"
    translated_interests = [translate_interest(user_id, i) for i in interests]
    caption += f"💫 {', '.join(translated_interests)}"
    return caption

# ===== Commands =====

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    if user and user['is_banned']:
        set_user_lang(user_id, user.get('language', 'ru'))
        builder = ReplyKeyboardBuilder()
        builder.button(text=t(user_id, 'menu_support'))
        await message.answer(t(user_id, 'banned_message'), reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(MainMenuState.main_menu)
        return
    if user and user['registration_complete']:
        set_user_lang(user_id, user.get('language', 'ru'))
        await message.answer(t(user_id, 'welcome_back'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu)
    else:
        await message.answer("🌐 Выберите язык / Choose language / აირჩიეთ ენა:", reply_markup=get_language_keyboard())
        await state.set_state(RegistrationState.choosing_language)

@dp.callback_query(RegistrationState.choosing_language)
async def choose_language_reg(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    user_id = query.from_user.id
    lang_map = {"lang_ru": "ru", "lang_en": "en", "lang_ka": "ka", "lang_es": "es", "lang_de": "de"}
    lang = lang_map.get(query.data)
    if not lang: return
    set_user_lang(user_id, lang)
    await state.update_data(language=lang)
    # Show welcome message with ОЗНАКОМИЛСЯ button
    welcome_msg = db.get_setting(f'welcome_msg_{lang}', t(user_id, 'default_welcome'))
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'welcome_acknowledged'), callback_data="welcome_ack")
    builder.button(text=get_back_text(user_id), callback_data="welcome_back")
    builder.adjust(1)
    await query.message.answer(welcome_msg, reply_markup=builder.as_markup())
    await state.set_state(RegistrationState.viewing_welcome)

@dp.callback_query(RegistrationState.viewing_welcome, F.data == "welcome_back")
async def welcome_back_to_lang(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'choose_language'), reply_markup=get_language_keyboard())
    await state.set_state(RegistrationState.choosing_language)

@dp.callback_query(RegistrationState.viewing_welcome, F.data == "welcome_ack")
async def welcome_acknowledged(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    user_id = query.from_user.id
    await show_country_step(query.message, state, user_id)

async def show_welcome_step(message: types.Message, state: FSMContext, user_id: int):
    data = await state.get_data()
    lang = data.get('language') or get_user_lang(user_id) or 'ru'
    welcome_msg = db.get_setting(f'welcome_msg_{lang}', t(user_id, 'default_welcome'))
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'welcome_acknowledged'), callback_data="welcome_ack")
    builder.button(text=get_back_text(user_id), callback_data="welcome_back")
    builder.adjust(1)
    await message.answer(welcome_msg, reply_markup=builder.as_markup())
    await state.set_state(RegistrationState.viewing_welcome)

async def show_country_step(
    message: types.Message,
    state: FSMContext,
    user_id: int,
    clear_reply_keyboard: bool = False,
):
    if clear_reply_keyboard:
        await message.answer(t(user_id, 'choose_country'), reply_markup=types.ReplyKeyboardRemove())
    await message.answer(t(user_id, 'choose_country'), reply_markup=get_country_keyboard(user_id))
    await state.set_state(RegistrationState.choosing_country)

async def open_city_step(message: types.Message, state: FSMContext, user_id: int, country_key: str):
    await state.update_data(country=country_key)
    await message.answer(t(user_id, 'choose_city'), reply_markup=get_cities_keyboard(user_id, country_key))
    await state.set_state(RegistrationState.waiting_for_city)

@dp.callback_query(RegistrationState.choosing_country)
async def choose_country_reg(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    user_id = query.from_user.id

    if query.data == "country_back":
        await show_welcome_step(query.message, state, user_id)
        return

    if not query.data or not query.data.startswith("country_"):
        return

    country_key = query.data.replace("country_", "", 1)
    if country_key not in COUNTRIES:
        return

    await open_city_step(query.message, state, user_id, country_key)

@dp.message(RegistrationState.choosing_country)
async def choose_country_reg_from_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = (message.text or "").strip()

    if is_back(user_id, text):
        await show_welcome_step(message, state, user_id)
        return

    country_key = get_country_key_from_text(text)
    if not country_key:
        await show_country_step(message, state, user_id, clear_reply_keyboard=True)
        return

    await open_city_step(message, state, user_id, country_key)

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer(t(message.from_user.id, 'admin_no_access')); return
    await message.answer(t(message.from_user.id, 'admin_title'), reply_markup=get_admin_keyboard())
    await state.set_state(MainMenuState.in_admin)

# ===== Registration =====

@dp.message(RegistrationState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        # Back to city selection
        data = await state.get_data()
        country = data.get('country', 'belarus')
        await message.answer(t(user_id, 'choose_city'), reply_markup=get_cities_keyboard(user_id, country))
        await state.set_state(RegistrationState.waiting_for_city)
        return
    try:
        if not message.text or message.text.startswith('/'): await message.answer(t(user_id, 'name_no_commands')); return
        name = message.text.strip()
        if not name: await message.answer(t(user_id, 'name_empty')); return
        if len(name) > MAX_NAME_LENGTH: await message.answer(t(user_id, 'name_too_long', max=MAX_NAME_LENGTH)); return
        if len(name) < 2: await message.answer(t(user_id, 'name_too_short')); return
        await state.update_data(name=name)
        await message.answer(t(user_id, 'choose_gender'), reply_markup=get_gender_keyboard(user_id))
        await state.set_state(RegistrationState.waiting_for_gender)
    except Exception as e:
        logger.error(f"Error in process_name: {e}"); await message.answer(t(user_id, 'name_error'))

@dp.message(RegistrationState.waiting_for_gender)
async def process_gender(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        await message.answer(t(user_id, 'enter_name'), reply_markup=get_back_keyboard(user_id))
        await state.set_state(RegistrationState.waiting_for_name); return
    try:
        if not message.text or message.text.startswith('/'): await message.answer(t(user_id, 'gender_no_commands')); return
        gender = extract_gender_from_text(message.text)
        if not gender: await message.answer(t(user_id, 'gender_invalid')); return
    except Exception as e:
        logger.error(f"Error in process_gender: {e}"); await message.answer(t(user_id, 'gender_error')); return
    await state.update_data(gender=gender)
    await message.answer(t(user_id, 'enter_age'), reply_markup=get_back_keyboard(user_id))
    await state.set_state(RegistrationState.waiting_for_age)

@dp.message(RegistrationState.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        await message.answer(t(user_id, 'choose_gender'), reply_markup=get_gender_keyboard(user_id))
        await state.set_state(RegistrationState.waiting_for_gender); return
    try:
        if not message.text or message.text.startswith('/'): await message.answer(t(user_id, 'age_no_commands')); return
        age = int(message.text.strip())
        if age < MIN_AGE or age > MAX_AGE: await message.answer(t(user_id, 'age_invalid_range', min=MIN_AGE, max=MAX_AGE)); return
    except ValueError: await message.answer(t(user_id, 'age_invalid')); return
    except Exception as e: logger.error(f"Error in process_age: {e}"); await message.answer(t(user_id, 'age_error')); return
    await state.update_data(age=age)
    await message.answer(t(user_id, 'choose_zodiac'), reply_markup=get_zodiac_keyboard(user_id))
    await state.set_state(RegistrationState.waiting_for_zodiac)

@dp.callback_query(RegistrationState.waiting_for_zodiac)
async def process_zodiac(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.answer()
    if query.data == "zodiac_reg_back":
        await query.message.answer(t(user_id, 'enter_age'), reply_markup=get_back_keyboard(user_id))
        await state.set_state(RegistrationState.waiting_for_age)
        return
    if query.data == "zodiac_skip":
        await state.update_data(zodiac=None)
    else:
        sign = query.data.replace("zodiac_", "")
        if sign in ZODIAC_SIGNS:
            await state.update_data(zodiac=sign)
        else:
            return
    await state.update_data(photos=[])
    await query.message.answer(t(user_id, 'upload_photo'), reply_markup=get_back_keyboard(user_id))
    await state.set_state(RegistrationState.waiting_for_photos)

@dp.message(RegistrationState.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = (message.text or "").strip()

    if is_back(user_id, text):
        await show_country_step(message, state, user_id, clear_reply_keyboard=True)
        return

    if not text:
        await message.answer(t(user_id, 'city_invalid'))
        return

    try:
        data = await state.get_data()
        country = data.get('country')
        if country not in COUNTRIES:
            await show_country_step(message, state, user_id, clear_reply_keyboard=True)
            return

        valid_cities = COUNTRIES[country]['cities']
        lang = get_user_lang(user_id)
        city_ru = get_city_ru_from_display(text, lang, valid_cities)
        if not city_ru:
            await message.answer(t(user_id, 'city_invalid'))
            return

        await state.update_data(city=city_ru)
        await message.answer(t(user_id, 'welcome_new'), reply_markup=get_back_keyboard(user_id))
        await state.set_state(RegistrationState.waiting_for_name)
    except Exception as e:
        logger.error(f"Error in process_city: {e}")
        await message.answer(t(user_id, 'error'))

@dp.message(RegistrationState.waiting_for_photos)
async def process_photos(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text and is_back(user_id, message.text):
        # Back to zodiac step
        await message.answer(t(user_id, 'choose_zodiac'), reply_markup=get_zodiac_keyboard(user_id))
        await state.set_state(RegistrationState.waiting_for_zodiac); return
    data = await state.get_data(); photos = data.get('photos', [])
    if message.photo:
        if len(photos) >= MAX_PHOTOS: await message.answer(t(user_id, 'photo_max', max=MAX_PHOTOS)); return
        photo = message.photo[-1]; photos.append(photo.file_id); await state.update_data(photos=photos)
        await message.answer(t(user_id, 'photo_uploaded'), reply_markup=get_bio_keyboard(user_id))
        await state.set_state(RegistrationState.waiting_for_bio); return
    await message.answer(t(user_id, 'photo_invalid'))

@dp.message(RegistrationState.waiting_for_bio)
async def process_bio(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text and is_back(user_id, message.text):
        await state.update_data(photos=[])
        await message.answer(t(user_id, 'upload_photo'), reply_markup=get_back_keyboard(user_id))
        await state.set_state(RegistrationState.waiting_for_photos); return
    if message.text and is_bio_skip(user_id, message.text):
        await state.update_data(bio='')
        await message.answer(t(user_id, 'choose_interests'), reply_markup=get_interests_keyboard(user_id, for_reg=True))
        await state.update_data(interests=[])
        await state.set_state(RegistrationState.waiting_for_interests); return
    if not message.text: await message.answer(t(user_id, 'bio_text_only')); return
    bio = message.text.strip()
    if len(bio) > MAX_BIO_LENGTH: await message.answer(t(user_id, 'bio_too_long', max=MAX_BIO_LENGTH)); return
    await state.update_data(bio=bio)
    await message.answer(t(user_id, 'choose_interests'), reply_markup=get_interests_keyboard(user_id, for_reg=True))
    await state.update_data(interests=[])
    await state.set_state(RegistrationState.waiting_for_interests)

@dp.callback_query(RegistrationState.waiting_for_interests)
async def process_interests(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    data = await state.get_data(); interests = data.get('interests', [])
    if query.data == "interests_back":
        await query.message.answer(t(user_id, 'enter_bio'), reply_markup=get_bio_keyboard(user_id))
        await state.set_state(RegistrationState.waiting_for_bio); return
    async def _complete_reg(uid, ud, chosen):
        language = ud.get('language', 'ru')
        db.create_user(user_id=uid, name=ud['name'], gender=ud['gender'],
                       age=ud['age'], city=ud['city'], language=language)
        for photo_id in ud['photos']: db.add_photo(uid, photo_id)
        db.update_user(uid, bio=ud.get('bio', ''), interests=json.dumps(chosen),
                       zodiac=ud.get('zodiac'),
                       registration_complete=True, last_seen=datetime.now().isoformat())
        await query.message.answer(t(uid, 'reg_complete'), reply_markup=get_main_menu_keyboard(uid))
        await state.set_state(MainMenuState.main_menu)
    if query.data == "interests_skip":
        user_data = await state.get_data()
        await _complete_reg(user_id, user_data, []); return
    if query.data == "interests_done":
        if len(interests) == 0: await query.answer(t(user_id, 'interests_min')); return
        user_data = await state.get_data()
        await _complete_reg(user_id, user_data, interests); return
    if query.data.startswith("interest_"):
        interest = query.data.replace("interest_", "")
        if interest in interests: interests.remove(interest)
        else:
            if len(interests) >= MAX_INTERESTS: await query.answer(t(user_id, 'interests_max', max=MAX_INTERESTS)); return
            interests.append(interest)
        await state.update_data(interests=interests)
        await query.message.edit_reply_markup(reply_markup=get_interests_keyboard(user_id, interests, for_reg=True))

# ===== Main menu =====

@dp.message(MainMenuState.main_menu, lambda m: m.text and any(m.text == t(m.from_user.id, k) for k in ['menu_feed']))
async def show_feed(message: types.Message, state: FSMContext):
    user_id = message.from_user.id; user = db.get_user(user_id)
    if user['is_banned']: await message.answer(t(user_id, 'banned_message')); return
    profile = get_next_profile_to_show(user_id)
    if not profile: await message.answer(t(user_id, 'feed_no_more')); return
    await state.update_data(current_profile_id=profile['user_id'])
    photos = db.get_user_photos(profile['user_id']); caption = build_profile_caption(profile, user_id)
    if photos: await message.answer_photo(photo=photos[0]['file_id'], caption=caption, reply_markup=get_feed_keyboard(user_id, profile['user_id']))
    else: await message.answer(caption, reply_markup=get_feed_keyboard(user_id, profile['user_id']))
    await state.set_state(MainMenuState.browsing_feed)

@dp.message(MainMenuState.main_menu, lambda m: m.text and any(m.text == t(m.from_user.id, k) for k in ['menu_likes']))
async def show_incoming_likes(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    if user and user['is_banned']:
        await message.answer(t(user_id, 'banned_message')); return
    incoming = db.get_incoming_likes(user_id)
    if not incoming:
        await message.answer(t(user_id, 'likes_empty')); return
    # Filter out banned users and get valid profiles
    valid_likes = []
    for liker_id in incoming:
        liker = db.get_user(liker_id)
        if liker and not liker['is_banned']:
            valid_likes.append(liker_id)
    if not valid_likes:
        await message.answer(t(user_id, 'likes_empty')); return
    await state.update_data(incoming_likes=valid_likes, likes_index=0)
    await message.answer(t(user_id, 'likes_title', count=len(valid_likes)))
    # Show first profile
    liker = db.get_user(valid_likes[0])
    photos = db.get_user_photos(valid_likes[0]); caption = build_profile_caption(liker, user_id)
    keyboard = get_feed_keyboard(user_id, valid_likes[0])
    if photos: await message.answer_photo(photo=photos[0]['file_id'], caption=caption, reply_markup=keyboard)
    else: await message.answer(caption, reply_markup=keyboard)
    await state.set_state(MainMenuState.viewing_likes)

@dp.callback_query(MainMenuState.viewing_likes, F.data.regexp(r'^like_\d+$'))
async def like_back_from_likes(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; to_user_id = int(query.data.split("_")[1])
    if not db.has_liked(user_id, to_user_id):
        db.add_like(user_id, to_user_id)
    if db.check_mutual_like(user_id, to_user_id):
        match_id = db.create_match(user_id, to_user_id)
        await bot.send_message(user_id, t(user_id, 'feed_mutual'), reply_markup=get_main_menu_keyboard(user_id))
        from_user = db.get_user(user_id)
        await bot.send_message(to_user_id, t(to_user_id, 'feed_mutual_partner', name=from_user['name']), reply_markup=get_main_menu_keyboard(to_user_id))
    else:
        await query.answer(t(user_id, 'feed_like_sent'))
    # Show next incoming like
    await _show_next_incoming_like(query, state)

@dp.callback_query(MainMenuState.viewing_likes, F.data.regexp(r'^skip_\d+$'))
async def skip_from_likes(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; to_user_id = int(query.data.split("_")[1])
    db.add_skip(user_id, to_user_id)
    await _show_next_incoming_like(query, state)

@dp.callback_query(MainMenuState.viewing_likes, F.data == "feed_back")
async def likes_back(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

async def _show_next_incoming_like(query, state):
    user_id = query.from_user.id
    data = await state.get_data()
    likes = data.get('incoming_likes', []); idx = data.get('likes_index', 0) + 1
    await state.update_data(likes_index=idx)
    if idx >= len(likes):
        await query.message.answer(t(user_id, 'likes_no_more'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu); return
    liker = db.get_user(likes[idx])
    if not liker:
        await _show_next_incoming_like(query, state); return
    photos = db.get_user_photos(likes[idx]); caption = build_profile_caption(liker, user_id)
    keyboard = get_feed_keyboard(user_id, likes[idx])
    if photos: await query.message.answer_photo(photo=photos[0]['file_id'], caption=caption, reply_markup=keyboard)
    else: await query.message.answer(caption, reply_markup=keyboard)

@dp.message(MainMenuState.browsing_feed, lambda m: m.text and is_menu_button(m.from_user.id, m.text))
async def menu_from_feed(message: types.Message, state: FSMContext):
    user_id = message.from_user.id; await state.set_state(MainMenuState.main_menu)
    text = message.text
    if text == t(user_id, 'menu_matches'): await show_matches(message, state)
    elif text == t(user_id, 'menu_profile'): await show_profile(message, state)
    elif text == t(user_id, 'menu_support'): await support(message, state)
    elif text == t(user_id, 'menu_my_exes'): await my_exes(message, state)
    elif text == t(user_id, 'menu_psychologist'): await psychologist_advice(message, state)
    elif text == t(user_id, 'menu_admin'): await admin_button(message, state)
    elif text == t(user_id, 'menu_feed'): await show_feed(message, state)
    elif text == t(user_id, 'menu_likes'): await show_incoming_likes(message, state)
    else: await message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))

@dp.callback_query(F.data == "feed_back")
async def feed_back(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(F.data.regexp(r'^like_\d+$'))
async def like_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; to_user_id = int(query.data.split("_")[1])
    if db.has_liked(user_id, to_user_id): await query.answer("Already liked!"); return
    db.add_like(user_id, to_user_id)
    if db.check_mutual_like(user_id, to_user_id):
        match_id = db.create_match(user_id, to_user_id)
        await bot.send_message(user_id, t(user_id, 'feed_mutual'), reply_markup=get_main_menu_keyboard(user_id))
        from_user = db.get_user(user_id)
        await bot.send_message(to_user_id, t(to_user_id, 'feed_mutual_partner', name=from_user['name']), reply_markup=get_main_menu_keyboard(to_user_id))
    else:
        await query.answer(t(user_id, 'feed_like_sent'))
        # Send notification to the liked user
        try:
            await bot.send_message(to_user_id, t(to_user_id, 'like_notification'))
        except Exception as e:
            logger.error(f"Failed to notify user {to_user_id} about like: {e}")
    profile = get_next_profile_to_show(user_id)
    if profile:
        await state.update_data(current_profile_id=profile['user_id'])
        photos = db.get_user_photos(profile['user_id']); caption = build_profile_caption(profile, user_id)
        if photos: await query.message.answer_photo(photo=photos[0]['file_id'], caption=caption, reply_markup=get_feed_keyboard(user_id, profile['user_id']))
        else: await query.message.answer(caption, reply_markup=get_feed_keyboard(user_id, profile['user_id']))
    else:
        await query.message.answer(t(user_id, 'feed_no_more'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu)

@dp.callback_query(F.data.regexp(r'^skip_\d+$'))
async def skip_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; to_user_id = int(query.data.split("_")[1])
    db.add_skip(user_id, to_user_id)
    profile = get_next_profile_to_show(user_id)
    if profile:
        await state.update_data(current_profile_id=profile['user_id'])
        photos = db.get_user_photos(profile['user_id']); caption = build_profile_caption(profile, user_id)
        if photos: await query.message.answer_photo(photo=photos[0]['file_id'], caption=caption, reply_markup=get_feed_keyboard(user_id, profile['user_id']))
        else: await query.message.answer(caption, reply_markup=get_feed_keyboard(user_id, profile['user_id']))
    else:
        await query.message.answer(t(user_id, 'feed_no_more'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu)

@dp.callback_query(F.data.regexp(r'^report_\d+$'))
async def report_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; to_user_id = int(query.data.split("_")[1])
    await state.update_data(report_user_id=to_user_id)
    await query.message.answer(t(user_id, 'complaint_choose'), reply_markup=get_complaint_types_keyboard(user_id, to_user_id, from_feed=True))

@dp.callback_query(F.data.startswith("complaint_"))
async def process_complaint(query: types.CallbackQuery, state: FSMContext):
    parts = query.data.split("_", 2); to_user_id = int(parts[1]); complaint_type = parts[2]
    user_id = query.from_user.id; db.add_complaint(user_id, to_user_id, complaint_type)
    from_user = db.get_user(user_id); to_user = db.get_user(to_user_id)
    try:
        from_name = from_user['name'] if from_user else '?'; to_name = to_user['name'] if to_user else '?'
        admin_text = f"🚨 Новая жалоба!\n\nОт: <a href='tg://user?id={user_id}'>{from_name}</a> (ID: <code>{user_id}</code>)\nНа: <a href='tg://user?id={to_user_id}'>{to_name}</a> (ID: <code>{to_user_id}</code>)\nТип: {complaint_type}"
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
    except Exception as e: logger.error(f"Failed to notify admin about complaint: {e}")
    await query.message.answer(t(user_id, 'complaint_sent'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

# ===== Reviews =====

@dp.callback_query(F.data.startswith("reviews_"))
async def show_reviews(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; target_user_id = int(query.data.split("_")[1])
    target_user = db.get_user(target_user_id)
    if not target_user: await query.answer(t(user_id, 'error')); return
    summary = db.get_user_reviews_summary(target_user_id)
    if summary['count'] == 0: await query.message.answer(t(user_id, 'reviews_empty')); return
    text = t(user_id, 'reviews_title', name=target_user['name'])
    text += t(user_id, 'reviews_summary', rating=summary['avg'], count=summary['count'])
    if summary['positive_tags']:
        tags_str = ', '.join(
            [
                f"{translate_positive_tag(user_id, tag)} ({count})"
                for tag, count in summary['positive_tags']
            ]
        )
        text += t(user_id, 'reviews_positive_summary', tags=tags_str)
    if summary['negative_tags']:
        tags_str = ', '.join(
            [
                f"{translate_negative_tag(user_id, tag)} ({count})"
                for tag, count in summary['negative_tags']
            ]
        )
        text += t(user_id, 'reviews_negative_summary', tags=tags_str)
    text += "\n"
    for r in summary['ratings'][:5]:
        is_anon = r.get('is_anonymous', 0)
        reviewer_name = t(user_id, 'reviews_anonymous') if is_anon else r.get('reviewer_name', '?')
        positive = ""; negative = ""
        if r['positive_tags']:
            try:
                tags = json.loads(r['positive_tags'])
                if isinstance(tags, str): tags = json.loads(tags)
                positive = "✅ " + ', '.join(
                    translate_positive_tag(user_id, t) for t in tags
                ) + " "
            except: pass
        if r['negative_tags']:
            try:
                tags = json.loads(r['negative_tags'])
                if isinstance(tags, str): tags = json.loads(tags)
                negative = "❌ " + ', '.join(
                    translate_negative_tag(user_id, t) for t in tags
                )
            except: pass
        text += f"{'⭐' * r['stars']} от {reviewer_name}: {positive}{negative}\n"
    await query.message.answer(text)

@dp.callback_query(F.data.startswith("compat_zodiac:"))
async def compat_zodiac_clicked(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    viewer_id = query.from_user.id
    try:
        target_user_id = int(query.data.split(":", 1)[1])
    except Exception:
        logger.warning("compat_zodiac_clicked: bad callback data: %s", query.data)
        await query.message.answer(t(viewer_id, "compat_zodiac_calc_failed"))
        return

    viewer = db.get_user(viewer_id)
    target = db.get_user(target_user_id)
    if not target:
        logger.info("compat_zodiac_clicked: target missing viewer_id=%s target_id=%s", viewer_id, target_user_id)
        await query.message.answer(t(viewer_id, "compat_zodiac_calc_failed"))
        return

    target_sign, target_ok = _get_zodiac_ru_and_validity(target)
    viewer_sign, viewer_ok = _get_zodiac_ru_and_validity(viewer)

    has_target_sign = bool(target_sign)
    has_viewer_sign = bool(viewer_sign)

    logger.info(
        "compat_zodiac_clicked viewer_id=%s target_id=%s has_viewer_sign=%s has_target_sign=%s",
        viewer_id,
        target_user_id,
        has_viewer_sign,
        has_target_sign,
    )

    if not target_ok or not viewer_ok:
        logger.warning(
            "compat_zodiac_invalid_data viewer_id=%s target_id=%s viewer_zodiac=%s target_zodiac=%s",
            viewer_id,
            target_user_id,
            viewer.get("zodiac") if viewer else None,
            target.get("zodiac") if target else None,
        )
        await query.message.answer(t(viewer_id, "compat_zodiac_calc_failed"))
        return

    if not has_target_sign:
        await query.message.answer(t(viewer_id, "compat_zodiac_target_not_selected"))
        return
    if not has_viewer_sign:
        await query.message.answer(t(viewer_id, "compat_zodiac_viewer_not_selected"))
        return

    percent = calc_zodiac_compat_percent(viewer, target)
    if percent is None:
        logger.warning(
            "compat_zodiac_failed viewer_id=%s target_id=%s viewer_zodiac=%s target_zodiac=%s viewer_gender=%s target_gender=%s",
            viewer_id,
            target_user_id,
            viewer.get("zodiac") if viewer else None,
            target.get("zodiac") if target else None,
            viewer.get("gender") if viewer else None,
            target.get("gender") if target else None,
        )
        await query.message.answer(t(viewer_id, "compat_zodiac_calc_failed"))
        return

    logger.info("compat_zodiac_result viewer_id=%s target_id=%s percent=%s", viewer_id, target_user_id, percent)
    await query.message.answer(t(viewer_id, "compat_zodiac_result", percent=percent))

@dp.callback_query(F.data.regexp(r'^viewprofile_\d+$'))
async def view_partner_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; partner_id = int(query.data.split("_")[1])
    partner = db.get_user(partner_id)
    if not partner: await query.answer(t(user_id, 'profile_not_found')); return
    photos = db.get_user_photos(partner_id); caption = build_profile_caption(partner, user_id)
    if photos: await query.message.answer_photo(photo=photos[0]['file_id'], caption=caption)
    else: await query.message.answer(caption)

# ===== Matches =====

@dp.message(MainMenuState.main_menu, lambda m: m.text and any(m.text == t(m.from_user.id, k) for k in ['menu_matches']))
async def show_matches(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    if user and user['is_banned']:
        await message.answer(t(user_id, 'banned_message')); return
    matches = db.get_user_matches(user_id)
    if not matches: await message.answer(t(user_id, 'no_matches')); return
    lang = get_user_lang(user_id)
    for match in matches:
        partner_id = match['user2_id'] if match['user1_id'] == user_id else match['user1_id']
        partner = db.get_user(partner_id)
        if not partner: continue
        city_display = get_city_display_name(partner['city'], lang)
        text = f"👤 {partner['name']}, {partner['age']}\n📍 {city_display}\n"
        text += f"⭐ {partner['rating']:.1f} ({partner['rating_count']} "
        text += {"ru": "отзывов", "ka": "შეფასება"}.get(lang, "reviews") + ")\n\n"
        await message.answer(text, reply_markup=get_match_keyboard(user_id, match['match_id'], partner_id))

# ===== Chat =====

@dp.callback_query(F.data.startswith("chat_"))
async def enter_chat(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; match_id = int(query.data.split("_")[1])
    partner_id = db.get_match_partner(match_id, user_id)
    if not partner_id: await query.answer(t(user_id, 'error')); return
    await state.update_data(chat_match_id=match_id, chat_partner_id=partner_id)
    messages = db.get_match_messages(match_id)
    if messages:
        text = t(user_id, 'chat_history')
        for msg in messages[-10:]:
            sender = "🟢 " if msg['from_user_id'] == user_id else "🔵 "
            text += f"{sender}{msg['content']}\n"
    else: text = t(user_id, 'chat_empty')
    text += t(user_id, 'chat_send_prompt')
    await query.message.answer(text, reply_markup=get_back_keyboard(user_id))
    await state.set_state(MainMenuState.in_chat)

@dp.message(MainMenuState.in_chat)
async def send_chat_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        await message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu); return
    if is_menu_button(user_id, message.text):
        await state.set_state(MainMenuState.main_menu)
        text = message.text
        if text == t(user_id, 'menu_feed'): await show_feed(message, state)
        elif text == t(user_id, 'menu_matches'): await show_matches(message, state)
        elif text == t(user_id, 'menu_profile'): await show_profile(message, state)
        elif text == t(user_id, 'menu_support'): await support(message, state)
        elif text == t(user_id, 'menu_my_exes'): await my_exes(message, state)
        elif text == t(user_id, 'menu_psychologist'): await psychologist_advice(message, state)
        elif text == t(user_id, 'menu_likes'): await show_incoming_likes(message, state)
        return
    data = await state.get_data(); match_id = data.get('chat_match_id'); partner_id = data.get('chat_partner_id')
    if not match_id or not partner_id: await message.answer(t(user_id, 'error')); return
    db.send_message(match_id, user_id, partner_id, message.text)
    await message.answer(t(user_id, 'chat_msg_sent'))
    from_user = db.get_user(user_id)
    try:
        await bot.send_message(partner_id, t(partner_id, 'chat_new_msg', name=from_user['name'], text=message.text),
                               reply_markup=get_reply_keyboard(partner_id, match_id))
    except Exception as e: logger.error(f"Failed to notify partner: {e}")

# ===== Date flow =====

@dp.callback_query(F.data.regexp(r'^date_\d+$'))
async def start_date(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; match_id = int(query.data.split("_")[1])
    await query.message.answer(t(user_id, 'date_choose_type'), reply_markup=get_date_type_keyboard(user_id, match_id))

@dp.callback_query(F.data == "datetype_back")
async def datetype_back(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(F.data.startswith("datetype_online_"))
async def datetype_online(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; match_id = int(query.data.split("_")[2])
    if db.has_pending_date(match_id): await query.answer(t(user_id, 'date_already_pending'), show_alert=True); return
    partner_id = db.get_match_partner(match_id, user_id); user = db.get_user(user_id)
    date_id = db.propose_date(match_id, user_id, date_type='online')
    await bot.send_message(partner_id, t(partner_id, 'date_proposed_online', name=user['name']), reply_markup=get_date_accept_keyboard(partner_id, date_id))
    await query.message.answer(t(user_id, 'date_sent'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(F.data.startswith("datetype_offline_"))
async def datetype_offline(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; match_id = int(query.data.split("_")[2])
    if db.has_pending_date(match_id): await query.answer(t(user_id, 'date_already_pending'), show_alert=True); return
    partner_id = db.get_match_partner(match_id, user_id); user = db.get_user(user_id)
    date_id = db.propose_date(match_id, user_id, date_type='offline')
    await bot.send_message(partner_id, t(partner_id, 'date_proposed_offline', name=user['name']), reply_markup=get_date_accept_keyboard(partner_id, date_id))
    await query.message.answer(t(user_id, 'date_sent'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(F.data.startswith("accept_date_"))
async def accept_date(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; date_id = int(query.data.split("_")[2])
    date_record = db.get_date(date_id)
    if not date_record: await query.answer(t(user_id, 'date_not_found')); return
    db.accept_date(date_id)
    proposer_id = date_record['proposer_id']; date_type = date_record.get('date_type', 'offline')
    accepter = db.get_user(user_id); accepter_name = accepter['name'] if accepter else '?'
    if date_type == 'online':
        await query.message.answer(t(user_id, 'date_confirmed_online'), reply_markup=get_date_arrival_keyboard(user_id, date_id))
        await bot.send_message(proposer_id, t(proposer_id, 'date_confirmed_online_proposer', name=accepter_name), reply_markup=get_date_arrival_keyboard(proposer_id, date_id))
    else:
        await query.message.answer(t(user_id, 'date_confirmed'), reply_markup=get_date_arrival_keyboard(user_id, date_id))
        await bot.send_message(proposer_id, t(proposer_id, 'date_confirmed_proposer', name=accepter_name), reply_markup=get_date_arrival_keyboard(proposer_id, date_id))

@dp.callback_query(F.data.startswith("decline_date_"))
async def decline_date(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; date_id = int(query.data.split("_")[2])
    date_record = db.get_date(date_id)
    if not date_record: await query.answer(t(user_id, 'date_not_found')); return
    conn = db.get_connection(); cursor = conn.cursor()
    cursor.execute("UPDATE dates SET status = 'declined' WHERE date_id = ?", (date_id,)); conn.commit(); conn.close()
    proposer_id = date_record['proposer_id']
    await query.message.answer(t(user_id, 'date_declined_you'))
    await bot.send_message(proposer_id, t(proposer_id, 'date_declined_partner'))

@dp.callback_query(F.data.startswith("arrived_date_"))
async def arrived_at_date(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; date_id = int(query.data.split("_")[2])
    date_record = db.get_date(date_id)
    if not date_record: await query.answer(t(user_id, 'date_not_found')); return
    db.confirm_arrival(date_id, user_id)
    updated = db.get_date(date_id); match = db.get_match_by_id(date_record['match_id'])
    partner_id = match['user2_id'] if match['user1_id'] == user_id else match['user1_id']
    partner = db.get_user(partner_id); partner_name = partner['name'] if partner else '?'
    own_user = db.get_user(user_id); own_name = own_user['name'] if own_user else '?'
    if updated['status'] == 'completed':
        await query.message.answer(t(user_id, 'date_both_arrived', name=partner_name), reply_markup=get_rating_keyboard(user_id, date_id))
        await bot.send_message(partner_id, t(partner_id, 'date_both_arrived', name=own_name), reply_markup=get_rating_keyboard(partner_id, date_id))
    else:
        await query.answer(t(user_id, 'date_arrived_ok'))
        await bot.send_message(partner_id, t(partner_id, 'date_partner_arrived'), reply_markup=get_date_arrival_keyboard(partner_id, date_id))

# ===== Rating =====

@dp.callback_query(F.data.startswith("ratestars_"))
async def rate_stars_selected(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; parts = query.data.split("_"); date_id = int(parts[1]); stars = int(parts[2])
    await state.update_data(rating_date_id=date_id, rating_stars=stars, pos_tags=[], neg_tags=[])
    await query.message.answer(
        t(user_id, 'rate_positive'),
        reply_markup=get_positive_tags_keyboard(user_id, date_id, stars, []),
    )

@dp.callback_query(F.data.startswith("pos_tag_"))
async def select_positive_tag(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    parts = query.data.split("_", 3); date_id = int(parts[2]); rest = parts[3]
    first_underscore = rest.index("_"); stars = int(rest[:first_underscore]); tag = rest[first_underscore+1:]
    data = await state.get_data(); pos_tags = data.get('pos_tags', [])
    if tag in pos_tags: pos_tags.remove(tag)
    else: pos_tags.append(tag)
    await state.update_data(pos_tags=pos_tags)
    try:
        await query.message.edit_reply_markup(
            reply_markup=get_positive_tags_keyboard(user_id, date_id, stars, pos_tags)
        )
    except: pass
    await query.answer()

@dp.callback_query(F.data.startswith("done_pos_tags_"))
async def done_positive_tags(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; parts = query.data.split("_"); date_id = int(parts[3]); stars = int(parts[4])
    data = await state.get_data(); neg_tags = data.get('neg_tags', [])
    await query.message.answer(
        t(user_id, 'rate_negative'),
        reply_markup=get_negative_tags_keyboard(user_id, date_id, stars, neg_tags),
    )

@dp.callback_query(F.data.startswith("neg_tag_"))
async def select_negative_tag(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    parts = query.data.split("_", 3); date_id = int(parts[2]); rest = parts[3]
    first_underscore = rest.index("_"); stars = int(rest[:first_underscore]); tag = rest[first_underscore+1:]
    data = await state.get_data(); neg_tags = data.get('neg_tags', [])
    if tag in neg_tags: neg_tags.remove(tag)
    else: neg_tags.append(tag)
    await state.update_data(neg_tags=neg_tags)
    try:
        await query.message.edit_reply_markup(
            reply_markup=get_negative_tags_keyboard(user_id, date_id, stars, neg_tags)
        )
    except: pass
    await query.answer()

@dp.callback_query(F.data.startswith("done_neg_tags_"))
async def done_negative_tags(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; parts = query.data.split("_"); date_id = int(parts[3]); stars = int(parts[4])
    await query.message.answer(t(user_id, 'rate_choose_anonymity'), reply_markup=get_anonymity_keyboard(user_id, date_id, stars))

@dp.callback_query(F.data.startswith("review_anon_") | F.data.startswith("review_named_"))
async def save_review(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; is_anonymous = query.data.startswith("review_anon_")
    parts = query.data.split("_"); date_id = int(parts[2]); stars = int(parts[3])
    data = await state.get_data(); pos_tags = data.get('pos_tags', []); neg_tags = data.get('neg_tags', [])
    date_record = db.get_date(date_id)
    if date_record:
        match = db.get_match_by_id(date_record['match_id'])
        partner_id = match['user2_id'] if match['user1_id'] == user_id else match['user1_id']
        db.add_rating(date_id, user_id, partner_id, stars, json.dumps(pos_tags), json.dumps(neg_tags), is_anonymous=is_anonymous)
    await query.message.answer(t(user_id, 'rate_saved'))
    await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
    await state.update_data(pos_tags=[], neg_tags=[]); await state.set_state(MainMenuState.main_menu)

# ===== Profile, Edit, Support, Delete =====

@dp.message(MainMenuState.main_menu, lambda m: m.text and any(m.text == t(m.from_user.id, k) for k in ['menu_profile']))
async def show_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id; user = db.get_user(user_id)
    if not user: await message.answer(t(user_id, 'profile_not_found')); return
    if user['is_banned']:
        await message.answer(t(user_id, 'banned_message')); return
    interests = json.loads(user['interests']) if user['interests'] else []
    text = t(user_id, 'profile_title') + t(user_id, 'profile_name', name=user['name'])
    lang = get_user_lang(user_id)
    text += t(user_id, 'profile_age', age=user['age']) + t(user_id, 'profile_city', city=get_city_display_name(user['city'], lang))
    if user.get('zodiac'):
        text += t(user_id, 'profile_zodiac', zodiac=t(user_id, f"zodiac_{user['zodiac']}"))
    text += t(user_id, 'profile_rating', rating=user['rating'], count=user['rating_count'])
    if user['bio']: text += t(user_id, 'profile_bio', bio=user['bio'])
    translated_interests = [translate_interest(user_id, i) for i in interests]
    text += t(user_id, 'profile_interests', interests=', '.join(translated_interests))
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'menu_edit'), callback_data="profile_edit")
    builder.button(text=t(user_id, 'menu_photos'), callback_data="profile_view_photos")
    builder.button(text=t(user_id, 'profile_my_reviews'), callback_data="profile_my_reviews")
    builder.button(text=t(user_id, 'profile_change_lang'), callback_data="profile_change_lang")
    builder.adjust(2)
    await message.answer(text, reply_markup=builder.as_markup())

async def view_photos_internal(user_id, message):
    """Internal helper to view photos, callable from edit submenu"""
    photos = db.get_user_photos(user_id)
    if not photos: await message.answer(t(user_id, 'no_photos')); return
    for photo in photos: await message.answer_photo(photo['file_id'])

@dp.callback_query(F.data == "profile_edit")
async def profile_edit_callback(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    user = db.get_user(user_id)
    if not user: return
    lang = get_user_lang(user_id)
    text = f"👤 {user['name']} | 🎂 {user['age']} | 📍 {get_city_display_name(user['city'], lang)}\n"
    if user['bio']: text += f"📝 {user['bio']}\n\n"
    else: text += "\n"
    text += t(user_id, 'edit_title')
    await query.message.answer(text, reply_markup=get_edit_profile_keyboard(user_id))
    await state.set_state(MainMenuState.editing_profile)

@dp.callback_query(F.data == "profile_view_photos")
async def profile_view_photos_callback(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await view_photos_internal(user_id, query.message)

@dp.callback_query(F.data == "profile_my_reviews")
async def profile_my_reviews_callback(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.answer()
    summary = db.get_user_reviews_summary(user_id)
    if summary['count'] == 0:
        await query.message.answer(t(user_id, 'reviews_empty')); return
    text = t(user_id, 'profile_my_reviews') + "\n\n"
    text += t(user_id, 'reviews_summary', rating=summary['avg'], count=summary['count'])
    if summary['positive_tags']:
        tags_str = ', '.join([f"{translate_positive_tag(user_id, tag)} ({cnt})" for tag, cnt in summary['positive_tags']])
        text += t(user_id, 'reviews_positive_summary', tags=tags_str)
    if summary['negative_tags']:
        tags_str = ', '.join([f"{translate_negative_tag(user_id, tag)} ({cnt})" for tag, cnt in summary['negative_tags']])
        text += t(user_id, 'reviews_negative_summary', tags=tags_str)
    text += "\n"
    for r in summary['ratings'][:10]:
        is_anon = r.get('is_anonymous', 0)
        reviewer_name = t(user_id, 'reviews_anonymous') if is_anon else r.get('reviewer_name', '?')
        positive = ""; negative = ""
        if r['positive_tags']:
            try:
                tags = json.loads(r['positive_tags'])
                if isinstance(tags, str): tags = json.loads(tags)
                positive = "✅ " + ', '.join(translate_positive_tag(user_id, tg) for tg in tags) + " "
            except: pass
        if r['negative_tags']:
            try:
                tags = json.loads(r['negative_tags'])
                if isinstance(tags, str): tags = json.loads(tags)
                negative = "❌ " + ', '.join(translate_negative_tag(user_id, tg) for tg in tags) + " "
            except: pass
        text += t(user_id, 'reviews_item', stars=r['stars'], positive=positive, negative=negative)
        text += f"  — {reviewer_name}\n"
    await query.message.answer(text)

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_back")
async def edit_back(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_view_photos")
async def edit_view_photos(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await view_photos_internal(user_id, query.message)

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_delete_profile")
async def edit_delete_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'delete_yes'), callback_data="confirm_delete_profile")
    builder.button(text=t(user_id, 'delete_no'), callback_data="cancel_delete_profile"); builder.adjust(2)
    await query.message.answer(t(user_id, 'delete_confirm'), reply_markup=builder.as_markup())

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_name")
async def edit_name_start(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'edit_enter_name'), reply_markup=get_back_keyboard(user_id))
    await state.set_state(MainMenuState.edit_name)

@dp.message(MainMenuState.edit_name)
async def edit_name_process(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        await message.answer(t(user_id, 'edit_title'), reply_markup=get_edit_profile_keyboard(user_id))
        await state.set_state(MainMenuState.editing_profile); return
    name = message.text.strip()
    if len(name) > MAX_NAME_LENGTH: await message.answer(t(user_id, 'name_too_long', max=MAX_NAME_LENGTH)); return
    if len(name) < 2: await message.answer(t(user_id, 'name_too_short')); return
    db.update_user(user_id, name=name); await message.answer(t(user_id, 'edit_saved'))
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
        await state.set_state(MainMenuState.editing_profile); return
    try:
        age = int(message.text.strip())
        if age < MIN_AGE or age > MAX_AGE: await message.answer(t(user_id, 'age_invalid_range', min=MIN_AGE, max=MAX_AGE)); return
    except ValueError: await message.answer(t(user_id, 'age_invalid')); return
    db.update_user(user_id, age=age); await message.answer(t(user_id, 'edit_saved'))
    await message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_country")
async def edit_country_start(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'edit_choose_country'), reply_markup=get_country_keyboard(user_id))
    await state.set_state(MainMenuState.edit_country)

@dp.callback_query(MainMenuState.edit_country)
async def edit_country_process(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    if query.data == "country_back":
        await query.message.answer(t(user_id, 'edit_title'), reply_markup=get_edit_profile_keyboard(user_id))
        await state.set_state(MainMenuState.editing_profile)
        return
    if not query.data or not query.data.startswith("country_"):
        return
    country_key = query.data.replace("country_", "", 1)
    if country_key not in COUNTRIES:
        return
    await state.update_data(edit_country=country_key)
    await query.message.answer(t(user_id, 'edit_choose_city'), reply_markup=get_cities_keyboard(user_id, country_key))
    await state.set_state(MainMenuState.edit_city)

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_city")
async def edit_city_start(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    user = db.get_user(user_id)
    user_country = None
    if user and user['city']:
        for key, country in COUNTRIES.items():
            if user['city'] in country['cities']:
                user_country = key
                break
    await query.message.answer(t(user_id, 'edit_choose_city'), reply_markup=get_cities_keyboard(user_id, user_country))
    await state.set_state(MainMenuState.edit_city)

@dp.message(MainMenuState.edit_city)
async def edit_city_process(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if is_back(user_id, message.text):
        data = await state.get_data()
        if data.get('edit_country'):
            await state.update_data(edit_country=None)
            await message.answer(t(user_id, 'edit_choose_country'), reply_markup=get_country_keyboard(user_id))
            await state.set_state(MainMenuState.edit_country)
        else:
            await message.answer(t(user_id, 'edit_title'), reply_markup=get_edit_profile_keyboard(user_id))
            await state.set_state(MainMenuState.editing_profile)
        return
    city_text = message.text.strip()
    lang = get_user_lang(user_id)
    city_ru = None
    data = await state.get_data()
    edit_country = data.get('edit_country')
    if edit_country and edit_country in COUNTRIES:
        city_ru = get_city_ru_from_display(city_text, lang, COUNTRIES[edit_country]['cities'])
    else:
        for key, country in COUNTRIES.items():
            city_ru = get_city_ru_from_display(city_text, lang, country['cities'])
            if city_ru:
                break
    if not city_ru:
        await message.answer(t(user_id, 'city_invalid')); return
    db.update_user(user_id, city=city_ru); await message.answer(t(user_id, 'edit_saved'))
    await state.update_data(edit_country=None)
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
        await state.set_state(MainMenuState.editing_profile); return
    bio = message.text.strip()
    if len(bio) > MAX_BIO_LENGTH: await message.answer(t(user_id, 'bio_too_long', max=MAX_BIO_LENGTH)); return
    db.update_user(user_id, bio=bio); await message.answer(t(user_id, 'edit_saved'))
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
        await state.set_state(MainMenuState.editing_profile); return
    if message.photo:
        photo = message.photo[-1]; db.delete_user_photos(user_id); db.add_photo(user_id, photo.file_id)
        await message.answer(t(user_id, 'edit_saved'))
        await message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu); return
    await message.answer(t(user_id, 'photo_invalid'))

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_interests")
async def edit_interests_start(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; user = db.get_user(user_id)
    current_interests = json.loads(user['interests']) if user['interests'] else []
    await state.update_data(interests=current_interests, editing_interests=True)
    await query.message.answer(t(user_id, 'edit_choose_interests'), reply_markup=get_interests_keyboard(user_id, current_interests))
    await state.set_state(MainMenuState.edit_interests)

@dp.callback_query(MainMenuState.edit_interests)
async def process_edit_interests(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    data = await state.get_data(); interests = data.get('interests', [])
    if query.data == "interests_back":
        await query.message.answer(t(user_id, 'edit_title'), reply_markup=get_edit_profile_keyboard(user_id))
        await state.set_state(MainMenuState.editing_profile); return
    if query.data == "interests_done":
        if len(interests) == 0: await query.answer(t(user_id, 'interests_min')); return
        db.update_user(user_id, interests=json.dumps(interests))
        await query.message.answer(t(user_id, 'edit_saved'))
        await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu); return
    if query.data.startswith("interest_"):
        interest = query.data.replace("interest_", "")
        if interest in interests: interests.remove(interest)
        else:
            if len(interests) >= MAX_INTERESTS: await query.answer(t(user_id, 'interests_max', max=MAX_INTERESTS)); return
            interests.append(interest)
        await state.update_data(interests=interests)
        await query.message.edit_reply_markup(reply_markup=get_interests_keyboard(user_id, interests))

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_zodiac")
async def edit_zodiac_start(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    user = db.get_user(user_id)
    zodiac = user.get('zodiac') if user else None
    prompt = t(user_id, 'edit_choose_zodiac')
    if zodiac:
        prompt += f"\n{t(user_id, 'profile_zodiac', zodiac=t(user_id, f'zodiac_{zodiac}'))}"
    await query.message.answer(prompt, reply_markup=get_zodiac_keyboard(user_id, for_edit=True))
    await state.set_state(MainMenuState.edit_zodiac)

@dp.callback_query(MainMenuState.edit_zodiac)
async def process_edit_zodiac(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.answer()
    if query.data == "zodiac_edit_back":
        await query.message.answer(t(user_id, 'edit_title'), reply_markup=get_edit_profile_keyboard(user_id))
        await state.set_state(MainMenuState.editing_profile)
        return
    if query.data == "zodiac_remove":
        db.update_user(user_id, zodiac=None)
        await query.message.answer(t(user_id, 'zodiac_removed'))
        await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu)
        return
    sign = query.data.replace("zodiac_", "")
    if sign in ZODIAC_SIGNS:
        db.update_user(user_id, zodiac=sign)
        await query.message.answer(t(user_id, 'edit_saved'))
        await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu)

@dp.message(MainMenuState.main_menu, lambda m: m.text and any(m.text == t(m.from_user.id, k) for k in ['menu_support']))
async def support(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer(t(user_id, 'support_text', admin_id=ADMIN_ID), parse_mode="Markdown")

@dp.message(MainMenuState.main_menu, lambda m: m.text and any(m.text == t(m.from_user.id, k) for k in ['menu_my_exes']))
async def my_exes(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer(t(user_id, 'msg_in_development'))

@dp.message(MainMenuState.main_menu, lambda m: m.text and any(m.text == t(m.from_user.id, k) for k in ['menu_psychologist']))
async def psychologist_advice(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer(t(user_id, 'msg_in_development'))

@dp.callback_query(F.data == "profile_change_lang")
async def profile_change_language(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.answer()
    await query.message.answer(t(user_id, 'choose_language'), reply_markup=get_language_keyboard())

@dp.callback_query(F.data.in_({"lang_ru", "lang_en", "lang_ka", "lang_es", "lang_de"}))
async def language_selected(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = {"lang_ru": "ru", "lang_en": "en", "lang_ka": "ka", "lang_es": "es", "lang_de": "de"}.get(query.data, "ru")
    set_user_lang(user_id, lang); db.update_user(user_id, language=lang)
    await query.message.answer(t(user_id, 'language_changed'))
    await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
    await state.set_state(MainMenuState.main_menu)

@dp.callback_query(F.data == "confirm_delete_profile")
async def confirm_delete_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id; success = db.delete_user(user_id)
    if success: await state.clear(); await query.message.answer(t(user_id, 'delete_done'), reply_markup=types.ReplyKeyboardRemove())
    else: await query.message.answer(t(user_id, 'delete_error'))

@dp.callback_query(F.data == "cancel_delete_profile")
async def cancel_delete_profile(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'delete_cancelled'), reply_markup=get_main_menu_keyboard(user_id))

# ===== Admin =====

@dp.message(MainMenuState.main_menu, lambda m: m.text and any(m.text == t(m.from_user.id, k) for k in ['menu_admin']))
async def admin_button(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: await message.answer(t(message.from_user.id, 'admin_no_access')); return
    await message.answer(t(message.from_user.id, 'admin_title'), reply_markup=get_admin_keyboard())
    await state.set_state(MainMenuState.in_admin)

@dp.message(MainMenuState.in_admin, lambda m: m.text == t(m.from_user.id, 'admin_menu_complaints'))
async def show_complaints(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    complaints = db.get_pending_complaints()
    if not complaints:
        await message.answer(t(message.from_user.id, 'admin_no_complaints'))
        return
    for complaint in complaints:
        from_user = db.get_user(complaint['from_user_id']); to_user = db.get_user(complaint['to_user_id'])
        from_name = from_user['name'] if from_user else 'Удалён'; to_name = to_user['name'] if to_user else 'Удалён'
        text = f"📋 Жалоба #{complaint['complaint_id']}\n\nОт: <a href='tg://user?id={complaint['from_user_id']}'>{from_name}</a> (ID: <code>{complaint['from_user_id']}</code>)\nНа: <a href='tg://user?id={complaint['to_user_id']}'>{to_name}</a> (ID: <code>{complaint['to_user_id']}</code>)\nТип: {complaint['complaint_type']}\nОписание: {complaint['description']}\n"
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Одобрить", callback_data=f"resolve_complaint_{complaint['complaint_id']}_approved")
        builder.button(text="❌ Отклонить", callback_data=f"resolve_complaint_{complaint['complaint_id']}_rejected"); builder.adjust(2)
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("resolve_complaint_"))
async def resolve_complaint(query: types.CallbackQuery):
    if query.from_user.id != ADMIN_ID: return
    parts = query.data.split("_"); complaint_id = int(parts[2]); status = parts[3]
    db.resolve_complaint(complaint_id, status)
    if status == "approved":
        complaint = db.get_complaint(complaint_id); db.ban_user(complaint['to_user_id'])
        try:
            await bot.send_message(complaint['to_user_id'], t(complaint['to_user_id'], 'banned_message'))
        except: pass
        await query.answer("✅ Жалоба одобрена, пользователь заблокирован")
    else: await query.answer("✅ Жалоба отклонена")

@dp.message(MainMenuState.in_admin, lambda m: m.text == t(m.from_user.id, 'admin_menu_users'))
async def manage_users(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await message.answer(t(message.from_user.id, 'admin_users_prompt'), reply_markup=get_back_keyboard(message.from_user.id))
    await state.set_state(MainMenuState.admin_search_user)

@dp.message(MainMenuState.admin_search_user)
async def search_user(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    if is_back(uid, message.text):
        await message.answer(t(uid, 'admin_title'), reply_markup=get_admin_keyboard())
        await state.set_state(MainMenuState.in_admin); return
    try:
        user_id = int(message.text.strip()); user = db.get_user(user_id)
        if not user: await message.answer(t(uid, 'error')); return
        banned_str = {'ru': 'Да', 'en': 'Yes', 'ka': 'დიახ', 'es': 'Sí', 'de': 'Ja'}.get(get_user_lang(uid), 'Yes') if user['is_banned'] else {'ru': 'Нет', 'en': 'No', 'ka': 'არა', 'es': 'No', 'de': 'Nein'}.get(get_user_lang(uid), 'No')
        text = f"👤 {user['name']}\nID: <code>{user['user_id']}</code>\n🎂 {user['age']} | 📍 {user['city']}\n⭐ {user['rating']:.1f} ({user['rating_count']})\n🌐 {user.get('language', 'ru')}\n🚫 {banned_str}\n"
        builder = InlineKeyboardBuilder()
        builder.button(text="🚫 Ban", callback_data=f"admin_ban_{user_id}")
        builder.button(text="🔓 Unban", callback_data=f"admin_unban_{user_id}")
        builder.button(text=t(uid, 'admin_reset_rating'), callback_data=f"admin_reset_rating_{user_id}")
        builder.button(text="🔄 Reset profile", callback_data=f"admin_full_reset_{user_id}")
        builder.adjust(2)
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
        await state.set_state(MainMenuState.in_admin)
    except ValueError: await message.answer(t(uid, 'error'))

@dp.callback_query(F.data.startswith("admin_ban_"))
async def admin_ban_user(query: types.CallbackQuery):
    if query.from_user.id != ADMIN_ID: return
    user_id = int(query.data.split("_")[2]); db.ban_user(user_id)
    try:
        await bot.send_message(user_id, t(user_id, 'banned_message'))
    except: pass
    await query.answer("✅ User banned")

@dp.callback_query(F.data.startswith("admin_reset_rating_"))
async def admin_reset_rating(query: types.CallbackQuery):
    if query.from_user.id != ADMIN_ID: return
    user_id = int(query.data.split("_")[3]); db.reset_user_rating(user_id)
    await query.answer("✅ Rating reset")

@dp.callback_query(F.data.startswith("admin_full_reset_"))
async def admin_full_reset(query: types.CallbackQuery):
    if query.from_user.id != ADMIN_ID: return
    user_id = int(query.data.split("_")[3])
    if db.full_reset_user_profile(user_id): await query.answer("✅ Profile reset")
    else: await query.answer("❌ Error")

@dp.callback_query(F.data.startswith("admin_unban_"))
async def admin_unban_user(query: types.CallbackQuery):
    if query.from_user.id != ADMIN_ID: return
    user_id = int(query.data.split("_")[2]); db.unban_user(user_id)
    await query.answer("✅ User unbanned")

@dp.message(MainMenuState.in_admin, lambda m: m.text == t(m.from_user.id, 'admin_menu_stats'))
async def show_stats(message: types.Message):
    uid = message.from_user.id
    if uid != ADMIN_ID: return
    stats = db.get_stats()
    text = t(uid, 'admin_stats_title')
    text += t(uid, 'admin_stats_users', count=stats['total_users'])
    text += t(uid, 'admin_stats_matches', count=stats['total_matches'])
    text += t(uid, 'admin_stats_dates', count=stats['confirmed_dates'])
    text += t(uid, 'admin_stats_by_city')
    for city, count in stats['city_stats'].items(): text += f"  {city}: {count}\n"
    await message.answer(text)

@dp.message(MainMenuState.in_admin, lambda m: m.text == t(m.from_user.id, 'admin_menu_broadcast'))
async def broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await message.answer(t(message.from_user.id, 'admin_broadcast_prompt'), reply_markup=get_back_keyboard(message.from_user.id))
    await state.set_state(MainMenuState.admin_broadcast)

@dp.message(MainMenuState.admin_broadcast)
async def send_broadcast(message: types.Message, state: FSMContext):
    if is_back(message.from_user.id, message.text):
        await message.answer(t(message.from_user.id, 'admin_title'), reply_markup=get_admin_keyboard()); await state.set_state(MainMenuState.in_admin); return
    if message.from_user.id != ADMIN_ID: return
    users = db.get_all_users(); sent_count = 0
    for user in users:
        try: await bot.send_message(user['user_id'], message.text); sent_count += 1
        except Exception as e: logger.error(f"Failed to send broadcast to {user['user_id']}: {e}")
    await message.answer(f"✅ Sent to {sent_count} users")
    await message.answer(t(message.from_user.id, 'action_choose'), reply_markup=get_admin_keyboard()); await state.set_state(MainMenuState.in_admin)

@dp.message(MainMenuState.in_admin, lambda m: m.text == t(m.from_user.id, 'admin_menu_welcome'))
async def admin_welcome(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    # Show current welcome messages
    text = "👋 Приветственные сообщения:\n\n"
    for lang_code, lang_name in [('ru', '🇷🇺 Русский'), ('en', '🇬🇧 English'), ('ka', '🇬🇪 ქართული'), ('es', '🇪🇸 Español'), ('de', '🇩🇪 Deutsch')]:
        msg = db.get_setting(f'welcome_msg_{lang_code}', '—')
        text += f"{lang_name}:\n{msg}\n\n"
    text += "Выберите язык для редактирования:"
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 Русский", callback_data="admin_welcome_ru")
    builder.button(text="🇬🇧 English", callback_data="admin_welcome_en")
    builder.button(text="🇬🇪 ქართული", callback_data="admin_welcome_ka")
    builder.button(text="🇪🇸 Español", callback_data="admin_welcome_es")
    builder.button(text="🇩🇪 Deutsch", callback_data="admin_welcome_de")
    builder.adjust(3, 2)
    await message.answer(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("admin_welcome_"))
async def admin_welcome_lang_selected(query: types.CallbackQuery, state: FSMContext):
    if query.from_user.id != ADMIN_ID: return
    lang = query.data.replace("admin_welcome_", "")
    await state.update_data(admin_welcome_lang=lang)
    lang_names = {'ru': 'Русский', 'en': 'English', 'ka': 'ქართული', 'es': 'Español', 'de': 'Deutsch'}
    current = db.get_setting(f'welcome_msg_{lang}', '—')
    await query.message.answer(f"Текущее сообщение ({lang_names.get(lang, lang)}):\n\n{current}\n\nВведите новое приветственное сообщение (или ◀️ Назад):")
    await state.set_state(MainMenuState.admin_welcome_text)

@dp.message(MainMenuState.admin_welcome_text)
async def admin_welcome_text_entered(message: types.Message, state: FSMContext):
    if is_back(message.from_user.id, message.text):
        await message.answer("🔧 Админ-панель", reply_markup=get_admin_keyboard()); await state.set_state(MainMenuState.in_admin); return
    data = await state.get_data()
    lang = data.get('admin_welcome_lang', 'ru')
    db.set_setting(f'welcome_msg_{lang}', message.text)
    lang_names = {'ru': 'Русский', 'en': 'English', 'ka': 'ქართული', 'es': 'Español', 'de': 'Deutsch'}
    await message.answer(f"✅ Приветственное сообщение ({lang_names.get(lang, lang)}) обновлено!")
    await message.answer("🔧 Админ-панель", reply_markup=get_admin_keyboard())
    await state.set_state(MainMenuState.in_admin)

@dp.message(MainMenuState.in_admin, lambda m: is_back(m.from_user.id, m.text))
async def admin_back(message: types.Message, state: FSMContext):
    await message.answer(t(message.from_user.id, 'action_choose'), reply_markup=get_main_menu_keyboard(message.from_user.id))
    await state.set_state(MainMenuState.main_menu)

# ===== Background =====

async def publish_ratings():
    while True:
        try: db.publish_pending_ratings()
        except Exception as e: logger.error(f"Error in publish_ratings: {e}")
        await asyncio.sleep(3600)

async def main():
    logger.info(f"Starting {BOT_NAME} bot...")
    try:
        asyncio.create_task(publish_ratings())
        logger.info("Bot started successfully, polling for updates...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except KeyboardInterrupt: logger.info("Bot interrupted by user")
    except Exception as e: logger.error(f"Critical error in main: {e}"); raise
    finally: await bot.session.close(); logger.info("Bot session closed")

if __name__ == "__main__":
    asyncio.run(main())
