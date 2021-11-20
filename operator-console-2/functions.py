from tkinter.messagebox import askyesno

import paho.mqtt.client as paho
from Robots import *
from player_functions import *
import time
import threading

markerCalculator = Robots()
client = paho.Client()

sendingKey = []

settings_popup = False

entries = {}
bindCommand = None
bindKeyboard = None

sendThread = None


def test():
    print("test button clicked!")


def openSettingsWindow():
    print("opening settings window")
    global settings_popup, entries, bindCommand, bindKeyboard
    if not settings_popup:
        settingsWindow = Window(language['settings'], 500, 250, topLevel=1)
        settings_popup = True
        settingsRoot = settingsWindow.getRoot()
        settingsRoot.attributes("-topmost", True)

        settingsRoot.protocol("WM_DELETE_WINDOW", lambda: on_settingsClose(settingsRoot))
        settingsRoot.resizable(False, False)

        settingsData = readSettingsData()
        if len(settingsData) > 0:
            i = 0
            for data in settingsData:
                label = Label(settingsRoot, text=language[data])
                label.grid(row=i, column=0)
                if len(entries) < len(settingsData):
                    entries[data] = StringVar()
                entry = Entry(settingsRoot, textvariable=entries[data])
                entry.delete(0, END)
                entry.insert(0, settingsData[data])
                entry.grid(row=i, column=1)
                i += 1
            bindCommand = StringVar()
            bindKeyboard = StringVar()

            entryKeyLabel = Label(settingsRoot, text=language['keyLabel'])
            entryKeyLabel.grid(row=1, column=2)

            bindEntryKey = Entry(settingsRoot, textvariable=bindKeyboard)
            bindEntryKey.grid(row=1, column=3)

            entryKeyLabel = Label(settingsRoot, text=language['cmdLabel'])
            entryKeyLabel.grid(row=2, column=2)

            bindEntryCommand = Entry(settingsRoot, textvariable=bindCommand)
            bindEntryCommand.grid(row=2, column=3)

            bindButton = Button(settingsRoot, text=language['Bindkey'], command=bindKey)
            bindButton.grid(row=3, column=3)

            clearBindsButton = Button(settingsRoot, text=language['clearBinds'], command=clearBinds)
            clearBindsButton.grid(row=6, column=3)
        else:
            data = {}
            data['mqtt_host'] = "0.0.0.0"
            data['mqtt_port'] = "1883"
            data['mqtt_login'] = "login"
            data['mqtt_pwd'] = "pwd"
            data['cmd_name'] = "name"
            data['robot_name'] = "rname"
            data['zm_host'] = "0.0.0.0"
            data['zm_login'] = "login"
            data['zm_pass'] = "pwd"
            saveSettingsData(data)


def clearBinds():
    answer = askyesno(title=language['deleteConfirmation'], message=language['deleteMessage'])
    if answer:
        settings = readKeyboardSettings()
        settings.clear()
        print(settings)
        with open('data/keyboard.json', 'w') as f:
            pass
        saveKeyboardSettings(settings)


def bindKey():
    global bindCommand, bindKeyboard, keyboard
    print("Binding key button")
    settings = readKeyboardSettings()
    settings[bindKeyboard.get()] = bindCommand.get()
    print(settings)
    saveKeyboardSettings(settings)
    with open('data/keyboard.json', 'r+', encoding='utf-8') as f:
        keyboard = json.load(f)


def readKeyboardSettings():
    with open('data/keyboard.json', 'r+', encoding='utf-8') as f:
        return json.load(f)


def saveKeyboardSettings(data):
    with open('data/keyboard.json', 'r+', encoding='utf-8') as f:
        json.dump(data, f)


def saveSettingsData(data):
    with open("data/settings.json", 'w', encoding='utf-8') as f:
        json.dump(data, f)


def readSettingsData():
    with open('data/settings.json', 'r+', encoding='utf-8') as f:
        data = json.load(f)
    return data


def on_settingsClose(root):
    global settings_popup, entries
    settings_popup = False
    root.destroy()
    data = {}
    for entry in entries:
        data[entry] = entries[entry].get()
    saveSettingsData(data)


def reloadMQTTConnection():
    print("reloading connections")
    with open('data/settings.json', 'r+', encoding='utf-8') as f:
        settings = json.load(f)
    global sendThread
    try:
        client.disconnect()
    except:
        pass
    client.username_pw_set(settings['mqtt_login'], settings['mqtt_pwd'])
    client.connect(host=settings['mqtt_host'])
    client.loop_start()
    try:
        sendThread = threading.Thread(target=send, args=(), daemon=True)
        sendThread.start()
    except:
        pass


def on_message(client, userdata, msg):
    global markerCalculator
    data = json.loads(msg.payload.decode('utf-8'))
    topic = str(msg.topic)
    markerCalculator.showAll(topic, data, param_1=topicBall[:len(topicBall) - 1],
                             param_2=topicRoot[:len(topicRoot) - 1])


def on_connect(client, userdata, flags, rc):
    print("Connected with code %d." % (rc))
    client.subscribe(topic=topicBall, qos=1)
    client.subscribe(topic=topicRoot, qos=1)


def createMQTTConnection():
    global sendThread
    # MQTT CONNECTION
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(settings['mqtt_login'], settings['mqtt_pwd'])
    try:
        client.connect(host=settings['mqtt_host'])
        sendThread = threading.Thread(target=send, args=(), daemon=True)
        sendThread.start()
    except:
        pass


def send():
    global sendingKey
    sendTopic = topicRobot + settings['robot_name']
    while True:
        time.sleep(0.08)
        if len(sendingKey) > 0:
            for key in sendingKey:
                client.publish(sendTopic, keyboard[key])


def key_pressed(event):
    global sendingKey
    try:
        if not (event.char in sendingKey) and event.char in keyboard:
            sendingKey.append(event.char)
    except KeyError:
        pass


def key_released(event):
    global sendingKey
    try:
        if event.char in sendingKey:
            sendingKey.remove(event.char)
    except KeyError:
        pass
