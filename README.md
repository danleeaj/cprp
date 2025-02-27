# cprp

Lets say I have this codebase that I built a few months ago, and I completely forgot what it was about. I want to send it over to Claude, or ChatGPT, or Deepseek, but it's a tedious task to copy and paste every file in there, and even if I did, the LLM has no idea what my file structure is like. This is what this tool aims to address.

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

## sqlite-connect.py
// Contents of sqlite-connect.py

## models.py
// Contents of models.py

## main.py
// Contents of sqlite-connect.py
```

If you want to just see the tree, you can use the `--tree-only` flag.

```
cprp --tree-only /path/to/directory
```

Any additional flags and commands can be viewed through the `-h` or `--help` flag.

```
cprp -h
```

### Requirements

* pypercut (for copying to clipboard)
* typer (for command-line utility)
* pathspec (for gitignore parsing)

### Changelog

**v0.0.3**
* Initial release

**Work in progress**
* Ignore functionality
  * Custom ignores (an 'exclude.txt' that could be entered as an argument)
  * .gitignore ignores (look for a .gitignore in the base directory)
* Include functionality
  * Custom includes (only include a certain filetype, for example, only .py files)
* Individual files
  * Add a single file as an argument to copy its contents directly to clipboard
* Custom formatting
  * Instead of outputting to keyboard, allow outputting to file
  * Multiple format support (.json)