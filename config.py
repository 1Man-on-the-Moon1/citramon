import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_NAME = 'CITRAMON DATING'
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1')
PSYCHOLOGIST_RATE_LIMIT_PER_MIN = int(os.getenv('PSYCHOLOGIST_RATE_LIMIT_PER_MIN', '5'))

# Static image shown after language selection.
# For Railway: keep the image inside the repo (e.g. `assets/welcome_lang.png`)
# and use a relative path so it exists in the deployed environment.
WELCOME_LANG_IMAGE_PATH = os.getenv(
    'WELCOME_LANG_IMAGE_PATH',
    os.path.join(os.path.dirname(__file__), 'assets', 'welcome_lang.png'),
)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set! Create a .env file with BOT_TOKEN=your_token")

if ADMIN_ID == 0:
    raise ValueError("ADMIN_ID is not set! Create a .env file with ADMIN_ID=your_telegram_id")

# Constants - Cities by country
USA_CITIES = [
    'Нью-Йорк', 'Лос-Анджелес', 'Чикаго', 'Хьюстон', 'Финикс',
    'Филадельфия', 'Сан-Антонио', 'Сан-Диего', 'Даллас', 'Сан-Хосе',
    'Остин', 'Джэксонвилл', 'Форт-Уэрт', 'Коламбус', 'Шарлотт',
    'Сан-Франциско', 'Индианаполис', 'Сиэтл', 'Денвер', 'Оклахома-Сити',
    'Нашвилл', 'Эль-Пасо', 'Вашингтон', 'Лас-Вегас', 'Мемфис',
    'Портленд', 'Детройт', 'Луисвилл', 'Балтимор', 'Милуоки',
    'Альбукерке', 'Тусон', 'Фресно', 'Сакраменто', 'Меса',
    'Канзас-Сити', 'Атланта', 'Омаха', 'Колорадо-Спрингс', 'Роли',
    'Лонг-Бич', 'Вирджиния-Бич', 'Окленд', 'Майами', 'Миннеаполис',
    'Арлингтон (Техас)', 'Талса', 'Бейкерсфилд', 'Уичито', 'Тампа',
    'Орландо', 'Аврора (Колорадо)', 'Новый Орлеан'
]

GEORGIA_CITIES = ['Тбилиси', 'Кутаиси', 'Батуми', 'Рустави', 'Зугдиди', 'Поти']

BELARUS_CITIES = ['Минск', 'Брест', 'Витебск', 'Гомель', 'Гродно', 'Могилёв']

UK_CITIES = [
    'Лондон', 'Бирмингем', 'Глазго', 'Манчестер', 'Лидс',
    'Ливерпуль', 'Ньюкасл-апон-Тайн', 'Ноттингем', 'Шеффилд', 'Бристоль'
]

SPAIN_CITIES = ['Мадрид', 'Барселона', 'Валенсия', 'Севилья', 'Сарагоса']

GERMANY_CITIES = [
    'Берлин', 'Гамбург', 'Мюнхен', 'Кёльн', 'Франкфурт-на-Майне',
    'Штутгарт', 'Дюссельдорф', 'Дортмунд', 'Эссен', 'Лейпциг',
    'Бремен', 'Дрезден', 'Ганновер', 'Нюрнберг', 'Дуйсбург',
    'Бохум', 'Вупперталь'
]

MEXICO_CITIES = [
    'Мехико', 'Гвадалахара', 'Монтеррей', 'Пуэбла', 'Толука',
    'Тихуана', 'Леон', 'Хуарес (Сьюдад-Хуарес)', 'Торреон',
    'Сан-Луис-Потоси', 'Керетаро', 'Мерида', 'Чихуахуа',
    'Агуаскальентес', 'Морелия', 'Сальтильо', 'Эрмосильо',
    'Кулиакан', 'Веракрус', 'Тустла-Гутьеррес', 'Вильяермоса',
    'Дуранго', 'Акапулько', 'Четумаль', 'Ногалес'
]

