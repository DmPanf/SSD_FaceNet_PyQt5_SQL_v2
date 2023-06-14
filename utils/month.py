# month.py
# 15-06-2023

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton, QWidget
from PyQt5.QtWidgets import QApplication
from datetime import datetime

class DateDialog(QDialog):
    def __init__(self, parent=None):
        current_year = datetime.now().year
        super(DateDialog, self).__init__(parent)
        self.setWindowTitle('Выбор месяца и года')
        
        layout = QVBoxLayout(self)
        
        # Создаем выпадающий список для выбора года
        self.year_combo = QComboBox(self)
        self.year_combo.addItems([str(year) for year in range(2020, current_year)])  # выбираем диапазон лет
        layout.addWidget(self.year_combo)

        # Создаем выпадающий список для выбора месяца
        self.month_combo = QComboBox(self)
        self.month_combo.addItems(['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'])
        layout.addWidget(self.month_combo)

        # Создаем кнопку для подтверждения выбора
        self.ok_button = QPushButton('OK', self)
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

class Calendar(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.date_button = QPushButton('📅 Выбрать месяц и год', self)
        self.date_button.clicked.connect(self.choose_date)
        layout.addWidget(self.date_button)

    def choose_date(self):
        dialog = DateDialog(self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            # Если пользователь нажал кнопку "OK", получаем выбранный год и месяц
            selected_year = dialog.year_combo.currentText()
            selected_month = dialog.month_combo.currentIndex() + 1  # +1, потому что индексация начинается с 0
            print(f'Выбранный год: {selected_year}, выбранный месяц: {selected_month}')

def main():
    app = QApplication([])
    window = Calendar()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
