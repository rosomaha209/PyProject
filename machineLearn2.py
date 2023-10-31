from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Завантажте історію цін на акції.
df = pd.read_csv('AAPL.csv')

# Якщо значення в стовпці 'StockPrice' представлені рядками, перетворимо їх у числа та замінимо кому на крапку
df['Цена'] = df['Цена'].str.replace(',', '.').astype(float)

# # Якщо значення в стовпці 'StockPrice' представлені рядками, перетворимо їх у числа та замінимо кому на крапку
# df['Изм. %'] = df['Изм. %'].str.replace(',', '.').astype(float)

# Видаляємо знаки відсотка (%) та інші непотрібні символи зі стовпця 'StockPrice'
df['Изм. %'] = df['Изм. %'].str.replace('%', '').str.replace(',', '.').astype(float)

df['Дата'] = pd.to_datetime(df['Дата'], dayfirst=True)



# Підготуйте дані для навчання моделі.
X = df['Цена'].to_numpy()
y = df['Изм. %'].to_numpy()[1:]

X = X.reshape(-1, 1)

X = X[:-1]



# Виберіть модель машинного навчання.
model = LinearRegression()

# Навчіть модель.
model.fit(X, y)

# Перевірте модель.
y_pred = model.predict(X)

# Оцініть модель.
print(model.score(X, y))

# Додайте дату та час до даних.
df['Дата'] = pd.to_datetime(df['Дата'])
# df['Time'] = pd.to_datetime(df['Time'])



# Додайте прогноз на майбутнє.
future_prices = model.predict(np.arange(len(df) + 10).reshape(-1, 1))
future_prices = future_prices[:937]

# Зобразіть дані.
plt.plot(df['Дата'].values[:-1], future_prices[:-1], label='Predicted Price')
plt.plot(df['Дата'].values[:-1], df['Цена'][:-1], label='Actual Price')
plt.plot(df['Дата'], future_prices)
plt.xlabel('Дата')
plt.ylabel('Цена')
plt.title("Порівняння дійсних і прогнозованих цін акцій")
plt.legend()
plt.grid(True)

# Визначте поточну ціну акцій.
current_price = df['Цена'].iloc[-1]

# Визначте прогнозовану ціну акцій.
predicted_price = future_prices[-1]

# Визначте, який ціна вища.
if current_price > predicted_price:
    higher_price = current_price
else:
    higher_price = predicted_price

# Виведіть результат.
print(f"Поточна ціна акцій: {current_price}")
print(f"Прогнозована ціна акцій: {predicted_price}")
print(f"Більше: {higher_price}")
