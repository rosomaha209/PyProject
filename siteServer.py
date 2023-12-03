import json
import os
import random
import string
from datetime import datetime

from flask import Flask, render_template, request, redirect, session, flash, url_for, abort
from werkzeug.utils import secure_filename
from wether import get_weather

from Translator import translate_text
from horoscope import get_daily_horoscope, zodiac_sign
from messages import get_dialogs, add_message
from news import get_latest_news

app = Flask(__name__)
app.secret_key = '1234'  # Встановіть власний секретний ключ

messages_with_friend = 'messages.json'


# Функція для генерації унікального userid
def generate_userid():
    return ''.join(random.choices(string.digits, k=10))


def is_user_authenticated():
    return 'userid' in session

@app.route('/game')
def game():
    return render_template('game.html')
@app.route('/logout', methods=['POST'])
def logout():
    # Очистка сесії
    session.clear()
    flash('Ви вийшли з системи', 'success')
    return redirect('/register')  # Повернення на головну сторінку або іншу, якщо потрібно


# Зчитування користувачів з файлу
def read_users():
    try:
        with open('all_users_data.json', 'r') as file:
            users_data = json.load(file)
    except FileNotFoundError:
        users_data = []
    return users_data


def get_user_by_id(userid, users_data):
    for user in users_data:
        if user['userid'] == userid:
            return user
    return None  # Повертаємо None, якщо користувача з таким ID не знайдено


def update_user_data(userid, **kwargs):
    try:
        # Зчитування наявних даних користувачів
        with open('all_users_data.json', 'r') as file:
            all_users_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Якщо файл порожній або відсутній, почнемо з порожнього списку
        all_users_data = []

    # Пошук користувача з вказаним userid
    user_index = next((index for index, user in enumerate(all_users_data) if user.get('userid') == userid), None)
    if user_index is not None:
        # Якщо користувач знайдений, оновіть його дані з вказаними аргументами
        all_users_data[user_index].update(kwargs)
    else:
        # Якщо користувача не знайдено, створіть нового користувача з новими даними
        user_data = {'userid': userid, **kwargs}
        all_users_data.append(user_data)

    # Збереження оновлених даних користувачів у файл
    with open('all_users_data.json', 'w') as file:
        json.dump(all_users_data, file, indent=5)


# Приклад виклику функції збереження даних користувача
update_user_data(userid='1234567890', username='JohnDoe', email='john@example.com', password='password123',
                 city='New York',
                 photo_path='static\\none.jpg')
update_user_data(userid='1234567890', usersurname='Mehailov')


@app.route('/settings')
def settings():
    def some_secure_page():
        if not is_user_authenticated():
            flash('Будь ласка, увійдіть або зареєструйтеся, щоб переглянути цю сторінку', 'danger')
            return redirect('/register')

        # Якщо користувач авторизований, виконайте логіку для цієї сторінки
        users_data = read_users()  # Відображення сторінки налаштувань для першого користувача у списку
        userid = session.get('userid')
        user = get_user_by_id(userid, users_data)
        # Поверніть сторінку профілю разом із постами
        return render_template('settings.html', user=user)

    return some_secure_page()


