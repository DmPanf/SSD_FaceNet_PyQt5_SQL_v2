# table.py
# 15-06-2023

import pandas as pd
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QLabel, QVBoxLayout, QHBoxLayout, QWidget

class TableWidget(QWidget):
    def __init__(self, parent=None):
        super(TableWidget, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # Создание таблицы
        self.table = QTableWidget(self)
        data = pd.read_csv('data.csv')
        self.table.setRowCount(data.shape[0])
        self.table.setColumnCount(data.shape[1])

        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                self.table.setItem(i, j, QTableWidgetItem(str(data.iloc[i, j])))

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(data.columns)

        ## Расчет ширины таблицы
        #self.table.resizeColumnsToContents()
        #width = self.table.verticalHeader().width() + 2  # +2 - это для границ
        #for i in range(self.table.columnCount()):
        #    width += self.table.columnWidth(i)  # получаем ширину каждого столбца
        #self.setMinimumWidth(width)  # устанавливаем минимальную ширину таблицы

        # Установка ширины столбцов
        column_width = 140  # фиксированная ширина столбцов
        table_width = column_width * 7 + 50
        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, column_width)
        self.setMinimumWidth(table_width)
        self.setMinimumHeight(table_width // 2 + 50)

        # Виджеты для вывода расчетных данных
        self.total_days_label = QLabel("Количество рабочих дней: ")
        self.total_time_label = QLabel("Суммарное время за месяц: ")
        self.average_day_label = QLabel("Средний рабочий день: ")

        # Расчет данных
        total_days = data.shape[0]
        total_time = pd.to_timedelta(data['загрузка']).sum()
        average_day = total_time / total_days

        # Конвертация в часы и минуты
        average_day_seconds = average_day.total_seconds()
        average_day_hours = average_day_seconds // 3600
        average_day_minutes = (average_day_seconds % 3600) // 60

        # Обновляем виджеты
        self.setWindowTitle(f"Таблица рабочего времени сотрудника {data['ID'][0]} за {data['месяц'][0]} месяц {data['год'][0]} года")
        self.total_days_label.setText(f"Количество рабочих дней: {total_days}")
        self.total_days_label.setFixedWidth(250)
        self.total_time_label.setText(f"Суммарное время за месяц: {total_time}")
        # self.average_day_label.setText(f"Средний рабочий день: {average_day}")
        self.average_day_label.setText(f"Средний рабочий день: {int(average_day_hours)} часов, {int(average_day_minutes)} минут")

        # Создаем горизонтальный layout
        hbox_layout = QHBoxLayout()

        # Добавляем виджеты в горизонтальный layout
        hbox_layout.addWidget(self.total_days_label)
        hbox_layout.addWidget(self.total_time_label)
        hbox_layout.addWidget(self.average_day_label)

        # Создаем основной layout
        self.layout = QVBoxLayout(self)

        # Добавляем таблицу и виджеты на форму
        self.layout.addWidget(self.table)  # Добавляем таблицу
        self.layout.addLayout(hbox_layout)  # Добавляем горизонтальный layout


def main():
    app = QApplication([])
    table_widget = TableWidget()
    table_widget.show()
    app.exec_()

if __name__ == '__main__':
    main()
