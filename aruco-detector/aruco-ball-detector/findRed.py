#from imutils.video import VideoStream as PiVideoStream
from t2 import PiVideoStream
import time
import numpy as np
import cv2
import json
from threading import Thread
import paho.mqtt.publish as publish

def sendMarkers(topic, msg):
	#print(json.dumps(msg))
	publish.single(topic, json.dumps(msg), hostname=hostName)

camId = "FootballCam-01"
topicRoot = "MIPT-SportRoboticsClub/LunokhodFootball/RawARUCO/"
topicBall = "MIPT-SportRoboticsClub/LunokhodFootball/RawBALL/"
hostName = "localhost"

#cv2.namedWindow( "result" ) # создаем главное окно
cv2.namedWindow( "origin" )
lower_red = np.array([0, 70, 80], dtype = "uint8")
upper_red = np.array([19, 255, 255], dtype = "uint8")

lower_violet = np.array([160, 85, 110], dtype = "uint8")
upper_violet = np.array([180, 255, 255], dtype = "uint8")

vs = PiVideoStream().start()
time.sleep(2.0)

minDist = 100
param1 = 30 
param2 = 15 #Меньше значение -> больше ложных кругов
minRadius = 5
maxRadius = 100 #Минимальный и максимальный радиус настроить при использовании камеры на нужной высоте

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11) #используем AprilTag

while True:
	frame = vs.read()
	if frame is None:
		break

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
			# print(json.dumps(marker))
			thread = Thread(target=sendMarkers, args=(topicRoot + camId, marker))
			thread.start()
            #publish.single(topicRoot + camId, json.dumps(marker), hostname=hostName)

		cv2.aruco.drawDetectedMarkers(frame, corners, ids)


	if cv2.waitKey(1) & 0xFF == ord(' '):  # Останавливаем, если нажат пробел
		break
		
	blurred = cv2.GaussianBlur(frame, (7, 7), 0.5)
	converted = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
	red_mask = cv2.inRange(converted, lower_red, upper_red) + cv2.inRange(converted, lower_violet, upper_violet)
	circles = cv2.HoughCircles(red_mask, cv2.HOUGH_GRADIENT, 1, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
	
	if circles is not None:
		circles = np.round(circles[0, :]).astype("int")
		
		for (x, y, r) in circles:
			cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
			cv2.rectangle(frame, (x-5, y-5), (x+5, y+5), (0, 128, 255), -1)
			ball = {'ball':{'cam-id': camId, 'center': {'x':float(x),'y':float(y)}}}
			thread1 = Thread(target=sendMarkers, args=(topicBall + camId, ball))
			thread1.start()
			
	cv2.imshow('origin', frame)
	ch = cv2.waitKey(5)
