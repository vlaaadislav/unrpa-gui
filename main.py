#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import thread
from Tkinter import *
from tkMessageBox import askokcancel, showerror, showinfo
from tkFileDialog import askopenfilenames, askdirectory
from ttk import *
from unrpa import UnRPA


class Program:
    def __init__(self, window=Tk):
        self.parent = window()
        self.dirPath = StringVar()
        self.filePath = StringVar()
        self.progress = IntVar()

        self.windowConfig()
        self.createFileFrame()
        self.createDirFrame()
        self.createProcessFrame()
        self.createButtonsFrame()

    def windowConfig(self):
        h, w = 130, 300
        self.parent.title("Unrpa GUI")
        self.parent.config(height=h, width=w)
        self.parent.update()
        self.parent.bind("<Configure>", self.configEvent)

    def createFileFrame(self):
        h, w = self.parent.winfo_height()//3, self.parent.winfo_width()
        frame = LabelFrame(self.parent, text="Rpa File", height=h, width=w)
        button = Button(frame, text="Browse", command=self.getFilePath)
        entry = Entry(frame, textvariable=self.filePath)

        frame.pack(side=TOP, fill=X)
        button.pack(side=LEFT)
        entry.pack(side=RIGHT, expand=YES, fill=X)

    def createDirFrame(self):
        h, w = self.parent.winfo_height()//3, self.parent.winfo_width()
        frame = LabelFrame(self.parent, text="Directory to unpack", height=h, width=w)
        button = Button(frame, text="Browse", command=self.getDirPath)
        entry = Entry(frame, textvariable=self.dirPath)

        frame.pack(side=TOP, fill=X)
        button.pack(side=LEFT)
        entry.pack(side=RIGHT, expand=YES, fill=X)

    def createProcessFrame(self):
        self.parent.update()
        self.progressbar = Progressbar(orient=HORIZONTAL, mode='determinate', variable=self.progress)
        self.progressbar.pack(side=TOP, fill=X)

    def createButtonsFrame(self):
        frame = Frame(self.parent)
        sbutton = Button(frame, text="Start", command=self.startProcess, state=DISABLED)
        qbutton = Button(frame, text="Quit", command=self.parent.quit)

        frame.pack(side=BOTTOM, fill=X)
        sbutton.pack(side=LEFT)
        qbutton.pack(side=RIGHT)

        self.startButton = sbutton

    def configEvent(self, event):
        pass
        #print(self.parent.winfo_height(), self.parent.winfo_width())

    def getFilePath(self):
        types = [
            ("RenPy Archive", '*.rpa'),
            ('All Files', '*')
        ]
        files = askopenfilenames(filetypes=types, initialdir=self.filePath.get() or os.getcwd())
        self.filePath.set(';'.join(files))
        self.setStartState()

    def getDirPath(self):
        self.dirPath.set(askdirectory(initialdir=self.dirPath.get() or os.getcwd()))
        self.setStartState()

    def setStartState(self):
        if self.filePath.get() and self.dirPath.get():
            self.startButton.config(state=NORMAL)
        else:
            self.startButton.config(state=DISABLED)

    def startProcess(self):
        pass


class Calculations(Program):
    def __init__(self, window=Tk):
        Program.__init__(self, window)
        self.status = 'init'
        self.errors = []
        self.unarchiver = []

    def startProcess(self):
        dirPath = self.dirPath.get()
        files = self.filePath.get().split(';') if self.filePath.get() else []
        if dirPath and files:
            self.status = 'start'
            self.startButton.config(state=DISABLED)
            self.unarchiver.extend([UnRPA(filePath, path=dirPath, mkdir=True) for filePath in files])
            thread.start_new_thread(self.extract_files, (self.unarchiver, ))
            self.parent.after(500, self.checkUpack)
        else:
            showerror("Error", "You should specify file path and directory path")

    def checkUpack(self):
        if self.status == 'complete':
            if len(self.errors) == 0:
                showinfo('Complete', "Unpacking is finished")
            else:
                showerror('Error', 'error ocured!')
            self.startButton.config(state=NORMAL)
            self.progress.set(0)
        else:
            self.parent.after(500, self.checkUpack)

    def extract_files(self, unrpaList):
        indexList = [(unrpa, unrpa.get_index()) for unrpa in unrpaList]
        maximum = sum([len(index[1]) for index in indexList])
        self.progressbar.config(maximum=maximum)
        for unrpa, index in indexList:
            unrpa.make_directory_structure(unrpa.path)
            for (item, data) in index.iteritems():
                self.progress.set(self.progress.get() + 1)
                unrpa.make_directory_structure(os.path.join(unrpa.path, os.path.split(item)[0]))
                raw_file = unrpa.extract_file(item, data)
                with open(os.path.join(unrpa.path, item.encode('UTF-8')), "wb") as f:
                    f.write(raw_file)
        self.status = 'complete'


def selftest():
    #Program()
    Calculations()
    mainloop()

if __name__ == '__main__': selftest()
