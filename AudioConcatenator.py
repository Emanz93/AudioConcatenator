# general imports
import fnmatch
import os
import sys
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path

# Tkinter imports
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import tkinter.messagebox


# TODO: use pathlib library instead of os.path
# TODO: add (infinite) progress bar

def syscmd(cmd):
    """ Runs a command on the system, waits for the command to finish, and then
    returns the text output of the command. If the command produces no text
    output, the command's return code will be returned instead.
    Parameter:
        cmd: String. Command to be executed.
    Returns:
        return_code: int. Return value of the command.
        output: string. standard output.
    """
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    p.wait()
    output = p.stdout.read()
    return p.returncode, output.decode()


class AudioConcatenator:
    def __init__(self, r):
        # setting title
        self.root = r
        style = ttk.Style(root)
        root.tk.call('source', 'styles/azure.tcl')
        style.theme_use('azure')
        self.root.title("AudioConcatenator")
        # setting window size
        width = 400
        height = 260
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(alignstr)
        self.root.resizable(width=False, height=False)

        # set some variable:
        self.out_file_title = None
        self.ordered_files = None

        # title
        self.titlestyle = ttk.Style()
        self.titlestyle.configure("titlestyle.TLabel", font=('Helvetica', 12))
        self.title_label = ttk.Label(self.root, text="Audio Concatenator", style='titlestyle.TLabel', justify='center')
        self.title_label.place(x=125, y=10, width=150, height=30)

        # Select Folder section
        self.folder_path = ""
        self.folder_select_label = ttk.Label(self.root, text="Folder Select")
        self.folder_select_label.place(x=10, y=60, width=81, height=30)

        self.folder_select_entry = ttk.Entry(self.root, text="")
        self.folder_select_entry.place(x=100, y=60, width=206, height=30)

        self.select_folder_btn = ttk.Button(self.root, text="Select", command=self.select_folder_btn_command)
        self.select_folder_btn.place(x=310, y=60, width=70, height=30)

        # Select title section
        self.new_title_label = ttk.Label(self.root, text="New Title")
        self.new_title_label.place(x=20, y=110, width=70, height=30)

        self.new_title_entry = ttk.Entry(self.root, text="")
        self.new_title_entry.place(x=100, y=110, width=205, height=30)

        # select extension section
        self.selected_extension = tk.StringVar(self.root, "mp3")
        self.available_extensions = sorted(["mp3", "mp4", "mp3a", "m4a", "m4b"])

        self.extension_label = ttk.Label(self.root, text="Extension")
        self.extension_label.place(x=20, y=160, width=110, height=30)

        self.extension_menu = ttk.Combobox(self.root, textvariable=self.selected_extension,
                                           values=self.available_extensions)
        self.extension_menu.place(x=100, y=160, width=110, height=30)

        # Convert button
        self.convert_btn = ttk.Button(self.root, text="Convert", command=self.convert_btn_command, style='Accentbutton')
        self.convert_btn.place(x=270, y=160, width=92, height=30)
        self.root.bind('<Return>', lambda e: self.convert_btn_command())

        # Exit button
        self.convert_btn = ttk.Button(self.root, text="Exit", command=sys.exit)
        self.convert_btn.place(x=width / 2 - 92 / 2, y=210, width=92, height=30)

    def select_folder_btn_command(self):
        self.folder_path = filedialog.askdirectory()
        self.folder_select_entry.insert(0, self.folder_path)
        print("folder_path={}".format(self.folder_path))
        self.new_title_entry.insert(0, os.path.split(self.folder_path)[-1])
        self.convert_btn["state"] = "normal"

    def convert_btn_command(self):
        # if self.new_title_entry == '' or self.folder_select_entry == '':
        self.out_file_title = self.new_title_entry.get()
        self._create_top_level_selection_order()
        self.order_the_list()

    def _create_top_level_selection_order(self):
        self.top = tk.Toplevel(self.root)
        width = 600
        height = 600
        screenwidth = self.top.winfo_screenwidth()
        screenheight = self.top.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.top.geometry(alignstr)
        self.top.resizable(width=False, height=False)

        # Listbox
        self.listbox = tk.Listbox(self.top)
        self.listbox.place(x=10, y=10, width=470, height=580)
        self.vertical_bar = ttk.Scrollbar(self.listbox) # , command=self.listbox.yview)
        self.vertical_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.horizontal_bar = ttk.Scrollbar(self.listbox, orient='horizontal', command=self.listbox.xview)
        self.horizontal_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.listbox.configure(yscrollcommand=self.vertical_bar.set, xscrollcommand=self.horizontal_bar.set)

        self.up_button = ttk.Button(self.top, text="UP", command=self.move_callback_up)
        self.up_button.place(x=490, y=265, width=92, height=30)
        self.delete_button = ttk.Button(self.top, text="DELETE", command=self.delete_callback)
        self.delete_button.place(x=490, y=300, width=92, height=30)
        self.down_button = ttk.Button(self.top, text="DOWN", command=self.move_callback_down)
        self.down_button.place(x=490, y=335, width=92, height=30)
        self.continue_button = ttk.Button(self.top, text="Continue", command=self.continue_callback, style='Accentbutton')
        self.top.bind('<Return>', lambda e: self.continue_callback)
        self.continue_button.place(x=490, y=30, width=92, height=30)

        self.root.withdraw()

    def move_callback_up(self):
        self.move_callback_helper(UP)

    def move_callback_down(self):
        self.move_callback_helper(DOWN)

    def move_callback_helper(self, direction):
        from_index = int(self.listbox.curselection()[0])
        value = self.listbox.get(from_index)
        self.listbox.delete(from_index)
        if direction == UP:
            self.listbox.insert(from_index - 1, value)
        else:
            self.listbox.insert(from_index + 1, value)

    def delete_callback(self):
        self.listbox.delete(int(self.listbox.curselection()[0]))

    def order_the_list(self):
        in_list = sorted(fnmatch.filter(os.listdir(self.folder_path), "*." + self.selected_extension.get()))
        for i in range(len(in_list)):
            self.listbox.insert(i, in_list[i])

    def continue_callback(self):
        self.ordered_files = list(self.listbox.get(0, tk.END))
        convert(self.folder_path, self.ordered_files, self.new_title_entry.get(), self.selected_extension.get())


