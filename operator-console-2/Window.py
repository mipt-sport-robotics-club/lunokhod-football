from tkinter import *


class Window:

    def __init__(self, title, width, height, topLevel=0):
        if topLevel:
            self.window = Toplevel()
        else:
            self.window = Tk()
        self.window.title(title)
        # self.window.geometry(str(width) + "x" + str(height))
        self.window.geometry("{}x{}".format(width, height))
        self.frameArray = []




    def setBinds(self, keyRelease, keyPress):
        self.gui.bind('<KeyRelease>', keyRelease)
        self.gui.bind('<KeyPress>', keyPress)
    def getRoot(self):
        return self.window

    # #
    # ███████╗██████╗░░█████╗░███╗░░░███╗███████╗
    # ██╔════╝██╔══██╗██╔══██╗████╗░████║██╔════╝
    # █████╗░░██████╔╝███████║██╔████╔██║█████╗░░
    # ██╔══╝░░██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝░░
    # ██║░░░░░██║░░██║██║░░██║██║░╚═╝░██║███████╗
    # ╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚═╝╚══════╝
    # #

    def createFrame(self, row, column, width, height, rwidth=1, bg='#fff'):
        frame = Frame(self.window, bg=bg, width=width, height=height)
        self.frameArray.append(frame)
        frameIndex = self.frameArray.index(frame)
        # self.frameArray[frameIndex].grid(row=row, column=column)
        if rwidth > 0:
            self.frameArray[frameIndex].place(x=row, y=column, relwidth=rwidth)
        else:
            self.frameArray[frameIndex].place(x=row, y=column)
        return frameIndex

    def getFrame(self, frameNum):
        return self.frameArray[frameNum]

    # #
    # ██████╗░██╗░░░██╗████████╗████████╗░█████╗░███╗░░██╗
    # ██╔══██╗██║░░░██║╚══██╔══╝╚══██╔══╝██╔══██╗████╗░██║
    # ██████╦╝██║░░░██║░░░██║░░░░░░██║░░░██║░░██║██╔██╗██║
    # ██╔══██╗██║░░░██║░░░██║░░░░░░██║░░░██║░░██║██║╚████║
    # ██████╦╝╚██████╔╝░░░██║░░░░░░██║░░░╚█████╔╝██║░╚███║
    # ╚═════╝░░╚═════╝░░░░╚═╝░░░░░░╚═╝░░░░╚════╝░╚═╝░░╚══╝
    # #

    def createButton(self, frameNum, command, text=None, image=None, background="#555", foreground="#ccc", padx="20", pady="8",
                     font="16"):
        if image is None:
            return Button(self.frameArray[frameNum], text=text, command=command)
        else:
            return Button(self.frameArray[frameNum], image=image, command=command)

    def placeButton(self, button, method, x, y, anchor=CENTER):
        if method == 0:
            button.grid(row=x, column=y)
        elif method == 1:
            button.place(x=x, y=y)
        elif method == 2:
            button.place(relx=x, rely=y, anchor=anchor)

    # #
    # ██╗░░░░░░█████╗░██████╗░███████╗██╗░░░░░
    # ██║░░░░░██╔══██╗██╔══██╗██╔════╝██║░░░░░
    # ██║░░░░░███████║██████╦╝█████╗░░██║░░░░░
    # ██║░░░░░██╔══██║██╔══██╗██╔══╝░░██║░░░░░
    # ███████╗██║░░██║██████╦╝███████╗███████╗
    # ╚══════╝╚═╝░░╚═╝╚═════╝░╚══════╝╚══════╝
    # #

    def createLabel(self, frameNum, text=None, image=None, background="#fff", foreground="#fff", padx="20", pady="8",
                    font="16", ):
        if image is None:
            return Label(self.frameArray[frameNum], text=text, fg=foreground, bg=background, font=font)
        else:
            return Label(image=image)

    def placeLabel(self, label, method, x, y):
        if method == 0:
            label.grid(row=x, column=y)
        elif method == 1:
            label.place(x=x, y=y)

    # #
    # ░█████╗░░█████╗░███╗░░██╗██╗░░░██╗░█████╗░░██████╗
    # ██╔══██╗██╔══██╗████╗░██║██║░░░██║██╔══██╗██╔════╝
    # ██║░░╚═╝███████║██╔██╗██║╚██╗░██╔╝███████║╚█████╗░
    # ██║░░██╗██╔══██║██║╚████║░╚████╔╝░██╔══██║░╚═══██╗
    # ╚█████╔╝██║░░██║██║░╚███║░░╚██╔╝░░██║░░██║██████╔╝
    # ░╚════╝░╚═╝░░╚═╝╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░╚═╝╚═════╝░
    # #

    def createCanvas(self, frameNum):
        canvas = Canvas(self.frameArray[frameNum])
        return canvas

    def placeCanvas(self, canvas, method, x, y, anchor=CENTER):
        if method == 0:
            canvas.grid(row=x, column=y)
        elif method == 1:
            canvas.place(x=x, y=y)
        elif method == 2:
            canvas.place(relx=x, rely=y, anchor=anchor)

    # #
    # ███╗░░░███╗███████╗███╗░░██╗██╗░░░██╗
    # ████╗░████║██╔════╝████╗░██║██║░░░██║
    # ██╔████╔██║█████╗░░██╔██╗██║██║░░░██║
    # ██║╚██╔╝██║██╔══╝░░██║╚████║██║░░░██║
    # ██║░╚═╝░██║███████╗██║░╚███║╚██████╔╝
    # ╚═╝░░░░░╚═╝╚══════╝╚═╝░░╚══╝░╚═════╝░
    # #

    def createMenu(self):
        return Menu(self.window)

    def addCommand(self, menu, text, command):
        menu.add_command(label=text, command=command)

    def configRoot(self, menu):
        self.window.config(menu=menu)

    def loop(self):
        self.window.mainloop()
