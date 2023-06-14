# image_viewer.py
# 15-06-2023

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QDesktopWidget
from PyQt5.QtWidgets import QApplication, QFileDialog, QTextEdit
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QIcon
import sys, os
import datetime
from ip_usb_cam import VideoCaptureThread
from send_message import send_message
from config import faces_folder_linux, faces_folder_windows

class ImageViewer(QWidget):
    start_report_signal = pyqtSignal()  # новый сигнал для открытия Video_Stream (без параметров)

    #def __init__(self, image_folder, ID='ID.01'):
    def __init__(self, image_folder, ID='ID.01', *args, **kwargs):
        #super().__init__()
        #super(ImageViewer, self).__init__(image_folder, ID='ID.01')
        super(ImageViewer, self).__init__(*args, **kwargs)
        self.capture_thread = VideoCaptureThread()  # Создаем экземпляр VideoCaptureThread

        # Подключаем сигнал start_video_signal к слоту start_video_stream_slot
        #self.start_report_signal.connect(self.start_users_report_slot)

        person_data = f'Фамилия Имя Отчество\nСотрудник Отдела управления имуществом' \
                      f'\ngreg_s@piligrim.ru\n12.12.1981\nmob.:+7962-113-8877\n{id}'

        self.image_folder = image_folder
        self.ID = ID
        self.images = [os.path.join(image_folder, f) for f in sorted(os.listdir(image_folder)) if f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        self.current_image_index = 0
        initial_image_name = self.ID + '.jpg'  # Задаем индекс текущего изображения
        initial_image_path = os.path.join(self.image_folder, initial_image_name)
        if initial_image_path in self.images:
            self.current_image_index = self.images.index(initial_image_path)

        self.initUI(person_data)
        self.file_name_edit.setText(self.ID) # Заполняем текстовое поле текущим ID сотрудника

    def initUI(self, person_data):
        self.setWindowTitle('Сотрудники компании "Пилигрим"')
 
        self.label = QLabel(self)
        self.pixmap = QPixmap(self.images[self.current_image_index])
        self.pixmap = self.pixmap.scaledToWidth(540)  # Масштабируем изображение до ширины 540 пикселей
        self.label.setPixmap(self.pixmap)

        self.first_btn = QPushButton('⏮', self)
        self.first_btn.clicked.connect(self.first_image)
        self.prev_btn = QPushButton('⏪', self)
        self.prev_btn.clicked.connect(self.previous_image)
        self.center_btn = QPushButton('⏺', self)
        self.center_btn.clicked.connect(self.center_image)
        self.next_btn = QPushButton('⏩', self)
        self.next_btn.clicked.connect(self.next_image)
        self.last_btn = QPushButton('⏭', self)
        self.last_btn.clicked.connect(self.last_image)

        self.file_name_edit = QLineEdit(self)
        self.file_name_edit.setPlaceholderText(self.ID)
        self.file_name_edit.returnPressed.connect(self.load_image_by_name)

        hbox = QHBoxLayout()  # добавляем виджет QLineEdit справа от кнопки "середина"
        for btn in [self.first_btn, self.prev_btn, self.center_btn, self.file_name_edit, self.next_btn, self.last_btn]:
            btn.setFixedSize(85, 40)  # Задаем ширину и высоту виджета
            btn.setStyleSheet("font-size: 20px")
            hbox.addWidget(btn)

        self.stop_btn = QPushButton('- ОТКАЗАТЬ -', self)
        self.stop_btn.setStyleSheet("font-size: 20px")
        self.stop_btn.setFixedSize(200, 50) # Задаем ширину и высоту виджета
        self.stop_btn.clicked.connect(self.prohibited)

        self.month_btn = QPushButton('📊', self)
        self.month_btn.setStyleSheet("font-size: 22px")
        self.month_btn.setFixedSize(120, 50)
        self.month_btn.clicked.connect(self.calendar)

        self.pass_btn = QPushButton('+ РАЗРЕШИТЬ +', self)
        self.pass_btn.setStyleSheet("font-size: 20px")
        self.pass_btn.setFixedSize(200, 50) # Задаем ширину и высоту виджета
        self.pass_btn.clicked.connect(self.allowed)

        self.text_widget = QTextEdit(self)  # виджет QTextEdit для отображения текста
        self.text_widget.setReadOnly(True)  # сделаем его только для чтения
        self.text_widget.setFixedSize(540, 110) # Задаем ширину и высоту виджета
        self.text_widget.setStyleSheet("font-size: 18px")

        bigs = QHBoxLayout()  # Горизонтальное размещение
        for dopwidget in[self.stop_btn, self.month_btn, self.pass_btn]:
            bigs.addWidget(dopwidget)

        vbox = QVBoxLayout(self)  # Вертикальное размещение
        vbox.addWidget(self.label)
        vbox.addWidget(self.text_widget) # виджет текста в вертикальный слой vbox
        vbox.addLayout(hbox)
        vbox.addLayout(bigs)

        self.setLayout(vbox)
        self.set_text(person_data)
        self.center()  # Центрировать окно на экране

    def center(self):
        #screen = QDesktopWidget().screenGeometry()
        #window = self.geometry()
        #self.move((screen.width() - window.width()) // 2, (screen.height() - window.height()) // 2)
        self.resize(560, 800)
        screen_geometry = QApplication.desktop().availableGeometry()  # Получаем геометрию экрана
        window_geometry = self.frameGeometry()  # Получаем геометрию окна
        window_geometry.moveCenter(screen_geometry.center())  # Устанавливаем центр окна в центр экрана
        window_geometry.moveTop(window_geometry.top() - 100)  # Добавляем смещение: отодвигаем окно вверх на 250 пикселей
        self.move(window_geometry.topLeft())  # Перемещаем главное окно по этим координатам

    def first_image(self):
        self.current_image_index = 0
        self.update_image()

    def previous_image(self):
        self.current_image_index -= 1
        if self.current_image_index < 0:
            self.current_image_index = 0
        self.update_image()

    def center_image(self):
        self.current_image_index = len(self.images) // 2
        self.update_image()

    def next_image(self):
        self.current_image_index += 1
        if self.current_image_index >= len(self.images):
            self.current_image_index = len(self.images) - 1
        self.update_image()

    def last_image(self):
        self.current_image_index = len(self.images) - 1
        self.update_image()

    def allowed(self):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        message = f'⏰ <b>{self.file_name_edit.text()} [{timestamp}] +</b>'
        sms = send_message(message, 'HTML')
        # self.start_video_signal.emit()
        self.close_window()

    def prohibited(self):
        # self.start_video_signal.emit()
        self.close_window()

    def calendar(self):
        self.close_window()

    @pyqtSlot()  # Определяем слот для закрытия окна ImageViewer
    def close_window(self):
        self.close() # закрыть текущее окно в главном потоке GUI
        #self.capture_thread.resume()

    @pyqtSlot()  # Определяем слот для открытия окна Report
    def start_users_report_slot(self):
        #from users_report import UsersRepport
        self.close_window()
        #self.users_report = UsersReport()  # создаем новое окно Video_Stream и открываем его
        #self.users_report.show()

    def load_image_by_name(self):
        file_name = self.file_name_edit.text()
        if not file_name:
            return

        file_path = os.path.join(self.image_folder, f"{file_name}.jpg")
        if os.path.exists(file_path):
            self.current_image_index = self.images.index(file_path)
            self.update_image()

    def update_image(self):
        self.pixmap.load(self.images[self.current_image_index])
        self.label.setPixmap(self.pixmap)

        # Получаем имя файла без расширения и устанавливаем его в виджет QLineEdit
        file_name = os.path.splitext(os.path.basename(self.images[self.current_image_index]))[0]
        self.file_name_edit.setText(file_name)
        file_size = os.path.getsize(self.images[self.current_image_index]) / 1024  # размер файла в килобайтах
        image_info = f'Сотрудник: {file_name}' \
                     f'\nРазмер изображения: {self.pixmap.width()}x{self.pixmap.height()} пикселей' \
                     f'\nРазмер файла: {file_size:.2f} КБ'
        self.set_text(image_info)  # Выводим новый текст в виджет QTextEdit

    def set_text(self, text):  # метод для установки текста в виджете QTextEdit
        self.text_widget.setText(text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    id = 'ID.11'
    default_folder = faces_folder_windows if os.name == 'nt' else faces_folder_linux # Выберите папку по умолчанию
    
    if not os.path.exists(default_folder):
        print(f"Папка {default_folder} не найдена. Запускается интерактивный выбор папки.")
        # default_folder = QFileDialog.getExistingDirectory(None, "Выберите папку")
        dialog = QFileDialog()
        dialog.setWindowFlags(Qt.WindowStaysOnTopHint)  # устанавливаем окно поверх остальных
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly)
        
        if dialog.exec_():
            default_folder = dialog.selectedFiles()[0]
    
    viewer = ImageViewer(default_folder, id)
    #viewer.set_text(f'Степанов Григорий Андреевич\nРуководитель Отдела управления имуществом\ngreg_s@piligrim.ru\n12.12.1981\nmob.:+7962-113-8877\n{id}')
    viewer.show()
    sys.exit(app.exec_())