def _write_list_file(ordered_files, folder):
    """ Write the ordered list of files + remove whitespaces in list file.
    Parameters:
        ordered_files: List of Strings.
        folder: String: absolute path ot the folder.
    """
    with open(LIST_FILE, 'w') as fd:
        lines = []
        for f in ordered_files:
            file_path = os.path.join(folder, f)
            lines.append("file '" + file_path + "'\n")
        fd.writelines(lines)


def _remove_unsupported_characters(folder, ordered_files):
    """Remove the unwanted characters from the filenames of the files: whitespaces and single quote.

    Parameters:
        folder: Path.
        ordered_files: List of strings. Paths of the list of files
    Returns:
        ordered_files:
    """
    for i in range(len(ordered_files)):
        if "'" in ordered_files[i] or " " in ordered_files[i]:
            old_name = ordered_files[i]
            ordered_files[i] = ordered_files[i].replace(" ", "_").replace("'", "")
            os.rename(folder / old_name, folder / ordered_files[i])
    return ordered_files


def _pre_conversion(folder, ordered_files, extension):
    """Helper function. It removes all unsupported charachters and then, if necessary, it performs a pre-conversion
     of the audio files.
     Paramters:
        folder: String. Absolute path of the folder.
        ordered_files: List of strings. List of the filenames in the correct order.
        extension: String. Extension of the input files.
     """
    folder = Path(folder)
    ordered_files = _remove_unsupported_characters(folder, ordered_files)

    # convert the m4a to mp3
    if extension == 'm4a' or extension == "m4b":
        # covert each file in mp3, with the same name.
        for i in range(len(ordered_files)):
            f_in = folder / ordered_files[i]
            # f_in = ordered_files[i]
            f_out = folder / ordered_files[i].replace('.m4a', '.mp3').replace('.m4b', '.mp3')
            # f_out = ordered_files[i].replace('.m4a', '.mp3').replace('.m4b', '.mp3')
            cmd = 'ffmpeg.exe -i {} {}'.format(f_in, f_out)
            os.system(cmd)
            # syscmd does not work for some reason. THe reason seems to be if the ffmpeg command requires an input
            # from the standard input.
            # ret_code, output = syscmd(cmd)
            # if ret_code != 0:
            #    tkinter.messagebox.showerror("Error", output)
            os.unlink(f_in)
            ordered_files[i] = ordered_files[i].replace('.m4a', '.mp3').replace('.m4b', '.mp3')

        # os.chdir(dot)
        # os.unlink(folder / "ffmpeg.exe")
        extension = 'mp3'
    return ordered_files, extension


def convert(folder, ordered_files, out_file_title, extension):
    # TODO: avoid renaming the files.

    # Remove the whitespaces from the folder name and rename it
    new_folder = folder.replace(" ", "_").replace("'", "")
    os.rename(folder, new_folder)

    # perform a pre-conversion
    ordered_files, extension = _pre_conversion(new_folder, ordered_files, extension)

    # write the ordered list of files + remove whitespaces in list file.
    _write_list_file(ordered_files, new_folder)

    default_out_name = "output_file.{}".format(extension)
    cmd = "ffmpeg -y -f concat -safe 0 -i {} -c copy {}".format(LIST_FILE, os.path.join(new_folder, default_out_name))
    # TODO: find a way to use syscmd instead of os.system that is deprecated.
    # the problem is that syscmd does not show the terminal, while in some cases ffmpeg does require
    # interaction with it. -> -y to overwrite
    # syscmd(cmd)
    os.system(cmd)
    os.unlink(LIST_FILE)

    # rename the output file
    os.rename(os.path.join(new_folder, default_out_name),
              "{}.{}".format(os.path.join(new_folder, out_file_title), extension))
    # out_file_title = out_file_title.replace(" ", "_").replace("'", "")

    # Rename the folder with the original name
    os.rename(new_folder, folder)

    tkinter.messagebox.showinfo(title="Finish", message="Process is completed.")
    exit(0)


# Constants
LIST_FILE = 'list.txt'
UP = "UP"
DOWN = "DOWN"

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = AudioConcatenator(root)
    root.mainloop()
