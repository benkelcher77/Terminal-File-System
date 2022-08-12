#!/bin/python3

import curses
import curses.ascii
from curses import wrapper

import enum

import os
import os.path

import pwd

import subprocess
import stat
import sys
import time

def parsePermissions(mode):
    perms = list("---------")

    # Owner Permissions
    if bool(mode & stat.S_IRUSR):
        perms[0] = "r"
    if bool(mode & stat.S_IWUSR):
        perms[1] = "w"
    if bool(mode & stat.S_IXUSR):
        perms[2] = "x"

    # Group Permissions
    if bool(mode & stat.S_IRGRP):
        perms[3] = "r"
    if bool(mode & stat.S_IWGRP):
        perms[4] = "w"
    if bool(mode & stat.S_IXGRP):
        perms[5] = "x"

    # Others Permissions
    if bool(mode & stat.S_IROTH):
        perms[6] = "r"
    if bool(mode & stat.S_IWOTH):
        perms[7] = "w"
    if bool(mode & stat.S_IXOTH):
        perms[8] = "x"

    return "".join(perms)


class PreviewType(enum.Enum):
    FILE = enum.auto()
    DIRECTORY = enum.auto()
    UNKNOWN = enum.auto()

class Renderer:
    def __init__(self, stdscr):
        curses.curs_set(False)

        self.stdscr = stdscr
        self.left = self.stdscr.subwin(curses.LINES, curses.COLS // 2 - 1, 0, 0)
        self.right = self.stdscr.subwin(curses.LINES, curses.COLS // 2, 0, curses.COLS // 2 - 1)

        # Colours. Format: (pair_index, FG_COLOR, BG_COLOR)
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

        # Class variables
        self.wd = os.getcwd()
        self.files = os.listdir(self.wd)
        self.files.sort()
        self.filesIndex = 0
        self.filesOffsFromTop = 0
        self.determinePreviewType(self.files)

        # Searching
        self.searchQuery = ""
        self.searching = False
        self.filteredFiles = self.files

    def determinePreviewType(self, files):
        if len(files) == 0:
            self.previewDirList = ["Preview unavailable."]
            return

        path = os.path.join(self.wd, files[self.filesIndex])

        if os.path.isdir(path):
            self.previewType = PreviewType.DIRECTORY
            try:
                self.previewDirList = os.listdir(path)
                self.previewDirList.sort()
            except PermissionError:
                self.previewDirList = ["ERROR: Failed to obtain contents of directory."]
        else:
            self.previewType = PreviewType.FILE
            
            try:
                fileInfo = os.stat(path)
                accessTime = fileInfo.st_atime
                modTime = fileInfo.st_mtime
                size = fileInfo.st_size
                perms = parsePermissions(fileInfo.st_mode)
                owner = pwd.getpwuid(fileInfo.st_uid).pw_name

                self.fileInfoStrs = [
                    f"Size: {size} B",
                    f"Previous Access: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(accessTime))}",
                    f"Previous Modification: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modTime))}",
                    f"Permissions: {perms}",
                    f"Owner: {owner}"
                ]
            except PermissionError:
                self.fileInfoStrs = ["ERROR: Failed to obtain file statistics."]


    def update(self):
        c = self.stdscr.getch()

        files = self.files if (len(self.searchQuery) == 0 and not self.searching) else self.filteredFiles

        if not self.searching:
            if c == curses.KEY_DOWN:
                self.filesIndex = self.filesIndex + 1
                if self.filesIndex >= len(files):
                    self.filesIndex = len(files) - 1
                if self.filesIndex > curses.LINES - 3 + self.filesOffsFromTop:
                    self.filesOffsFromTop += 1
            elif c == curses.KEY_UP:
                self.filesIndex = self.filesIndex - 1
                if self.filesIndex < 0:
                    self.filesIndex = 0
                if self.filesIndex < self.filesOffsFromTop:
                    self.filesOffsFromTop -= 1
            elif (c == curses.KEY_ENTER or c == 10 or c == 13) and len(files) > 0:
                self.determinePreviewType(files)

                if self.previewType == PreviewType.FILE:
                    # Suspend curses
                    curses.endwin()

                    # Open the file
                    proc = subprocess.Popen(["nvim", os.path.join(self.wd, files[self.filesIndex])])
                    proc.wait()

                    # Restart curses
                    self.stdscr = curses.initscr()
                    self.stdscr.clear()
                    self.stdscr.refresh()
                elif self.previewType == PreviewType.DIRECTORY:
                    # Change directories into the file and update everything
                    os.chdir(os.path.join(self.wd, files[self.filesIndex]))
                    self.wd = os.getcwd()
                    self.files = os.listdir(self.wd)
                    self.files.sort()
                    self.filesIndex = 0
                    self.filesOffsFromTop = 0
                    self.searchQuery = "" # Clear the search query
                    files = self.files
            elif c == curses.KEY_BACKSPACE:
                # Go to parent dir
                os.chdir("../")
                self.wd = os.getcwd()
                self.files = os.listdir(self.wd)
                self.files.sort()
                self.filesIndex = 0
                self.searchQuery = ""
                files = self.files
            elif c == ord('\\'):
                # Clear the search query
                self.searchQuery = ""
                self.files = os.listdir(self.wd)
                self.files.sort()
            elif c == ord("/"):
                self.searching = True
                self.filteredFiles = self.files
            elif c == ord('q'):
                return True
        else:
            if c == curses.KEY_ENTER or c == 10 or c == 13:
                self.searching = False
            elif c == curses.KEY_BACKSPACE:
                self.searchQuery = self.searchQuery[:-1]
                self.filteredFiles = [f for f in self.files if self.searchQuery in f]
                self.filesIndex = 0
                self.filesOffsFromTop = 0
                files = self.filteredFiles
            elif c == curses.KEY_DOWN:
                self.filesIndex = self.filesIndex + 1
                if self.filesIndex >= len(files):
                    self.filesIndex = len(files) - 1
                if self.filesIndex > curses.LINES - 3 + self.filesOffsFromTop:
                    self.filesOffsFromTop += 1
            elif c == curses.KEY_UP:
                self.filesIndex = self.filesIndex - 1
                if self.filesIndex < 0:
                    self.filesIndex = 0
                if self.filesIndex < self.filesOffsFromTop:
                    self.filesOffsFromTop -= 1
            else:
                self.searchQuery = self.searchQuery + chr(c)
                self.filteredFiles = [f for f in self.files if self.searchQuery in f]
                self.filesIndex = 0
                self.filesOffsFromTop = 0
                files = self.filteredFiles

        self.determinePreviewType(files)

        return False

    def render(self):
        self.left.erase()
        self.right.erase()

        self.left.box()
        self.right.box()

        # Left screen (current directory)
        i = 1
        files = self.files if (len(self.searchQuery) == 0 and not self.searching) else self.filteredFiles
        for f in files[self.filesOffsFromTop:(self.filesOffsFromTop + curses.LINES - 2)]:
            col = curses.color_pair(1) if (i - 1 + self.filesOffsFromTop) != self.filesIndex else curses.color_pair(2)
            self.left.addstr(i, 1, f, col)
            i = i + 1
            if i > curses.LINES - 2:
                break # TODO Fix this so that we can "scroll" through the files if there are too many

        if self.searching or len(self.searchQuery) > 0:
            self.left.addstr(0, 1, f"Filter: {self.searchQuery}")
        self.left.addstr(curses.LINES - 1, 1, f"{self.wd} [{self.filesIndex + 1}/{len(files)}]")

        # Right screen (preview)
        if len(files) > 0:
            if self.previewType == PreviewType.FILE:
                self.right.addstr(1, 1, f"File: {os.path.join(self.wd, files[self.filesIndex])}", curses.color_pair(1))
                i = 2
                for s in self.fileInfoStrs:
                    self.right.addstr(i, 1, s, curses.color_pair(1))
                    i = i + 1
            elif self.previewType == PreviewType.DIRECTORY:
                self.right.addstr(1, 1, f"Directory: {os.path.join(self.wd, files[self.filesIndex])}", curses.color_pair(1))
                i = 2
                for f in self.previewDirList:
                    self.right.addstr(i, 1, f"\t> {f}", curses.color_pair(1))
                    i = i + 1
                    if i > curses.LINES - 2:
                        break # TODO Fix this so that we can "scroll" through the files if there are too many
            else:
                pass

        self.left.refresh()
        self.right.refresh()

def main(stdscr):
    r = Renderer(stdscr)
    stdscr.clear()

    r.render() # Get something onto the screen

    while True:
        if r.update():
            break

        r.render()

    if len(sys.argv) > 1:
        # sys.argv[1] will contain the tmpfile to write the working directory into IF it exists
        with open(sys.argv[1], "w") as out:
            out.write(r.wd)

if __name__ == "__main__":
    wrapper(main)
