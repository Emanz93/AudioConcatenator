import fnmatch
import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import tkinter.messagebox

# TODO: add exit button
# TODO: add support to m4b -> m4a
# TODO: do not rename the files. At least the input folder name and the output filename

class App:
    def __init__(self, root):
        # setting title
        self.root = root
        self.root.title("AudioConcatenator")
        # setting window size
        width = 400
        height = 300
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(alignstr)
        self.root.resizable(width=False, height=False)

        # title
        self.titlestyle = ttk.Style()
        self.titlestyle.configure("titlestyle.TLabel", font=('Helvetica', 12))
        self.title_label = ttk.Label(self.root, text="Audio Concatenator", style='titlestyle.TLabel', justify='center')
        self.title_label.place(x=125, y=10, width=150, height=30)

        # Select Folder section
        self.folder_path = ""
        self.folder_select_label = ttk.Label(self.root, text="Folder Select")
        self.folder_select_label.place(x=10, y=60, width=81, height=25)

        self.folder_select_entry = ttk.Entry(self.root, text="")
        self.folder_select_entry.place(x=100, y=60, width=206, height=25)

        self.select_folder_btn = ttk.Button(self.root, text="Select")
        self.select_folder_btn.place(x=310, y=60, width=70, height=25)
        self.select_folder_btn["command"] = self.select_folder_btn_command

        # Select title section
        self.new_title_label = ttk.Label(self.root, text="New Title")
        self.new_title_label.place(x=20, y=110, width=70, height=25)

        self.new_title_entry = ttk.Entry(self.root, text="")
        self.new_title_entry.place(x=100, y=110, width=205, height=25)
        
        # TODO: remove radio button in favour of dropdown menu
        self.selected_extension = tk.StringVar(self.root, "mp3")
        self.available_extensions = sorted(["mp3", "mp4", "mp3a", "m4a", "m4b"])

        self.extension_label = ttk.Label(self.root, text="Extension")
        self.extension_label.place(x=20, y=160, width=110, height=25)

        self.extension_menu = ttk.Combobox(self.root, textvariable=self.selected_extension, values=self.available_extensions)
        self.extension_menu.place(x=100, y=160, width=110, height=25)

        # Convert button
        self.convert_btn = ttk.Button(self.root, text="Convert", command=self.convert_btn_command)
        self.convert_btn.place(x=270, y=160, width=92, height=25)

    def select_folder_btn_command(self):
        self.folder_path = filedialog.askdirectory()
        self.folder_select_entry.insert(0, self.folder_path)
        print("folder_path={}".format(self.folder_path))
        self.new_title_entry.insert(0, os.path.split(self.folder_path)[-1])
        self.convert_btn["state"] = "normal"

    def convert_btn_command(self):
        print(self.selected_extension.get())
        #self.out_file_title = self.new_title_entry.get()
        #self._create_top_level_selection_order()
        #self.order_the_list()

    def _create_top_level_selection_order(self):
        self.top = tk.Toplevel(self.root)
        width = 500
        height = 600
        screenwidth = self.top.winfo_screenwidth()
        screenheight = self.top.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.top.geometry(alignstr)
        self.top.resizable(width=False, height=False)

        # Listbox
        self.listbox = tk.Listbox(self.top)
        self.listbox.place(x=10, y=10, width=400, height=580)
        self.vertical_bar = ttk.Scrollbar(self.listbox, command=self.listbox.yview)
        self.vertical_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.horizontal_bar = ttk.Scrollbar(self.listbox, orient='horizontal', command=self.listbox.xview)
        self.horizontal_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.up_button = ttk.Button(self.top, text="UP", command=self.move_callback_up)
        self.up_button.place(x=420, y=265, width=70, height=25)
        self.down_button = ttk.Button(self.top, text="DOWN", command=self.move_callback_down)
        self.down_button.place(x=420, y=335, width=70, height=25)
        self.continue_button = ttk.Button(self.top, text="Continue", command=self.continue_callback)
        self.continue_button.place(x=420, y=30, width=70, height=25)

        self.root.withdraw()

    def move_callback_up(self):
        self.move_callback_helper(UP)

    def move_callback_down(self):
        self.move_callback_helper(DOWN)

    def move_callback_helper(self, type):
        from_index = int(self.listbox.curselection()[0])
        value = self.listbox.get(from_index)
        self.listbox.delete(from_index)
        if type == UP:
            self.listbox.insert(from_index - 1, value)
        else:
            self.listbox.insert(from_index + 1, value)

    def order_the_list(self):
        l = sorted(fnmatch.filter(os.listdir(self.folder_path), "*." + self.selected_extension.get()))
        for i in range(len(l)):
            self.listbox.insert(i, l[i])

    def continue_callback(self):
        self.ordered_files = self.listbox.get(0, tk.END)
        convert(self.folder_path, self.ordered_files, self.new_title_entry.get(), self.selected_extension.get())


def convert(folder, ordered_files, out_file_title, extension):
    # Remove the whitespaces from the folder name
    if " " in folder or "'" in folder:
        new_folder = folder.replace(" ", "_").replace("'", "")
        os.rename(folder, new_folder)
        folder = new_folder
        out_file_title = out_file_title.replace(" ", "_").replace("'", "")

    # write the ordered list of files + remove whitespaces in list file.
    with open(LIST_FILE, 'w') as fd:
        lines = []
        for f in ordered_files:
            if " " in f or "'" in f:
                file_path = os.path.join(folder, f.replace(" ", "_").replace("'", ""))
                os.rename(os.path.join(folder, f), file_path)
            else:
                file_path = os.path.join(folder, f)
            lines.append("file '" + file_path + "'\n")
        fd.writelines(lines)

    out_name = "{}.{}".format(out_file_title, extension)
    cmd = "ffmpeg -f concat -safe 0 -i {} -c copy {}".format(LIST_FILE, os.path.join(folder, out_name))
    os.system(cmd)
    os.unlink(LIST_FILE)
    tkinter.messagebox.showinfo(title="Finish", message="Process is completed.")
    exit(0)


# Constants
LIST_FILE = 'list.txt'
UP = "UP"
DOWN = "DOWN"

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
