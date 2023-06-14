import sys
import cv2
import os
import json
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QDesktopWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, QTimer, Qt

TEMP_RESOLUTION_FILE = "temp_resolution.json"

class VideoCaptureThread(QThread):
    def __init__(self, camera_index=0):
        super().__init__()
        self.camera = cv2.VideoCapture(camera_index)
        self.camera_connected = self.camera.isOpened()
        self.running = False

        # Установите разрешение видеопотока на 720p [1280, 720]
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


    def run(self):
        if not self.camera_connected:
            return

        self.running = True
        while self.running:
            ret, self.frame = self.camera.read()

    def stop(self):
        if not self.camera_connected:
            return

        self.running = False
        self.wait()
        self.camera.release()


    def change_resolution(self, width, height):
        if not self.camera_connected:
            return False

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        new_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        new_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)

        return new_width == width and new_height == height


class VideoStream(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.center_on_screen()  # Центрировать окно перед началом видеопотока
        self.capture_thread = VideoCaptureThread()

        # Загрузите сохраненное разрешение и установите его
        #width, height = self.load_resolution()
        #self.capture_thread.change_resolution(width, height)

        # Загрузите сохраненные настройки и установите их
        settings = self.load_settings()
        if settings:
            x, y, width, height = settings
            self.move(x, y)
            self.capture_thread.change_resolution(width, height)

            # Обновите заголовок окна с текущим разрешением
            self.update_window_title(width, height)

        self.capture_thread.start()

        if not self.capture_thread.camera_connected:
            self.video_label.setText("Камера не найдена")
        else:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_video)
            self.timer.start(30)

    def load_resolution(self):
        if os.path.exists(TEMP_RESOLUTION_FILE):
            with open(TEMP_RESOLUTION_FILE, "r") as f:
                res = json.load(f)
                return res["width"], res["height"]
        else:
            # Если файл не найден, верните оптимальное разрешение (720p)
            return 1280, 720


    def init_ui(self):
        self.setWindowTitle('Видеопоток с USB-камеры [1280x720]')

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)

        # Создайте размещение с кнопками разрешения
        self.resolution_buttons = QHBoxLayout()

        for resolution in ["1080p", "720p", "WSVGA", "VGA", "360p"]:
            button = QPushButton(resolution)
            button.clicked.connect(lambda checked, r=resolution: self.change_resolution(r))
            self.resolution_buttons.addWidget(button)

        self.action_buttons = QHBoxLayout()

        for label, func in [("Настройки", self.settings), ("Снимок", self.take_snapshot), ("Перезапуск", self.restart_video_stream)]:
            button = QPushButton(label)
            button.clicked.connect(func)
            self.action_buttons.addWidget(button)

        vbox = QVBoxLayout(self)  # Создайте vbox перед добавлением размещений
        vbox.addWidget(self.video_label)
        vbox.addLayout(self.resolution_buttons)  # Добавьте размещение с кнопками разрешения в основной контейнер
        vbox.addLayout(self.action_buttons)

        self.setLayout(vbox)


    def update_video(self):
        if not self.capture_thread.camera_connected or not hasattr(self.capture_thread, 'frame') or self.capture_thread.frame is None:
            return

        rgb_image = cv2.cvtColor(self.capture_thread.frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap)

    def settings(self):
        print("Настройки")

    # "Снимок"
    def take_snapshot(self):
        snapshot = self.capture_thread.frame.copy()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"snapshot_{timestamp}.jpg"

        cv2.imwrite(file_name, snapshot)

    # "Перезапуск"
    def restart_video_stream(self):
        self.close()  # Закройте текущее окно
        self.__init__()  # Инициализируйте новое окно
        self.show()  # Покажите новое окно
        self.center_on_screen()  # Центрируйте новое окно на экране


    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        self.capture_thread.stop()

        event.accept()


    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def showEvent(self, event):
        super().showEvent(event)
        self.center_on_screen()


    def save_settings(self, x, y, width, height):
        settings = {
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }

        with open(TEMP_RESOLUTION_FILE, "w") as f:
            json.dump(settings, f)


    def load_settings(self):
        if os.path.exists(TEMP_RESOLUTION_FILE):
            with open(TEMP_RESOLUTION_FILE, "r") as f:
                settings = json.load(f)
                return settings["x"], settings["y"], settings["width"], settings["height"]
        else:
            return None


    def change_resolution(self, resolution):
        res_dict = {
            "1080p": (1920, 1080),
            "720p": (1280, 720),
            "WSVGA": (1024, 576),
            "VGA": (640, 480),
            "360p": (480, 360)
        }

        if resolution in res_dict:
            width, height = res_dict[resolution]

            # Остановите текущий поток видеозахвата и освободите камеру
            self.timer.stop()
            self.capture_thread.stop()

            # Создайте и запустите новый поток видеозахвата с новым разрешением
            self.capture_thread = VideoCaptureThread()
            # Измените разрешение !!! Важен порядок команд !!! 
            self.capture_thread.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.capture_thread.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.capture_thread.start()

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_video)
            self.timer.start(30)

            # Обновите заголовок окна с новым разрешением
            self.update_window_title(width, height)
            # Измените размер виджета в соответствии с новым разрешением
            self.resize_video_widget(width, height)

            # Обновите размер окна с виджетами
            self.adjustSize()

            # Сохраните настройки окна и разрешение
            x, y = self.pos().x(), self.pos().y()
            self.save_settings(x, y, width, height)            

            # После изменения размера виджета обновите его положение
            self.center_on_screen()

    def update_window_title(self, width, height):
        self.setWindowTitle(f"Видеопоток с USB-камеры [{width}x{height}]")


    def resize_video_widget(self, width, height):
        screen_geometry = QDesktopWidget().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Проверьте, подходит ли новый размер виджета для экрана
        if width > screen_width or height > screen_height:
            width = min(width, screen_width)
            height = min(height, screen_height)

        # Измените размер виджета
        self.video_label.setFixedSize(int(width), int(height))
        self.adjustSize()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    video_stream = VideoStream()
    video_stream.show()
    sys.exit(app.exec_())
