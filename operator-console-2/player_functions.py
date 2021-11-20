import random

from Window import *
from PIL import ImageTk, Image
import vlc
from vars import *


popup_init = False
players = [None, None]
playersFrame = [None, None]

def on_close(root):
    global popup_init
    popup_init = False
    root.destroy()


def chooseCamera(frame, changeBtn, stopBtn, cameraNum):
    global popup_init
    if not popup_init:
        chooseCameraWindow = Window(language['titleChoosingWindow'], pitchSize[0], pitchSize[1], topLevel=1)
        print(chooseCameraWindow)
        chooseCameraRoot = chooseCameraWindow.getRoot()
        chooseCameraRoot.protocol("WM_DELETE_WINDOW", lambda: on_close(chooseCameraRoot))
        chooseCameraRoot.resizable(False, False)
        chooseCameraRoot.attributes("-topmost", True)
        chooseCameraFrame = chooseCameraWindow.createFrame(0, 0, pitchSize[0], pitchSize[1], rwidth=0)

        chooseCameraCanvas = chooseCameraWindow.createCanvas(chooseCameraFrame)
        chooseCameraCanvas.config(width=pitchSize[0], height=pitchSize[1])
        chooseCameraWindow.placeCanvas(chooseCameraCanvas, 2, 0.5, 0.5)

        pitchImage = ImageTk.PhotoImage(Image.open("images/pitch.png"), Image.ANTIALIAS)

        chooseCameraCanvas.background = pitchImage
        chooseCameraCanvas.create_image(pitchSize[0] / 2, pitchSize[1] / 2, image=pitchImage, anchor=CENTER)

        cameraImage = PhotoImage(file="images/cctv-camera.png")

        for camera in camConfig:
            print(camera['address'])
            video_host = zm_pattern.format(settings['zm_host'], camera['address'], random.randint(1000, 100000),
                                           settings['zm_login'], settings['zm_pass'])

            btn = chooseCameraWindow.createButton(chooseCameraFrame,
                                                  lambda address=video_host: onCameraSet(frame, address,
                                                                                                chooseCameraRoot,
                                                                                                changeBtn,
                                                                                                stopBtn, cameraNum),
                                                  image=cameraImage)
            btn.image = cameraImage
            chooseCameraWindow.placeButton(btn, 1, x=camera['x'], y=camera['y'])

        popup_init = True


def stopCameraStream(cameraNum, changeBtn, stopBtn):
    cameraNum -= 1
    players[cameraNum].stop()
    playersFrame[cameraNum].place_forget()
    stopBtn.place_forget()
    changeBtn.place_forget()
    changeBtn.place(relx=0.5, rely=0.5)


def onCameraSet(frame, address, root, changeBtn, stopBtn, cameraNum):
    cameraNum -= 1
    global popup_init
    print("connecting to camera: {}".format(address))
    popup_init = False

    if players[cameraNum] is not None:
        players[cameraNum].stop()
        playersFrame[cameraNum].place_forget()
    playersFrame[cameraNum] = Frame(frame, width=width / 2, height=(height / 2) - 25, bg="black")
    playersFrame[cameraNum].place(x=0, y=0)
    players[cameraNum] = vlcPlayer(playersFrame[cameraNum], address)
    changeBtn.place_forget()
    changeBtn.place(relx=0, rely=0.93)
    stopBtn.place(relx=0.90, rely=0.93)
    root.destroy()

def vlcPlayer(videopanel, server):
    Instance = vlc.Instance()
    player = Instance.media_player_new()
    srvMedia = Instance.media_new(server)
    srvMedia.add_option('network-caching=0')
    srvMedia.add_option('--http-caching 0')
    player.set_media(srvMedia)
    h = videopanel.winfo_id()
    print(h)
    player.set_hwnd(h)
    player.play()
    return player
