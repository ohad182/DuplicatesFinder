#!/usr/bin/env python
import sys
import os
import time
import ConfigParser

from Tkinter import *
import tkMessageBox
import tkFileDialog

DELETE_MISSING_TEXT = "Delete Missing"

cwd = os.getcwd()
tcl_lib = cwd + '\\tcl\\tcl8.4'
tk_lib = cwd + '\\tcl\\tcl8.4'
select_file_dir = cwd
settings_path = os.path.join(cwd, 'settings.ini')

PATH_SEP = os.path.sep

if PATH_SEP == '/':
    NON_PATH_SEP = '\\'
else:
    NON_PATH_SEP = '/'

DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

verbose = False
ask_delete = True
log_file = "C:\\Temp\\DupsFinderLog.txt"
work_file = None
fs_search_dir = None
duplicates = list(set())
file_types = '.SET'
missing_files_lines = []

config = ConfigParser.ConfigParser()
if os.path.exists(settings_path):
    config.read(settings_path)
    select_file_dir = config.get('defaults', 'file_dialog_default_dir', cwd)
    file_types = config.get('defaults', 'file_dialog_types', '.SET')


def write_to_log_file(message):
    global log_file
    if os.path.exists(log_file):
        f = open(log_file, "ab")
    else:
        f = open(log_file, "w")

    try:
        f.write("%s%s" % (message, os.linesep))
    finally:
        f.close()


def log(message):
    print(message)
    log_panel.insert(END, "%s\n" % message)
    log_panel.see(END)
    write_to_log_file(message)


def get_file_lines():
    global work_file
    f = open(work_file, 'r')
    file_lines = []
    try:
        file_lines = f.readlines()
    except Exception, e:
        # except Exception as e:
        log(str(e))
    f.close()
    return file_lines


def write_file_lines(file_lines):
    global work_file
    f = open(work_file, 'w')
    try:
        f.writelines(file_lines)
    except Exception, e:
        # except Exception as e:
        log(str(e))
    f.close()


def reset_buttons():
    fix_dups_btn.config(state="disabled")
    fix_missing_btn.config(state="disabled")
    # strip_file_btn.config(state="normal")


def reset():
    reset_buttons()
    clear_log()


def create_file_nested(file_path, content="Sample Text"):
    directory = None
    try:
        directory = os.path.dirname(file_path)
        os.makedirs(directory)
    except OSError, e:
        if directory is not None and not os.path.isdir(directory):
            raise

    f = open(file_path, 'w')
    try:
        f.write(content)
    except Exception, e:
        # except Exception as e:
        log(str(e))
    f.close()


write_to_log_file("setting TCL_LIBRARY to %s" % tcl_lib)
os.environ['TCL_LIBRARY'] = tcl_lib
write_to_log_file("setting TK_LIBRARY to %s" % tk_lib)
os.environ['TK_LIBRARY'] = tk_lib


def search_file(file_path, root=None, stop_first=False):
    file_name = os.path.basename(file_path)
    if root is None:
        drive, _ = os.path.splitdrive(file_path)
        directories = os.path.dirname(file_path).split(os.sep)
        root = os.path.join(drive, os.sep, directories[1])

    log("Searching for '%s' in '%s'" % (file_name, root))
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(root):
        for cf in f:
            if file_name.lower() == cf.lower():
                path = os.path.join(r, cf)
                path = path.replace(NON_PATH_SEP, PATH_SEP)
                files.append(path)
                if stop_first:
                    break

        if stop_first and len(files) > 0:
            break

    log("Candidates: %s" % ','.join(files))

    return files


def get_file_path_from_line(line):
    split_text = line.strip().split(' ')
    current_file = ""
    for part in split_text:
        if '.' in part:
            current_file = current_file + ("%s " % part)
            break
        current_file = current_file + ("%s " % part)
    current_file = current_file.strip()
    return current_file


