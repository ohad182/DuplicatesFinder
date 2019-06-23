#!/usr/bin/env python
import sys
import os
verbose = False
ask_delete = True
log_file = "C:\\Temp\\DupsFinderLog.txt"


def log(message):
    print(message)
    global log_file
    if os.path.exists(log_file):
        f = open(log_file, "ab")
    else:
        f = open(log_file, "w")

    try:
        f.write("%s%s" % (message, os.linesep))
    finally:
        f.close()


def find_dups(path):
    f = open(path, 'r')
    file_lines = []
    try:
        file_lines = f.readlines()
    except Exception, e:
        log(str(e))
    f.close()

    log("Searching duplicates in %s" % path)
    dups = list(set())
    for i in range(0, len(file_lines)):

        split_text = file_lines[i].split(' ')
        current_file = ""
        for part in split_text:
            if '.' in part:
                current_file = current_file + ("%s " % part)
                break
            current_file = current_file + ("%s " % part)
        current_file = current_file.strip()

        if verbose:
            if not os.path.exists(current_file):
                log("Error! file doesn't exist: %s" % current_file)

        for j in range(1, len(file_lines)):
            if i != j and file_lines[i] == file_lines[j]:
                for match in dups:
                    if i + 1 in match and j + 1 in match:
                        break
                    elif i + 1 in match:
                        match.add(j + 1)
                    elif j + 1 in match:
                        match.add(i + 1)
                else:
                    new_set = set()
                    new_set.add(i + 1)
                    new_set.add(j + 1)
                    dups.append(new_set)

    if not dups:
        log("No duplicates found!")
    else:
        log("Found %s Duplicate groups." % str(len(dups)))
        for group in dups:
            lines = ','.join(str(x) for x in list(group))
            lines_content = file_lines[list(group)[0] - 1]
            log("lines %s are the same(%s)" % (lines, lines_content.replace("\n", "")))

        if ask_delete:
            fix_file = raw_input("Fix duplicates? (y/n)").lower() != 'n'
        else:
            fix_file = True

        if fix_file:
            for match in dups:
                log("Found:")
                for line_num in match:
                    log(
                        "line: %s, content: %s" % (line_num, file_lines[line_num - 1].replace('\n', '')))
                log("Keeping line No.: %s" % match.pop())
                while len(match) > 0:
                    next_to_kill = match.pop() - 1
                    log("Removing line No: %s" % str(next_to_kill + 1))
                    file_lines[next_to_kill] = ""
                log("")

            f = open(path, 'w')
            try:
                f.writelines(file_lines)
            except Exception, e:
                log(str(e))
            f.close()
        else:
            log("Duplicates kept in file.")


def run(file_path=None):
    try:
        while file_path is None or not os.path.exists(file_path):
            file_path = raw_input("Please specify the full path of your file:")
            if "exit" in file_path.lower():
                sys.exit(0)

        if os.path.isdir(file_path):
            global ask_delete
            ask_delete = False
            for file_in_path in os.listdir(file_path):
                try:
                    find_dups(os.path.join(file_path, file_in_path))
                except Exception, ex:
                    log("ERROR : %s" % str(ex))
        else:
            find_dups(file_path)
        run()
    except Exception, e:
        if str(e) == "0":
            log("Bye")
        else:
            log("RUN ERROR: %s" % str(e))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        #     verbose = sys.argv[2] if len(sys.argv) > 2 else False
        run(sys.argv[1])
    else:
        # print("Error! No file was specified.")
        # print("CMD option: DupsFinder.exe {file_path} [-verbose].\n")
        run()

        # print("Searching duplicates in {}".format(file_path))
        # find_dups(file_path)
        # raw_input("Press enter to exit")
