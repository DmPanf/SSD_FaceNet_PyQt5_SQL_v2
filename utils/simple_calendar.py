# simple_calendar.py
# 15-06-2023

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

class Calendar(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        # Создаем кнопку с эмодзи в качестве текста
        self.date_button = QPushButton('📅 Выбрать месяц и год', self)
        self.date_button.clicked.connect(self.choose_date)
        layout.addWidget(self.date_button)

    def choose_date(self):
        # Здесь вы можете написать код для открытия виджета выбора даты
        pass

def main():
    app = QApplication([])
    window = Calendar()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
