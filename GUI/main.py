__author__ = 'Odd'

import tkinter as tk
import oddGUItools
import oddconfig
import threading
import handbrake
import subprocess
from GUI import RipperWindow


class MainWindow(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.config()
        self.pack()
        self.path = tk.StringVar(value="" if oddconfig.get_setting('drive') is None
            else oddconfig.get_setting('drive'))
        in_path = oddGUItools.fileselect(self, self.path, True)
        in_path.pack()
        variable = tk.StringVar(self)
        variable.set("Film")
        type = tk.OptionMenu(self, variable, "Anime", "Film", "Tv show")
        type.pack(side="right")
        self.starter = tk.Button(self, text="Start rip",
                            command=self.start_rip)
        self.starter.pack(side="bottom")

    def start_rip(self):
        self.starter.config(state=tk.DISABLED)
        st = ScanThread(self.path.get(), self.starter)
        st.start()


class ScanThread(threading.Thread):
    def __init__(self, path, button):
        threading.Thread.__init__(self)
        self.path = path
        self.button = button

    def run(self):
        #output = subprocess.getoutput('"C:\Program Files\Handbrake\HandBrakeCLI.exe" --input '
        #                              + self.path + ' --title 0')
        output = open("../handbrake_example.txt").read()
        data = handbrake.parse_handbrake(output)
        print(data)
        root = tk.Tk()
        app = RipperWindow.RipperWindow(self.path, data, master=root)
        app.mainloop()
        self.button.config(state=tk.NORMAL)

if __name__ == '__main__':
    root = tk.Tk()
    app = MainWindow(master=root)
    app.mainloop()