#!/usr/bin/env python
import sys
import os
import ConfigParser

from Tkinter import *
import tkFileDialog

DELETE_MISSING_TEXT = "Delete Missing"

cwd = os.getcwd()
tcl_lib = cwd + '\\tcl\\tcl8.4'
tk_lib = cwd + '\\tcl\\tcl8.4'
select_file_dir = cwd
settings_path = os.path.join(cwd, 'settings.ini')

verbose = False
ask_delete = True
log_file = "C:\\Temp\\DupsFinderLog.txt"
work_file = None
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
    log_panel.insert(END, message + '\n')
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
    try:
        directory = os.path.dirname(file_path)
        os.makedirs(directory)
    except OSError, e:
        if not os.path.isdir(directory):
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


def find_file(file_path):
    file_name = os.path.basename(file_path)
    drive, _ = os.path.splitdrive(file_path)
    directories = os.path.dirname(file_path).split(os.sep)
    root = os.path.join(drive, os.sep, directories[1])

    log("Searching for '%s' in '%s'" % (file_name, root))
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(root):
        for cf in f:
            if file_name == cf:
                files.append(os.path.join(r, cf))

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

    counter = 0
    for line in file_lines:
        current_file = get_file_path_from_line(line)
        if current_file != '':
            if current_file and not os.path.exists(current_file):
                missing_files_lines.append(counter + 1)
                # create_file_nested(current_file) # debug purpose only
                log("Warning! file doesn't exist: '%s'" % current_file)
        counter += 1

    alternative_list = []
    if missing_files_lines is not None and len(missing_files_lines) > 0:
        for i in missing_files_lines:
            if (i - 1) < len(file_lines):
                current_file = get_file_path_from_line(file_lines[i - 1])
                alternatives = find_file(current_file)
                af = AlternativeFile(old_path=current_file, os_path="###".join(alternatives), line_index=i - 1)
                alternative_list.append(af)
            else:
                log("Warning! request to delete out of range entry (possibly deleted as duplicate")

        d = AlternativeFileDialog("Please check if alternative files are ok", alternative_list)
        app.wait_window(d.top)

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


def clear_log():
    log_panel.delete('1.0', END)


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
        self.top = Toplevel(AlternativeFileDialog.root)
        dialog_height = 120
        if alternative_list:
            dialog_height += (len(alternative_list) * 20)
        self.top.geometry("400x%s+200+200" % dialog_height)
        frm = Frame(self.top, borderwidth=4, relief='ridge')
        frm.pack(fill='both', expand=True)

        label = Label(frm, text=msg)
        label.pack(padx=4, pady=4)

        headers_frm = Frame(frm)
        headers_frm.pack(fill='both')

        header1 = Label(headers_frm, text="Path in SET")
        header1.pack(side=LEFT, padx=3, pady=4, fill=X, expand=True)
        header2 = Label(headers_frm, text="Path in File System")
        header2.pack(side=LEFT, padx=3, pady=4, fill=X, expand=True)

        self.cancelled = False
        self.table_frame = Frame(frm)
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

        dialog_actions_frame = Frame(frm)
        dialog_actions_frame.pack(side=BOTTOM)

        b_submit = Button(dialog_actions_frame, text='Submit')
        b_submit['command'] = lambda: self.entry_to_dict(alternative_list)
        b_submit.pack(side=LEFT)

        b_cancel = Button(dialog_actions_frame, text='Cancel')
        b_cancel['command'] = self.cancel
        b_cancel.pack(side=LEFT, padx=4, pady=4)

    def entry_to_dict(self, alternative_list):
        it = iter(self.table_frame.winfo_children())
        for child in it:
            to_change = [x for x in alternative_list if x.path_in_set == child.get()]
            if len(to_change) == 0:
                log("Error! cannot find %s in %s" % (child.get(), alternative_list))
            elif len(to_change) > 1:
                log("Error! Found multiple entries named %s in %s" % (child.get(), alternative_list))
            else:
                to_change = to_change[0]
                to_change.path_in_fs = it.next().get()
        self.top.destroy()

    def cancel(self):
        self.cancelled = True
        self.top.destroy()


app = Tk()
app.title("Duplicate Finder")
app.geometry("560x220+200+200")

AlternativeFileDialog.root = app

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
actions_frame.pack(side=BOTTOM)

fix_dups_btn = Button(actions_frame, text='Fix Duplicates', command=fix_dups)
fix_dups_btn.config(state=DISABLED)
fix_dups_btn.pack(side=LEFT, padx=5, pady=5)

find_dups_btn = Button(actions_frame, text='Find Errors', command=find_dups)
find_dups_btn.config(state=DISABLED)
find_dups_btn.pack(side=LEFT, padx=5, pady=5)

fix_missing_btn = Button(actions_frame, text='Fix Missing', command=fix_missing)
fix_missing_btn.config(state=DISABLED)
fix_missing_btn.pack(side=LEFT, padx=5, pady=5)

# app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
# >c:\Python24\python.exe setup.py py2exe
