import asyncio
import cv2
import concurrent
import logging
import math
import time
import numpy as np
from imutils.video import FPS
import imutils
import paho.mqtt.client as paho
import json
from collections import deque

camId = "FootballCam-01"
topicRoot = "MIPT-SportRoboticsClub/LunokhodFootball/RawARUCO/"
topicBall = "MIPT-SportRoboticsClub/LunokhodFootball/RawBALL/"
hostName = "192.168.0.104"
mqtt_login = "explorer"
mqtt_pwd = "hnt67kl"
show = False

client = paho.Client()
client.username_pw_set(mqtt_login, mqtt_pwd)
client.connect(host=hostName)

DICTIONARY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)

# pi cam
CAMERA_MATRIX = np.array([[1481.7527738084875, 0.0, 936.8020968222914],[0.0, 1479.6348449552158, 557.8124212584266],[0.0, 0.0, 1.0]])
DIST_COEFFS = np.array([0.0006378238490344762,  2.4530717876176675,  0.00014402748184350837, -0.008451368578742634, -15.123459467944718])

PARAMETERS =  cv2.aruco.DetectorParameters_create()
MARKER_EDGE = 0.05


buffer = 64

greenLower = (170, 106, 70)
greenUpper = (185, 255, 255)
pts = deque(maxlen=buffer)

def sendMarkers(topic, msg):
	#publish.single(topic, json.dumps(msg), hostname=hostName, auth={'username' : mqtt_login, 'password': mqtt_pwd})
	client.publish(topic, json.dumps(msg))

def angles_from_rvec(rvec):
    r_mat, _jacobian = cv2.Rodrigues(rvec)
    a = math.atan2(r_mat[2][1], r_mat[2][2])
    b = math.atan2(-r_mat[2][0], math.sqrt(math.pow(r_mat[2][1],2) + math.pow(r_mat[2][2],2)))
    c = math.atan2(r_mat[1][0], r_mat[0][0])
    return [a,b,c]

def calc_heading(rvec):
    angles = angles_from_rvec(rvec)
    degree_angle =  math.degrees(angles[2])
    if degree_angle < 0:
        degree_angle = 360 + degree_angle
    return degree_angle

def find_markers(frame, show=False):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, DICTIONARY, parameters=PARAMETERS)
    if show:
    	cv2.aruco.drawDetectedMarkers(frame, corners, ids)

    rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, MARKER_EDGE, CAMERA_MATRIX, DIST_COEFFS)

    result = set()
    if ids is None:
        return result

    for i in range(0, len(ids)):
        try:
            id = str(ids[i][0])

            marker = np.squeeze(corners[i])

            x0, y0 = marker[0]
            x2, y2 = marker[2]
            x = int((x0 + x2)/2)
            y = int((y0 + y2)/2)

            heading = calc_heading(rvecs[i][0])
            result.add((id, x, y, heading))
        except Exception:
            traceback.print_exc()

    return result

def find_ball(frame, show=False):
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None

	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		# only proceed if the radius meets a minimum size
		if radius > 0 and show:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)
	# update the points queue
	if show:
		pts.appendleft(center)

	# #Ball Tracking with OpenCV
	# # loop over the set of tracked points
	if show:
		for i in range(1, len(pts)):
			# if either of the tracked points are None, ignore
			# them
			if pts[i - 1] is None or pts[i] is None:
				continue
			# otherwise, compute the thickness of the line and
			# draw the connecting lines
			thickness = int(np.sqrt(buffer / float(i + 1)) * 2.5)
			cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
	return center

def capture():
	if show:
		cv2.namedWindow("input")
	cap = cv2.VideoCapture(0)
	cap.set( cv2.CAP_PROP_FRAME_HEIGHT, 720 )
	cap.set( cv2.CAP_PROP_FRAME_WIDTH, 1280 )
	cap.set(cv2.CAP_PROP_FPS, 15)
	cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
	cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.3)
	frame_rate = cap.get(cv2.CAP_PROP_FPS)
	width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
	height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
	print("Frame Rate: ", frame_rate)
	print("Height: ", height)
	print("Width: ", width)
	time.sleep(2.0)

	logging.info("Start capturing from pi camera.")
	try:
		frame_num = 0
		time1 = 0
		time2 = 0
		# stream = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
		# for capture in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		while True:
			print(time.time())
			time1 = time.time()
			print("Calculating time: ",time1 - time2)
			frame_num += 1
			# capture =  next(stream)
			ret, img = cap.read()
			time2 = time.time()
			print("Capturing time: ",time2 - time1)
			# frame = capture.array
			# if frame_num % 5 != 0:
			ball_img = imutils.resize(img, width=640, height=480)
			markers = find_markers(img, show)
			for marker in markers:
				sendMarkers(topicRoot + camId, marker)
			ball = find_ball(ball_img, show)
			sendMarkers(topicBall + camId, ball)
			# rawCapture.truncate(0)
			# cv2.imshow("origin", frame)
			print('fps - ', 1/(time.time() - time1))
			if show:
				cv2.imshow("input", ball_img)
			key = cv2.waitKey(10)
			if key == 27:
				break
			# print(frame_num/(time.time() - timeCheck1))
			# fps.update()

	except Exception as e:
		logging.error("Capturing stopped with an error:" + str(e))
	finally:
		# camera.close()
		cv2.destroyAllWindows()
		cv2.VideoCapture(0).release()

if __name__ == "__main__":
	capture()