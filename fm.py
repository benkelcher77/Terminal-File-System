#!/bin/python3

import curses
from curses import wrapper
import curses.ascii

import enum
import os
import os.path

import subprocess
import time

class PreviewType(enum.Enum):
    FILE = enum.auto()
    DIRECTORY = enum.auto()
    UNKNOWN = enum.auto()

class Renderer:
    def __init__(self):
        curses.curs_set(False)

        # Colours. Format: (pair_index, FG_COLOR, BG_COLOR)
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

        # Class variables
        self.wd = os.getcwd()
        self.files = os.listdir(self.wd)
        self.files.sort()
        self.filesIndex = 0
        self.determinePreviewType()

    def determinePreviewType(self):
        path = os.path.join(self.wd, self.files[self.filesIndex])

        if os.path.isdir(path):
            self.previewType = PreviewType.DIRECTORY
            self.previewDirList = os.listdir(path)
            self.previewDirList.sort()
        else:
            self.previewType = PreviewType.FILE
            
            fileInfo = os.stat(path)
            modTime = fileInfo.st_mtime
            size = fileInfo.st_size

            self.fileInfoStrs = [
                f"Size: {size} B",
                f"Previous Modification: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modTime))}"
            ]

    def update(self, stdscr):
        c = stdscr.getch()

        if c == curses.KEY_DOWN:
            self.filesIndex = self.filesIndex + 1
            if self.filesIndex >= len(self.files):
                self.filesIndex = len(self.files) - 1
        elif c == curses.KEY_UP:
            self.filesIndex = self.filesIndex - 1
            if self.filesIndex < 0:
                self.filesIndex = 0
        elif c == curses.KEY_ENTER or c == 10 or c == 13:
            self.determinePreviewType()

            if self.previewType == PreviewType.FILE:
                # Open the file
                proc = subprocess.Popen(["nvim", os.path.join(self.wd, self.files[self.filesIndex])])
                proc.wait()
                stdscr.clear()
                stdscr.refresh()
            elif self.previewType == PreviewType.DIRECTORY:
                # Change directories into the file and update everything
                os.chdir(os.path.join(self.wd, self.files[self.filesIndex]))
                self.wd = os.getcwd()
                self.files = os.listdir(self.wd)
                self.files.sort()
                self.filesIndex = 0
        elif c == curses.KEY_BACKSPACE:
            # Go to parent dir
            os.chdir("../")
            self.wd = os.getcwd()
            self.files = os.listdir(self.wd)
            self.files.sort()
            self.filesIndex = 0
        elif c == curses.ascii.ESC:
            #print("Exiting...")
            #return True
            pass

        self.determinePreviewType()

        return False

    def render(self, left, right, stdscr):
        left.erase()
        right.erase()

        left.box()
        right.box()

        # Left screen (current directory)
        i = 1
        for f in self.files:
            col = curses.color_pair(1) if (i - 1) != self.filesIndex else curses.color_pair(2)
            left.addstr(i, 1, f, col)
            i = i + 1

        left.addstr(curses.LINES - 1, 1, self.wd)

        # Right screen (preview)
        if self.previewType == PreviewType.FILE:
            right.addstr(1, 1, f"File: {os.path.join(self.wd, self.files[self.filesIndex])}", curses.color_pair(1))
            i = 2
            for s in self.fileInfoStrs:
                right.addstr(i, 1, s, curses.color_pair(1))
                i = i + 1
        elif self.previewType == PreviewType.DIRECTORY:
            right.addstr(1, 1, f"Directory: {os.path.join(self.wd, self.files[self.filesIndex])}", curses.color_pair(1))
            i = 2
            for f in self.previewDirList:
                right.addstr(i, 1, f"\t> {f}", curses.color_pair(1))
                i = i + 1
        else:
            pass

        left.refresh()
        right.refresh()


def main(stdscr):
    r = Renderer()

    #stdscr.immedok(True)

    stdscr.clear()

    left = stdscr.subwin(curses.LINES, curses.COLS // 2 - 1, 0, 0)
    #left.immedok(True)

    right = stdscr.subwin(curses.LINES, curses.COLS // 2, 0, curses.COLS // 2 - 1)
    #right.immedok(True)

    r.render(left, right, stdscr) # Get something onto the screen

    while True:
        if r.update(stdscr):
            break

        r.render(left, right, stdscr)

if __name__ == "__main__":
    wrapper(main)
