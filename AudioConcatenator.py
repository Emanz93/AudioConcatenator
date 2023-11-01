# general imports
import shutil
import os
import sys
from subprocess import Popen, PIPE, STDOUT
import threading

# Tkinter imports
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from tkinter import font

# TODO: add icon
# TODO: add infinite progressbar
# TODO: popup for some reason does not get highlighted and stays behind the other screens
# TODO: use logger instead of the print
# TODO: add a final message in the terminal of completion

# Constants
LIST_FILE = 'list.txt'
TEMP = "D:\\temp"
UP = "UP"
DOWN = "DOWN"


""" Stript that concatenates and/or convert the audio(s) in mp3 format. """

# TODO: add (infinite) progress bar

class AudioConcatenator:
    def __init__(self, r):
        """ Constructor of the graphical user interface. """
        # setting title
        self.root = r

        self.width = 600
        self.height = 260
        self._set_screen_settings("Audio Concatenator", width=self.width, height=self.height)      
        
        # setting window size
        self._set_azure_style()

        # set some variable:
        self.out_file_title = None # Filename of the final output file
        self.input_path = None  # Contains the list of files to be concatenated

        # set the GUI
        self._create_main_frame()

    def _set_screen_settings(self, title, width=500, height=500):
        """ Set the screen settings and the wingow placement. """
        # set the title
        self.root.title(title)

        # set the icon
        #self.icon_path = 'path'
        #if not os.path.isfile(self.icon_path):
        #    # if not locally called, use the absolute path
        #    self.icon_path = os.path.join(os.path.dirname(sys.argv[0]), self.icon_path)
        #self.root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=self.icon_path))

        # setting window size
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(alignstr)
        self.root.resizable(width=False, height=False)

    def _set_azure_style(self):
        """ Set the Azure style. """
        style = ttk.Style(self.root)
        style_path = 'styles/azure.tcl'
        if not os.path.isfile(style_path):
            # if not locally called, use the absolute path
            style_path = os.path.join(os.path.dirname(sys.argv[0]), style_path)
        self.root.tk.call('source', style_path)
        style.theme_use('azure')

    def _create_main_frame(self):
        # Title section
        highlightFont = font.Font(family='Helvetica', name='appHighlightFont', size=12, weight='bold')
        self.title_label = ttk.Label(self.root, text="Audio Concatenator", font=highlightFont)
        self.title_label.place(x=220, y=10, width=200, height=30)

        # Select Files section
        self.files_select_label = ttk.Label(self.root, text="Select Audio Files")
        self.files_select_label.place(x=10, y=60, width=100, height=30)

        self.files_select_entry = ttk.Entry(self.root, text="")
        self.files_select_entry.place(x=120, y=60, width=390, height=30)

        self.select_files_btn = ttk.Button(self.root, text="Select", command=self.select_files_btn_command)
        self.select_files_btn.place(x=520, y=60, width=70, height=30)

        # Select title section
        self.new_title_label = ttk.Label(self.root, text="New Title")
        self.new_title_label.place(x=10, y=110, width=100, height=30)

        self.new_title_entry = ttk.Entry(self.root, text="")
        self.new_title_entry.place(x=120, y=110, width=390, height=30)

        # select extension section
        self.selected_extension = tk.StringVar(self.root, "mp3")
        self.available_extensions = sorted(["mp3", "mp4", "mp3a", "m4a", "m4b"])

        self.extension_label = ttk.Label(self.root, text="Extension")
        self.extension_label.place(x=80, y=160, width=110, height=30)

        self.extension_menu = ttk.Combobox(self.root, textvariable=self.selected_extension, values=self.available_extensions)
        self.extension_menu.place(x=160, y=160, width=110, height=30)

        # Convert button
        self.convert_btn = ttk.Button(self.root, text="Convert", command=self.convert_btn_command, style='Accentbutton')
        self.convert_btn.place(x=330, y=160, width=92, height=30)
        self.root.bind('<Return>', lambda e: self.convert_btn_command())

        # Exit button
        self.convert_btn = ttk.Button(self.root, text="Exit", command=sys.exit)
        self.convert_btn.place(x=self.width / 2 - 92 / 2, y=210, width=92, height=30)

    def select_files_btn_command(self):
        """ Callback of the button to select the files. """
        # initialdir = "/",
        self.input_path = sorted(list(filedialog.askopenfilenames(title = "Select file(s)")))
        self.files_select_entry.insert(0, str(self.input_path)) # populate the entry of the input files section.
        self.new_title_entry.insert(0, os.path.split(self.input_path[0])[-1]) # try to autocomplete the entry containing the title of the output file.
        self.convert_btn["state"] = "normal" # re-enable the button to perform the conversion.

    def convert_btn_command(self):
        """ Callback of the button to perform the conversion. 
            If it is a single file to be converted, then it goes directly to the conversion function.
            Otherwise, it will open the top_level window to select the concatenation order.
        """
        if self.new_title_entry.get() == '':
            messagebox.showerror(title="Input needed", message="Please enter the title.")
        elif self.files_select_entry.get() == '':
            messagebox.showerror(title="Input needed", message="Please select the input files.")
        else:
            # only one file:
            if len(self.input_path) == 0:
                convert(self.input_path, self.new_title_entry.get(), self.selected_extension.get())
            else:
                self.out_file_title = self.new_title_entry.get()
            self._create_top_level_selection_order()

    def _create_top_level_selection_order(self):
        """ Create the top_level windows. It allows to chose the order of the files to be concatenated. """
        self.top = tk.Toplevel(self.root)
        self.top_lvl_width = 600
        self.top_lvl_height = 600
        screenwidth = self.top.winfo_screenwidth()
        screenheight = self.top.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (self.top_lvl_width, self.top_lvl_height, (screenwidth - self.top_lvl_width) / 2, (screenheight - self.top_lvl_height) / 2)
        self.top.geometry(alignstr)
        self.top.resizable(width=False, height=False)

        # Listbox
        self.listbox = tk.Listbox(self.top)
        self.listbox.place(x=10, y=10, width=470, height=580)
        self.vertical_bar = ttk.Scrollbar(self.listbox)  # , command=self.listbox.yview)
        self.vertical_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.horizontal_bar = ttk.Scrollbar(self.listbox, orient='horizontal', command=self.listbox.xview)
        self.horizontal_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.listbox.configure(yscrollcommand=self.vertical_bar.set, xscrollcommand=self.horizontal_bar.set)

        # populate the listbox
        self.base_path = os.path.split(self.input_path[0])[0]
        for i in range(len(self.input_path)):
            self.listbox.insert(i, os.path.split(self.input_path[i])[1])

        # create the buttons
        self.up_button = ttk.Button(self.top, text="UP", command=self.move_callback_up)
        self.up_button.place(x=490, y=265, width=92, height=30)
        self.delete_button = ttk.Button(self.top, text="DELETE", command=self.delete_callback)
        self.delete_button.place(x=490, y=300, width=92, height=30)
        self.down_button = ttk.Button(self.top, text="DOWN", command=self.move_callback_down)
        self.down_button.place(x=490, y=335, width=92, height=30)
        self.continue_button = ttk.Button(self.top, text="Continue", command=self.continue_callback,
                                          style='Accentbutton')

        # keyboard bindings
        self.top.bind('<Return>', lambda e: self.continue_callback)
        #self.top.bind('<Key-w>', lambda e: self.move_callback_up)
        #self.top.bind('<Key-S>', lambda e: self.move_callback_down)
        self.continue_button.place(x=490, y=30, width=92, height=30)

        # withdraw the main window 
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
            self.listbox.select_set(from_index - 1)
        else:
            self.listbox.insert(from_index + 1, value)
            self.listbox.select_set(from_index + 1)

    def delete_callback(self):
        self.listbox.delete(int(self.listbox.curselection()[0]))

    '''def create_progressbar(self):
        self.progr_bar_frame = ttk.Frame()
        self.progr_bar_frame.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
        pb_hD = ttk.Progressbar(self.progr_bar_frame, orient='horizontal', mode='indeterminate')
        pb_hD.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
        pb_hD.start(50)'''

    def continue_callback(self):
        # update the list of files with the personalized order order.
        self.input_path = list(self.listbox.get(0, tk.END))
        for i in range(len(self.input_path)):
            self.input_path[i] = os.path.join(self.base_path, self.input_path[i])

        #t1=threading.Thread(target=convert, args=(self.input_path, self.new_title_entry.get(), self.selected_extension.get(),))
        #t1.start()
        #self.create_progressbar()  # This will block while the mainloop runs
        #t1.join()
        convert(self.input_path, self.new_title_entry.get(), self.selected_extension.get())


