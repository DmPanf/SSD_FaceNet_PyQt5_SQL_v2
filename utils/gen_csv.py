# gen_csv.py
# 15-06-2023

import pandas as pd
import random
from datetime import datetime, timedelta, time

months_ru = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

# Создаем диапазон дат для апреля 2023 года
dates = pd.date_range('2023-04-01', '2023-04-30')
my_id = 'ID.11'

data = []
for date in dates:
    # Создаем случайное время в указанном диапазоне
    time1 = datetime.combine(date, time(8, 0)) + timedelta(minutes=random.randint(0, 150))
    time2 = datetime.combine(date, time(16, 30)) + timedelta(minutes=random.randint(0, 350))

    # Вычисляем загрузку как разницу между время2 и время1
    loading = time2 - time1
    loading = divmod(loading.total_seconds(), 3600)  # переводим в часы:минуты:секунды
    loading = f"{int(loading[0])}:{int(loading[1]//60)}:{int(loading[1]%60)}"

    data.append([my_id, date.year, months_ru[date.month], date.day, time1.time(), time2.time(), loading])

# Создаем DataFrame
df = pd.DataFrame(data, columns=['ID', 'год', 'месяц', 'дата', 'время 1', 'время 2', 'загрузка'])

# Сохраняем DataFrame в файл CSV
df.to_csv('data.csv', index=False)
