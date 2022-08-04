# Terminal-File-System

A small terminal file explorer for Linux. Written in Python Curses. Inspired by Ranger, Vim, and other terminal file explorers.

## Getting Started

To get started with this file manager, you must add the `fm.sh` and `fm.py` files to your PATH, and add the following code to your `.bashrc` file:
```
fm() {
    . fm.sh
}
```
If this is done correctly, then the file manager can be launched in the current directory simply by running `fm`. 

## TODOs

- File type inference; opening files with correct program rather than just nvim for everything
