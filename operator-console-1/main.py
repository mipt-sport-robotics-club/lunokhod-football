from tkinter import *
import vlc
from MQTT import *
from Notification import *
import json
import keyboard

setting_names = ['Command server address', 'Command server port', 'Command server login', 'Command server password',
                 'Telemetry server address', 'Telemetry server login', 'Telemetry server password',
                 'Telemetry server port',
                 'Command name', 'Robot name', 'Bluetooth MAC-address']

codeNames = {
    '200': 'Bluetooth connected',
    '202': 'Bluetooth connection error',
    '203': 'Bluetooth disconnected',
    '204': 'Bluetooth sending error'

}

setting_entry = []

settings = {}

language = {}

sendingKey = []

MACEXPRESSION = "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})|([0-9a-fA-F]{4}\\.[0-9a-fA-F]{4}\\.[0-9a-fA-F]{4})$"
camList = """
{}
"""
cams = json.loads(camList)
millis1 = 0
millis2 = 0


def vlcPlayer(videopanel, server):
    Instance = vlc.Instance()
    player = Instance.media_player_new()
    srvMedia = Instance.media_new(server)
    srvMedia.add_option('network-caching=0')
    player.set_media(srvMedia)
    h = videopanel.winfo_id()
    player.set_hwnd(h)
    player.play()
    return player


