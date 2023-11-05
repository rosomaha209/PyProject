import json
from wether import get_weather
from Translator import translate_text


from flask import Flask, render_template, request, redirect, session, flash

app = Flask(__name__)
app.secret_key = '1234'  # Встановіть власний секретний ключ

# Створюємо  файл для збереження користувачів
users_file = 'users.json'


# Зчитайте користувачів з файлу при запуску додатка
def read_users_from_file():
    try:
        with open(users_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def is_user_logged_in():
    return 'username' in session


@app.route('/home.html')
def home():
    return render_template('home.html')


@app.route('/register.html')
def registers():
    return render_template('register.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' in session:
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
    else:
        return redirect('/register.html')  # Перенаправте користувача на сторінку авторизації, якщо він не залогінений


@app.route('/SocialNetwork.html')
def socialnetwork():
    # lat = session.get('lat') # Отримуємо широту
    # lon = session.get('lon') # Отримуємо довготу
    # sity = get_city_name(lat,lon)
    city = get_selected_city()
    print(city)
    wether = get_weather(city)
    translate_water = translate_text(wether, "en", "uk")
    username = session.get('username')  # Отримуємо ім'я користувача з сесії
    email = session.get('email')  # Отримуємо email користувача з сесії
    password = session.get('password')  # Отримуємо password користувача з сесії
    return render_template("SocialNetwork.html", username=username, email=email, password=password,
                           wether=translate_water,city=city)


def get_selected_city():
    try:
        with open('selected_city.json', 'r') as file:
            data = json.load(file)
            return data['city']
    except FileNotFoundError:
        return None  # Повернемо None, якщо файл не знайдено


# Збережіть користувачів у файлі
def save_users_to_file(users):
    with open(users_file, 'w') as file:
        json.dump(users, file)


# Перевірка, чи користувача з таким іменем не існує вже
def is_user_exists(username):
    users = read_users_from_file()
    for user in users:
        if user['username'] == username:
            return True
    return False


# Додавання нового користувача
def add_user(username, email, password):
    users = read_users_from_file()
    users.append({'username': username, 'email': email, 'password': password})
    save_users_to_file(users)


from datetime import datetime


@app.route('/wether', methods=['POST'])
def save_city():
    if request.method == 'POST':
        city = request.form['city']  # Отримання міста, введеного користувачем з форми
        username = session.get('username')  # Отримання імені користувача з сесії

        # Створення структури даних з містом та ім'ям користувача
        data = {'city': city, 'username': username}

        # Збереження структури даних у файлі у форматі JSON
        with open('selected_city.json', 'w') as file:
            json.dump(data, file)

        # Перенаправте користувача на сторінку /profile після збереження міста
        return redirect('/SocialNetwork.html')


@app.route('/create_post', methods=['POST'])
def create_post():
    if request.method == 'POST':
        post_content = request.form.get('post-content')
        username = session.get('username')

        # Отримати поточну дату та час
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # Створіть рядок для збереження у файлі, включаючи ім'я користувача, дату і час
        post_entry = f"{username} {formatted_datetime},{post_content}\n"

        # Збережіть новий пост у файлі
        with open('posts.txt', 'a') as file:
            file.write(post_entry)
        # Ви можете використовувати базу даних або файли для збереження постів

        # Після збереження посту перенаправте користувача на сторінку /profile.html
        return redirect('/profile')


def is_valid_user(username, password):
    users = read_users_from_file()  # Функція для читання користувачів з файлу
    for user in users:
        if user['username'] == username and user['password'] == password:
            return True
    return False


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    # Отримайте завантажений файл (фото профілю)
    photo = request.files['photo']
    # Перевірте, чи файл було завантажено
    if photo:
        # Збережіть файл десь на сервері, наприклад, у папці "uploads"
        photo.save(f'uploads/{username}.jpg')
        # Ви можете створити імена файлів унікальними, щоб уникнути конфліктів.
    # Перевірка, чи користувача з таким іменем не існує вже
    if is_user_exists(username):
        flash("Користувач з таким іменем вже існує", "error")
        print("Користувач з таким іменем вже існує")
        return redirect('/SocialNetwork.html')

    # Збереження користувача (в цьому випадку у пам'яті, але зазвичай в базі даних)
    add_user(username, email, password)

    session['username'] = username  # Зберігаємо ім'я користувача в сесії
    session['email'] = email  # Зберігаємо email користувача в сесії
    session['password'] = password  # Зберігаємо пароль користувача в сесії
    flash("Користувач успішно зареєстрований", "success")
    print("Користувач успішно зареєстрований")

    return redirect('/SocialNetwork.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('login-username')
        login_password = request.form.get('login-password')

        # Тут ви повинні перевірити введені дані з даними, які ви зберегли під час реєстрації
        # Наприклад, якщо у вас є список користувачів, ви можете перевірити, чи існує користувач із таким ім'ям і паролем

        if is_user_exists(username):
            # Ви успішно увійшли в систему
            session['username'] = username  # Зберігаємо ім'я користувача в сесії
            flash("Ви успішно увійшли в систему", "success")
            return redirect('/SocialNetwork.html')
        else:
            # Помилка входу
            flash("Неправильний ім'я користувача або пароль", "error")
            return redirect('/register.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)  # Змініть 'port' на потрібний номер порту
