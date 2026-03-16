# ============================================================
# ИЗМЕНЕНИЯ В bot_enhanced.py ДЛЯ ДОБАВЛЕНИЯ ЗНАКА ЗОДИАКА
# ============================================================
# Ниже указаны ВСЕ изменения, которые нужно внести в файл.
# Файл слишком большой для полного включения — показаны только изменённые участки.
# ============================================================

# --- ИЗМЕНЕНИЕ 1: Добавить состояние в RegistrationState (строка ~36) ---
# БЫЛО:
#     waiting_for_age = State()
#     waiting_for_city = State()
#     waiting_for_photos = State()
# СТАЛО:
class RegistrationState(StatesGroup):
    choosing_language = State()
    viewing_welcome = State()
    choosing_country = State()
    waiting_for_name = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_zodiac = State()       # <-- НОВЫЙ СТЕЙТ
    waiting_for_city = State()
    waiting_for_photos = State()
    waiting_for_bio = State()
    waiting_for_interests = State()
    registration_complete = State()

# --- ИЗМЕНЕНИЕ 2: Добавить состояние в MainMenuState (строка ~63) ---
# Добавить после edit_interests:
#     edit_zodiac = State()
class MainMenuState(StatesGroup):
    # ... все существующие состояния ...
    edit_zodiac = State()              # <-- НОВЫЙ СТЕЙТ
    # ...

# --- ИЗМЕНЕНИЕ 3: Список знаков зодиака (после импортов) ---
ZODIAC_SIGNS = [
    'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
    'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'
]

# --- ИЗМЕНЕНИЕ 4: Клавиатура выбора знака зодиака ---
def get_zodiac_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    for sign in ZODIAC_SIGNS:
        builder.button(text=t(user_id, f'zodiac_{sign}'), callback_data=f"zodiac_{sign}")
    builder.button(text=t(user_id, 'zodiac_skip'), callback_data="zodiac_skip")
    builder.adjust(3)  # 3 колонки -> 4 ряда знаков + ряд с кнопкой пропустить
    return builder.as_markup()

# --- ИЗМЕНЕНИЕ 5: Обработчик возраста — после ввода возраста показать зодиак ---
# БЫЛО (строка ~509):
#     await state.update_data(age=age)
#     await message.answer(t(user_id, 'upload_photo'), reply_markup=get_back_keyboard(user_id))
#     await state.update_data(photos=[])
#     await state.set_state(RegistrationState.waiting_for_photos)
# СТАЛО:
@dp.message(RegistrationState.waiting_for_age)
async def process_age(message, state):
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
    # Показать выбор знака зодиака вместо фото
    await message.answer(t(user_id, 'choose_zodiac'), reply_markup=get_zodiac_keyboard(user_id))
    await state.set_state(RegistrationState.waiting_for_zodiac)

# --- ИЗМЕНЕНИЕ 6: Обработчик выбора знака зодиака при регистрации ---
@dp.callback_query(RegistrationState.waiting_for_zodiac)
async def process_zodiac(query, state):
    await query.answer()
    user_id = query.from_user.id
    if query.data == "zodiac_skip":
        await state.update_data(zodiac=None)
        await query.message.answer(t(user_id, 'zodiac_skipped'))
    else:
        sign = query.data.replace("zodiac_", "")
        if sign in ZODIAC_SIGNS:
            zodiac_display = t(user_id, f'zodiac_{sign}')
            await state.update_data(zodiac=sign)
            await query.message.answer(t(user_id, 'zodiac_selected', zodiac=zodiac_display))
        else:
            return
    # Переход к загрузке фото
    await query.message.answer(t(user_id, 'upload_photo'), reply_markup=get_back_keyboard(user_id))
    await state.update_data(photos=[])
    await state.set_state(RegistrationState.waiting_for_photos)

# --- ИЗМЕНЕНИЕ 7: Фото — кнопка "Назад" возвращает к зодиаку ---
# БЫЛО (строка ~552):
#     if message.text and is_back(user_id, message.text):
#         await message.answer(t(user_id, 'enter_age'), reply_markup=get_back_keyboard(user_id))
#         await state.set_state(RegistrationState.waiting_for_age); return
# СТАЛО:
@dp.message(RegistrationState.waiting_for_photos)
async def process_photos(message, state):
    user_id = message.from_user.id
    if message.text and is_back(user_id, message.text):
        # Назад к выбору знака зодиака
        await message.answer(t(user_id, 'choose_zodiac'), reply_markup=types.ReplyKeyboardRemove())
        await message.answer(t(user_id, 'choose_zodiac'), reply_markup=get_zodiac_keyboard(user_id))
        await state.set_state(RegistrationState.waiting_for_zodiac); return
    # ... остальной код без изменений ...

# --- ИЗМЕНЕНИЕ 8: Сохранение зодиака при завершении регистрации ---
# В обработчике interests_done (строка ~596):
# БЫЛО:
#     db.update_user(user_id, bio=user_data.get('bio', ''), interests=json.dumps(interests),
#                    registration_complete=True, last_seen=datetime.now().isoformat())
# СТАЛО:
#     zodiac = user_data.get('zodiac')
#     update_kwargs = dict(bio=user_data.get('bio', ''), interests=json.dumps(interests),
#                          registration_complete=True, last_seen=datetime.now().isoformat())
#     if zodiac:
#         update_kwargs['zodiac'] = zodiac
#     db.update_user(user_id, **update_kwargs)

