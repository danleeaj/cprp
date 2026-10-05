# cprp

Let's say I have this codebase that I built a few months ago, and I completely forgot what it was about. I want to send it over to Claude, ChatGPT, or DeepSeek, but it's tedious to copy and paste every file, and even if I did, the LLM would have no idea what my file structure looks like. This is what this tool aims to address.

cprp (or copyrepo) is a command-line tool designed to help users easily convert a directory into a LLM-friendly format.

This program recursively searches through a specified directory and outputs, _directly to the clipboard_, a directory structure, as well as the content of any non-directory files.

### Installation

```
pip install cprp
```

### Usage

```
cprp /path/to/directory
```

This outputs the following directly to the clipboard, as well as in the terminal:

```
# DIRECTORY STRUCTURE

my-project/
|-- database/
|   |-- sqlite-connect.py
|  `-- models.py
`-- main.py

## database/sqlite-connect.py
// Contents of sqlite-connect.py

## database/models.py
// Contents of models.py

## main.py
// Contents of main.py
```

If you want to just see the tree, you can use the `--tree-only` flag.

```
cprp --tree-only /path/to/directory
```

Any additional flags and commands can be viewed through the `-h` or `--help` flag.

```
cprp -h
```

### Ignore behavior

Directory entries are processed alphabetically so the generated output is stable between runs. cprp applies its packaged default exclusions, such as `.git`, `.venv`, and Python cache files, followed by the `.gitignore` in the root of the directory being scanned. Ignore patterns are matched relative to that root directory.

Only the root `.gitignore` is loaded currently; discovering additional `.gitignore` files in nested directories remains planned work.

File-content headings use paths relative to the scanned directory, such as `## database/models.py`, so files with the same name in different directories remain distinguishable.

### Requirements

* pyperclip (for copying to clipboard)
* typer (for command-line utility)
* pathspec (for gitignore parsing)

### Changelog

**v0.0.4**
* Fixed a bug where errors were printed in the wrong format.
* Fixed a bug where invalid directories still resulted in output being printed.
* Added deterministic output and support for the scanned directory's root `.gitignore`.
* Changed file-content headings to use root-relative paths.

**v0.0.3**
* Initial release

**Work in progress**
* Ignore functionality
  * Custom ignores (an 'exclude.txt' that could be entered as an argument)
  * Discover `.gitignore` files in nested directories
* Include functionality
  * Custom includes (only include a certain filetype, for example, only .py files)
* Individual files
  * Add a single file as an argument to copy its contents directly to clipboard
* Custom formatting
  * Instead of outputting to keyboard, allow outputting to file
  * Multiple format support (.json)
