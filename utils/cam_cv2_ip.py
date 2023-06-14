# cam_cv2_ip.py
# 15-06-2023

import cv2

#camera_url = "rtsp://10.10.8.70:554/11?user:myQ-1987ip"
camera_url = 'rtsp://"office@cietrussia.ru":"g9xq9tk#"@195.91.179.130'
camera = cv2.VideoCapture(camera_url)

while True:
    ret, frame = camera.read()
    cv2.imshow('IP Camera', frame)
    if cv2.waitKey(1) == 27:
        break

camera.release()
cv2.destroyAllWindows()
