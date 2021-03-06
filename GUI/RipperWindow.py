import MKVTag
from OddTools.GUI import Listbox
import handbrake

__author__ = 'Odd'

import tkinter as tk
from MKVTag.GUI import search_interface
from OddTools.GUI import fileselect
import threading


class RipperWindow(tk.Frame):
    def __init__(self, drive, data, master=None):
        self.drive = drive
        self.data = data
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
        lister = self.tracklist = Listbox.Listbox(items, trackframe, True, orderable=False)
        lister.pack()

        audioframe = tk.Frame(self)
        audio_naming = tk.Frame(self)
        subtitle_naming = tk.Frame(self)
        subtitleframe = tk.Frame(self)
        label = tk.Label(audioframe, text="Select audio and order:")
        label.pack()
        audio_list = self.audio_list = Listbox.Listbox(None, audioframe, True, height=5)
        audio_list.pack()
        self.audio_tuple = list()
        self.subtitle_tuple = list()

        def add_audio():
            self.add_textitems(audio_naming, self.audio_langtuple, audio_list.get_selected())

        audio_button = tk.Button(audioframe, text="Go",
                                 command=add_audio)
        audio_button.pack()
        audioframe.grid(row=0, column=1)

        label = tk.Label(subtitleframe, text="Select subtitles and order:");                        label.pack()
        subtitle_list = self.subtitle_list = Listbox.Listbox(None, subtitleframe, True, height=5);  subtitle_list.pack()

        def add_subs():
            self.add_textitems(subtitle_naming, self.subtitle_langtuple, subtitle_list.get_selected())

        subtitle_button = tk.Button(subtitleframe, text="Go",
                                    command=add_subs);                                          subtitle_button.pack()
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
        titlestring = self.title_string = tk.StringVar()
        titlestring.set("No title")
        self.title_id = None
        self.scraper = None

        def search():
            search_result, self.scraper, result_id = search_interface.search_title(None, self, True, True)
            if search_result is not None:
                print(search_result)
                self.title_id = result_id
                if 'TITLE' in search_result['item']:
                    titlestring.set(search_result['item']['TITLE'])
                else:
                    titlestring.set(search_result['collection']['TITLE'])

        titleframe = tk.Frame(self);                                                titleframe.grid(row=2, column=0)
        scraperbutton = tk.Button(titleframe, text="Find info", command=search);    scraperbutton.pack(side=tk.TOP)
        titlelabel = tk.Label(titleframe, textvariable=titlestring);                titlelabel.pack(side=tk.BOTTOM)
        seasonframe = tk.Frame(self);                                               seasonframe.grid(row=2, column=1)
        seasonlabel = tk.Label(seasonframe, text="Season:");                        seasonlabel.pack(side=tk.LEFT)
        seasonentry = self.season_entry = tk.Entry(seasonframe, width=3);           seasonentry.pack(side=tk.RIGHT)
        episodeframe = tk.Frame(self);                                              episodeframe.grid(row=2, column=2)
        episodelabel = tk.Label(episodeframe, text="First ep:");                    episodelabel.pack(side=tk.LEFT)
        episodeentry = self.episode_entry = tk.Entry(episodeframe, width=3);        episodeentry.pack(side=tk.RIGHT)
        output_string = self.outputfolder = tk.StringVar()
        output_string.set("")
        output = fileselect.fileselect(self, output_string, dir=True);      output.grid(row=3, column=0, columnspan=3)
        self.info = tk.Label(self, text="Infoline");                    self.info.grid(row=4, column=0, columnspan=2)
        launch = tk.Button(self, text="LAUNCH", command=self.start_rip);            launch.grid(row=4, column=2)

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
        tracklist = list()
        for track in self.tracklist.get_selected():
            tracklist.append(self.tracklist.get_items()[track].split(" ")[0])
        audio_list = list()
        for audio in self.audio_list.get_selected():
            audio_list.append(audio + 1)

        subtitle_list = list()
        for subtitle in self.subtitle_list.get_selected():
            subtitle_list.append(subtitle + 1)
        lock = threading.Lock()
        finished_episodes = list()
        enc = EncodeThread(self.drive, tracklist, self.outputfolder.get(), self.title_string.get(),
            audio_list, subtitle_list, self.season_entry.get(),
            self.episode_entry.get(), self.data, lock, finished_episodes, self.title_id)
        enc.start()
        tag = TaggerThread(lock, finished_episodes, self.scraper, len(tracklist))
        tag.start()

