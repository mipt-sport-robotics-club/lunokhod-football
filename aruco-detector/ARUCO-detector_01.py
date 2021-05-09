import cv2
import cv2.aruco
import paho.mqtt.publish as publish
import json

# устанавливаем основные атрибуты
camId = "FootballCam-01"
topicRoot = "MIPT-SportRoboticsClub/LunokhodFootball/RawARUCO/"
hostName = "localhost"

camera = cv2.VideoCapture(0)  # создаем объект VideoCapture  с 'первой' камерой (Вашей вебкой)
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11) #используем AprilTag
while (True):
    ret, frame = camera.read()  # фиксируем кадр с помощью frame

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    (corners,ids,rejected)=cv2.aruco.detectMarkers(gray, dictionary) #находим маркеры

    if len(corners) > 0:
        markers = []
        for i in [0, len(corners)-1]: #если найден хоть один маркер
            #формируем объект для записи в формате JSON
            marker = {'marker':{'cam-id': camId, 'marker-id':int(ids[i][0]),
                      'corners': {'1':{'x':float(corners[i][0][0][0]),'y':float(corners[i][0][0][1])},
                                  '2':{'x':float(corners[i][0][1][0]),'y':float(corners[i][0][1][1])},
                                  '3':{'x':float(corners[i][0][2][0]),'y':float(corners[i][0][2][1])},
                                  '4':{'x':float(corners[i][0][3][0]),'y':float(corners[i][0][3][1])}
                      }}}
            #публикуем строковый dump JSON объекта в топик, состоящий из корневого и id камеры
            publish.single(topicRoot + camId, json.dumps(marker), hostname=hostName)
        cv2.aruco.drawDetectedMarkers(gray, corners, ids)

    cv2.imshow('Press Spacebar to Exit', gray)  # отображаем  frame

    if cv2.waitKey(1) & 0xFF == ord(' '):  # Останавливаем, если нажат пробел
        break

camera.release()  # Очистка после обнаружения нажатого пробела.
cv2.destroyAllWindows()