# --- ИЗМЕНЕНИЕ 9: build_profile_caption — показать знак зодиака ---
# БЫЛО (строка ~330):
#     caption = f"👤 {profile['name']}, {profile['age']}\n📍 {city_display}\n"
# СТАЛО:
def build_profile_caption(profile, user_id):
    interests = json.loads(profile['interests']) if profile['interests'] else []
    lang = get_user_lang(user_id)
    city_display = get_city_display_name(profile['city'], lang)
    zodiac = profile.get('zodiac')
    zodiac_str = ""
    if zodiac:
        zodiac_str = f" {t(user_id, f'zodiac_{zodiac}')}"
    caption = f"👤 {profile['name']}, {profile['age']}{zodiac_str}\n📍 {city_display}\n"
    caption += f"⭐ {profile['rating']:.1f} ({profile['rating_count']} "
    caption += {"ru": "отзывов", "ka": "შეფასება"}.get(lang, "reviews") + ")\n\n"
    if profile['bio']: caption += f"📝 {profile['bio']}\n\n"
    caption += f"💫 {', '.join(interests)}"
    return caption

# --- ИЗМЕНЕНИЕ 10: show_profile — показать знак зодиака ---
# После строки с profile_city (строка ~1028):
# БЫЛО:
#     text += t(user_id, 'profile_rating', rating=user['rating'], count=user['rating_count'])
# СТАЛО:
#     zodiac = user.get('zodiac')
#     if zodiac:
#         text += t(user_id, 'profile_zodiac', zodiac=t(user_id, f'zodiac_{zodiac}'))
#     text += t(user_id, 'profile_rating', rating=user['rating'], count=user['rating_count'])

# --- ИЗМЕНЕНИЕ 11: Кнопка зодиака в меню редактирования ---
# В get_edit_profile_keyboard (строка ~244):
# Добавить после edit_interests:
#     builder.button(text=t(user_id, 'edit_zodiac'), callback_data="edit_zodiac")
def get_edit_profile_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    builder.button(text=t(user_id, 'edit_name'), callback_data="edit_name")
    builder.button(text=t(user_id, 'edit_age'), callback_data="edit_age")
    builder.button(text=t(user_id, 'edit_country'), callback_data="edit_country")
    builder.button(text=t(user_id, 'edit_city'), callback_data="edit_city")
    builder.button(text=t(user_id, 'edit_bio'), callback_data="edit_bio")
    builder.button(text=t(user_id, 'edit_photo'), callback_data="edit_photo")
    builder.button(text=t(user_id, 'edit_interests'), callback_data="edit_interests")
    builder.button(text=t(user_id, 'edit_zodiac'), callback_data="edit_zodiac")  # <-- НОВОЕ
    builder.button(text=t(user_id, 'menu_photos'), callback_data="edit_view_photos")
    builder.button(text=t(user_id, 'menu_delete'), callback_data="edit_delete_profile")
    builder.button(text=get_back_text(user_id), callback_data="edit_back")
    builder.adjust(2)
    return builder.as_markup()

# --- ИЗМЕНЕНИЕ 12: Обработчик редактирования знака зодиака ---
def get_zodiac_edit_keyboard(user_id):
    """Клавиатура для редактирования знака зодиака: выбор + удаление"""
    user = db.get_user(user_id)
    builder = InlineKeyboardBuilder()
    for sign in ZODIAC_SIGNS:
        builder.button(text=t(user_id, f'zodiac_{sign}'), callback_data=f"edit_zodiac_{sign}")
    if user and user.get('zodiac'):
        builder.button(text=t(user_id, 'edit_zodiac_delete'), callback_data="edit_zodiac_delete")
    builder.button(text=get_back_text(user_id), callback_data="edit_zodiac_back")
    builder.adjust(3)
    return builder.as_markup()

@dp.callback_query(MainMenuState.editing_profile, F.data == "edit_zodiac")
async def edit_zodiac_start(query, state):
    user_id = query.from_user.id
    await query.message.answer(t(user_id, 'choose_zodiac'), reply_markup=get_zodiac_edit_keyboard(user_id))
    await state.set_state(MainMenuState.edit_zodiac)

@dp.callback_query(MainMenuState.edit_zodiac)
async def edit_zodiac_process(query, state):
    user_id = query.from_user.id
    if query.data == "edit_zodiac_back":
        await query.message.answer(t(user_id, 'edit_title'), reply_markup=get_edit_profile_keyboard(user_id))
        await state.set_state(MainMenuState.editing_profile); return
    if query.data == "edit_zodiac_delete":
        db.update_user(user_id, zodiac=None)
        await query.message.answer(t(user_id, 'zodiac_deleted'))
        await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
        await state.set_state(MainMenuState.main_menu); return
    if query.data.startswith("edit_zodiac_"):
        sign = query.data.replace("edit_zodiac_", "")
        if sign in ZODIAC_SIGNS:
            db.update_user(user_id, zodiac=sign)
            zodiac_display = t(user_id, f'zodiac_{sign}')
            await query.message.answer(t(user_id, 'zodiac_selected', zodiac=zodiac_display))
            await query.message.answer(t(user_id, 'action_choose'), reply_markup=get_main_menu_keyboard(user_id))
            await state.set_state(MainMenuState.main_menu)
