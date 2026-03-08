# Internationalization module for ЦИТРАМОН bot
# All bot messages and button labels in Russian and English

TEXTS = {
    'ru': {
        # General
        'back': '◀️ Назад',
        'error': '❌ Ошибка',
        'action_choose': 'Выберите действие:',

        # Language selection
        'choose_language': '🌐 Выберите язык / Choose language:',
        'lang_ru': '🇷🇺 Русский',
        'lang_en': '🇬🇧 English',

        # Registration
        'welcome_new': '👋 Добро пожаловать в ЦИТРАМОН - приложение для знакомств в Беларуси!\n\nДавайте создадим вашу анкету. Как вас зовут? (максимум 20 символов)\n\nДля отмены нажмите ◀️ Назад',
        'welcome_back': '👋 Добро пожаловать в ЦИТРАМОН!\n\nВыберите действие:',
        'reg_cancelled': 'Регистрация отменена. Напишите /start чтобы начать заново.',
        'enter_name': 'Как вас зовут? (максимум 20 символов)',
        'name_no_commands': '❌ Пожалуйста, введите ваше имя (текст без команд).',
        'name_empty': '❌ Имя не может быть пустым.',
        'name_too_long': '❌ Имя слишком длинное. Максимум {max} символов.',
        'name_too_short': '❌ Имя слишком короткое. Минимум 2 символа.',
        'name_error': '❌ Ошибка при обработке имени. Попробуйте снова.',
        'choose_gender': 'Выберите ваш пол:',
        'gender_male': '👨 Мужской',
        'gender_female': '👩 Женский',
        'gender_invalid': '❌ Пожалуйста, выберите пол из предложенных вариантов.',
        'gender_no_commands': '❌ Пожалуйста, выберите пол из кнопок.',
        'gender_error': '❌ Ошибка при обработке пола. Попробуйте снова.',
        'enter_age': 'Сколько вам лет? (введите число, минимум 18)',
        'age_invalid_range': '❌ Возраст должен быть от {min} до {max} лет.',
        'age_invalid': '❌ Пожалуйста, введите корректный возраст (число).',
        'age_no_commands': '❌ Пожалуйста, введите число.',
        'age_error': '❌ Ошибка при обработке возраста. Попробуйте снова.',
        'choose_city': 'Выберите ваш город:',
        'city_invalid': '❌ Пожалуйста, выберите город из предложенных вариантов.',
        'upload_photo': 'Загрузите фотографию вашего профиля.',
        'photo_max': '❌ Максимум {max} фотография.',
        'photo_uploaded': '✅ Фотография загружена!\n\nНапишите о себе (максимум 200 символов):',
        'photo_invalid': '❌ Пожалуйста, отправьте фотографию.',
        'enter_bio': 'Напишите о себе (максимум 200 символов):',
        'bio_text_only': '❌ Пожалуйста, введите текст о себе.',
        'bio_too_long': '❌ Описание слишком длинное. Максимум {max} символов.',
        'choose_interests': 'Выберите ваши интересы (максимум 5). Нажимайте на кнопки для выбора:',
        'interests_min': '❌ Выберите хотя бы один интерес',
        'interests_max': '❌ Максимум {max} интересов',
        'interests_done': '✅ Готово',
        'reg_complete': '✅ Ваша анкета создана!\n\nДобро пожаловать в ЦИТРАМОН! 🎉',

        # Main menu
        'menu_feed': '❤️ Лента анкет',
        'menu_matches': '💬 Мои мэтчи',
        'menu_profile': '👤 Мой профиль',
        'menu_photos': '🔍 Просмотр фото',
        'menu_edit': '✏️ Отредактировать',
        'menu_support': '📞 Поддержка',
        'menu_delete': '🗑 Удалить анкету',
        'menu_admin': '🔧 Админ',
        'menu_language': '🌐 Язык',

        # Feed
        'feed_like': '❤️ Лайк',
        'feed_skip': '👎 Пропустить',
        'feed_report': '🚨 Пожаловаться',
        'feed_no_more': '😔 Больше нет анкет для просмотра',
        'feed_banned': '❌ Ваш аккаунт заблокирован',
        'feed_like_sent': '❤️ Лайк отправлен!',
        'feed_mutual': '❤️ Взаимный лайк! Вы мэтчились!\n\nТеперь вы можете общаться с этим пользователем.',
        'feed_mutual_partner': '❤️ Взаимный лайк! Вы мэтчились с {name}!\n\nТеперь вы можете общаться.',
        'complaint_choose': 'Выберите тип жалобы:',
        'complaint_sent': '✅ Жалоба отправлена. Спасибо за помощь в модерации!',

        # Matches
        'no_matches': '😔 У вас пока нет мэтчей',
        'match_chat': '💬 Чат',
        'match_date': '📅 Свидание',
        'match_rate': '⭐ Оценить',

        # Chat
        'chat_history': '💬 История сообщений:\n\n',
        'chat_empty': '💬 Нет сообщений. Начните разговор!\n\n',
        'chat_send_prompt': '\nОтправьте сообщение (или нажмите ◀️ Назад):',
        'chat_msg_sent': '✅ Сообщение отправлено!',
        'chat_new_msg': '💬 Новое сообщение от {name}:\n\n{text}',

        # Date flow
        'date_choose_type': '📅 Выберите тип свидания:',
        'date_online': '📱 ОНЛАЙН',
        'date_offline': '🌟 ОФЛАЙН',
        'date_proposed_online': '📱 {name} предлагает ОНЛАЙН свидание!\n\nПодтвердите или отклоните.',
        'date_proposed_offline': '🌟 {name} предлагает ОФЛАЙН свидание!\n\nПодтвердите или отклоните.',
        'date_sent': '✅ Приглашение на свидание отправлено! Ожидаем подтверждения.',
        'date_accept': '✅ Подтвердить свидание',
        'date_decline': '❌ Отклонить',
        'date_confirmed': '✅ Свидание подтверждено! Когда будете на месте, нажмите кнопку.',
        'date_confirmed_proposer': '✅ Партнёр подтвердил свидание! Когда будете на месте, нажмите кнопку.',
        'date_declined_you': '❌ Вы отклонили свидание.',
        'date_declined_partner': '😔 Партнёр отклонил свидание.',
        'date_arrived': '✅ Я на месте',
        'date_arrived_ok': '✅ Вы отметились! Ожидаем партнёра.',
        'date_partner_arrived': '📍 Ваш партнёр уже на месте! Отметьтесь, когда придёте.',
        'date_both_arrived': '🎉 СВИДАНИЕ СОСТОЯЛОСЬ!\n\nОба участника на месте. Приятного времяпровождения!\n\nТеперь вы можете оставить отзыв и оценку.',
        'date_not_found': '❌ Свидание не найдено',
        'date_rate_prompt': '🌟 Оцените вашего партнёра:',
        'date_need_both_arrived': '❌ Оба участника должны отметиться "Я на месте" чтобы оставить отзыв!',

        # Rating
        'rate_positive': '😊 Выберите положительные качества:',
        'rate_negative': '😮 Выберите отрицательные качества:',
        'rate_saved': '✅ Оценка сохранена!',
        'rate_done': '✅ Готово',

        # Profile
        'profile_title': '👤 Ваш профиль\n\n',
        'profile_name': 'Имя: {name}\n',
        'profile_age': 'Возраст: {age}\n',
        'profile_city': 'Город: {city}\n',
        'profile_rating': '⭐ Рейтинг: {rating:.1f}\n\n',
        'profile_bio': '📝 О себе: {bio}\n\n',
        'profile_interests': '💫 Интересы: {interests}',
        'profile_not_found': '❌ Профиль не найден',
        'no_photos': '❌ У вас нет фото',

        # Edit profile
        'edit_title': '✏️ Что вы хотите изменить?',
        'edit_name': '📝 Имя',
        'edit_age': '🎂 Возраст',
        'edit_city': '📍 Город',
        'edit_bio': '📄 О себе',
        'edit_photo': '📷 Фото',
        'edit_interests': '💫 Интересы',
        'edit_enter_name': '📝 Введите новое имя (максимум 20 символов):',
        'edit_enter_age': '🎂 Введите новый возраст:',
        'edit_choose_city': '📍 Выберите новый город:',
        'edit_enter_bio': '📄 Введите новое описание (максимум 200 символов):',
        'edit_upload_photo': '📷 Отправьте новое фото:',
        'edit_choose_interests': '💫 Выберите новые интересы:',
        'edit_saved': '✅ Изменения сохранены!',

        # Delete profile
        'delete_confirm': '⚠️ Вы уверены, что хотите удалить свою анкету?\n\nЭто действие необратимо. Все ваши данные, мэтчи, сообщения и оценки будут удалены.',
        'delete_yes': '✅ Да, удалить',
        'delete_no': '❌ Отмена',
        'delete_done': '✅ Ваша анкета удалена. Спасибо, что пользовались ЦИТРАМОН!\n\nЧтобы создать новую анкету, напишите /start',
        'delete_error': '❌ Ошибка при удалении. Попробуйте позже.',
        'delete_cancelled': '✅ Удаление отменено.',

        # Support
        'support_text': '📞 Поддержка\n\nДля связи с администратором нажмите на ссылку ниже:\n👉 [Написать админу](tg://user?id={admin_id})',

        # Admin
        'admin_title': '🔧 Админ-панель',
        'admin_no_access': '❌ У вас нет доступа к админ-панели',
        'admin_complaints': '📋 Жалобы',
        'admin_users': '👥 Управление пользователями',
        'admin_stats': '📊 Статистика',
        'admin_broadcast': '📢 Рассылка',
        'admin_no_complaints': '✅ Нет новых жалоб',
        'admin_enter_user_id': 'Введите ID пользователя для поиска:',
        'admin_user_not_found': '❌ Пользователь не найден',
        'admin_invalid_id': '❌ Введите корректный ID',
        'admin_ban': '🚫 Заблокировать',
        'admin_shadow_ban': '👻 Теневой бан',
        'admin_reset_rating': '⭐ Обнулить рейтинг',
        'admin_banned': '✅ Пользователь заблокирован',
        'admin_shadow_banned': '✅ Пользователь получил теневой бан',
        'admin_rating_reset': '✅ Рейтинг пользователя обнулен',
        'admin_broadcast_prompt': 'Введите текст рассылки (или ◀️ Назад для отмены):',
        'admin_broadcast_done': '✅ Рассылка отправлена {count} пользователям',
        'admin_complaint_approved': '✅ Жалоба одобрена, пользователь теневой бан',
        'admin_complaint_rejected': '✅ Жалоба отклонена',
        'admin_approve': '✅ Одобрить',
        'admin_reject': '❌ Отклонить',

        # Language
        'language_changed': '✅ Язык изменён на Русский',
    },
    'en': {
        # General
        'back': '◀️ Back',
        'error': '❌ Error',
        'action_choose': 'Choose an action:',

        # Language selection
        'choose_language': '🌐 Выберите язык / Choose language:',
        'lang_ru': '🇷🇺 Русский',
        'lang_en': '🇬🇧 English',

        # Registration
        'welcome_new': '👋 Welcome to ЦИТРАМОН - a dating app in Belarus!\n\nLet\'s create your profile. What is your name? (max 20 characters)\n\nPress ◀️ Back to cancel',
        'welcome_back': '👋 Welcome to ЦИТРАМОН!\n\nChoose an action:',
        'reg_cancelled': 'Registration cancelled. Type /start to begin again.',
        'enter_name': 'What is your name? (max 20 characters)',
        'name_no_commands': '❌ Please enter your name (text without commands).',
        'name_empty': '❌ Name cannot be empty.',
        'name_too_long': '❌ Name is too long. Max {max} characters.',
        'name_too_short': '❌ Name is too short. Min 2 characters.',
        'name_error': '❌ Error processing name. Try again.',
        'choose_gender': 'Choose your gender:',
        'gender_male': '👨 Male',
        'gender_female': '👩 Female',
        'gender_invalid': '❌ Please choose from the options provided.',
        'gender_no_commands': '❌ Please use the buttons to select gender.',
        'gender_error': '❌ Error processing gender. Try again.',
        'enter_age': 'How old are you? (enter a number, minimum 18)',
        'age_invalid_range': '❌ Age must be between {min} and {max}.',
        'age_invalid': '❌ Please enter a valid age (number).',
        'age_no_commands': '❌ Please enter a number.',
        'age_error': '❌ Error processing age. Try again.',
        'choose_city': 'Choose your city:',
        'city_invalid': '❌ Please choose a city from the options.',
        'upload_photo': 'Upload your profile photo.',
        'photo_max': '❌ Maximum {max} photo.',
        'photo_uploaded': '✅ Photo uploaded!\n\nWrite about yourself (max 200 characters):',
        'photo_invalid': '❌ Please send a photo.',
        'enter_bio': 'Write about yourself (max 200 characters):',
        'bio_text_only': '❌ Please enter text about yourself.',
        'bio_too_long': '❌ Description is too long. Max {max} characters.',
        'choose_interests': 'Choose your interests (max 5). Tap buttons to select:',
        'interests_min': '❌ Choose at least one interest',
        'interests_max': '❌ Maximum {max} interests',
        'interests_done': '✅ Done',
        'reg_complete': '✅ Your profile is created!\n\nWelcome to ЦИТРАМОН! 🎉',

        # Main menu
        'menu_feed': '❤️ Browse profiles',
        'menu_matches': '💬 My matches',
        'menu_profile': '👤 My profile',
        'menu_photos': '🔍 View photos',
        'menu_edit': '✏️ Edit profile',
        'menu_support': '📞 Support',
        'menu_delete': '🗑 Delete profile',
        'menu_admin': '🔧 Admin',
        'menu_language': '🌐 Language',

        # Feed
        'feed_like': '❤️ Like',
        'feed_skip': '👎 Skip',
        'feed_report': '🚨 Report',
        'feed_no_more': '😔 No more profiles to show',
        'feed_banned': '❌ Your account is banned',
        'feed_like_sent': '❤️ Like sent!',
        'feed_mutual': '❤️ Mutual like! You matched!\n\nNow you can chat with this user.',
        'feed_mutual_partner': '❤️ Mutual like! You matched with {name}!\n\nNow you can chat.',
        'complaint_choose': 'Choose complaint type:',
        'complaint_sent': '✅ Complaint sent. Thanks for helping us moderate!',

        # Matches
        'no_matches': '😔 You have no matches yet',
        'match_chat': '💬 Chat',
        'match_date': '📅 Date',
        'match_rate': '⭐ Rate',

        # Chat
        'chat_history': '💬 Message history:\n\n',
        'chat_empty': '💬 No messages. Start a conversation!\n\n',
        'chat_send_prompt': '\nSend a message (or press ◀️ Back):',
        'chat_msg_sent': '✅ Message sent!',
        'chat_new_msg': '💬 New message from {name}:\n\n{text}',

        # Date flow
        'date_choose_type': '📅 Choose date type:',
        'date_online': '📱 ONLINE',
        'date_offline': '🌟 OFFLINE',
        'date_proposed_online': '📱 {name} invites you to an ONLINE date!\n\nAccept or decline.',
        'date_proposed_offline': '🌟 {name} invites you to an OFFLINE date!\n\nAccept or decline.',
        'date_sent': '✅ Date invitation sent! Waiting for confirmation.',
        'date_accept': '✅ Accept date',
        'date_decline': '❌ Decline',
        'date_confirmed': '✅ Date confirmed! Press the button when you arrive.',
        'date_confirmed_proposer': '✅ Partner confirmed the date! Press the button when you arrive.',
        'date_declined_you': '❌ You declined the date.',
        'date_declined_partner': '😔 Partner declined the date.',
        'date_arrived': '✅ I\'m here',
        'date_arrived_ok': '✅ You checked in! Waiting for your partner.',
        'date_partner_arrived': '📍 Your partner is already there! Check in when you arrive.',
        'date_both_arrived': '🎉 DATE CONFIRMED!\n\nBoth participants are here. Enjoy your time!\n\nNow you can leave a review and rating.',
        'date_not_found': '❌ Date not found',
        'date_rate_prompt': '🌟 Rate your partner:',
        'date_need_both_arrived': '❌ Both participants need to check in "I\'m here" to leave a review!',

        # Rating
        'rate_positive': '😊 Choose positive qualities:',
        'rate_negative': '😮 Choose negative qualities:',
        'rate_saved': '✅ Rating saved!',
        'rate_done': '✅ Done',

        # Profile
        'profile_title': '👤 Your profile\n\n',
        'profile_name': 'Name: {name}\n',
        'profile_age': 'Age: {age}\n',
        'profile_city': 'City: {city}\n',
        'profile_rating': '⭐ Rating: {rating:.1f}\n\n',
        'profile_bio': '📝 About: {bio}\n\n',
        'profile_interests': '💫 Interests: {interests}',
        'profile_not_found': '❌ Profile not found',
        'no_photos': '❌ You have no photos',

        # Edit profile
        'edit_title': '✏️ What would you like to change?',
        'edit_name': '📝 Name',
        'edit_age': '🎂 Age',
        'edit_city': '📍 City',
        'edit_bio': '📄 About',
        'edit_photo': '📷 Photo',
        'edit_interests': '💫 Interests',
        'edit_enter_name': '📝 Enter new name (max 20 characters):',
        'edit_enter_age': '🎂 Enter new age:',
        'edit_choose_city': '📍 Choose new city:',
        'edit_enter_bio': '📄 Enter new description (max 200 characters):',
        'edit_upload_photo': '📷 Send new photo:',
        'edit_choose_interests': '💫 Choose new interests:',
        'edit_saved': '✅ Changes saved!',

        # Delete profile
        'delete_confirm': '⚠️ Are you sure you want to delete your profile?\n\nThis action is irreversible. All your data, matches, messages and ratings will be deleted.',
        'delete_yes': '✅ Yes, delete',
        'delete_no': '❌ Cancel',
        'delete_done': '✅ Your profile is deleted. Thanks for using ЦИТРАМОН!\n\nTo create a new profile, type /start',
        'delete_error': '❌ Error deleting. Try later.',
        'delete_cancelled': '✅ Deletion cancelled.',

        # Support
        'support_text': '📞 Support\n\nTo contact the administrator click the link below:\n👉 [Message admin](tg://user?id={admin_id})',

        # Admin (admin panel stays in Russian for admin)
        'admin_title': '🔧 Админ-панель',
        'admin_no_access': '❌ You don\'t have access to the admin panel',
        'admin_complaints': '📋 Жалобы',
        'admin_users': '👥 Управление пользователями',
        'admin_stats': '📊 Статистика',
        'admin_broadcast': '📢 Рассылка',
        'admin_no_complaints': '✅ Нет новых жалоб',
        'admin_enter_user_id': 'Введите ID пользователя для поиска:',
        'admin_user_not_found': '❌ Пользователь не найден',
        'admin_invalid_id': '❌ Введите корректный ID',
        'admin_ban': '🚫 Заблокировать',
        'admin_shadow_ban': '👻 Теневой бан',
        'admin_reset_rating': '⭐ Обнулить рейтинг',
        'admin_banned': '✅ Пользователь заблокирован',
        'admin_shadow_banned': '✅ Пользователь получил теневой бан',
        'admin_rating_reset': '✅ Рейтинг пользователя обнулен',
        'admin_broadcast_prompt': 'Введите текст рассылки (или ◀️ Назад для отмены):',
        'admin_broadcast_done': '✅ Рассылка отправлена {count} пользователям',
        'admin_complaint_approved': '✅ Жалоба одобрена, пользователь теневой бан',
        'admin_complaint_rejected': '✅ Жалоба отклонена',
        'admin_approve': '✅ Одобрить',
        'admin_reject': '❌ Отклонить',

        # Language
        'language_changed': '✅ Language changed to English',
    }
}

# User language cache (user_id -> lang)
_user_langs = {}

def set_user_lang(user_id: int, lang: str):
    _user_langs[user_id] = lang

def get_user_lang(user_id: int) -> str:
    return _user_langs.get(user_id, 'ru')

def t(user_id: int, key: str, **kwargs) -> str:
    lang = get_user_lang(user_id)
    text = TEXTS.get(lang, TEXTS['ru']).get(key, TEXTS['ru'].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text

def get_back_text(user_id: int) -> str:
    return t(user_id, 'back')
