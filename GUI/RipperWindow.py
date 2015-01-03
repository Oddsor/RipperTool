import handbrake

__author__ = 'Odd'

import tkinter as tk
import oddGUItools

class RipperWindow(tk.Frame):
    def __init__(self, drive, data, master=None):
        tk.Frame.__init__(self, master)
        self.config()
        self.pack()
        items = list()
        for item in data:
            items.append(item['track_number'] + " (" + item['duration'] + ")")
        lister = oddGUItools.Listbox(items, self, True)
        lister.pack()
        def get_item():
            print(lister.get_items())
            print(lister.get_selected())
        get_button = tk.Button(self, command=get_item)
        get_button.pack()

if __name__ == '__main__':
    root = tk.Tk()
    app = RipperWindow("D:\\", handbrake.parse_handbrake(open("../handbrake_example.txt").read()), master=root)
    app.mainloop()