def find_dups():
    reset()
    global work_file, missing_files_lines, duplicates
    duplicates = list(set())
    missing_files_lines = []
    f = open(work_file, 'r')
    file_lines = []
    try:
        file_lines = f.readlines()
    except Exception, e:
        # except Exception as e:
        log(str(e))
    f.close()

    log("Searching duplicates in %s" % work_file)

    counter = 0
    for line in file_lines:
        # print(line)
        current_file = get_file_path_from_line(line)

        if current_file != '':
            if current_file and not os.path.exists(current_file):
                missing_files_lines.append(counter + 1)
                # create_file_nested(current_file) # debug purpose only
                log("Warning! file doesn't exist: '%s'" % current_file)

            for j in range(counter, len(file_lines)):
                if counter != j and file_lines[counter].strip() == file_lines[j].strip():
                    for match in duplicates:
                        if counter + 1 in match and j + 1 in match:
                            break
                        elif (counter + 1) in match:
                            match.add(j + 1)
                            break
                        elif j + 1 in match:
                            match.add(counter + 1)
                            break
                    else:
                        new_set = set()
                        new_set.add(counter + 1)
                        new_set.add(j + 1)
                        duplicates.append(new_set)
        counter += 1

    if missing_files_lines is not None and len(missing_files_lines) > 0:
        fix_missing_btn.config(state=NORMAL)
    if not duplicates:
        log("No duplicates found!")
    else:
        log("Found %s Duplicate groups." % str(len(duplicates)))
        for group in duplicates:
            lines = ','.join(str(x) for x in list(group))
            lines_content = file_lines[list(group)[0] - 1]
            log("lines %s are the same(%s)" % (lines, lines_content.replace("\n", "")))

        log("To fix duplicates, press 'Fix Duplicates' button")
        fix_dups_btn.config(state=NORMAL)


def fix_dups():
    file_lines = get_file_lines()
    for match in duplicates:
        log("Found:")
        for line_num in match:
            log("line: %s, content: %s" % (line_num, file_lines[line_num - 1].replace('\n', '')))
        log("Keeping line No.: %s" % match.pop())
        while len(match) > 0:
            next_to_kill = match.pop() - 1
            log("Removing line No: %s" % str(next_to_kill + 1))
            file_lines[next_to_kill] = ""

    new_lines = get_stripped_lines(file_lines)
    write_file_lines(new_lines)
    log("Fix Duplicates Done!")


# def delete_missing():
#     global missing_files_lines
#     file_lines = get_file_lines()
#     clear_count = 0
#     if missing_files_lines is not None and len(missing_files_lines) > 0:
#         for i in missing_files_lines:
#             if (i - 1) < len(file_lines):
#                 file_lines[i - 1] = ""
#                 clear_count += 1
#             else:
#                 log("Warning! request to delete out of range entry (possibly deleted as duplicate")
#
#         log("Cleared %s line(s)" % clear_count)
#         write_file_lines(file_lines)


def get_stripped_lines(file_lines):
    new_lines = []
    stripped = 0
    for line in file_lines:
        if line and line.strip() != '':
            new_lines.append(line)
        else:
            stripped += 1

    log("Stripped %s line(s)" % stripped)
    return new_lines


def strip_file():
    file_lines = get_file_lines()
    new_lines = get_stripped_lines(file_lines)
    write_file_lines(new_lines)


def fix_missing():
    global missing_files_lines
    missing_files_lines = []
    file_lines = get_file_lines()

    log("Started fix missing files!")
    counter = 0
    for line in file_lines:
        current_file = get_file_path_from_line(line)
        if current_file != '':
            if current_file and not os.path.exists(current_file):
                missing_files_lines.append(counter + 1)
                # create_file_nested(current_file) # debug purpose only
                log("Warning! file doesn't exist: '%s'" % current_file)
        counter += 1

    log("Found %s missing files ^^..." % counter)

    alternative_list = []
    if missing_files_lines is not None and len(missing_files_lines) > 0:
        for i in missing_files_lines:
            if (i - 1) < len(file_lines):
                current_file = get_file_path_from_line(file_lines[i - 1])
                alternatives = search_file(current_file)
                af = AlternativeFile(old_path=current_file, os_path="###".join(alternatives), line_index=i - 1)
                alternative_list.append(af)
            else:
                log("Warning! request to delete out of range entry (possibly deleted as duplicate)")

        d = AlternativeFileDialog("Please check if alternative files are ok", alternative_list)
        app.wait_window(d.top)
        print(d.top)
        if not d.cancelled:
            for alternative in alternative_list:
                if alternative.path_in_fs == '':
                    file_lines[alternative.line_index] = os.linesep
                else:
                    file_lines[alternative.line_index] = file_lines[alternative.line_index].replace(
                        alternative.path_in_set,
                        alternative.path_in_fs)

            new_lines = get_stripped_lines(file_lines)
            write_file_lines(new_lines)
            log("Fix Missing Done!")
        else:
            log("Fix Missing Aborted!")