@app.route('/update_settings', methods=['POST'])
def update_settings():
    userid = session.get('userid')
    # Отримання даних з форми
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    city = request.form['city']
    usersurname = request.form['usersurname']
    dateofbirth = request.form['dateofbirth']

    # Перевірка, чи було надіслано фото
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != '' and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            # Збереження фото у папці користувача за його ідентифікатором
            photo_path = os.path.join('static', f'{userid}_{filename}')
            photo.save(photo_path)

            # Оновлення даних користувача з новим фото
            update_user_data(userid=userid,
                             username=username,
                             email=email,
                             password=password,
                             city=city,
                             photo_path=photo_path,
                             usersurname=usersurname,
                             dateofbirth=dateofbirth
                             )

            flash("Фото профілю було успішно змінено", "success")
            return redirect(url_for('settings'))
        elif photo.filename == '':
            # Оновлення даних користувача без зміни фото, якщо файл не було вибрано
            update_user_data(userid=userid,
                             username=username,
                             email=email,
                             password=password,
                             city=city,
                             usersurname=usersurname,
                             dateofbirth=dateofbirth
                             )

            flash("Дані користувача були успішно змінені", "success")
            return redirect(url_for('settings'))
        else:
            flash("Помилка при завантаженні нового фото", "error")
            return redirect(url_for('settings'))
    else:
        # Оновлення даних користувача без зміни фото, якщо файл не було надіслано
        update_user_data(userid=userid,
                         username=username,
                         email=email,
                         password=password,
                         city=city,
                         usersurname=usersurname,
                         dateofbirth=dateofbirth
                         )

        flash("Дані користувача були успішно змінені", "success")
        return redirect(url_for('settings'))


@app.route('/friends/<username>')
def friends(username):
    userid = session.get('userid')
    users = read_users()
    friends_list = get_user_friends(userid)
    print(friends_list)
    photos = [get_user_photo_path(friend_id) for friend_id in friends_list]
    print(photos)
    name = [get_user_name(friend_id) for friend_id in friends_list]
    return render_template('friends.html', username=username, friends=friends_list, all_users=users, photo=photos,
                           name=name)


def get_user_photo_path(userid):
    # Завантажити дані з JSON файлу
    with open('all_users_data.json', 'r', encoding='utf-8') as file:
        users_data = json.load(file)

    # Пошук користувача за userid та отримання шляху до фото
    for user in users_data:
        if user.get('userid') == userid:
            return user.get('photo_path', '')

    return 'static\\none.jpg'  # Повертає порожню аватарку, якщо userid не знайдено


def get_user_name(userid):
    # Завантажити дані з JSON файлу
    with open('all_users_data.json', 'r', encoding='utf-8') as file:
        users_data = json.load(file)

    # Пошук користувача за userid та отримання шляху до фото
    for user in users_data:
        if user.get('userid') == userid:
            return user.get('username', '')

    return 'безіменний'  # Повертає, якщо userid не знайдено


def get_user_friends(userid):
    try:
        with open('friends_data.json', 'r') as file:
            friends_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Повертаємо пустий список, якщо немає даних про друзів або файл не знайдено

    return friends_data.get(userid,
                            [])  # Повертаємо список друзів для вказаного користувача або порожній список,
    # якщо користувача немає у списку друзів


def update_friends(userid, friend_userid):
    try:
        with open('friends_data.json', 'r') as file:
            friends_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        friends_data = {}

    if userid not in friends_data:
        friends_data[userid] = []

    if friend_userid not in friends_data[userid]:
        friends_data[userid].append(friend_userid)

    if friend_userid not in friends_data:
        friends_data[friend_userid] = []

    if userid not in friends_data[friend_userid]:
        friends_data[friend_userid].append(userid)

    with open('friends_data.json', 'w') as file:
        json.dump(friends_data, file, indent=5)
    return True  # Повертаємо True після успішного додавання друзів


@app.route('/add_friend', methods=['POST'])
def add_friend_route():
    userid = session.get('userid')
    friend_userid = request.form['friend_userid']

    if update_friends(userid, friend_userid):  # Оновити список друзів
        flash("Друг доданий до списку друзів.", "success")

        return redirect('/friends/<username>')
    else:
        flash("Не вдалося додати друга.", "error")
        return "Не вдалося додати друга. Перевірте імена користувачів."


def remove_friend(userid, friend_userid):
    try:
        with open('friends_data.json', 'r') as file:
            friends_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        friends_data = {}

    if userid in friends_data and friend_userid in friends_data[userid]:
        friends_data[userid].remove(friend_userid)
        friends_data[friend_userid].remove(userid)

        with open('friends_data.json', 'w') as file:
            json.dump(friends_data, file, indent=5)
        return True
    else:
        return False


