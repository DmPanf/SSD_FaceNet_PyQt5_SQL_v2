# facenet_recognition.py
# 15-06-2023

import os
import cv2
# import datetime
import numpy as np
import pickle
from keras_facenet import FaceNet  # pip install -q keras-facenet scipy tensorflow
from ssd_face_detection import detect_face

facenet_model = FaceNet()
face_embeddings_path = './data/230418_facenet_ssd_video2_full.pkl'  # './data/230418_facenet_ssd_all_limited.pkl'
with open(face_embeddings_path, 'rb') as file:
    face_embeddings_dict = pickle.load(file)


def cosine_distance(emb1, emb2):
    emb1 = emb1.reshape(-1)
    emb2 = emb2.reshape(-1)
    return 1 - np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))


def facenet_recognition(frame, threshold=0.4):
    faces = detect_face(frame)
    #print(faces)

    for face in faces:
        x, y, w, h = face['box']

        # Игнорирование лиц меньше 100x120
        if w < 100 or h < 120:
            continue

        face_crop = frame[y:y+h, x:x+w]
        face_img = cv2.resize(face_crop, (160, 160))
        face_embedding = facenet_model.embeddings(np.expand_dims(face_img, 0))

        min_distance = float('inf') # устанавливаем переменную min_distance равной бесконечности
        identity = None

        for image_path, data in face_embeddings_dict.items():
            distance = cosine_distance(face_embedding, data['embeddings'])

            if distance < min_distance:
                min_distance = distance
                identity = data['label']

        # Если минимальное расстояние больше порога, считаем лицо неизвестным
        if min_distance > threshold:
            #print('\n', min_distance, threshold, identity)
            return None
        else:
            return identity # возвращаем ID сотрудника


if __name__ == '__main__':
    # video_capture = cv2.VideoCapture(video_path)
    # ret, frame = video_capture.read()
    frame = cv2.imread('./Faces.Best/ID.08.jpg')
    print(facenet_recognition(frame, threshold=0.4))
