# ip_usb_cam.py
# 15-06-2023

# класс VideoCaptureThread представляет собой поток, который отвечает за видеозахват из камеры 
# и распознавание лиц на каждом пятом кадре. В основе его работы лежит библиотека OpenCV (cv2).
# Метод __init__: Инициализирует камеру и устанавливает ее разрешение. Если камера не может быть открыта, он отправляет сигнал об ошибке.
# Метод run: Запускает бесконечный цикл, который считывает кадры с камеры. На каждом пятом кадре он выполняет распознавание лица. Если лицо распознается, он отправляет сигнал для отображения изображения.
# Метод stop: Останавливает захват видео и освобождает камеру.
# Метод change_resolution: Изменяет разрешение камеры.

import cv2
import pickle
import os
import time
from PyQt5.QtCore import pyqtSignal, pyqtSlot # сигнал для открытия окон или сообщений об ошибках
from PyQt5.QtCore import QThread, QTimer, Qt

from facenet_recognition import facenet_recognition # функция идентификации сотрудников
from config import CAM_RESOLUTION

class VideoCaptureThread(QThread):
    close_window_signal = pyqtSignal()   # новый сигнал для закрытия окна
    error_signal = pyqtSignal(str)       # для определения сигнала ошибки
    show_image_signal = pyqtSignal(str)  # для открытия ImageViewer

    def __init__(self, camera_index="-1", resolution=(640, 480)):
        # super(VideoCaptureThread, self).__init__(parent)
        super().__init__()
        self.load_settings()
        if not self.camera_connected:
            print("Ошибка: Камера не найдена")
            self.error_signal.emit("Ошибка: Камера не найдена")
            return
        self.running = False
        #self.change_resolution(*self.resolution)

    def load_settings(self):
        if os.path.exists(CAM_RESOLUTION):
            with open(CAM_RESOLUTION, "rb") as f:
                settings = pickle.load(f)
                self.camera_index = settings.get('camera_index', -1)      # получаем значения по заданному ключу
                self.resolution = settings.get('resolution', (640, 480))  # если таких нет, то задаем значение по-умолчанию
        else:
            self.camera_index = -1
            self.resolution = (640, 480)
        
        # self.camera = cv2.VideoCapture(RTSP_PATH)
        self.camera = cv2.VideoCapture(self.camera_index)
        ## Установка разрешения видеопотока из файла конфигурации или на 640х480
        # self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        # self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
        self.camera_connected = self.camera.isOpened()

    def save_settings(self):
        settings = {'camera_index': self.camera_index, 'resolution': self.resolution}
        with open(CAM_RESOLUTION, 'wb') as file:
            pickle.dump(settings, file)

    def run(self):
        if not self.camera_connected:
            return
        self.running = True
        self.paused = False # **** NEW ****
        frame_count = 0 # Перебор кадров для уменьшения задержек (или для Тестовой заглушки)
        while self.running:
            while self.paused:   # **** NEW **** Дополнительный цикл для реализации паузы
                time.sleep(2.5)  # **** NEW **** Небольшая задержка, чтобы избежать ненужного потребления CPU
                self.paused = False
            
            ret, self.frame = self.camera.read()
            frame_count += 1

            if frame_count % 5 == 0:  # Проверяем каждый 5-й кадр (или Тестовая заглушка: frame_count % 750 == 0)
                face_id = facenet_recognition(self.frame)  # Распознавание лиц
                if face_id is not None:  # РАБОЧЕЕ УСЛОВИЕ!!! или для тестов face_id = 'ID.11'
                    #self.running = False # **** ОБЯЗАТЕЛЬНО, ИНАЧЕ ЗАВИСАЕТ ВИДЕО!!! ****
                    self.paused = True   # **** NEW **** Вместо остановки потока полностью, мы просто ставим его на паузу
                    self.show_image_signal.emit(face_id) # Отправляем сигнал для открытия ImageViewer при распознавании лица

    def resume(self):  # Метод для снятия паузы
        self.paused = False
        #self.running = True

    def stop(self):
        if not self.camera_connected:
            return
        self.running = False
        self.wait()
        self.save_settings()
        self.camera.release()

    def change_resolution(self, width, height):
        if not self.camera_connected:
            return False
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        new_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        new_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.resolution = (new_width, new_height)
        return new_width == width and new_height == height


    #@pyqtSlot()
    #def stop_video_stream(self):
    #    self.running = False

    #@pyqtSlot()
    #def start_video_stream(self):
    #    self.running = True