def search_folder():
    d = SearchDuplicatesDialog()
    app.wait_window(d.top)


def set_file_types():
    global file_types
    if not isinstance(file_types, (list,)):
        ft = []
        types = file_types.split(" ")

        for tp in types:
            typ = tp.lstrip(".")
            ft.append(("%s files" % typ.title(), "*.%s" % typ))

        print(ft)
        file_types = ft


def select_file():
    global work_file, file_types
    set_file_types()
    dialog_result = tkFileDialog.askopenfile(title="Select File", initialdir=select_file_dir,
                                             filetypes=file_types)
    if dialog_result is not None:
        work_file = dialog_result.name
        print(work_file)
        source_entry_text.set(work_file)
        find_dups_btn.config(state="normal")
        reset()


def select_folder(title="Select Folder"):
    global fs_search_dir
    dlg_result = tkFileDialog.askdirectory(title=title, initialdir=select_file_dir)
    if dlg_result is not None:
        fs_search_dir = dlg_result
        print("Search fs set to %s" % fs_search_dir)
        fs_src_entry_text.set(fs_search_dir)
        fs_search_btn.config(state=NORMAL)


def clear_log():
    log_panel.delete('1.0', END)


def search_fs_duplicates():
    global fs_search_dir
    files_info = []
    grouped_files = dict()
    # r=root, d=directories, f = files
    for r, d, f in os.walk(fs_search_dir):
        for fi in f:
            files_info.append(FileInfo(name=fi, full_path=os.path.join(r, fi)))

    log("Scanned %s files" % len(files_info))

    has_duplicates = False
    for f in files_info:
        if f.name in grouped_files:
            if not has_duplicates:
                has_duplicates = True
            grouped_files[f.name].append(f)
        else:
            grouped_files[f.name] = [f]

    if not has_duplicates:
        log("No duplicates found!")
        # self.table_label.config(text="No duplicates found!")
    else:
        # for widget in self.table_frame.winfo_children():
        #     widget.destroy()

        # self.table_label.config(text="Found duplicates:")
        # fs_show_duplicates_btn.config(state=NORMAL)
        for filename, file_info in grouped_files.iteritems():
            if len(file_info) > 1:
                log("%s has %d duplicates" % (filename, len(file_info)))
                for fi in file_info:
                    log("\t%s - %s" % (fi.full_path, time.strftime(DATE_FORMAT, time.localtime(fi.date))))
                log("")
                # TODO: keep from here
                # file_name_label = LabelFrame(self.table_frame, text=filename)
                # file_name_label.pack(fill="both", expand="yes")


def show_fs_duplicates():
    d = SearchDuplicatesDialog()
    app.wait_window(d.top)


# def get_next(iterator, default=None):
#     try:
#         return iterator.__next__()
#     except StopIteration:
#         if default is not None:
#             return default
#         else:
#             raise
def get_next(iterator, default=None):
    try:
        return iterator.next()
    except AttributeError:  # Handle generators
        try:
            return iterator.__next__()
        except AttributeError:
            raise TypeError("'%s' object is not an iterator or generator" % type(iterator).__name__)
    except StopIteration:
        if default is not None:
            return default
        else:
            raise

class FileInfo(object):
    def __init__(self, **kwargs):
        fp = kwargs.get("full_path")
        if NON_PATH_SEP in fp:
            fp = fp.replace(NON_PATH_SEP, PATH_SEP)
        self.name = kwargs.get("name")
        self.full_path = fp
        self.date = kwargs.get("date", None)
        if self.date is None:
            self.date = os.path.getmtime(self.full_path)


class AlternativeFile(object):
    def __init__(self, **kwargs):
        self.path_in_set = kwargs.get("old_path", None)
        self.path_in_fs = kwargs.get("os_path", None)
        self.line_index = kwargs.get("line_index")

    def __str__(self):
        return "i: %s - set: %s, fs: %s" % (self.line_index, self.path_in_set, self.path_in_fs)