import os
import time
from OddTools import filenames

class EncodeThread(threading.Thread):

    def __init__(self, drive, tracks, outputdir, title, audio, subtitles, season, episode_offset, drive_data, lock,
                 finished_episodes, title_id):
        threading.Thread.__init__(self)
        self.drive = drive
        self.tracks = tracks
        self.title = title
        self.outputdir = outputdir
        self.audio = audio
        self.subtitles = subtitles
        self.season = season if season is not None else "X"
        self.episode_offset = episode_offset if episode_offset is not None else "X"
        self.drive_data = drive_data
        self.lock = lock
        self.finished_episodes = finished_episodes
        self.title_id = title_id

    def run(self):
        for i in range(0, len(self.tracks)):
            real_sub = list()
            real_audio = list()
            for item in self.drive_data:
                if item['track_number'] == self.tracks[i]:
                    for aud in self.audio:
                        if aud < len(item['audio']):
                            real_audio.append(aud)
                    for sub in self.subtitles:
                        if sub < len(item['subtitles']):
                            real_sub.append(sub)
            handbrake.run_encode(self.drive, self.tracks[i], str(os.path.join(self.outputdir, '') + filenames.clean_filename(self.title) +
                                                        ("" if not str(self.season).isdigit() else " - S" + str(self.season).zfill(2)) +
                                                        ("" if not str(self.episode_offset).isdigit() else "E" + str(int(self.episode_offset) + i).zfill(2))
                                                        + ".mkv"), self.audio, self.subtitles)
            self.lock.acquire()
            self.finished_episodes.append((str(os.path.join(self.outputdir, '') + filenames.clean_filename(self.title) +
                        ("" if not str(self.season).isdigit() else " - S" + str(self.season).zfill(2)) +
                        ("" if not str(self.episode_offset).isdigit() else "E" + str(int(self.episode_offset) + i).zfill(2))
                        + ".mkv"), self.title_id, self.season,
                                          '' if not str(self.episode_offset).isdigit() else int(self.episode_offset) + i))
            self.lock.release()

from MKVTag import file_handler
from MKVTag import xml_maker


class TaggerThread(threading.Thread):
    def __init__(self, lock, finished_episodes, scraper, items):
        threading.Thread.__init__(self)
        self.lock = lock
        self.finished_episodes = finished_episodes
        self.scraper = scraper
        self.num_items = items

    def run(self):
        counter = 0
        while counter != self.num_items:
            item = None
            self.lock.acquire()
            if len(self.finished_episodes) > 0:
                item = self.finished_episodes.pop()
            self.lock.release()
            if item is not None:
                print(item)
                print(self.scraper)
                if str(item[1]).isdigit() and self.scraper is not None:
                    if str(item[2]).isdigit() and str(item[3]).isdigit():
                        data = self.scraper.get_info(item[1], item[2], item[3])
                    else:
                        data = self.scraper.get_info(item[1])
                    print(data)
                    file_handler.add_tags(item[0], xml_maker.get_xml(data))
                    file_handler.attach_files(data['attachments'], item[0])
                    if str(item[2]).isdigit() and str(item[3]).isdigit():
                        os.rename(item[0], os.path.splitext(item[0])[0] + " - " + data['item']['TITLE'] + ".mkv")
                    counter += 1
            time.sleep(10)

if __name__ == '__main__':
    root = tk.Tk()
    app = RipperWindow("D:\\", handbrake.parse_handbrake(open("../handbrake_example3.txt").read()), master=root)
    app.mainloop()