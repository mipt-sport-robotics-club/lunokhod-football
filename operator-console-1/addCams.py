import json
from tkinter import ttk
from re import match

import vlc
from tkinter import *
from tkinter import messagebox

videoPanels = []
buttons = []

camList = []

DOMAINEXPRESSION = "^([a-z0-9])(([a-z0-9-]{1,61})?[a-z0-9]{1})?(\.[a-z0-9](([a-z0-9-]{1,61})?[a-z0-9]{1})?)?(\.[a-zA-Z]{2,4})+$"
IPEXPRESSIOM = "[0-9]+(?:\.[0-9]+){3}(:[0-9]+)?"


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


class App(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.videoPanels = []
        self.buttons = []
        self.parent = parent
        self.adding = False
        self.parent.bind('<Escape>', self.showMap)
        self.parent.bind('<Button>', self.setCam)
        Button(text="Добавить камеру", command=self.addCam).grid(column=0, row=0)
        Label(text="Адрес камеры").grid(column=0, row=1)
        self.address = Entry(width=20)
        self.address.grid(column=1, row=1)
        self.initUI()

    def initUI(self):
        self.parent.title("Main")
        self.pitchImage = PhotoImage(file="pitch.png")
        self.footMap = Label(image=self.pitchImage)
        self.footMap.place(relx=0.5, anchor=N)
        self.camImage = PhotoImage(file="cctv-camera.png")
        try:
            with open('camsConfig.json', 'r+') as f:
                self.camList = json.load(f)
            i = 0
            for camera in self.camList:
                btn = Button(self.footMap, image=self.camImage)
                btn.place(x=camera['x'], y=camera['y'])
                self.buttons.append(btn)
                i += 1
        except Exception as e:
            print(e)
            self.camList = []
            pass

    def addCam(self):
        if not self.address.get() == "":
            self.adding = True
            pass
        else:
            messagebox.showerror("Ошибка", "Некорректный адрес сервера")

    def changeToCam(self, cam):
        global videoPanels, buttons
        self.footMap.place_forget()
        for i in range(len(videoPanels)):
            self.videoPanels[i].place_forget()
            self.buttons[i].place_forget()
        self.videoPanels[cam].place(relx=.5, rely=0.1, anchor='n')
        self.videoPanels[cam].pack_propagate(False)
        self.videoPanels[cam].grid_propagate(False)
        self.videoPanels[cam].configure(height=self.parent.winfo_height() / 1.5, width=self.parent.winfo_width() / 1.5)

    def setCam(self, event):
        position = "(x={}, y={})".format(event.x, event.y)
        print(event.type, "event", position)
        cam = {}
        if self.adding:
            self.adding = False
            cam['x'] = event.x
            cam['y'] = event.y
            cam['address'] = self.address.get()
            self.camList.append(cam)
            self.buttons.append(Button(self.footMap, image=self.camImage))
            i = 0
            for camera in self.camList:
                self.buttons[i].place_forget()
                self.buttons[i].place(x=camera['x'], y=camera['y'])
                i += 1
            with open('camsConfig.json', 'w+') as f:
                json.dump(self.camList, f)
            messagebox.showinfo("Информация", "Камера успешно добавлена")

    def showMap(self, event):
        i = 0
        # for camera in cams:
        #     self.buttons[i].place(x=camera['x'], y=camera['y'])
        #     self.videoPanels[i].place_forget()
        #     i += 1
        self.footMap.place(relx=0.5, anchor=N)


if __name__ == '__main__':
    root = Tk()
    root.geometry("1280x720")
    app = App(root)
    root.mainloop()
