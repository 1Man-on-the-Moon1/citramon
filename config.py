import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_NAME = 'CITRAMON DATING'
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set! Create a .env file with BOT_TOKEN=your_token")

if ADMIN_ID == 0:
    raise ValueError("ADMIN_ID is not set! Create a .env file with ADMIN_ID=your_telegram_id")

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
    'Фейк'
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

# Rating configuration
RATING_PRIOR_WEIGHT = 2  # Bayesian prior weight
RATING_PRIOR_VALUE = 5.0  # Starting rating for new users
