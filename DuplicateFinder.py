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


def reset():
    delete_missing_btn.config(state="disabled")
    fix_dups_btn.config(state="disabled")
    strip_file_btn.config(state="normal")


write_to_log_file("setting TCL_LIBRARY to %s" % tcl_lib)
os.environ['TCL_LIBRARY'] = tcl_lib
write_to_log_file("setting TK_LIBRARY to %s" % tk_lib)
os.environ['TK_LIBRARY'] = tk_lib


def find_dups():
    clear_log()
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
        print(line)
        split_text = line.strip().split(' ')
        current_file = ""
        for part in split_text:
            if '.' in part:
                current_file = current_file + ("%s " % part)
                break
            current_file = current_file + ("%s " % part)
        current_file = current_file.strip()

        if not os.path.exists(current_file):
            missing_files_lines.append(counter + 1)
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
        delete_missing_btn.config(state=NORMAL)
        delete_missing_btn["text"] = "%s (%s)" % (DELETE_MISSING_TEXT, len(missing_files_lines))
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

    write_file_lines(file_lines)
    log("Done!")


def delete_missing():
    global missing_files_lines
    file_lines = get_file_lines()
    clear_count = 0
    if missing_files_lines is not None and len(missing_files_lines) > 0:
        for i in missing_files_lines:
            if (i - 1) < len(file_lines):
                file_lines[i - 1] = ""
                clear_count += 1
            else:
                log("Warning! request to delete out of range entry (possibly deleted as duplicate")

        log("Cleared %s line(s)" % clear_count)
        write_file_lines(file_lines)


def strip_file():
    file_lines = get_file_lines()
    new_lines = []
    stripped = 0
    for line in file_lines:
        if line and line.strip() != '':
            new_lines.append(line)
        else:
            stripped += 1

    log("Stripped %s line(s)" % stripped)
    write_file_lines(new_lines)


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


app = Tk()
app.title("Duplicate Finder")
app.geometry("560x220+200+200")

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

find_dups_btn = Button(actions_frame, text='Find Duplicates', command=find_dups)
find_dups_btn.config(state=DISABLED)
find_dups_btn.pack(side=LEFT, padx=5, pady=5)

delete_missing_btn = Button(actions_frame, text='Delete Missing', command=delete_missing)
delete_missing_btn.config(state=DISABLED)
delete_missing_btn.pack(side=LEFT, padx=5, pady=5)

strip_file_btn = Button(actions_frame, text='Strip File', command=strip_file)
strip_file_btn.config(state=DISABLED)
strip_file_btn.pack(side=LEFT, padx=5, pady=5)
# app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
# >c:\Python24\python.exe setup.py py2exe
