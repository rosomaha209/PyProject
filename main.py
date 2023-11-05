import datetime

#print("Hallo Roman", "\\", round(24 / 6), sep="-", end="!")
print('Введiть вашу дату народження, наприклад: 2023-10-22 ')
num = datetime.date.fromisoformat(input())
print("\n")

timenow = datetime.date.today()
yourBirthdayDay =timenow-num
print("Вам виповнилося: ",round( yourBirthdayDay.days//365.25 )," Років")
#print(num)

import datetime

def get_age(birth_date):
  """
  Визначає вік людини на основі дати народження.

  Параметри:
    birth_date: Дата народження у форматі "YYYY-MM-DD".

  Повертає:
    Вік людини у цілих числах.
  """

  today = datetime.date.today()
  birth_date = datetime.date.fromisoformat(birth_date)
  return (today - birth_date).days // 365.25


if __name__ == "__main__":
  birth_date = input("Введіть дату народження у форматі 'YYYY-MM-DD': ")
  age = get_age(birth_date)
  print(f"Вік людини: {age} років")
