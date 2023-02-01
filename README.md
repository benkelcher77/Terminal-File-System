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

Upon launching the file manager, you will be presented with two panels. The left-hand panel shows the contents of the directory that you are currently
in. This is the panel that you can interact with via the arrow keys (to scroll through files), the enter key (to open a file/directory), etc. A full list
of key bindings is available below. The right-hand panel provides some preview information of the file currently selected in the left-hand panel. If the
left-hand panel has selected a file, information about that file is presented including the owner, modification/access times, etc. If the left-hand panel
has selected a directory, the contents of that directory are presented.

## Searching

Typing the forward slash key ('/') will allow you to enter "search mode". In this mode, anything you type becomes a filter for the contents of the left-hand
panel. To exit search mode, hit the enter key.

## Key Bindings

| Key | Action |
| --- | ------ |
| q | If not in search mode, exit the file manager. |
| / | If not in search mode, enter search mode. |
| [Enter] | If not in search mode, access the selected file/directory. If in search mode, exit search mode. |
| [Backspace] | If not in search mode, access the parent directory. If in search mode, delete last character of search query. |
| [Up/Down] | Navigate through the items listed in the left-hand panel. |


## TODOs

- File type inference; opening files with correct program rather than just nvim for everything
    - Different file previews for different file types (eg. for sound files, display length; for text files, display wordcount etc.)
- Configuration settings in a .json or .ini file or similar