def convert(files_list, out_title, target_extension):
    """ Function that performs the actual conversion. As ffmpeg has some limitation, the following assumptions are taken:
        1. the actual conversion will be performed under C:/temp folder. If not present, it will be created and then deleted.
        2. 
        Parameters:
            files_list: List. Paths of the files to be converted.
            out_title: String. Output file filename. The new file will be written in the same folder as the input files.
            target_extension. String. Output file extension.
    """
    # if it does not exist, create the temp folder
    temp_exists = True # true if there was already a folder called temp.
    if not os.path.isdir(TEMP):
        os.mkdir(TEMP)
        temp_exists = False
        print("created temp folder")

    # copy each of the input file(s) in the temp folder
    # remove the unsupported characters from the filenames of the files: whitespaces and single quote.
    print("creating the temp files and renaming them")
    files_list_temp = []
    for i in range(len(files_list)):
        filename = os.path.split(files_list[i])[1]
        new_filename = filename.replace(" ", "_").replace("'", "")
        shutil.copy(files_list[i], os.path.join(TEMP, new_filename))
        files_list_temp.append(os.path.join(TEMP, new_filename))

    # perform a pre-conversion M4A or M4B to MP3
    print("preconversion")
    files_list_temp = _pre_conversion(files_list_temp)

    # distinguish between single file case and list of files.
    if len(files_list) == 1:
        # convert single file.
        default_out_name = files_list[0]
    else:
        # write the ordered list of files + remove whitespaces in list file.
        list_file_path = _write_list_file(files_list_temp, TEMP)
        print("file list written")

        # perform the conversion by list. The output file will be written in the temp folder.
        print("starting conversion")
        default_out_name = os.path.join(TEMP, "output_file.mp3")
        cmd = "ffmpeg -y -f concat -safe 0 -i {} -c copy {}".format(list_file_path, default_out_name)
        os.system(cmd)
        print("conversion completed")
        # TODO: find a way to use syscmd instead of os.system that is deprecated.
        # the problem is that syscmd does not show the terminal, while in some cases ffmpeg does require
        # interaction with it. -> -y to overwrite
        # syscmd(cmd)

        # delete the list file
        os.unlink(list_file_path)

    # rename (and move) the output file
    original_dir = os.path.split(files_list[0])[0]
    print("moving the output file to the original directory: {}".format(original_dir))
    if not out_title.endswith(".mp3"):
        out_title = "{}.mp3".format(out_title)
    final_file_location = os.path.join(original_dir, out_title)
    shutil.copy(default_out_name, final_file_location)
    print("Final file: {}".format(final_file_location))

    # remove the content of the temp folder:
    for f in files_list_temp:
        os.unlink(f)
    
    # delete the default out filename
    os.unlink(default_out_name)
    
    print("removed temporary files")

    # remove the folder
    if os.path.isdir(TEMP) and not temp_exists:
        os.unlink(TEMP)
        temp_exists = True
        print("deleted temp folder")

    #self.progr_bar_frame.destroy()
    messagebox.showinfo(title="Finish", message="Process is completed.")
    exit(0)


