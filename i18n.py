# Internationalization module for CITRAMON DATING bot
# All bot messages and button labels in Russian, English, and Georgian

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
        'lang_ka': '🇬🇪 ქართული',

        # Country selection
        'choose_country': '🌍 Выберите вашу страну:',

        # Registration
        'welcome_new': '👋 Добро пожаловать в CITRAMON DATING — приложение для знакомств!\n\nДавайте создадим вашу анкету.\n\n✍️ Напишите ваше имя:\n(максимум 20 символов)\n\nДля отмены нажмите ◀️ Назад',
        'welcome_back': '👋 Добро пожаловать в CITRAMON DATING!\n\nВыберите действие:',
        'reg_cancelled': 'Регистрация отменена. Напишите /start чтобы начать заново.',
        'enter_name': '✍️ Напишите ваше имя:\n(максимум 20 символов)',
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
        'photo_uploaded': '✅ Фотография загружена!\n\nНапишите о себе (максимум 200 символов) или нажмите ⏩ Пропустить:',
        'photo_invalid': '❌ Пожалуйста, отправьте фотографию.',
        'enter_bio': 'Напишите о себе (максимум 200 символов) или нажмите ⏩ Пропустить:',
        'bio_skip': '⏩ Пропустить',
        'bio_text_only': '❌ Пожалуйста, введите текст о себе.',
        'bio_too_long': '❌ Описание слишком длинное. Максимум {max} символов.',
        'choose_interests': 'Выберите ваши интересы (максимум 5). Нажимайте на кнопки для выбора:',
        'interests_min': '❌ Выберите хотя бы один интерес',
        'interests_max': '❌ Максимум {max} интересов',
        'interests_done': '✅ Готово',
        'reg_complete': '✅ Ваша анкета создана!\n\nДобро пожаловать в CITRAMON DATING! 🎉',

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
        'match_view_profile': '👤 Анкета',
        'match_reviews': '📝 Отзывы',

        # Chat
        'chat_history': '💬 История сообщений:\n\n',
        'chat_empty': '💬 Нет сообщений. Начните разговор!\n\n',
        'chat_send_prompt': '\nОтправьте сообщение (или нажмите ◀️ Назад):',
        'chat_msg_sent': '✅ Сообщение отправлено!\n\nМожете продолжить общение или нажмите ◀️ Назад.',
        'chat_new_msg': '💬 Новое сообщение от {name}:\n\n{text}',
        'chat_reply': '💬 Ответить',

        # Date flow
        'date_choose_type': '📅 Выберите тип свидания:',
        'date_online': '📱 ОНЛАЙН',
        'date_offline': '🌟 ОФЛАЙН',
        'date_proposed_online': '📱 {name} предлагает ОНЛАЙН свидание!\n\nПодтвердите или отклоните.',
        'date_proposed_offline': '🌟 {name} предлагает ОФЛАЙН свидание!\n\nПодтвердите или отклоните.',
        'date_sent': '✅ Приглашение на свидание отправлено! Ожидаем подтверждения.',
        'date_already_pending': '⏳ У вас уже есть активное приглашение с этим пользователем. Дождитесь ответа.',
        'date_accept': '✅ Подтвердить свидание',
        'date_decline': '❌ Отклонить',
        'date_confirmed': '✅ Свидание подтверждено! Когда будете на месте, нажмите кнопку.',
        'date_confirmed_proposer': '✅ {name} подтвердил(а) свидание! Когда будете на месте, нажмите кнопку.',
        'date_confirmed_online': '✅ Онлайн-свидание подтверждено!\n\n📱 Обменяйтесь ссылкой на видеозвонок:\n• Zoom\n• Google Meet\n\nОтправьте ссылку партнёру в чат, затем нажмите кнопку «Я на месте» когда будете готовы.',
        'date_confirmed_online_proposer': '✅ {name} подтвердил(а) онлайн-свидание!\n\n📱 Обменяйтесь ссылкой на видеозвонок:\n• Zoom\n• Google Meet\n\nОтправьте ссылку партнёру в чат, затем нажмите кнопку «Я на месте» когда будете готовы.',
        'date_declined_you': '❌ Вы отклонили свидание.',
        'date_declined_partner': '😔 Партнёр отклонил свидание.',
        'date_arrived': '✅ Я на месте',
        'date_arrived_ok': '✅ Вы отметились! Ожидаем партнёра.',
        'date_partner_arrived': '📍 Ваш партнёр уже на месте! Отметьтесь, когда придёте.',
        'date_both_arrived': '🎉 СВИДАНИЕ С {name} СОСТОЯЛОСЬ!\n\nОба участника на месте. Приятного времяпровождения!\n\nТеперь вы можете оставить отзыв и оценку.',
        'date_not_found': '❌ Свидание не найдено',
        'date_rate_prompt': '🌟 Оцените вашего партнёра:',
        'date_need_both_arrived': '❌ Оба участника должны отметиться "Я на месте" чтобы оставить отзыв!',

        # Rating
        'rate_positive': '😊 Выберите положительные качества:',
        'rate_negative': '😮 Выберите отрицательные качества:',
        'rate_saved': '✅ Оценка сохранена! Рейтинг партнёра обновлён.',
        'rate_done': '✅ Готово',
        'rate_choose_anonymity': '🔒 Как опубликовать отзыв?',
        'review_with_name': '📝 С моим именем',
        'review_anonymous': '🔒 Анонимно',
        'anonymous_reviewer': '🔒 Аноним',

        # Reviews
        'reviews_title': '📝 Отзывы о {name}\n\n',
        'reviews_empty': '📝 Пока нет отзывов о этом пользователе.',
        'reviews_summary': '⭐ Средний рейтинг: {rating:.1f} ({count} отзывов)\n\n',
        'reviews_positive_summary': '✅ Чаще отмечают: {tags}\n',
        'reviews_negative_summary': '❌ Замечания: {tags}\n',
        'reviews_item': '⭐ {stars}/5 — {positive}{negative}\n',

        # Profile
        'profile_title': '👤 Ваш профиль\n\n',
        'profile_name': 'Имя: {name}\n',
        'profile_age': 'Возраст: {age}\n',
        'profile_city': 'Город: {city}\n',
        'profile_rating': '⭐ Рейтинг: {rating:.1f} ({count} оценок)\n\n',
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
        'delete_done': '✅ Ваша анкета удалена. Спасибо, что пользовались CITRAMON DATING!\n\nЧтобы создать новую анкету, напишите /start',
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
        'admin_full_reset': '🔄 Обнулить анкету',
        'admin_unban': '🔓 Разблокировать',
        'admin_banned': '✅ Пользователь заблокирован',
        'admin_shadow_banned': '✅ Пользователь получил теневой бан',
        'admin_rating_reset': '✅ Рейтинг пользователя обнулен',
        'admin_full_reset_done': '✅ Анкета обнулена: рейтинг сброшен, все отзывы удалены',
        'admin_unbanned': '✅ Пользователь разблокирован',
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
        'lang_ka': '🇬🇪 ქართული',

        # Country selection
        'choose_country': '🌍 Choose your country:',

        # Registration
        'welcome_new': '👋 Welcome to CITRAMON DATING — a dating app!\n\nLet\'s create your profile.\n\n✍️ Write your name:\n(max 20 characters)\n\nPress ◀️ Back to cancel',
        'welcome_back': '👋 Welcome to CITRAMON DATING!\n\nChoose an action:',
        'reg_cancelled': 'Registration cancelled. Type /start to begin again.',
        'enter_name': '✍️ Write your name:\n(max 20 characters)',
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
        'photo_uploaded': '✅ Photo uploaded!\n\nWrite about yourself (max 200 characters) or press ⏩ Skip:',
        'photo_invalid': '❌ Please send a photo.',
        'enter_bio': 'Write about yourself (max 200 characters) or press ⏩ Skip:',
        'bio_skip': '⏩ Skip',
        'bio_text_only': '❌ Please enter text about yourself.',
        'bio_too_long': '❌ Description is too long. Max {max} characters.',
        'choose_interests': 'Choose your interests (max 5). Tap buttons to select:',
        'interests_min': '❌ Choose at least one interest',
        'interests_max': '❌ Maximum {max} interests',
        'interests_done': '✅ Done',
        'reg_complete': '✅ Your profile is created!\n\nWelcome to CITRAMON DATING! 🎉',

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
        'match_view_profile': '👤 Profile',
        'match_reviews': '📝 Reviews',

        # Chat
        'chat_history': '💬 Message history:\n\n',
        'chat_empty': '💬 No messages. Start a conversation!\n\n',
        'chat_send_prompt': '\nSend a message (or press ◀️ Back):',
        'chat_msg_sent': '✅ Message sent!\n\nYou can continue chatting or press ◀️ Back.',
        'chat_new_msg': '💬 New message from {name}:\n\n{text}',
        'chat_reply': '💬 Reply',

        # Date flow
        'date_choose_type': '📅 Choose date type:',
        'date_online': '📱 ONLINE',
        'date_offline': '🌟 OFFLINE',
        'date_proposed_online': '📱 {name} invites you to an ONLINE date!\n\nAccept or decline.',
        'date_proposed_offline': '🌟 {name} invites you to an OFFLINE date!\n\nAccept or decline.',
        'date_sent': '✅ Date invitation sent! Waiting for confirmation.',
        'date_already_pending': '⏳ You already have a pending invitation with this user. Please wait for a response.',
        'date_accept': '✅ Accept date',
        'date_decline': '❌ Decline',
        'date_confirmed': '✅ Date confirmed! Press the button when you arrive.',
        'date_confirmed_proposer': '✅ {name} confirmed the date! Press the button when you arrive.',
        'date_confirmed_online': '✅ Online date confirmed!\n\n📱 Share a video call link with your partner:\n• Zoom\n• Google Meet\n\nSend the link in chat, then press "I\'m here" when you\'re ready.',
        'date_confirmed_online_proposer': '✅ {name} confirmed the online date!\n\n📱 Share a video call link with your partner:\n• Zoom\n• Google Meet\n\nSend the link in chat, then press "I\'m here" when you\'re ready.',
        'date_declined_you': '❌ You declined the date.',
        'date_declined_partner': '😔 Partner declined the date.',
        'date_arrived': '✅ I\'m here',
        'date_arrived_ok': '✅ You checked in! Waiting for your partner.',
        'date_partner_arrived': '📍 Your partner is already there! Check in when you arrive.',
        'date_both_arrived': '🎉 DATE WITH {name} CONFIRMED!\n\nBoth participants are here. Enjoy your time!\n\nNow you can leave a review and rating.',
        'date_not_found': '❌ Date not found',
        'date_rate_prompt': '🌟 Rate your partner:',
        'date_need_both_arrived': '❌ Both participants need to check in "I\'m here" to leave a review!',

        # Rating
        'rate_positive': '😊 Choose positive qualities:',
        'rate_negative': '😮 Choose negative qualities:',
        'rate_saved': '✅ Rating saved! Partner\'s rating updated.',
        'rate_done': '✅ Done',
        'rate_choose_anonymity': '🔒 How to publish the review?',
        'review_with_name': '📝 With my name',
        'review_anonymous': '🔒 Anonymously',
        'anonymous_reviewer': '🔒 Anonymous',

        # Reviews
        'reviews_title': '📝 Reviews for {name}\n\n',
        'reviews_empty': '📝 No reviews for this user yet.',
        'reviews_summary': '⭐ Average rating: {rating:.1f} ({count} reviews)\n\n',
        'reviews_positive_summary': '✅ Often noted: {tags}\n',
        'reviews_negative_summary': '❌ Issues: {tags}\n',
        'reviews_item': '⭐ {stars}/5 — {positive}{negative}\n',

        # Profile
        'profile_title': '👤 Your profile\n\n',
        'profile_name': 'Name: {name}\n',
        'profile_age': 'Age: {age}\n',
        'profile_city': 'City: {city}\n',
        'profile_rating': '⭐ Rating: {rating:.1f} ({count} reviews)\n\n',
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
        'delete_done': '✅ Your profile is deleted. Thanks for using CITRAMON DATING!\n\nTo create a new profile, type /start',
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
        'admin_full_reset': '🔄 Обнулить анкету',
        'admin_unban': '🔓 Разблокировать',
        'admin_banned': '✅ Пользователь заблокирован',
        'admin_shadow_banned': '✅ Пользователь получил теневой бан',
        'admin_rating_reset': '✅ Рейтинг пользователя обнулен',
        'admin_full_reset_done': '✅ Анкета обнулена: рейтинг сброшен, все отзывы удалены',
        'admin_unbanned': '✅ Пользователь разблокирован',
        'admin_broadcast_prompt': 'Введите текст рассылки (или ◀️ Назад для отмены):',
        'admin_broadcast_done': '✅ Рассылка отправлена {count} пользователям',
        'admin_complaint_approved': '✅ Жалоба одобрена, пользователь теневой бан',
        'admin_complaint_rejected': '✅ Жалоба отклонена',
        'admin_approve': '✅ Одобрить',
        'admin_reject': '❌ Отклонить',

        # Language
        'language_changed': '✅ Language changed to English',
    },
    'ka': {
        # General
        'back': '◀️ უკან',
        'error': '❌ შეცდომა',
        'action_choose': 'აირჩიეთ მოქმედება:',

        # Language selection
        'choose_language': '🌐 Выберите язык / Choose language:',
        'lang_ru': '🇷🇺 Русский',
        'lang_en': '🇬🇧 English',
        'lang_ka': '🇬🇪 ქართული',

        # Country selection
        'choose_country': '🌍 აირჩიეთ თქვენი ქვეყანა:',

        # Registration
        'welcome_new': '👋 კეთილი იყოს თქვენი მობრძანება CITRAMON DATING-ში — გაცნობის აპლიკაცია!\n\nშევქმნათ თქვენი ანკეტა.\n\n✍️ დაწერეთ თქვენი სახელი:\n(მაქსიმუმ 20 სიმბოლო)\n\nგასაუქმებლად დააჭირეთ ◀️ უკან',
        'welcome_back': '👋 კეთილი იყოს თქვენი მობრძანება CITRAMON DATING-ში!\n\nაირჩიეთ მოქმედება:',
        'reg_cancelled': 'რეგისტრაცია გაუქმებულია. თავიდან დასაწყებად დაწერეთ /start',
        'enter_name': '✍️ დაწერეთ თქვენი სახელი:\n(მაქსიმუმ 20 სიმბოლო)',
        'name_no_commands': '❌ გთხოვთ, შეიყვანოთ თქვენი სახელი (ტექსტი ბრძანებების გარეშე).',
        'name_empty': '❌ სახელი არ შეიძლება იყოს ცარიელი.',
        'name_too_long': '❌ სახელი ძალიან გრძელია. მაქსიმუმ {max} სიმბოლო.',
        'name_too_short': '❌ სახელი ძალიან მოკლეა. მინიმუმ 2 სიმბოლო.',
        'name_error': '❌ სახელის დამუშავების შეცდომა. სცადეთ თავიდან.',
        'choose_gender': 'აირჩიეთ თქვენი სქესი:',
        'gender_male': '👨 მამაკაცი',
        'gender_female': '👩 ქალი',
        'gender_invalid': '❌ გთხოვთ, აირჩიოთ შემოთავაზებული ვარიანტებიდან.',
        'gender_no_commands': '❌ გთხოვთ, გამოიყენოთ ღილაკები სქესის ასარჩევად.',
        'gender_error': '❌ სქესის დამუშავების შეცდომა. სცადეთ თავიდან.',
        'enter_age': 'რამდენი წლის ხართ? (შეიყვანეთ რიცხვი, მინიმუმ 18)',
        'age_invalid_range': '❌ ასაკი უნდა იყოს {min}-დან {max}-მდე.',
        'age_invalid': '❌ გთხოვთ, შეიყვანოთ სწორი ასაკი (რიცხვი).',
        'age_no_commands': '❌ გთხოვთ, შეიყვანოთ რიცხვი.',
        'age_error': '❌ ასაკის დამუშავების შეცდომა. სცადეთ თავიდან.',
        'choose_city': 'აირჩიეთ თქვენი ქალაქი:',
        'city_invalid': '❌ გთხოვთ, აირჩიოთ ქალაქი შემოთავაზებული ვარიანტებიდან.',
        'upload_photo': 'ატვირთეთ თქვენი პროფილის ფოტო.',
        'photo_max': '❌ მაქსიმუმ {max} ფოტო.',
        'photo_uploaded': '✅ ფოტო ატვირთულია!\n\nდაწერეთ თქვენს შესახებ (მაქსიმუმ 200 სიმბოლო) ან დააჭირეთ ⏩ გამოტოვება:',
        'photo_invalid': '❌ გთხოვთ, გაგზავნოთ ფოტო.',
        'enter_bio': 'დაწერეთ თქვენს შესახებ (მაქსიმუმ 200 სიმბოლო) ან დააჭირეთ ⏩ გამოტოვება:',
        'bio_skip': '⏩ გამოტოვება',
        'bio_text_only': '❌ გთხოვთ, შეიყვანოთ ტექსტი თქვენს შესახებ.',
        'bio_too_long': '❌ აღწერა ძალიან გრძელია. მაქსიმუმ {max} სიმბოლო.',
        'choose_interests': 'აირჩიეთ თქვენი ინტერესები (მაქსიმუმ 5). დააჭირეთ ღილაკებს ასარჩევად:',
        'interests_min': '❌ აირჩიეთ მინიმუმ ერთი ინტერესი',
        'interests_max': '❌ მაქსიმუმ {max} ინტერესი',
        'interests_done': '✅ მზადაა',
        'reg_complete': '✅ თქვენი ანკეტა შექმნილია!\n\nკეთილი იყოს თქვენი მობრძანება CITRAMON DATING-ში! 🎉',

        # Main menu
        'menu_feed': '❤️ ანკეტების ლენტა',
        'menu_matches': '💬 ჩემი მეჩები',
        'menu_profile': '👤 ჩემი პროფილი',
        'menu_photos': '🔍 ფოტოების ნახვა',
        'menu_edit': '✏️ რედაქტირება',
        'menu_support': '📞 მხარდაჭერა',
        'menu_delete': '🗑 ანკეტის წაშლა',
        'menu_admin': '🔧 ადმინი',
        'menu_language': '🌐 ენა',

        # Feed
        'feed_like': '❤️ მომწონს',
        'feed_skip': '👎 გამოტოვება',
        'feed_report': '🚨 ჩივილი',
        'feed_no_more': '😔 მეტი ანკეტა არ არის სანახავი',
        'feed_banned': '❌ თქვენი ანგარიში დაბლოკილია',
        'feed_like_sent': '❤️ მოწონება გაგზავნილია!',
        'feed_mutual': '❤️ ორმხრივი მოწონება! თქვენ დამეჩეთ!\n\nახლა შეგიძლიათ ესაუბროთ ამ მომხმარებელს.',
        'feed_mutual_partner': '❤️ ორმხრივი მოწონება! თქვენ დამეჩეთ {name}-თან!\n\nახლა შეგიძლიათ ესაუბროთ.',
        'complaint_choose': 'აირჩიეთ ჩივილის ტიპი:',
        'complaint_sent': '✅ ჩივილი გაგზავნილია. მადლობა მოდერაციაში დახმარებისთვის!',

        # Matches
        'no_matches': '😔 ჯერ არ გაქვთ მეჩები',
        'match_chat': '💬 ჩატი',
        'match_date': '📅 პაემანი',
        'match_view_profile': '👤 ანკეტა',
        'match_reviews': '📝 მიმოხილვები',

        # Chat
        'chat_history': '💬 შეტყობინებების ისტორია:\n\n',
        'chat_empty': '💬 შეტყობინებები არ არის. დაიწყეთ საუბარი!\n\n',
        'chat_send_prompt': '\nგაგზავნეთ შეტყობინება (ან დააჭირეთ ◀️ უკან):',
        'chat_msg_sent': '✅ შეტყობინება გაგზავნილია!\n\nშეგიძლიათ გააგრძელოთ საუბარი ან დააჭირეთ ◀️ უკან.',
        'chat_new_msg': '💬 ახალი შეტყობინება {name}-სგან:\n\n{text}',
        'chat_reply': '💬 პასუხი',

        # Date flow
        'date_choose_type': '📅 აირჩიეთ პაემნის ტიპი:',
        'date_online': '📱 ონლაინ',
        'date_offline': '🌟 ოფლაინ',
        'date_proposed_online': '📱 {name} გეპატიჟებათ ონლაინ პაემანზე!\n\nდაადასტურეთ ან უარყავით.',
        'date_proposed_offline': '🌟 {name} გეპატიჟებათ ოფლაინ პაემანზე!\n\nდაადასტურეთ ან უარყავით.',
        'date_sent': '✅ პაემნის მოწვევა გაგზავნილია! ველოდებით დადასტურებას.',
        'date_already_pending': '⏳ თქვენ უკვე გაქვთ აქტიური მოწვევა ამ მომხმარებელთან. დაელოდეთ პასუხს.',
        'date_accept': '✅ პაემნის დადასტურება',
        'date_decline': '❌ უარყოფა',
        'date_confirmed': '✅ პაემანი დადასტურებულია! როცა ადგილზე იქნებით, დააჭირეთ ღილაკს.',
        'date_confirmed_proposer': '✅ {name}-მ დაადასტურა პაემანი! როცა ადგილზე იქნებით, დააჭირეთ ღილაკს.',
        'date_confirmed_online': '✅ ონლაინ პაემანი დადასტურებულია!\n\n📱 გაუზიარეთ ვიდეოზარის ბმული პარტნიორს:\n• Zoom\n• Google Meet\n\nგაგზავნეთ ბმული ჩატში, შემდეგ დააჭირეთ ღილაკს «ადგილზე ვარ» როცა მზად იქნებით.',
        'date_confirmed_online_proposer': '✅ {name}-მ დაადასტურა ონლაინ პაემანი!\n\n📱 გაუზიარეთ ვიდეოზარის ბმული პარტნიორს:\n• Zoom\n• Google Meet\n\nგაგზავნეთ ბმული ჩატში, შემდეგ დააჭირეთ ღილაკს «ადგილზე ვარ» როცა მზად იქნებით.',
        'date_declined_you': '❌ თქვენ უარყავით პაემანი.',
        'date_declined_partner': '😔 პარტნიორმა უარყო პაემანი.',
        'date_arrived': '✅ ადგილზე ვარ',
        'date_arrived_ok': '✅ თქვენ მონიშნეთ! ველოდებით პარტნიორს.',
        'date_partner_arrived': '📍 თქვენი პარტნიორი უკვე ადგილზეა! მონიშნეთ, როცა მოხვალთ.',
        'date_both_arrived': '🎉 პაემანი {name}-თან შედგა!\n\nორივე მონაწილე ადგილზეა. სასიამოვნო დროს გისურვებთ!\n\nახლა შეგიძლიათ დატოვოთ მიმოხილვა და შეფასება.',
        'date_not_found': '❌ პაემანი ვერ მოიძებნა',
        'date_rate_prompt': '🌟 შეაფასეთ თქვენი პარტნიორი:',
        'date_need_both_arrived': '❌ ორივე მონაწილემ უნდა მონიშნოს "ადგილზე ვარ" მიმოხილვის დასატოვებლად!',

        # Rating
        'rate_positive': '😊 აირჩიეთ დადებითი თვისებები:',
        'rate_negative': '😮 აირჩიეთ უარყოფითი თვისებები:',
        'rate_saved': '✅ შეფასება შენახულია! პარტნიორის რეიტინგი განახლდა.',
        'rate_done': '✅ მზადაა',
        'rate_choose_anonymity': '🔒 როგორ გამოაქვეყნოთ მიმოხილვა?',
        'review_with_name': '📝 ჩემი სახელით',
        'review_anonymous': '🔒 ანონიმურად',
        'anonymous_reviewer': '🔒 ანონიმი',

        # Reviews
        'reviews_title': '📝 მიმოხილვები {name}-ზე\n\n',
        'reviews_empty': '📝 ჯერ არ არის მიმოხილვები ამ მომხმარებლის შესახებ.',
        'reviews_summary': '⭐ საშუალო რეიტინგი: {rating:.1f} ({count} მიმოხილვა)\n\n',
        'reviews_positive_summary': '✅ ხშირად აღნიშნავენ: {tags}\n',
        'reviews_negative_summary': '❌ შენიშვნები: {tags}\n',
        'reviews_item': '⭐ {stars}/5 — {positive}{negative}\n',

        # Profile
        'profile_title': '👤 თქვენი პროფილი\n\n',
        'profile_name': 'სახელი: {name}\n',
        'profile_age': 'ასაკი: {age}\n',
        'profile_city': 'ქალაქი: {city}\n',
        'profile_rating': '⭐ რეიტინგი: {rating:.1f} ({count} შეფასება)\n\n',
        'profile_bio': '📝 ჩემს შესახებ: {bio}\n\n',
        'profile_interests': '💫 ინტერესები: {interests}',
        'profile_not_found': '❌ პროფილი ვერ მოიძებნა',
        'no_photos': '❌ თქვენ არ გაქვთ ფოტოები',

        # Edit profile
        'edit_title': '✏️ რისი შეცვლა გსურთ?',
        'edit_name': '📝 სახელი',
        'edit_age': '🎂 ასაკი',
        'edit_city': '📍 ქალაქი',
        'edit_bio': '📄 ჩემს შესახებ',
        'edit_photo': '📷 ფოტო',
        'edit_interests': '💫 ინტერესები',
        'edit_enter_name': '📝 შეიყვანეთ ახალი სახელი (მაქსიმუმ 20 სიმბოლო):',
        'edit_enter_age': '🎂 შეიყვანეთ ახალი ასაკი:',
        'edit_choose_city': '📍 აირჩიეთ ახალი ქალაქი:',
        'edit_enter_bio': '📄 შეიყვანეთ ახალი აღწერა (მაქსიმუმ 200 სიმბოლო):',
        'edit_upload_photo': '📷 გაგზავნეთ ახალი ფოტო:',
        'edit_choose_interests': '💫 აირჩიეთ ახალი ინტერესები:',
        'edit_saved': '✅ ცვლილებები შენახულია!',

        # Delete profile
        'delete_confirm': '⚠️ ნამდვილად გსურთ თქვენი ანკეტის წაშლა?\n\nეს მოქმედება შეუქცევადია. ყველა თქვენი მონაცემი, მეჩები, შეტყობინებები და შეფასებები წაიშლება.',
        'delete_yes': '✅ დიახ, წაშლა',
        'delete_no': '❌ გაუქმება',
        'delete_done': '✅ თქვენი ანკეტა წაშლილია. მადლობა, რომ სარგებლობდით CITRAMON DATING-ით!\n\nახალი ანკეტის შესაქმნელად დაწერეთ /start',
        'delete_error': '❌ წაშლის შეცდომა. სცადეთ მოგვიანებით.',
        'delete_cancelled': '✅ წაშლა გაუქმებულია.',

        # Support
        'support_text': '📞 მხარდაჭერა\n\nადმინისტრატორთან დასაკავშირებლად დააჭირეთ ქვემოთ მოცემულ ბმულს:\n👉 [მიწერეთ ადმინს](tg://user?id={admin_id})',

        # Admin (admin panel stays in Russian)
        'admin_title': '🔧 Админ-панель',
        'admin_no_access': '❌ თქვენ არ გაქვთ წვდომა ადმინ-პანელზე',
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
        'admin_full_reset': '🔄 Обнулить анкету',
        'admin_unban': '🔓 Разблокировать',
        'admin_banned': '✅ Пользователь заблокирован',
        'admin_shadow_banned': '✅ Пользователь получил теневой бан',
        'admin_rating_reset': '✅ Рейтинг пользователя обнулен',
        'admin_full_reset_done': '✅ Анкета обнулена: рейтинг сброшен, все отзывы удалены',
        'admin_unbanned': '✅ Пользователь разблокирован',
        'admin_broadcast_prompt': 'Введите текст рассылки (или ◀️ Назад для отмены):',
        'admin_broadcast_done': '✅ Рассылка отправлена {count} пользователям',
        'admin_complaint_approved': '✅ Жалоба одобрена, пользователь теневой бан',
        'admin_complaint_rejected': '✅ Жалоба отклонена',
        'admin_approve': '✅ Одобрить',
        'admin_reject': '❌ Отклонить',

        # Language
        'language_changed': '✅ ენა შეიცვალა ქართულზე',
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
