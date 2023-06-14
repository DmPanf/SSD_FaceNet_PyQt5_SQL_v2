# video_stream.py
# 15-06-2023

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QDesktopWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot # сигнал для открытия окон или сообщений об ошибках
from PyQt5.QtCore import QThread, QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2
import datetime
import random
import sys, os
import json

from image_viewer import ImageViewer  # импортируем класс ImageViewer
from ip_usb_cam import VideoCaptureThread
from config import WINDOW_POSITION, faces_folder_linux, faces_folder_windows, IMAGES_PATH


# os.environ['OPENCV_IO_ENABLE_JASPER'] = 'False'
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/path/to/your/platforms/directory'


class VideoStream(QWidget):
    error_signal = pyqtSignal(str) # определяем error_signal в классе VideoStream

    def __init__(self):
        super().__init__()
        # super(VideoStream, self).__init__(parent)
        self.initUI()
        self.capture_thread = VideoCaptureThread()  # Создаем экземпляр VideoCaptureThread
        self.capture_thread.error_signal.connect(self.show_error_message)  # Подключаем сигнал Вывода Ошибки к слоту
        self.capture_thread.close_window_signal.connect(self.close_window)  # Подключаем сигнал Закрытия окна к слоту
        self.capture_thread.show_image_signal.connect(self.show_image_viewer)  # Подключаем сигнал Вывода окна Сотрудников к слоту

        settings = self.load_settings()  # Загружаем сохраненные настройки и устанавливаем их
        if settings:
            x, y, width, height = settings
            self.move(x, y)
            self.capture_thread.change_resolution(width, height)
            self.update_window_title(width, height)  # Обновляем заголовок окна с текущим разрешением

        self.capture_thread.start()

        self.timer = QTimer(self)
        if not self.capture_thread.camera_connected:
            self.video_label.setText("Камера не найдена")
        else:
            self.timer.timeout.connect(self.update_video)
            self.timer.start(30)

        self.resize_video_widget(width, height)
        #self.adjustSize()           # изменяем размер виджета так, чтобы он соответствовал его минимальному размеру
        #self.center_on_screen()     # Центрируем новое окно на экране

    @pyqtSlot(str)  # Определяем слот для вывода сообщения об ошибке
    def show_error_message(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Ошибка")
        error_dialog.exec_()

    @pyqtSlot()  # Определяем слот для закрытия окна
    def close_window(self):
        self.close() # закрыть текущее окно в главном потоке GUI

    @pyqtSlot(str)  # Определяем слот для открытия окна
    def show_image_viewer(self, face_id):  # Выбор папки по умолчанию (Linux и Windows)
        default_folder = faces_folder_windows if os.name == 'nt' else faces_folder_linux
        #self.image_viewer = ImageViewer(default_folder, face_id)
        # self.close_window()
        # создаем новое окно и открываем его
        self.image_viewer = ImageViewer(default_folder, face_id)
        self.image_viewer.show()

    def load_resolution(self):
        if os.path.exists(WINDOW_POSITION):
            with open(WINDOW_POSITION, "r") as f:
                res = json.load(f)
                return res["width"], res["height"]
        else:  # Если файл не найден, то будет оптимальное разрешение (480p)
            return 640, 480

    def initUI(self):
        self.setWindowTitle('Видеопоток с USB-камеры [640x480]')
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        # Создаем размещение с кнопками разрешения
        self.resolution_buttons = QHBoxLayout()

        for resolution in ["1080p", "720p", "WSVGA", "VGA", "360p"]:
            button = QPushButton(resolution)
            button.clicked.connect(lambda checked, r=resolution: self.change_resolution(r))
            self.resolution_buttons.addWidget(button)

        self.action_buttons = QHBoxLayout()

        for label, func in [("Сотрудники", self.settings), ("Снимок", self.take_snapshot), ("Перезапуск", self.restart_video_stream)]:
            button = QPushButton(label)
            button.clicked.connect(func)
            self.action_buttons.addWidget(button)


        vbox = QVBoxLayout(self)  # Создаем vbox перед добавлением размещений
        vbox.addWidget(self.video_label)
        vbox.addLayout(self.resolution_buttons)  # Добавляем размещение с кнопками разрешения в основной контейнер
        vbox.addLayout(self.action_buttons)
        self.setLayout(vbox)

    #def center(self):
    #    #screen = QDesktopWidget().screenGeometry()
    #    screen_geometry = QApplication.desktop().availableGeometry()  # Получаем геометрию экрана
    #    window_geometry = self.frameGeometry()  # Получаем геометрию окна
    #    window_geometry.moveCenter(screen_geometry.center())  # Устанавливаем центр окна в центр экрана
    #    window_geometry.moveTop(window_geometry.top() - 50)  # Добавляем смещение: отодвигаем окно вверх на 250 пикселей
    #    self.move(window_geometry.topLeft())  # Перемещаем главное окно по этим координатам

    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        qr.moveTop(qr.top() - 50)
        self.move(qr.topLeft())

    def update_video(self):
        if not self.capture_thread.camera_connected or not hasattr(self.capture_thread, 'frame') or self.capture_thread.frame is None:
            return
        rgb_image = cv2.cvtColor(self.capture_thread.frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap)

    def settings(self):  # &&&&&=== "Сотрудники" ===&&&&&
        # Выбор папки по умолчанию в зависимости от операционной системы
        default_folder = faces_folder_windows if os.name == 'nt' else faces_folder_linux
        # закрываем текущее окно
        # self.close_window()
        # создаем новое окно и открываем его
        random_number = random.randint(1, 12)
        id_string = "ID." + str(random_number).zfill(2)
        self.image_viewer = ImageViewer(default_folder, id_string)  # 'ID.11'
        self.image_viewer.show()

    def take_snapshot(self):  # &&&&&=== "Снимок" ===&&&&&
        if not hasattr(self.capture_thread, 'frame') or self.capture_thread.frame is None:
            print("Ошибка: Нет доступных кадров для снимка")
            self.error_signal.emit("Ошибка: Нет доступных кадров для снимка")
            return

        snapshot = self.capture_thread.frame.copy()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{IMAGES_PATH}/photo_{timestamp}.jpg"

        cv2.imwrite(file_name, snapshot)

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Снимок успешно сохранен в {file_name}")
        msg.setWindowTitle("Сохранение снимка")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def restart_video_stream(self):  # &&&&&=== "Перезапуск" ===&&&&&
        self.close()                 # Закрываем текущее окно
        self.__init__()              # Инициализируем новое окно
        self.show()                  # Показываем новое окно
        self.adjustSize()            # изменяем размер виджета так, чтобы он соответствовал его минимальному размеру
        #self.center_on_screen()     # Центрируем новое окно на экране

    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        self.capture_thread.stop()
        event.accept()


    def showEvent(self, event):
        super().showEvent(event)
        self.center_on_screen()

    def save_settings(self, x, y, width, height):
        settings = {"x": x, "y": y, "width": width, "height": height}
        with open(WINDOW_POSITION, "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        if os.path.exists(WINDOW_POSITION):
            with open(WINDOW_POSITION, "r") as f:
                settings = json.load(f)
                return settings["x"], settings["y"], settings["width"], settings["height"]
        else:
            return None

    def change_resolution(self, resolution):
        if hasattr(self, 'timer'): # Это предотвратит попытку остановить таймер, если он еще не был инициализирован
            self.timer.stop()

        res_dict = {"1080p": (1920, 1080), "720p": (1280, 720), "WSVGA": (1024, 576), "VGA": (640, 480), "360p": (480, 360)}

        if resolution in res_dict:
            width, height = res_dict[resolution]
            # Останавливаем текущий поток видеозахвата и освобождаем камеру
            self.timer.stop()
            self.capture_thread.stop()

            # Создаем и запускаем новый поток видеозахвата с новым разрешением
            self.capture_thread = VideoCaptureThread()
            # Изменяем разрешение !!! Важен порядок команд !!! 
            self.capture_thread.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.capture_thread.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.capture_thread.start()

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_video)
            self.timer.start(30)

            self.update_window_title(width, height)  # Обновляем заголовок окна с новым разрешением
            self.resize_video_widget(width, height)  # Изменяем размер виджета в соответствии с новым разрешением
            # self.adjustSize()                        # изменяем размер виджета так, чтобы он соответствовал его минимальному размеру
            x, y = self.pos().x(), self.pos().y()
            self.save_settings(x, y, width, height)  # Сохраняем настройки окна и разрешение      
            self.adjustSize()            # изменяем размер виджета так, чтобы он соответствовал его минимальному размеру
            self.center_on_screen()      # После изменения размера виджета обновляем его положение

    def update_window_title(self, width, height):
        self.setWindowTitle(f"Видеопоток с USB-камеры [{width}x{height}]")

    def resize_video_widget(self, width, height):
        screen_geometry = QDesktopWidget().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Проверяем, подходит ли новый размер виджета для экрана
        if width > screen_width or height > screen_height:
            width = min(width, screen_width)
            height = min(height, screen_height)
        self.video_label.setFixedSize(int(width), int(height))  # Изменяем размер виджета
        self.adjustSize()   # изменяем размер виджета так, чтобы он соответствовал его минимальному размеру

if __name__ == '__main__':
    app = QApplication(sys.argv)  # sys.argv используется, чтобы получить аргументы командной строки для настроек
    video_stream = VideoStream()  # Создаём объект VideoStream, который представляет видеопоток
    video_stream.show()           # Вызываем метод show() у объекта video_stream, чтобы отобразить его на экране
    sys.exit(app.exec_())         # app.exec_() возвращает статус выхода, который затем передается в sys.exit = корректное завершение