class AlternativeFileDialog(object):
    root = None

    def __init__(self, msg, alternative_list=None):
        """
        msg = <str> the message to be displayed
        dict_key = <sequence> (dictionary, key) to associate with user input
        (providing a sequence for dict_key creates an entry for user input)
        """

        def on_close_window():
            self.cancel()

        self.top = Toplevel(AlternativeFileDialog.root)
        self.top.protocol("WM_DELETE_WINDOW", on_close_window)
        dialog_height = 320
        # if alternative_list:
        #     dialog_height += (len(alternative_list) * 20)
        self.top.geometry("600x%s+200+200" % dialog_height)
        # frm = Frame(self.top, borderwidth=4, relief='ridge')
        # frm.pack(fill='both', expand=True)

        canvas = Canvas(self.top)
        canvas.pack(side=LEFT, fill='both', expand=True)
        # yscrollcommand=scrollbar.set
        scrollbar = Scrollbar(self.top, orient=VERTICAL, command=canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.config(yscrollcommand=scrollbar.set)

        scrollable_frame = Frame(canvas)
        # scrollable_frame.grid_propagate(False)
        scrollable_frame.pack(side=LEFT, fill='both', expand=True)
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor=NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        # canvas.pack(side="left", fill="both", expand=True)
        # ,width=scrollable_frame.winfo_width()
        # scrollable_frame.config(width=frm.winfo_width())

        def on_canvas_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = event.width
            canvas.itemconfig(canvas_frame, width=canvas_width)

        canvas.bind("<Configure>", on_canvas_configure)

        search_frame = Frame(scrollable_frame)
        search_frame.pack(fill='both')

        search_folder_entry_text = StringVar()
        search_folder_entry = Entry(search_frame, textvariable=search_folder_entry_text, width=50)
        search_folder_entry.config(state=DISABLED)
        search_folder_entry.pack(side=LEFT, expand=YES, padx=5, pady=15, fill=X)

        def select_search_dir():
            dlg_result = tkFileDialog.askdirectory(title="Select Search Base", initialdir=select_file_dir,
                                                   parent=self.top)
            if dlg_result is not None:
                search_directory_path = dlg_result
                log("Search fs set to %s" % search_directory_path)
                search_folder_entry_text.set(search_directory_path)
                search_in_folder_btn.config(state=NORMAL)
                self.update_table(search_directory_path, alternative_list)

        search_in_folder_btn = Button(search_frame, text='Select Search Folder', command=select_search_dir)
        search_in_folder_btn.pack(side=LEFT, padx=5, pady=15)

        keep_original_frame = Frame(scrollable_frame)
        keep_original_frame.pack(fill='both')

        keep_original_btn = Button(search_frame, text='Keep Missing Original Files', command=self.copy_missing_keys)
        keep_original_btn.pack(side=LEFT, padx=5, pady=15)

        label = Label(scrollable_frame, text=msg)
        label.pack(padx=4, pady=4, fill=X)

        headers_frm = Frame(scrollable_frame)
        headers_frm.pack(fill='both')

        header1 = Label(headers_frm, text="Path in SET")
        header1.pack(side=LEFT, padx=3, pady=4, fill=X, expand=True)
        header2 = Label(headers_frm, text="Path in File System")
        header2.pack(side=LEFT, padx=3, pady=4, fill=X, expand=True)

        self.cancelled = False
        self.table_frame = Frame(scrollable_frame)
        self.table_frame.pack(anchor=N, fill=X, expand=True, side=TOP)

        row = 0
        if alternative_list is not None:
            for item in alternative_list:  # Rows
                self.table_frame.grid_columnconfigure(0, weight=1, uniform="group%s" % row)
                self.table_frame.grid_columnconfigure(1, weight=1, uniform="group%s" % row)
                self.table_frame.grid_rowconfigure(row)

                key_entry_text = StringVar()
                key_entry_text.set(item.path_in_set)
                b0 = Entry(self.table_frame, textvariable=key_entry_text)
                b0.config(state=DISABLED)
                b0.grid(row=row, column=0, sticky='news', padx=3)

                value_entry_text = StringVar()
                value_entry_text.set(item.path_in_fs)
                b1 = Entry(self.table_frame, textvariable=value_entry_text)
                b1.grid(row=row, column=1, sticky='news', padx=3)

                row += 1

        dialog_actions_frame = Frame(scrollable_frame)
        dialog_actions_frame.pack(side=BOTTOM)

        b_submit = Button(dialog_actions_frame, text='Submit')
        b_submit['command'] = lambda: self.entry_to_dict(alternative_list)
        b_submit.pack(side=LEFT)

        b_cancel = Button(dialog_actions_frame, text='Cancel')
        b_cancel['command'] = self.cancel
        b_cancel.pack(side=LEFT, padx=4, pady=4)

    def update_table(self, search_directory_path, alternatives_list):
        table_items = self.table_frame.winfo_children()
        for i in range(len(table_items)):
            if i == 0 or i % 2 == 0:
                original_file_path = table_items[i].get()
                file_name = os.path.basename(original_file_path)

                alternative_entry = table_items[i + 1]
                alternative_entry_value = alternative_entry.get()

                if alternative_entry_value.strip() == "":
                    log("file %s has empty value" % original_file_path)
                    alternative_file = search_file(file_name, search_directory_path, True)
                    log(alternative_file)
                    alternative_entry.delete(0, END)
                    alternative_entry.insert(0, "###".join(alternative_file))
                    model_file = get_next((x for x in alternatives_list if x.path_in_set == original_file_path), None)
                    if model_file is not None:
                        model_file.path_in_fs = alternative_file

    def copy_missing_keys(self):
        """
        Will copy the missing origin file path to the destination file path if its missing
        :return:
        """
        table_items = self.table_frame.winfo_children()
        for i in range(len(table_items)):
            if i == 0 or i % 2 == 0:
                original_file_path = table_items[i].get()

                alternative_entry = table_items[i + 1]
                alternative_entry_value = alternative_entry.get()

                if alternative_entry_value.strip() == "":
                    alternative_entry.delete(0, END)
                    alternative_entry.insert(0, original_file_path)

    def entry_to_dict(self, alternative_list):
        it = iter(self.table_frame.winfo_children())
        has_empty = False
        for child in it:
            to_change = [x for x in alternative_list if x.path_in_set == child.get()]
            if len(to_change) == 0:
                log("Error! cannot find %s in %s" % (child.get(), alternative_list))
            elif len(to_change) > 1:
                log("Error! Found multiple entries named %s in %s" % (child.get(), alternative_list))
            else:
                to_change = to_change[0]
                to_change.path_in_fs = it.next().get()
                if to_change.path_in_fs == "":
                    has_empty = True

        if has_empty:
            result = tkMessageBox.askokcancel("Empty Path", "Cannot save if filesystem path is empty")
            if result is True:
                self.cancelled = False
                self.top.destroy()
        else:
            self.top.destroy()

    def cancel(self):
        print("cancel")
        self.cancelled = True
        self.top.destroy()


class SearchDuplicatesDialog(object):
    root = None

    def __init__(self):
        """
        msg = <str> the message to be displayed
        dict_key = <sequence> (dictionary, key) to associate with user input
        (providing a sequence for dict_key creates an entry for user input)
        """
        self.top = Toplevel(SearchDuplicatesDialog.root)
        # self.top.wm_attributes('-topmost', 1)  # TODO: find fix
        dialog_height = 120
        self.files_info = []
        self.grouped_files = dict()

        self.top.geometry("500x%s+200+200" % dialog_height)
        frm = Frame(self.top, borderwidth=4, relief='ridge')
        frm.pack(fill='both', expand=True)

        src_frame = Frame(frm)
        src_frame.pack()

        # self.src_entry_text = StringVar()
        # src_entry = Entry(src_frame, textvariable=self.src_entry_text, width=50)
        # src_entry.config(state=DISABLED)
        # src_entry.pack(side=LEFT, expand=YES, padx=5, pady=15, fill=X)
        # # select file button
        # selectFolderBtn = Button(src_frame, text='Select Folder', command=self.select_folder)
        # selectFolderBtn.pack(side=LEFT, padx=5, pady=15)
        #
        # self.searchBtn = Button(src_frame, text='Search', command=self.search)
        # self.searchBtn.config(state=DISABLED)
        # self.searchBtn.pack(side=LEFT, padx=5, pady=15)
        #
        # # TODO: ui idea -> [textbox with path] - [openlocationbutton, deletefilebuton]
        # self.table_frame = Frame(frm)
        # self.table_frame.pack(anchor=N, fill=X, expand=True, side=TOP)
        #
        # self.table_label = Label(self.table_frame, text="Click Search")
        # self.table_label.pack(padx=4, pady=4)

        # row = 0
        # if alternative_list is not None:
        #     for item in alternative_list:  # Rows
        #         self.table_frame.grid_columnconfigure(0, weight=1, uniform="group%s" % row)
        #         self.table_frame.grid_columnconfigure(1, weight=1, uniform="group%s" % row)
        #         self.table_frame.grid_rowconfigure(row)
        #
        #         key_entry_text = StringVar()
        #         key_entry_text.set(item.path_in_set)
        #         b0 = Entry(self.table_frame, textvariable=key_entry_text)
        #         b0.config(state=DISABLED)
        #         b0.grid(row=row, column=0, sticky='news', padx=3)
        #
        #         value_entry_text = StringVar()
        #         value_entry_text.set(item.path_in_fs)
        #         b1 = Entry(self.table_frame, textvariable=value_entry_text)
        #         b1.grid(row=row, column=1, sticky='news', padx=3)
        #
        #         row += 1

        dialog_actions_frame = Frame(frm)
        dialog_actions_frame.pack(side=BOTTOM)

        b_submit = Button(dialog_actions_frame, text='Close')
        b_submit['command'] = self.ok
        b_submit.pack(side=LEFT)

    def ok(self):
        self.top.destroy()

    def cancel(self):
        self.cancelled = True
        self.top.destroy()


app = Tk()
app.title("Duplicate Finder")
app.geometry("560x300+200+200")

AlternativeFileDialog.root = app
SearchDuplicatesDialog.root = app

source_frame = Frame(app)
source_frame.pack()

source_entry_text = StringVar()
source_entry = Entry(source_frame, textvariable=source_entry_text, width=50)
source_entry.config(state=DISABLED)
source_entry.pack(side=LEFT, expand=YES, padx=5, pady=15, fill=X)
# select file button
selectFileBtn = Button(source_frame, text='Select File', command=select_file)
selectFileBtn.pack(side=LEFT, padx=5, pady=15)

log_frame = Frame(app)
log_frame.pack(anchor=N, fill=Y, expand=True)

text_scroll = Scrollbar(log_frame)
log_panel = Text(log_frame, height=7)
text_scroll.pack(side=RIGHT, fill=Y)
log_panel.pack(side=LEFT, fill=Y)
text_scroll.config(command=log_panel.yview)
log_panel.config(yscrollcommand=text_scroll.set)

# dup_actions_frame = Frame(app)
# dup_actions_frame.pack()
actions_frame = Frame(app)
actions_frame.pack()

fix_dups_btn = Button(actions_frame, text='Fix Duplicates', command=fix_dups)
fix_dups_btn.config(state=DISABLED)
fix_dups_btn.pack(side=LEFT, padx=5, pady=5)

find_dups_btn = Button(actions_frame, text='Find Errors', command=find_dups)
find_dups_btn.config(state=DISABLED)
find_dups_btn.pack(side=LEFT, padx=5, pady=5)

fix_missing_btn = Button(actions_frame, text='Fix Missing', command=fix_missing)
fix_missing_btn.config(state=DISABLED)
fix_missing_btn.pack(side=LEFT, padx=5, pady=5)

# search_dups_btn = Button(actions_frame, text='Search Folder', command=search_folder)
# search_dups_btn.pack(side=LEFT, padx=5, pady=5)

fs_src_frame = Frame(app, pady=10)
fs_src_frame.pack()

fs_src_label = Label(fs_src_frame, text="Search duplicates on file system:")
fs_src_label.pack()

fs_src_entry_text = StringVar()
fs_src_entry = Entry(fs_src_frame, textvariable=fs_src_entry_text, width=50)
fs_src_entry.config(state=DISABLED)
fs_src_entry.pack(side=LEFT, expand=YES, padx=5, pady=15, fill=X)
# select file button
fs_selectFolderBtn = Button(fs_src_frame, text='Select Folder', command=select_folder)
fs_selectFolderBtn.pack(side=LEFT, padx=5, pady=15)

fs_search_btn = Button(fs_src_frame, text='Search', command=search_fs_duplicates)
fs_search_btn.config(state=DISABLED)
fs_search_btn.pack(side=LEFT, padx=5, pady=15)

fs_show_duplicates_btn = Button(fs_src_frame, text='Show fs duplicates', command=show_fs_duplicates)
fs_show_duplicates_btn.config(state=DISABLED)
fs_show_duplicates_btn.pack(side=LEFT, padx=5, pady=15)

# app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
# >c:\Python24\python.exe setup.py py2exe