class test(Frame):
    mosquittoCommand = None
    mosquittoTelemetry = None
    bindCommand = None
    useTelemetry = None
    fStart = False
    keyCommand = {}
    notification_manager = Notification_Manager(background="white")
    videoPanels = []
    buttons = []

    def __init__(self, parent):
        super().__init__(parent)
        self.pitchImage = PhotoImage(file="pitch.png")
        self.camImage = PhotoImage(file="cctv-camera.png")
        self.pitchMap = Label(image=self.pitchImage)
        self.gui = parent
        self.useTelemetry = BooleanVar()
        self.gui.bind('<KeyRelease>', self.keyRelease)
        self.gui.bind('<Escape>', self.showMap)
        self.gui.bind('<KeyPress>', self.keyPress)
        self.n1Flag = False
        try:
            self.initMQTT()
        except TypeError:
            self.fStart = True
            pass
        self.initUI()
        if not self.fStart:
            makeUI = threading.Thread(target=self.initButtons, args=(), daemon=False)
            makeUI.start()

        pingThread = threading.Thread(target=self.robotPing, args=(), daemon=True)
        pingThread.start()

    def initUI(self):
        self.gui.title(language['titleMainWindow'])
        self.gui.geometry('1280x720')
        self.gui.menubar = Menu()
        self.gui.config(menu=self.gui.menubar)
        self.gui.menubar.add_command(label=language['settings'], command=self.settings_clicked)

    def initButtons(self):
        global cams
        ml1 = int(round(time.time() * 1000))
        while cams == json.loads('{}') and int(round(time.time() * 1000)) - ml1 < 2000:
            print(int(round(time.time() * 1000)) - ml1 < 2000)
            time.sleep(0.1)
        print(cams)
        if int(round(time.time() * 1000)) - ml1 > 2000:
            self.notification_manager.alert(language['serverTimeError'])
        else:
            i = 0
            for camera in cams:
                vp = Frame(self.gui)
                can = Canvas(vp)
                can.place(x=0, y=0)
                self.videoPanels.append(vp)
                print(camera['address'])
                vlcPlayer(self.videoPanels[i], camera['address'])
                btn = Button(self.pitchMap, command=lambda i=i: self.changeToCam(i), image=self.camImage)
                self.buttons.append(btn)
                btn.place(x=camera['x'], y=camera['y'])
                i += 1
            self.pitchMap.place(relx=0.5, anchor=N)

    def initMQTT(self):
        self.mosquittoCommand = MQTT(server=settings['Command server address'], login=settings['Command server login'],
                                     password=settings['Command server password'],
                                     port=int(settings['Command server port']))
        self.mosquittoCommand.sendTopic = settings['Robot name']
        self.mosquittoCommand.client.on_connect = self.onCon
        self.mosquittoCommand.client.on_message = self.onMessage
        self.mosquittoCommand.isMain = True
        self.mosquittoCommand.connect()

        print(settings['UseTelemetry'])
        try:
            if settings['UseTelemetry']:
                print('Using Telem')
                self.mosquittoTelemetry = MQTT(server=settings['Telemetry server address'],
                                               login=settings['Telemetry server login'],
                                               password=settings['Telemetry server password'],
                                               port=int(settings['Telemetry server port']))
                self.mosquittoTelemetry.sendTopic = settings['Robot name']
                self.mosquittoTelemetry.on_connect = self.onTelemCon
        except KeyError:
            pass
        try:
            with open('keyboard.json', 'r+') as file:
                self.keyCommand = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            pass

    def changeToCam(self, cam):
        self.pitchMap.place_forget()
        for i in range(len(self.videoPanels)):
            self.videoPanels[i].place_forget()
            self.buttons[i].place_forget()

        self.videoPanels[cam].place(relx=.5, rely=0.1, anchor='n')
        self.videoPanels[cam].pack_propagate(False)
        self.videoPanels[cam].grid_propagate(False)
        self.videoPanels[cam].configure(height=self.gui.winfo_height() / 1.5, width=self.gui.winfo_width() / 1.5)

    def showMap(self, event):
        i = 0
        for camera in cams:
            self.buttons[i].place(x=camera['x'], y=camera['y'])
            self.videoPanels[i].place_forget()
            i += 1
        self.pitchMap.place(relx=0.5, anchor=N)

    def setCams(self, cameras):
        global cams
        cams = json.loads(cameras)

    def onMessage(self, client, userdata, msg):
        rec = str(msg.payload)
        rec = rec[2:len(rec) - 1]
        print(msg.topic)
        topic = str(msg.topic)

        global cams
        if topic.find('server') > -1:
            if not rec == 'cams':
                try:
                    self.setCams(rec)
                except ValueError:
                    pass
        elif topic.find('status') > -1:
            if rec == '200':
                self.notification_manager.success(codeNames[rec])
                self.n1Flag = False
                print("yEP3")
            elif rec == '202' or rec == '203' or rec == '204':
                if not self.n1Flag:
                    self.notification_manager.alert(codeNames[rec])
                    self.n1Flag = True
            elif rec == '201':
                global millis2
                millis2 = int(round(time.time() * 1000))
                # It`s a ping to a bluetooth car
                # Do what you need
                print(millis2 - millis1)
                if self.nFlag:
                    self.notification_manager.success('Ping answer received')
                pass
        elif topic.find('/') > -1:
            pass
        else:
            print(rec)

    def robotPing(self):
        while True:
            self.mosquittoCommand.publish(self.mosquittoCommand.sendTopic, "w")
            global millis1, millis2
            if millis2 - millis1 < -1000:
                if not self.nFlag:
                    self.notification_manager.alert('Bluetooth ping error')
                self.nFlag = True
            else:
                self.nFlag = False
            millis1 = int(round(time.time() * 1000))
            time.sleep(10)

    def onCon(self, client, userdata, flags, rc):
        print('Mqtt connected')
        client.subscribe(self.mosquittoCommand.sendTopic + '/status')
        client.publish(self.mosquittoCommand.sendTopic + '/server', 'cams')
        client.subscribe(self.mosquittoCommand.sendTopic + '/server')
        client.publish(self.mosquittoCommand.sendTopic + '/status', 'Connected')
        if not settings['UseTelemetry']:
            print('Using command telemetry')
            client.subscribe(self.mosquittoCommand.sendTopic + '/telemetry')

    def onTelemCon(self, client, userdata, flags, rc):
        print('Mqtt connected')
        client.publish(self.mosquittoTelemetry.sendTopic + '/telem/status', 'Connected')

    def settings_clicked(self):
        print('Settings clicked!')
        gui1 = Toplevel(self.gui)
        global setting_entry, settings
        gui1.title(language['titleSettingsWindow'])
        gui1.geometry("730x300")
        row = 0
        setting_entry = []
        with open('config.json', 'r+', encoding='utf-8') as f:
            settings = json.load(f)
        for name in setting_names:
            Label(gui1, text=language[name], font=('Arial', 8), width=40).grid(column=0, row=row)

            setting_entry.append(Entry(gui1, width=20))
            setting_entry[row].grid(column=1, row=row)
            try:
                setting_entry[row].insert(0, settings[setting_names[row]])
            except KeyError:
                settings[setting_names[row]] = None
            except TclError:
                pass
            row += 1
        Button(gui1, text=language['SaveBtn'], command=self.saveBtn).grid(column=0, row=row)
        row = 0
        Button(gui1, text=language['Bindkey'], command=self.bindBtn).grid(column=3, row=row)
        row += 1
        Button(gui1, text=language['ClearBinds'], command=self.clearBind).grid(column=3, row=row)
        row += 1
        Label(gui1, text=language['InputCommand'], font=('Arial', 8), width=20).grid(column=3, row=row)
        self.bindCommand = Entry(gui1, width=20)
        self.bindCommand.grid(column=4, row=row)
        row += 1
        Checkbutton(gui1, text=language['UseTelemetryServer'], variable=self.useTelemetry).grid(column=3, row=row)

        gui1.grab_set()

    def bindBtn(self):
        key = keyboard.read_key()
        try:
            with open('keyboard.json', 'r+') as file:
                self.keyCommand = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            pass
        self.keyCommand[key] = self.bindCommand.get()
        with open('keyboard.json', 'w+') as file:
            file.write(json.dumps(self.keyCommand))
        self.notification_manager.success(
            "Command {0} successfully bounded to key {1}".format(self.keyCommand[key], key)
        )

    def clearBind(self):
        self.keyCommand = """{}"""
        with open('keyboard.json', 'w+') as file:
            json.dump(self.keyCommand, file)

    def saveBtn(self):
        print("Save button clicked!")
        err = False
        global settings
        old = settings.copy()
        for i in range(len(setting_names)):
            data = setting_entry[i].get()
            if data == '':
                err = True
            else:
                settings[setting_names[i]] = data
        settings['UseTelemetry'] = self.useTelemetry.get()
        if self.fStart:
            try:
                self.initMQTT()
                self.fStart = False
            except TypeError:
                self.notification_manager.alert(language['incorrectData'])

        if self.useTelemetry.get():
            if self.mosquittoTelemetry is None:
                print('Creating mt copy')
                self.mosquittoTelemetry = MQTT(server=settings['Telemetry server address'],
                                               login=settings['Telemetry server login'],
                                               password=settings['Telemetry server password'],
                                               port=int(settings['Telemetry server port']))
                self.mosquittoTelemetry.sendTopic = settings['Robot name']
                self.mosquittoTelemetry.on_connect = self.onTelemCon
            else:
                try:
                    self.mosquittoTelemetry.reconnect(address=settings['Telemetry server address'],
                                                      login=settings['Telemetry server login'],
                                                      password=settings['Telemetry server password'],
                                                      port=int(settings['Telemetry server port']))
                except AttributeError:
                    self.mosquittoTelemetry = MQTT(server=settings['Telemetry server address'],
                                                   login=settings['Telemetry server login'],
                                                   password=settings['Telemetry server password'],
                                                   port=int(settings['Telemetry server port']))
                    self.mosquittoTelemetry.sendTopic = settings['Robot name']
                    self.mosquittoTelemetry.on_connect = self.onTelemCon
        else:
            print('Subscribing')
            self.mosquittoCommand.subscribe(self.mosquittoCommand.sendTopic + '/telemetry')
            self.mosquittoCommand.publish(self.mosquittoCommand.sendTopic + '/telemetry',
                                          'Saved')

        if not old['Robot name'] == settings['Robot name']:
            self.mosquittoCommand.updateTopic(topic=settings['Robot name'],
                                              old_topic=old['Robot name'])
        if old['Command server address'] is not settings['Command server address'] \
                or old['Command server port'] is not settings['Command server port'] \
                or old['Command server login'] is not settings['Command server login'] \
                or old['Command server password'] is not settings['Command server password']:
            if not bool(match(DOMAINEXPRESSION, settings['Command server address'])) \
                    and not bool(match(IPEXPRESSIOM, settings['Command server address'])):
                err = True
            else:
                self.mosquittoCommand.reconnect(address=settings['Command server address'],
                                                login=settings['Command server login'],
                                                password=settings['Command server password'],
                                                port=int(settings['Command server port']))

        if bool(match(MACEXPRESSION, settings['Bluetooth MAC-address'])):
            self.mosquittoCommand.publish("{0}/{1}".format(settings['Robot name'], 'addMac'),
                                          settings['Bluetooth MAC-address'])
        else:
            self.notification_manager.warning("Wrong MAC address format, file not saved")
            err = True

        if not err:
            print('Saved')
            with open('config.json', 'w+') as file:
                json.dump(settings, file)

    def keyRelease(self, event):
        global sendingKey
        try:
            command = self.keyCommand[event.char]
            if command in sendingKey:
                sendingKey.remove(command)
                self.mosquittoCommand.setKey(sendingKey)
        except KeyError:
            pass

    def keyPress(self, event):
        global sendingKey
        try:
            command = self.keyCommand[event.char]
            if not (command in sendingKey):
                sendingKey.append(command)
                self.mosquittoCommand.setKey(sendingKey)
        except KeyError:
            pass


if __name__ == '__main__':
    try:
        with open('config.json', 'r+', encoding='utf-8') as f:
            settings = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        with open('config.json', 'w+', encoding='utf-8') as f:
            for i in range(len(setting_names)):
                settings[setting_names[i]] = None
            json.dump(settings, f)
    try:
        with open('language.json', 'r+', encoding='utf-8') as f:
            language = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pass
    root = Tk()
    app = test(root)
    root.mainloop()
