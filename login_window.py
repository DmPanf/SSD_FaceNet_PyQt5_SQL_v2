# login_window.py
# 15-06-2023

import hashlib
import pickle
import sys
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QMessageBox, QFormLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from video_stream import VideoStream
from send_message import send_message
from config import USERS_PASSWORD, START_IMAGE

class LoginWindow(QWidget):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)
        self.setWindowTitle('Login Window')
        self.resize(400, 500)
        self.initUI()

    def initUI(self):
        description_text = " ".join([
            "Эта программа разработана для автоматического распознавания лиц и идентификации сотрудников с целью регистрации рабочего времени.",
            "\nОна использует продвинутые технологии обработки изображений и искусственного интеллекта, включая SSD (Single Shot MultiBox Detector) и FaceNet.",
            "\nДля использования программы требуется база данных лиц сотрудников.",
            "\nПрограмма представляет собой мощный инструмент для автоматического контроля рабочего времени, который облегчает процесс учета времени и помогает повысить производительность и эффективность управления персоналом."
        ])

        layout = QVBoxLayout()

        # Заголовок
        title = QLabel('Программа FaceID Tracking')
        title_font = QFont("Arial", 24)
        title.setFont(title_font)
        layout.addWidget(title, alignment=Qt.AlignCenter)

        # Изображение
        image = QLabel(self)
        pixmap = QPixmap(START_IMAGE)
        image.setPixmap(pixmap)
        layout.addWidget(image, alignment=Qt.AlignCenter)

        # Описание
        description = QTextEdit()
        description.setReadOnly(True)
        description.setText(description_text)
        description.setFixedHeight(100)
        description.setStyleSheet("font-size: 16px")
        layout.addWidget(description)


        # Поля ввода и кнопка
        form_layout = QFormLayout()
        self.login_field = QLineEdit()
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)
        form_layout.addRow('Login:', self.login_field)
        form_layout.addRow('Password:', self.password_field)
        layout.addLayout(form_layout)

        login_button = QPushButton('ЗАПУСК')
        login_button.clicked.connect(self.check_credentials)
        login_button.setFixedSize(200, 50)
        login_button.setStyleSheet("font-size: 18px")
        layout.addWidget(login_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.center()

    def center(self):
        #screen = QDesktopWidget().screenGeometry()
        screen_geometry = QApplication.desktop().availableGeometry()  # Получаем геометрию экрана
        window_geometry = self.frameGeometry()  # Получаем геометрию окна
        window_geometry.moveCenter(screen_geometry.center())  # Устанавливаем центр окна в центр экрана
        window_geometry.moveTop(window_geometry.top() - 150)  # Добавляем смещение: отодвигаем окно вверх на 250 пикселей
        self.move(window_geometry.topLeft())  # Перемещаем главное окно по этим координатам

    def check_credentials(self):
        login = self.login_field.text()
        password = self.password_field.text()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        with open(USERS_PASSWORD, 'rb') as f:  # Загружаем данные пользователей
            users = pickle.load(f)
        for user in users:  # Проверка учетных данных
            if user['login'] == login and user['password'] == password_hash:
                user['active'] = True
                with open(USERS_PASSWORD, 'wb') as f:  # Сохраняем обновленные данные пользователей
                    pickle.dump(users, f)
                self.close()
                
                timestamp1 = datetime.datetime.now().strftime("%d-%m-%Y")
                timestamp2 = datetime.datetime.now().strftime("%H:%M:%S")
                message = f'..... <b>{timestamp1}</b>\n✅ Старт системы: <b>{timestamp2}</b>\n👤 Пользователь:  <b>{login}</b>'
                sms = send_message(message, 'HTML')
                video_stream = VideoStream()  # запуск основного окна
                video_stream.show()
                break
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')

def main():
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
