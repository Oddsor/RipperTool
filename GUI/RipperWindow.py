from OddTools.GUI import Listbox
import handbrake

__author__ = 'Odd'

import tkinter as tk
from MKVTag.GUI import search_interface


class RipperWindow(tk.Frame):
    def __init__(self, drive, data, master=None):
        tk.Frame.__init__(self, master)
        self.config()
        self.pack()
        print(data)
        items = list()
        for item in data:
            items.append(item['track_number'] + " (" + item['duration'] + ")")

        trackframe = tk.Frame(self)
        label = tk.Label(trackframe, text="Select tracks:")
        label.pack()
        lister = Listbox.Listbox(items, trackframe, True, orderable=False)
        lister.pack()

        audioframe = tk.Frame(self)
        audio_naming = tk.Frame(self)
        subtitle_naming = tk.Frame(self)
        subtitleframe = tk.Frame(self)
        label = tk.Label(audioframe, text="Select audio and order:")
        label.pack()
        audio_list = Listbox.Listbox(None, audioframe, True, height=5)
        audio_list.pack()
        self.audio_tuple = list()
        self.subtitle_tuple = list()

        def add_audio():
            self.add_textitems(audio_naming, self.audio_langtuple, audio_list.get_selected())

        audio_button = tk.Button(audioframe, text="Go",
                                 command=add_audio)
        audio_button.pack()
        audioframe.grid(row=0, column=1)

        label = tk.Label(subtitleframe, text="Select subtitles and order:")
        label.pack()
        subtitle_list = Listbox.Listbox(None, subtitleframe, True, height=5)
        subtitle_list.pack()

        def add_subs():
            self.add_textitems(subtitle_naming, self.subtitle_langtuple, subtitle_list.get_selected())

        subtitle_button = tk.Button(subtitleframe, text="Go",
                                    command=add_subs)
        subtitle_button.pack()
        subtitleframe.grid(row=1, column=1)

        def get_item():
            indexes = lister.get_selected()
            audio_data = list()
            for item in indexes:
                audio_data.append(data[item]['audio'])
            subtitle_data = list()
            for item in indexes:
                subtitle_data.append(data[item]['subtitles'])
            self.audio_langtuple = handbrake.consolidate_languages(audio_data)
            audio_langs = list()
            for item in self.audio_langtuple:
                if item[0] == 1:
                    audio_langs.append("A: " + item[1])
                else:
                    audio_langs.append("S: " + item[1])
            audio_list.add_data(audio_langs)
            self.subtitle_langtuple = handbrake.consolidate_languages(subtitle_data)
            subtitle_langs = list()
            for item in self.subtitle_langtuple:
                if item[0] == 1:
                    subtitle_langs.append("A: " + item[1])
                else:
                    subtitle_langs.append("S: " + item[1])
            subtitle_list.add_data(subtitle_langs)

        get_button = tk.Button(trackframe, text="Ok", command=get_item)
        get_button.pack()
        trackframe.grid(row=0, rowspan=2, column=0)
        audio_naming.grid(row=0, column=2)
        subtitle_naming.grid(row=1, column=2)
        titlestring = tk.StringVar()
        titlestring.set("No title")

        def search():
            search_result = search_interface.search_title(None, self, True)
            if search_result is not None:
                print(search_result)
                titlestring.set(search_result['item']['TITLE'])

        titleframe = tk.Frame(self)
        scraperbutton = tk.Button(titleframe, text="Find info", command=search)
        scraperbutton.pack(side=tk.TOP)
        titlelabel = tk.Label(titleframe, textvariable=titlestring)
        titlelabel.pack(side=tk.BOTTOM)
        titleframe.grid(row=2, column=0)
        seasonframe = tk.Frame(self)
        seasonlabel = tk.Label(seasonframe, text="Season:")
        seasonlabel.pack(side=tk.LEFT)
        seasonentry = tk.Entry(seasonframe, width=3)
        seasonentry.pack(side=tk.RIGHT)
        seasonframe.grid(row=2, column=1)
        episodeframe = tk.Frame(self)
        episodelabel = tk.Label(episodeframe, text="First ep:")
        episodelabel.pack(side=tk.LEFT)
        episodeentry = tk.Entry(episodeframe, width=3)
        episodeentry.pack(side=tk.RIGHT)
        episodeframe.grid(row=2, column=2)

        self.info = tk.Label(self, text="Infoline")
        self.info.grid(row=3, column=0, columnspan=2)
        launch = tk.Button(self, text="LAUNCH", command=self.start_rip)
        launch.grid(row=3, column=2)

    def add_textitems(self, frame, dataset, selected):
        print(dataset)
        for widget in frame.winfo_children():
                widget.destroy()
        for index in selected:
            text = tk.Text(frame)
            text.config(height=1, width=20)
            text.insert(tk.END, dataset[index][1])
            text.pack()

    def start_rip(self):
        self.info.config(text="Starting rip")
        #TODO complete run_encode()
        handbrake.run_encode()

if __name__ == '__main__':
    root = tk.Tk()
    app = RipperWindow("D:\\", handbrake.parse_handbrake(open("../handbrake_example3.txt").read()), master=root)
    app.mainloop()