RUSSIA_CITIES = [
    'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань',
    'Нижний Новгород', 'Челябинск', 'Красноярск', 'Самара', 'Уфа',
    'Ростов-на-Дону', 'Краснодар', 'Омск', 'Воронеж', 'Пермь',
    'Волгоград', 'Саратов', 'Тюмень', 'Тольятти', 'Ижевск',
    'Барнаул', 'Ульяновск', 'Иркутск', 'Хабаровск', 'Ярославль',
    'Владивосток', 'Махачкала', 'Томск', 'Оренбург', 'Кемерово',
    'Новокузнецк', 'Рязань', 'Астрахань', 'Набережные Челны', 'Пенза',
    'Липецк', 'Киров', 'Чебоксары', 'Тула', 'Калининград',
    'Курск', 'Севастополь', 'Сочи', 'Ставрополь', 'Улан-Удэ',
    'Тверь', 'Магнитогорск', 'Иваново', 'Брянск', 'Белгород',
    'Сургут', 'Владимир', 'Архангельск', 'Чита', 'Нижний Тагил'
]

ALL_CITIES = USA_CITIES + GEORGIA_CITIES + BELARUS_CITIES + UK_CITIES + SPAIN_CITIES + GERMANY_CITIES + MEXICO_CITIES + RUSSIA_CITIES

COUNTRIES = {
    'usa': {
        'ru': '🇺🇸 США',
        'en': '🇺🇸 USA',
        'ka': '🇺🇸 აშშ',
        'es': '🇺🇸 EE.UU.',
        'de': '🇺🇸 USA',
        'cities': USA_CITIES
    },
    'georgia': {
        'ru': '🇬🇪 Грузия',
        'en': '🇬🇪 Georgia',
        'ka': '🇬🇪 საქართველო',
        'es': '🇬🇪 Georgia',
        'de': '🇬🇪 Georgien',
        'cities': GEORGIA_CITIES
    },
    'belarus': {
        'ru': '🇧🇾 Беларусь',
        'en': '🇧🇾 Belarus',
        'ka': '🇧🇾 ბელარუსი',
        'es': '🇧🇾 Bielorrusia',
        'de': '🇧🇾 Belarus',
        'cities': BELARUS_CITIES
    },
    'uk': {
        'ru': '🇬🇧 Великобритания',
        'en': '🇬🇧 United Kingdom',
        'ka': '🇬🇧 გაერთიანებული სამეფო',
        'es': '🇬🇧 Reino Unido',
        'de': '🇬🇧 Vereinigtes Königreich',
        'cities': UK_CITIES
    },
    'spain': {
        'ru': '🇪🇸 Испания',
        'en': '🇪🇸 Spain',
        'ka': '🇪🇸 ესპანეთი',
        'es': '🇪🇸 España',
        'de': '🇪🇸 Spanien',
        'cities': SPAIN_CITIES
    },
    'germany': {
        'ru': '🇩🇪 Германия',
        'en': '🇩🇪 Germany',
        'ka': '🇩🇪 გერმანია',
        'es': '🇩🇪 Alemania',
        'de': '🇩🇪 Deutschland',
        'cities': GERMANY_CITIES
    },
    'mexico': {
        'ru': '🇲🇽 Мексика',
        'en': '🇲🇽 Mexico',
        'ka': '🇲🇽 მექსიკა',
        'es': '🇲🇽 México',
        'de': '🇲🇽 Mexiko',
        'cities': MEXICO_CITIES
    },
    'russia': {
        'ru': '🇷🇺 Россия',
        'en': '🇷🇺 Russia',
        'ka': '🇷🇺 რუსეთი',
        'es': '🇷🇺 Rusia',
        'de': '🇷🇺 Russland',
        'cities': RUSSIA_CITIES
    },
}

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

ZODIAC_SIGNS = [
    'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
    'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'
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
