import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_NAME = 'ЦИТРАМОН'
BOT_TOKEN = os.getenv('BOT_TOKEN', '8611752604:AAFH3iCc_0X6bWXa1jP9fqjLJm0s48vdE4Q')
ADMIN_ID = int(os.getenv('ADMIN_ID', '783321437'))

# Constants
BELARUS_CITIES = ['Минск', 'Брест', 'Витебск', 'Гомель', 'Гродно', 'Могилёв']

INTERESTS = [
    'Спорт', 'Кино', 'Игры', 'Музыка', 'Путешествия',
    'Кофе', 'Книги', 'Прогулки', 'IT', 'Кулинария',
    'Животные', 'Йога', 'Искусство', 'Авто/Мото', 'Танцы',
    'Фотография', 'Походы', 'Театр'
]

POSITIVE_TAGS = [
    'Соответствует фото',
    'Интересный собеседник',
    'Пунктуальность',
    'Вежливость',
    'Опрятный вид',
    'Харизма'
]

NEGATIVE_TAGS = [
    'Не соответствует фото',
    'Скука',
    'Опоздание',
    'Токсичность',
    'Постоянно в телефоне'
]

COMPLAINT_TYPES = [
    'Не пришёл на встречу',
    'Фейк',
    'Агрессия'
]

# Limits
MAX_PHOTOS = 1
MAX_BIO_LENGTH = 200
MAX_NAME_LENGTH = 20
MAX_INTERESTS = 5
MIN_AGE = 18
MAX_AGE = 120

# Newbie boost duration (in hours)
NEWBIE_BOOST_HOURS = 48

# Rating publication delay (in hours)
RATING_PUBLICATION_DELAY_HOURS = 24