def _write_list_file(ordered_files, folder):
    """ Write the ordered list of files and remove whitespaces in list file.
        Parameters:
            ordered_files: List of Strings.
            folder: String. Path where the list file should be written.
        Return:
            target_file_path: String. Path where the list file is written.
    """
    target_file_path = os.path.join(folder, LIST_FILE)
    with open(target_file_path, 'w') as fd:
        lines = []
        for f in ordered_files:
            lines.append("file '" + f + "'\n")
        fd.writelines(lines)
    return target_file_path


def _pre_conversion(ordered_files):
    """ Helper function. It removes all unsupported charachters and then, if necessary, it performs a pre-conversion
        of the audio files from M4A OR M4B to MP3.

        syscmd does not work for some reason. THe reason seems to be if the ffmpeg command requires an input
        from the standard input.
        ret_code, output = syscmd(cmd)
        if ret_code != 0:
        messagebox.showerror("Error", output)

        Parameters:
            ordered_files: List of strings. List of the paths of the files to be converted in the correct order.
     """
    # covert each file in mp3, with the same name.
    for i in range(len(ordered_files)):
        if ordered_files[i].endswith(".m4a") or ordered_files[i].endswith(".m4b"):
            f_in = ordered_files[i]
            f_out = ordered_files[i].replace('.m4a', '.mp3').replace('.m4b', '.mp3')

            # apply the conversion with ffmpeg
            cmd = 'ffmpeg.exe -y -i {} {}'.format(f_in, f_out)
            os.system(cmd)

            # remove the original file.
            os.unlink(f_in)

            # update the list.
            ordered_files[i] = f_out
    return ordered_files


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

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = AudioConcatenator(root)
    root.mainloop()
