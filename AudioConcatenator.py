import fnmatch
import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
from tkinter import filedialog


class App:
    def __init__(self, root):
        # setting title
        root.title("AudioConcatenator")
        # setting window size
        width = 400
        height = 300
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        # title
#        style = tk.Style()
#        style.configure("BW.TLabel", foreground="black", dimension=20, justify="center")
        self.title_style = ttk.Style()
        self.title_style.configure('my.TitleLabel', font=('Helvetica', 12), justify="center")
        self.title_label = ttk.Label(root, text="Audio Concatenator", style=self.title_style)
        #self.title_label["font"] = tkFont.Font(size=15)
        #self.title_label["justify"] = "center"
        self.title_label.place(x=10, y=10, width=385, height=30)

        # Select Folder section
        self.folder_path = ""
        self.folder_select_label = tk.Label(root)
        self.folder_select_label["font"] = tkFont.Font(size=10)
        self.folder_select_label["justify"] = "center"
        self.folder_select_label["text"] = "Folder Select"
        self.folder_select_label.place(x=10, y=60, width=81, height=25)

        self.folder_select_entry = ttk.Entry(root)
        self.folder_select_entry["text"] = ""
        self.folder_select_entry.place(x=100, y=60, width=206, height=25)

        self.select_folder_btn = ttk.Button(root, text="Select")
        self.select_folder_btn.place(x=310, y=60, width=70, height=25)
        self.select_folder_btn["command"] = self.select_folder_btn_command

        # Select title section
        self.new_title_label = tk.Label(root)
        self.new_title_label["justify"] = "center"
        self.new_title_label["text"] = "New Title"
        self.new_title_label.place(x=20, y=110, width=70, height=25)

        self.new_title_entry = ttk.Entry(root)
        self.new_title_entry["text"] = ""
        self.new_title_entry.place(x=100, y=110, width=205, height=25)

        # radio button section
        self.selected_extension = tk.StringVar(root, "mp3")
        extensions = ["mp3", "mp4", "mp3a"]

        self.group = tk.LabelFrame(root, text="Extension", padx=5, pady=5)
        self.group.place(x=10, y=150, width=120, height=100)

        for e in extensions:
            radio = tk.Radiobutton(self.group)
            radio["text"] = e
            radio["value"] = e
            radio["variable"] = self.selected_extension
            radio.pack()

        # Convert button
        self.convert_btn = ttk.Button(root, text="Convert")
        self.convert_btn.place(x=160, y=170, width=92, height=25)
        self.convert_btn["command"] = self.convert_btn_command
        self.convert_btn["state"] = "disabled"

    def select_folder_btn_command(self):
        self.folder_path = filedialog.askdirectory()
        self.folder_select_entry.insert(0, self.folder_path)
        print("folder_path={}".format(self.folder_path))
        self.new_title_entry.insert(0, os.path.split(self.folder_path)[-1])
        self.convert_btn["state"] = "normal"

    def convert_btn_command(self):
        print("convert_btn_command")
        self.out_file_title = self.new_title_entry.get()
        print("file_title={}".format(self.out_file_title))
        print("selected_extension={}".format(self.selected_extension.get()))
        convert(self.folder_path, self.out_file_title, self.selected_extension.get())


def convert(folder, out_file_title, extension):
    # Constants
    LIST_FILE = 'list.txt'

    if " " in folder or "'" in folder:
        new_folder = folder.replace(" ", "_").replace("'", "")
        os.rename(folder, new_folder)
        folder = new_folder
        out_file_title = out_file_title.replace(" ", "_").replace("'", "")

    with open(LIST_FILE, 'w') as fd:
        lines = []
        for f in sorted(fnmatch.filter(os.listdir(folder), "*." + extension)):
            if " " in f or "'" in f:
                file_path = os.path.join(folder, f.replace(" ", "_").replace("'", ""))
                os.rename(os.path.join(folder, f), file_path)
            else:
                file_path = os.path.join(folder, f)
            lines.append("file '" + file_path + "'\n")
        fd.writelines(lines)

    out_name = "{}.{}".format(out_file_title, extension)
    cmd = "ffmpeg -f concat -safe 0 -i list.txt -c copy {}".format(os.path.join(folder, out_name))
    os.system(cmd)
    os.unlink(LIST_FILE)


# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
