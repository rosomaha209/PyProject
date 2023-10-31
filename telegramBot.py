import requests
import telebot
from telebot import types

bot = telebot.TeleBot("6772188030:AAH-RUxQoglEmghlIujwEifALFn01eaw6ZA")


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    mess = f'Привіт <b>{message.from_user.first_name}</b>,тут ти можеш дізнатися що віщують тобі зірки, щоб продовжити зайди в меню, або набери /menu'
    bot.send_message(message.chat.id, mess, parse_mode='html')

    @bot.message_handler(func=lambda msg: True)
    def echo_all(message):
        bot.reply_to(message, "Для того щоб дізнатися гороскоп небери: /menu")


ukr_to_eng_horoscope = {
    "It may be that you've come back deeply changed from a long voyage. Of course, travel changes everyone to some extent, but in your case, the change is more profound. You're going to have a problem getting back into your old life. It may feel too limiting for you. So what are you waiting for? Change it!": "Можливо, ви повернулися глибоко зміненими після довгої подорожі. Звичайно, подорожі певною мірою змінюють кожного, але у вашому випадку зміни більш глибокі. У вас виникнуть проблеми з поверненням до старого життя. Це може здатися вам занадто обмежуючим. Так чого ви чекаєте? Зміни це!",
    "The solar system is liable to trigger a transformation that will last several months. The change will center on the means you use to fulfill yourself in terms of your career and love life. If you feel hemmed in by your training or upbringing, you can expect to seek liberation from these inhibitions in the months to come.": "Сонячна система може спровокувати трансформацію, яка триватиме кілька місяців. Зміна буде зосереджена на засобах, які ви використовуєте для самореалізації в плані кар’єри та любовного життя. Якщо ви відчуваєте себе обмеженими своїм навчанням або вихованням, ви можете очікувати, що протягом наступних місяців ви зможете звільнитися від цих обмежень.",
    "Change": "Змінити"
    # Додайте відповідність для інших гороскопів
}
ukr_to_eng_zodiac = {
    "Овен": "Aries",
    "Телець": "Taurus",
    "Близнюки": "Gemini",
    "Рак": "Cancer",
    "Лев": "Leo",
    "Діва": "Virgo",
    "Терези": "Libra",
    "Скорпіон": "Scorpio",
    "Стрілець": "Sagittarius",
    "Козеріг": "Capricorn",
    "Водолій": "Aquarius",
    "Риби": "Pisces"
}
# Словник для перекладу днів тижня
ukr_to_eng_days = {
    "СЬОГОДНІ": "TODAY",
    "ЗАВТРА": "TOMORROW",
    "УЧОРА": "YESTERDAY",
    # Додайте інші переклади, якщо потрібно
}


@bot.message_handler(commands=['menu'])
def menu(message):
    mess = 'Виберіть хто ви по гороскопу:'
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row("Овен", "Телець", "Близнюки")
    markup.row("Рак", "Лев", "Діва")
    markup.row("Терези", "Скорпіон", "Стрілець")
    markup.row("Козеріг", "Водолій", "Риби")
    sent_msg = bot.send_message(
        message.chat.id, mess, reply_markup=markup)
    bot.register_next_step_handler(sent_msg, day_handler)


def day_handler(message):
    mess = "Який день ви хочете знати?\nВиберіть один: *СЬОГОДНІ*, *ЗАВТРА*, *УЧОРА* або дату у форматі РРРР-ММ-ДД."
    ukrainian_sign = message.text
    english_sign = ukr_to_eng_zodiac.get(ukrainian_sign)
    if english_sign:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("СЬОГОДНІ", "ЗАВТРА")
        markup.add("УЧОРА")
        sent_msg = bot.send_message(
            message.chat.id, mess, reply_markup=markup)
        bot.register_next_step_handler(sent_msg, fetch_horoscope, english_sign)
    else:
        bot.send_message(message.chat.id, "Оберіть один з варіантів зі списку.")


def fetch_horoscope(message, sign):
    day = message.text
    ukrainian_time = day
    english_time = ukr_to_eng_days.get(ukrainian_time)
    if english_time:
        horoscope = get_daily_horoscope(sign, english_time)
        data = horoscope["data"]
        translated_horoscope = translate_text(
            ukr_to_eng_horoscope.get(data["horoscope_data"], data["horoscope_data"]),
            source_lang="en",  # Перекладаємо з англійської
            target_lang="uk"  # Перекладаємо на українську
        )
        horoscope_message = f'*Гороскоп:* {translated_horoscope} \n*Знак:* {sign} \n*День:* {ukrainian_time}'
        bot.send_message(message.chat.id, "Ось ваш гороскоп!")
        bot.send_message(message.chat.id, horoscope_message, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Оберіть один з варіантів зі списку.")

def get_daily_horoscope(sign: str, day: str) -> dict:
    """Отримати щоденний гороскоп для знака зодіаку.
    Аргументи ключових слів:
    sign:str - знак зодіаку
    day:str - дата у форматі (РРРР-ММ-ДД) АБО СЬОГОДНІ АБО ЗАВТРА АБО ВЧОРА
    Return:dict – дані JSON
    """
    url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
    params = {"sign": sign, "day": day}
    response = requests.get(url, params)

    return response.json()


def translate_text(text, source_lang, target_lang):
    url = "https://translated-mymemory---translation-memory.p.rapidapi.com/get"
    querystring = {
        "langpair": f"{source_lang}|{target_lang}",
        "q": text,
        "mt": "1",
        "onlyprivate": "0",
        "de": "a@b.c"
    }

    headers = {
        "X-RapidAPI-Key": "2a9f6b760dmsh6ddc4270410ad7cp1a29f6jsn72bd39472d4f",
        "X-RapidAPI-Host": "translated-mymemory---translation-memory.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    translation_data = response.json()

    if "responseData" in translation_data:
        translated_text = translation_data["responseData"]["translatedText"]
        return translated_text

    return "Помилка перекладу"  # Якщо щось пішло не так


print(translate_text("Hello Roman", source_lang="en", target_lang="uk"))
bot.infinity_polling()
