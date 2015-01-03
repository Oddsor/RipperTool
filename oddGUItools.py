__author__ = 'Odd'

import tkinter as tk
from tkinter import filedialog

def fileselect(root, path, dir=True, func=None):
    '''
    :param root: The root frame in which to insert the file select
    :param path: The file or directory path in a stringvar
    :param dir: Opening a directory or just files? True for directory
    :param func: Not implemented yet
    :return: The file select frame
    '''
    #TODO: add functions? not sure what to do here
    file_frame = tk.Frame(root)
    entry = tk.Entry(file_frame, textvariable=path)

    def open_file():
        if dir:
            newpath = tk.filedialog.askdirectory(initialdir=path.get())
        else:
            newpath = tk.filedialog.askopenfilename(initialfile=path.get())

        if entry.get() != newpath and newpath != '':
            path.set(newpath)

    entry.config(width=30)
    entry.pack(side="left")

    button = tk.Button(file_frame, command=open_file)
    button.config(text="Select")

    button.pack(side="left")
    return file_frame


class Listbox(tk.Frame):
    def __init__(self, data, master=None, multiple=False, orderable=True):
        tk.Frame.__init__(self, master)
        self.config()
        self.pack()
        self.list = data
        boxframe = tk.Frame(self)
        scrollbar = tk.Scrollbar(boxframe, orient=tk.VERTICAL)
        self.lister = tk.Listbox(boxframe, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.lister.yview)
        #scrollbar.grid(row=0, column=1)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        for item in self.list:
            self.lister.insert(tk.END, item)
        if multiple:
            self.lister.config(selectmode=tk.EXTENDED)
        self.lister.pack(side=tk.LEFT)
        #lister.grid(row=0, column=0)
        #boxframe.pack(side=tk.LEFT)
        boxframe.grid(row=0, rowspan=2, column=0)

        if orderable:
            def move_up():
                if len(self.lister.curselection()) == 1 and self.lister.curselection()[0] > 0:
                    self.list.insert(self.lister.curselection()[0] - 1, self.list.pop(self.lister.curselection()[0]))
                    refresh_list(self.lister.curselection()[0] - 1)
            def move_down():
                if len(self.lister.curselection()) == 1 and self.lister.curselection()[0] < len(self.list) - 1:
                    self.list.insert(self.lister.curselection()[0] + 1, self.list.pop(self.lister.curselection()[0]))
                    refresh_list(self.lister.curselection()[0] + 1)

            def refresh_list(selected):
                self.lister.delete(0, tk.END)
                for item in self.list:
                    self.lister.insert(tk.END, item)
                self.lister.selection_set(selected)


            container = tk.Frame(self)
            up_button = tk.Button(container, command=move_up)
            up_button.config(text="↑")
            up_button.pack(side="top")
            down_button = tk.Button(container, command=move_down)
            down_button.config(text="↓")
            down_button.pack(side="bottom")
            #container.pack(side=tk.RIGHT)
            container.grid(row=1, column=1, sticky=tk.S)

    def get_items(self):
        return self.list

    def get_selected(self):
        return self.lister.curselection()