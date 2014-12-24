__author__ = 'Odd'

import tkinter as tk
import subprocess
import oddGUItools
import oddconfig
import threading
import re

class MainWindow(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.config()
        self.pack()
        self.path = tk.StringVar(value="" if oddconfig.get_setting('drive') is None
            else oddconfig.get_setting('drive'))
        in_path = oddGUItools.create_fileselect(self, self.path, True)
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


class RipperWindow(tk.Frame):
    def __init__(self, drive, data, master=None):
        tk.Frame.__init__(self, master)
        self.config()
        self.pack()
        lister = tk.Listbox(self)
        for item in data:
            lister.insert(tk.END, item['track_number'] + " (" + item['duration'] + ")")
        lister.pack()


class ScanThread(threading.Thread):
    def __init__(self, path, button):
        threading.Thread.__init__(self)
        self.path = path
        self.button = button

    def run(self):
        output = subprocess.getoutput('"C:\Program Files\Handbrake\HandBrakeCLI.exe" --input '
                                      + self.path + ' --title 0')
        print(output)
        data = parse_handbrake(output)
        root = tk.Tk()
        app = RipperWindow(self.path, data, master=root)
        app.mainloop()
        self.button.config(state=tk.NORMAL)


def parse_handbrake(output):
    tracks = list()
    output_split = output.splitlines()
    line = None if not output_split else output_split.pop(0)
    while line is not None:
        if line.startswith('+ title'):
            track_info = dict()
            track_info['track_number'] = re.search("[0-9]{1,3}", line).group(0)
            line = None if not output_split else output_split.pop(0)
            while line is not None and not line.startswith("+ title"):
                if "+ duration" in line:
                    track_info['duration'] = \
                        re.search("[0-9]{1,2}:[0-9]{2}:[0-9]{2}", line).group(0)
                    line = None if not output_split else output_split.pop(0)
                elif "audio tracks" in line:
                    audio = list()
                    line = None if not output_split else output_split.pop(0)
                    while line is not None and re.search("\+ \d{1,2}", line) is not None:
                        audio.append(re.search("(?<=\d\,\s)\w+", line).group(0))
                        line = None if not output_split else output_split.pop(0)
                    track_info["audio"] = audio
                elif "subtitle tracks" in line:
                    subtitles = list()
                    line = None if not output_split else output_split.pop(0)
                    while line is not None and re.search("\+ \d{1,2}", line) is not None:
                        subtitles.append(re.search("(?<=\d\,\s)\w+", line).group(0))
                        line = None if not output_split else output_split.pop(0)
                    track_info["subtitles"] = subtitles
                else:
                    line = None if not output_split else output_split.pop(0)

            tracks.append(track_info)
        else:
            line = None if not output_split else output_split.pop(0)
    return tracks

if __name__ == '__main__':
    root = tk.Tk()
    app = MainWindow(master=root)
    app.mainloop()