# ssd_face_detection.py
# 15-06-2023

import cv2  # pip install -q opencv-python
import numpy as np

# Путь к модели и файлу конфигурации
model_path = './model/res10_300x300_ssd_iter_140000.caffemodel'
proto_path = './model/deploy.prototxt'


def detect_face(frame, confidence_threshold=0.55, model_path=model_path, proto_path=proto_path):
    min_w, min_h = 100, 120
    # Загрузка модели
    net = cv2.dnn.readNetFromCaffe(proto_path, model_path)

    # Препроцессинг изображения
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

    # Применение модели SSD
    net.setInput(blob)
    detections = net.forward()

    # Фильтрация обнаруженных лиц с учетом порога уверенности
    faces = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > confidence_threshold:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x, y, x1, y1) = box.astype("int")
            width = x1 - x
            height = y1 - y
            # Проверка, что размер лица не меньше min_w и min_h
            if width >= min_w and height >= min_h:
                faces.append({'box': [x, y, width, height]})

    return faces


if __name__ == '__main__':
    frame = cv2.imread('./Faces.Best/ID.11.jpg')
    print(detect_face(frame, confidence_threshold=0.55, model_path=model_path, proto_path=proto_path))
