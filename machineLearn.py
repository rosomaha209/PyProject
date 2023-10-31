# Імпортуємо необхідні бібліотеки
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Завантажуємо дані. Припустимо, що у вас є CSV-файл з даними про акції.
data = pd.read_csv('AAPL.csv')

# Якщо значення в стовпці 'StockPrice' представлені рядками, перетворимо їх у числа та замінимо кому на крапку
data['Цена'] = data['Цена'].str.replace(',', '.').astype(float)

# Якщо значення в стовпці 'StockPrice' представлені рядками, перетворимо їх у числа та замінимо кому на крапку
data['Откр.'] = data['Откр.'].str.replace(',', '.').astype(float)

# Якщо значення в стовпці 'StockPrice' представлені рядками, перетворимо їх у числа та замінимо кому на крапку
data['Макс.'] = data['Макс.'].str.replace(',', '.').astype(float)

# Видаляємо знаки відсотка (%) та інші непотрібні символи зі стовпця 'StockPrice'
data['Изм. %'] = data['Изм. %'].str.replace('%', '').str.replace(',', '.').astype(float)

# Розділяємо дані на ознаки (фічі) і цільову змінну (ціну акцій)
X = data[['Откр.', 'Макс.', 'Изм. %']]  # Замініть це на ваші фічі
y = data['Цена']

# Розділяємо дані на тренувальний і тестовий набори
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Створюємо модель лінійної регресії
model = LinearRegression()

# Навчаємо модель на тренувальних даних
model.fit(X_train, y_train)

# Робимо прогнози на тестових даних
y_pred = model.predict(X_test)

# Оцінюємо модель
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Середньоквадратична помилка: {mse}")
print(f"R^2: {r2}")

# Визначте бажані розміри графіка та його розширення (dpi)
fig, ax = plt.subplots(figsize=(12, 8), dpi=80)
# Візуалізація результатів
ax.plot(y_test.values, label='Дійсна ціна акцій', marker='o', linestyle='', markersize=6)
ax.plot(y_pred, label='Прогнозована ціна акцій', marker='x', linestyle='-', markersize=6)
ax.set_xlabel("Спостереження")
ax.set_ylabel("Ціна акцій")
ax.set_title("Порівняння дійсних і прогнозованих цін акцій")
ax.grid(True)
ax.legend()

# Отримуємо поточну ціну акцій (залежить від вашого джерела даних)
current_stock_price = data['Цена'].iloc[0]
# Додайте поточну ціну акцій тут

# Додаємо числове значення прогнозованої ціни акцій на графік
for i, price in enumerate(y_pred):
    ax.text(i, price, f'{price:.2f}', ha='center', va='bottom', fontsize=8)

# Отримуємо час і дату з вашого датасету з врахуванням формату дати
date_and_time = pd.to_datetime(data['Дата'], dayfirst=True)  # Замініть 'Дата' на відповідний стовпець з датою та часом

# Позначаємо поточну ціну акцій на графіку

ax.axhline(y=current_stock_price, color='r', linestyle='--', label='Поточна ціна акцій')

# Додаємо час і дату на графік
for i, dt in enumerate(date_and_time):
    ax.text(i, max(max(y_test), max(y_pred)), dt.strftime('%Y-%m-%d %H:%M'), ha='center', va='top', fontsize=8)

ax.set_xticks(range(len(date_and_time)))
ax.set_xticklabels(date_and_time, rotation=45)

ax.legend()

plt.show()
