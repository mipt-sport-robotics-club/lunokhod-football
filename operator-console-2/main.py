# /
# Консоль оператора для управления луноходами.
# Возможности:
# Отображения роботов и мяча на поле
# Просмотрел камер с поля/робота
# Управление роботом путём нажатия на клавиши клавиатуры
# Программирование клавиш
#
#
# Разработчик: Клименко Алексей
# Дата: 10.10.2021
# #


from functions import *

robotsArray = {}
robotsImageArray = {}
robotsTextArray = {}

app = Window(language['titleMainWindow'], width, height)

app.getRoot().bind("<KeyPress>", key_pressed)
app.getRoot().bind("<KeyRelease>", key_released)
app.getRoot().resizable(False, False)

if __name__ == '__main__':
    createMQTTConnection()

    # CREATE WINDOW
    pitchFrame = app.createFrame(0, 0, width, height / 2)
    camera1Frame = app.createFrame(0, height / 2, width / 2, height / 2, rwidth=0.5)
    camera2Frame = app.createFrame(width / 2, height / 2, width / 2, height / 2, rwidth=0.5)
    print(camera1Frame, camera2Frame)

    sc1 = app.createButton(camera1Frame, lambda: stopCameraStream(camera1Frame, cc1, sc1), text=language['stopCamera'])
    cc1 = app.createButton(camera1Frame, lambda: chooseCamera(app.getFrame(camera1Frame), cc1, sc1, camera1Frame),
                           text=language['ChooseCamera0'])
    app.placeButton(cc1, 2, 0.5, 0.5, CENTER)

    sc2 = app.createButton(camera2Frame, lambda: stopCameraStream(camera2Frame, cc2, sc2), text=language['stopCamera'])
    cc2 = app.createButton(camera2Frame, text=language['ChooseCamera1'],
                           command=lambda: chooseCamera(app.getFrame(camera2Frame), cc2, sc2, camera2Frame))
    app.placeButton(cc2, 2, 0.5, 0.5, CENTER)

    mainMenu = app.createMenu()
    app.addCommand(mainMenu, language['settings'], openSettingsWindow)
    app.addCommand(mainMenu, language['reloadConnections'], reloadMQTTConnection)
    app.configRoot(mainMenu)

    pitchCanvas = app.createCanvas(pitchFrame)
    pitchCanvas.config(width=pitchSize[0], height=pitchSize[1])

    app.placeCanvas(pitchCanvas, 2, 0.5, 0.5, CENTER)

    pitchImage = ImageTk.PhotoImage(Image.open("images/pitch.png"), Image.ANTIALIAS)

    pitchCanvas.background = pitchImage
    bg = pitchCanvas.create_image(pitchSize[0] / 2, pitchSize[1] / 2, image=pitchImage, anchor=CENTER)

    markerCalculator.setCanvas(pitchCanvas)  # Create marker drawer on canvas pitchCanvas

    client.loop_start()
    app.loop()
    # /CREATE WINDOW
