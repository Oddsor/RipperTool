from OddTools import oddconfig

__author__ = 'Odd'

import tkinter as tk
import threading

import handbrake
from GUI import RipperWindow
from OddTools.GUI import fileselect
import subprocess


class MainWindow(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.config()
        self.pack()
        self.path = tk.StringVar(value="")
        in_path = fileselect.fileselect(self, self.path, True)
        in_path.pack()
        self.starter = tk.Button(self, text="Start rip",
                                 command=self.start_rip)
        self.starter.pack(side="bottom")

    def start_rip(self):
        self.starter.config(state=tk.DISABLED)
        st = ScanThread(self.path.get(), self.starter, self.master)
        st.start()


class ScanThread(threading.Thread):
    def __init__(self, path, button, master):
        threading.Thread.__init__(self)
        self.path = path
        self.button = button
        self.master = master

    def run(self):
        output = subprocess.getoutput('"C:\Program Files\Handbrake\HandBrakeCLI.exe" --input '
                                     + self.path + ' --title 0')
        #output = open("../handbrake_example.txt").read()
        data = handbrake.parse_handbrake(output)
        app = RipperWindow.RipperWindow(self.path, data, master=self.master)
        #app.mainloop()
        self.button.config(state=tk.NORMAL)


if __name__ == '__main__':
    root = tk.Tk()
    app = MainWindow(master=root)
    app.mainloop()