import paho.mqtt.client as paho
from tkinter import *
import json
from PIL import Image, ImageTk
from math import atan, degrees

mqtt_username = ""
mqtt_password = ""
mqtt_host = "192.168.0.102"
robotsNum = 6
pitchCornersIdList = [1, 2, 3]

pitchSize = (474, 336)
cameraResolution = (1280, 720)

topicRoot = "MIPT-SportRoboticsClub/LunokhodFootball/RawARUCO/#"
topicBall = "MIPT-SportRoboticsClub/LunokhodFootball/RawBALL/#"

oldMarkerIdList = []


def centroid(vertexes):
    _x_list = [vertex[0] for vertex in vertexes]
    _y_list = [vertex[1] for vertex in vertexes]
    _len = len(vertexes)
    _x = sum(_x_list) / _len
    _y = sum(_y_list) / _len
    return (_x, _y)


def mapp(n, a1, a2, b1, b2):
    return (n - a1) * (b2 - b1) / (a2 - a1) + b1


def on_connect(client, userdata, flags, rc):
    print("Connected with code %d." % (rc))


def on_message(client, userdata, msg):
    global oldMarkerIdList, robotImage, robotsArray, robotsImageArray
    data = json.loads(msg.payload.decode('utf-8'))
    topic = str(msg.topic)

    if topic.__contains__(topicRoot[:len(topicRoot) - 1]):
        markerIdList = []
        if data['count'] > 0:
            for marker in data['markers']:
                markerIdList.append(marker['marker-id'])
                try:
                    oldMarkerIdList.remove(marker['marker-id'])
                except ValueError:
                    pass
                aruco_center = centroid(((marker['corners']['1']['x'], marker['corners']['1']['y']),
                                         (marker['corners']['2']['x'], marker['corners']['2']['y']),
                                         (marker['corners']['3']['x'], marker['corners']['3']['y']),
                                         (marker['corners']['4']['x'], marker['corners']['4']['y'])
                                         ))
                coordsX = mapp(aruco_center[0], 0, cameraResolution[0], 0, pitchSize[0])
                coordsY = mapp(aruco_center[1], 0, cameraResolution[1], 0, pitchSize[1])
                leftCornerX = mapp(marker['corners']['1']['x'], 0, cameraResolution[0], 0, pitchSize[0])
                leftCornerY = mapp(marker['corners']['1']['y'], 0, cameraResolution[1], 0, pitchSize[1])
                rightCornerX = mapp(marker['corners']['2']['x'], 0, cameraResolution[0], 0, pitchSize[0])
                rightCornerY = mapp(marker['corners']['2']['y'], 0, cameraResolution[1], 0, pitchSize[1])
                try:
                    angle = degrees(atan((rightCornerY - leftCornerY) / (rightCornerX - leftCornerX)))
                except ZeroDivisionError:
                    angle = 90
                    pass
                localCoordinateX1 = leftCornerX - coordsX
                localCoordinateY1 = leftCornerY - coordsY
                localCoordinateX2 = rightCornerX - coordsX
                localCoordinateY2 = rightCornerY - coordsY

                try:
                    canvas.delete(robotsArray[i])
                except:
                    pass

                if marker['marker-id'] in pitchCornersIdList:
                    canvas.coords(pitchMarkersArray[marker['marker-id'] - 1], coordsX - 10, coordsY - 10, coordsX + 10,
                                  coordsY + 10)
                    canvas.coords(pitchTextArray[marker['marker-id'] - 1], coordsX, coordsY)
                else:
                    if (
                            localCoordinateX1 > 0 and localCoordinateY1 > 0 and localCoordinateX2 > 0 and localCoordinateY2 > 0) or \
                            (
                                    localCoordinateX1 < 0 and localCoordinateY1 > 0 and localCoordinateX2 < 0 and localCoordinateY2 > 0) or \
                            (
                                    localCoordinateX1 > 0 and localCoordinateY1 > 0 and localCoordinateX2 < 0 and localCoordinateY2 > 0) or \
                            (
                                    localCoordinateX1 > 0 and localCoordinateY1 < 0 and localCoordinateX2 > 0 and localCoordinateY2 > 0 and -90 < angle < 0) or \
                            (
                                    localCoordinateX1 < 0 and localCoordinateY1 > 0 and localCoordinateX2 < 0 and localCoordinateY2 < 0 and 0 < angle < 90):
                        angle = angle - 180
                    robotsImageArray[marker['marker-id'] - 1] = ImageTk.PhotoImage(robotImage.rotate(-angle))
                    robotsArray[marker['marker-id'] - 1] = canvas.create_image(coordsX, coordsY, image=robotsImageArray[marker['marker-id'] - 1])
                    canvas.coords(robotsTextArray[marker['marker-id'] - 1], coordsX, coordsY)

            for marker in oldMarkerIdList:
                if marker in pitchCornersIdList:
                    canvas.coords(pitchMarkersArray[marker - 1], 0, 0, 0, 0)
                    canvas.coords(pitchTextArray[marker - 1], 0, 0)
                else:
                    canvas.delete(robotsArray[marker-1])
                    canvas.coords(robotsTextArray[marker - 1], 0, 0)

            oldMarkerIdList = markerIdList.copy()
        else:
            for marker in oldMarkerIdList:
                if marker in pitchCornersIdList:
                    canvas.coords(pitchMarkersArray[marker - 1], 0, 0, 0, 0)
                    canvas.coords(pitchTextArray[marker - 1], 0, 0)
                else:
                    canvas.delete(robotsArray[marker-1])
                    canvas.coords(robotsTextArray[marker - 1], 0, 0)
            pass

    if topic.__contains__(topicBall[:len(topicBall) - 2]):
        if data['ball'] == "None":
            canvas.coords(ball, 0, 0, 0, 0)
        else:
            ballX = mapp(data['ball']['center']['x'], 0, cameraResolution[0], 0, pitchSize[0])
            ballY = mapp(data['ball']['center']['y'], 0, cameraResolution[1], 0, pitchSize[1])
            canvas.coords(ball, ballX - 5, ballY - 5, ballX + 5, ballY + 5)


client = paho.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqtt_username, mqtt_password)
client.connect(host=mqtt_host)

client.subscribe(topic=topicBall, qos=1)
client.subscribe(topic=topicRoot, qos=1)

root = Tk()
root.geometry("474x336")

canvas = Canvas(root)
canvas.pack(fill=BOTH, expand=1)

robotsArray = {}
robotsImageArray = {}
robotsTextArray = {}

pitchMarkersArray = {}
pitchTextArray = {}
robotImage = Image.open("robotIcon.png")

for i in range(robotsNum):
    robotsArray[i] = canvas.create_image(0, 0)
    robotsImageArray[i] = ImageTk.PhotoImage(robotImage.rotate(0))
    robotsTextArray[i] = canvas.create_text(0, 0, text=i + 1)

for i in range(len(pitchCornersIdList)):
    pitchMarkersArray[i] = canvas.create_rectangle(0, 0, 0, 0)
    pitchTextArray[i] = canvas.create_text(0, 0, text=i + 1)

ball = canvas.create_oval(0, 0, 10, 10, fill='red')

client.loop_start()
root.mainloop()