@app.route('/remove_friend', methods=['POST'])
def remove_friend_route():
    userid = session.get('userid')
    friend_userid = request.form['friend_userid']

    if remove_friend(userid, friend_userid):
        flash("Друг видалений зі списку друзів.", "success")
    else:
        flash("Не вдалося видалити друга.", "error")

    return redirect('/friends/<username>')


def allowed_file(filename):
    # Допустимі розширення файлів (зображень)
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}

    # Перевірте, чи розширення файлу є в допустимих розширеннях
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/')
def home():
    return redirect('/register')


@app.route('/news', methods=['GET', 'POST'])
def news():
    country = 'ua'
    category = 'science'
    username = session.get("username")

    if request.method == 'POST':
        category = request.form.get('category')
        latest_news = get_latest_news(country, category)
    else:
        # За замовчуванням виводимо загальні новини
        latest_news = get_latest_news(country, 'general')

    if latest_news:
        return render_template('news.html', news=latest_news, category=category, username=username)
    else:
        # Якщо отримання новин не вдалося, виведемо повідомлення про помилку
        return "Не вдалося отримати актуальні новини."


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Обробка даних форми при POST-запиті
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Перевірка, чи користувач вже існує
        if is_user_exists(email):
            flash('Користувач з таким емайл адресою  вже зареэстрований', 'danger')
            return redirect('/register')

        # Генерування унікального userid
        userid = generate_userid()
        # Збереження користувача в базу даних
        update_user_data(userid=userid, username=username, email=email, password=password)
        # Встановлення сесійних змінних після реєстрації
        session['userid'] = userid
        session['username'] = username
        session['email'] = email
        session['password'] = password
        flash('Ви успішно зареєстровані!', 'success')
        return redirect('/SocialNetwork.html')

    # Відображення сторінки реєстрації при GET-запиті
    return render_template('register.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    def some_secure_page():
        if not is_user_authenticated():
            flash('Будь ласка, увійдіть або зареєструйтеся, щоб переглянути цю сторінку', 'danger')
            return redirect('/register')

        # Якщо користувач авторизований, виконайте логіку для цієї сторінки
        username = session.get('username')
        email = session.get('email')
        password = session.get('password')

        if request.method == 'POST':
            post_content = request.form.get('post-content')
            username = session.get('username')

            # Збережіть новий пост у файлі разом з часом та іменем
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            with open('posts.txt', 'a') as file:
                file.write(f"{username} ({formatted_datetime}), {post_content}\n")

        # Зчитайте пости з файлу
        with open('posts.txt', 'r') as file:
            posts = file.readlines()
            postsreversed = list(reversed(posts))

        # Поверніть сторінку профілю разом із постами
        return render_template("profile.html", username=username, email=email, password=password, posts=postsreversed)

    return some_secure_page()


@app.route('/update_weather', methods=['GET', 'POST'])
def update_weather():
    # lat = session.get('lat') # Отримуємо широту
    # lon = session.get('lon') # Отримуємо довготу
    # city = get_city_name(lat,lon) # Отримуэмо місто на основі координат
    users_data = read_users()  # Зчитуємо всіх користувачів
    userid = session.get('userid')  # Витягуємо ІД із сесії
    user = get_user_by_id(userid, users_data)  # Отримуємо інпрориацію про активного користувача
    city = user["city"]  # Отримайте місто з сесії
    weather = get_weather(city)  # Отримати оновлені погодні дані
    translate_water = translate_text(weather, "en", "uk")  # Перекладаємо на українську
    print("погода по виклику функції update_weather(): ", translate_water)  #
    update_user_data(userid=userid, weather=translate_water)

    return redirect('/SocialNetwork.html')  # Повернення на сторінку після оновлення гороскопу


@app.route('/update_horoscope', methods=['GET', 'POST'])
def update_horoscope():
    users_data = read_users()  # Зчитуємо всіх користувачів
    userid = session.get('userid')  # Витягуємо ІД із сесії
    user = get_user_by_id(userid, users_data)  # Отримуємо інформацію про активного користувача
    if "dateofbirth" in user:
        dateofbirth = user["dateofbirth"]
    else:
        # Обробка випадку, коли параметр "city" відсутній
        dateofbirth = "1111-11-11"

    sign = zodiac_sign(dateofbirth)  # Отримуємо знак зодіаку з дати народження
    update_user_data(userid=userid, sign=sign)  # Записуємо знак зодіаку в файл
    horoscope = get_daily_horoscope(sign, "TODAY")

    horoscopedata = horoscope['data']

    dateh = horoscopedata['date']

    datah = horoscopedata['horoscope_data']

    translatehorosckop = translate_text(datah, 'en', 'uk')
    translatehorosckopdate = translate_text(dateh, 'en', 'uk')
    translatehorosckopsign = translate_text(sign, 'en', 'uk')
    print("Гороскоп по виклику функції update_horoscope(): ", translatehorosckop)
    update_user_data(userid=userid, translatehorosckop=translatehorosckop,
                     translatehorosckopdate=translatehorosckopdate,
                     translatehorosckopsign=translatehorosckopsign)  # Записуємо знак зодіаку в файл
    return redirect('/SocialNetwork.html')  # Повернення на сторінку після оновлення гороскопу


@app.route('/SocialNetwork.html')
def socialnetwork():
    def some_secure_page():
        if not is_user_authenticated():
            flash('Будь ласка, увійдіть або зареєструйтеся, щоб переглянути цю сторінку', 'danger')
            return redirect('/register')
        users_data = read_users()  # Зчитуємо всіх користувачів
        userid = session.get('userid')  # Витягуємо ІД із сесії
        user = get_user_by_id(userid, users_data)  # Отримуємо інпрориацію про активного користувача
        if "city" in user:
            city = user["city"]
        else:
            # Обробка випадку, коли параметр "city" відсутній
            city = "Місто не вказано"

        if "photo_path" in user:
            photo_path = user["photo_path"]
        else:
            # Обробка випадку, коли параметр "city" відсутній
            photo_path = "static\\none.jpg"

        if "dateofbirth" in user:
            dateofbirth = user["dateofbirth"]
        else:
            # Обробка випадку, коли параметр "city" відсутній
            dateofbirth = "1111-11-11"

        if "weather" in user:
            weather = user["weather"]
        else:
            # Обробка випадку, коли параметр "city" відсутній
            weather = "Помилка отримання погоди"

        if "translatehorosckop" in user:
            translatehorosckop = user["translatehorosckop"]
        else:
            # Обробка випадку, коли параметр "дати гороскопу" відсутній
            translatehorosckop = "Помилка отримання дати"

        if "translatehorosckopdate" in user:
            translatehorosckopdate = user["translatehorosckopdate"]
        else:
            # Обробка випадку, коли параметр "перекладеного тексту" відсутній
            translatehorosckopdate = "Помилка отримання гороскопу"

        if "translatehorosckopsign" in user:
            translatehorosckopsign = user["translatehorosckopsign"]
        else:
            # Обробка випадку, коли параметр "перекладенийзнак" відсутній
            translatehorosckopsign = "Помилка отримання знаку зодіаку"

        userid = session.get('userid')  # Отримуємо userid користувача з сесії
        username = session.get('username')  # Отримуємо ім'я користувача з сесії
        email = session.get('email')  # Отримуємо email користувача з сесії
        password = session.get('password')  # Отримуємо password користувача з сесії
        print(username, password, email)
        return render_template("SocialNetwork.html", username=username, email=email, password=password,
                               weather=weather, city=city, userid=userid, photo=photo_path,
                               sign=translatehorosckopsign,
                               horoscope=translatehorosckop, horoscopedate=translatehorosckopdate)

    return some_secure_page()


# Перевірка, чи користувача з такою електронною адресою не існує вже
def is_user_exists(email):
    users = read_users()
    for user in users:
        if user['email'] == email:
            return True
    return False


@app.route('/create_post', methods=['POST'])
def create_post():
    if request.method == 'POST':
        post_content = request.form.get('post-content')
        username = session.get('username')

        # Отримати поточну дату та час
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # Створіть рядок для збереження у файлі, включаючи ім'я користувача, дату і час
        post_entry = f"{username}, {formatted_datetime},{post_content}\n"

        # Збережіть новий пост у файлі
        with open('posts.txt', 'a') as file:
            file.write(post_entry)
        # Ви можете використовувати базу даних або файли для збереження постів

        # Після збереження посту перенаправте користувача на сторінку /profile.html
        return redirect('/profile')


def find_user(email, login_password):
    users = read_users()  # Функція для читання користувачів з файлу
    for user in users:
        if user['email'] == email and user['password'] == login_password:
            return user
    return None


@app.route('/message', methods=['GET', 'POST'])
def message():
    # Перевірка, чи існує сесія та username
    if 'userid' not in session or not session['userid']:
        abort(401)  # 401 - Unauthorized

    # Отримання всіх діалогів користувача
    user_dialogs = get_dialogs(session['userid'])

    # Виведення діалогів для перевірки
    print("User dialogs:", user_dialogs)

    # Логіка виведення повідомлень
    return render_template("message.html", dialogs=user_dialogs, username=session.get("username"),
                           userid=session.get("userid"))


@app.route('/send_message', methods=['GET', 'POST'])
def send_message():

    if 'userid' not in session or not session['userid']:
        abort(401)  # 401 - Unauthorized


    if request.method == 'POST':

        new_message_content = request.form.get('message')
        print(new_message_content)
        friend_userid = request.form.get('friend_userid')
        print(friend_userid, "Ід друга з яким ведеться переписка")

        if not new_message_content:
            return render_template("error.html", message="Порожній вміст повідомлення.")

        userid = session.get("userid")

        add_message(userid, friend_userid, new_message_content)

        return redirect(url_for('message_with_friend', friend_userid=friend_userid))

    # Цей рядок виконується тільки при GET-запитах, не пов'язаних з відправкою повідомлення
    return render_template("message_with_friend.html")


@app.route('/message/<friend_userid>', methods=['GET', 'POST'])
def message_with_friend(friend_userid):
    username = session.get("username")
    userid = session.get("userid")

    if not username or not userid:
        abort(401)  # Unauthorized
    # Зчитуємо дані з файлу JSON
    with open('all_users_data.json', 'r') as file:
        users_data = json.load(file)
    users_dict = {user['userid']: user['username'] for user in users_data} # Перетворюємо список користувачів у
    # словник для зручності
    user_dialogs = get_dialogs(userid)
    friend_dialog = user_dialogs.get(friend_userid, [])
    friend_username = get_user_name(friend_userid)
    print(user_dialogs, 'user_dialogs')
    print(friend_dialog, 'friend_dialog')
    print(friend_userid, 'friend_userid')

    if request.method == 'POST':
        new_message_content = request.form.get('message')
        if not new_message_content:
            return render_template("error.html", message="Порожній вміст повідомлення.")

        add_message(userid, friend_userid, new_message_content)
        return redirect(url_for('message_with_friend', friend_userid=friend_userid))

    return render_template("message_with_friend.html", dialogs=user_dialogs,
                           messages=friend_dialog, userid=userid, username=username,
                           friend_userid=friend_userid,friend_username=friend_username,users_dict=users_dict)


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('login-email')
        login_password = request.form.get('login-password')

        # Перевірка, чи існує користувач з такою електронною адресою та паролем
        user = find_user(email, login_password)

        if user:
            # Успішний вхід - встановлення сесійних змінних
            session['userid'] = user['userid']
            session['username'] = user['username']
            session['email'] = user['email']
            session['password'] = user['password']
            flash("Ви успішно увійшли в систему", "success")
            return redirect('/SocialNetwork.html')
        else:
            # Помилка входу
            flash("Неправильна електронна адреса або пароль", "error")
            return redirect('/register')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)  # Змініть 'port' на потрібний номер порту
