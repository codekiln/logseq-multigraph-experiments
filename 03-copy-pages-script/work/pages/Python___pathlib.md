logseq-remote-page:: true
logseq-remote-page-link:: logseq://graph/python?page=Python%2Fpathlib

title:: Python/pathlib

- ## [pathlib — Object-oriented filesystem paths — Python 3.9.12 documentation](https://docs.python.org/3.9/library/pathlib.html#pathlib.PurePath)
	- Path classes are divided between [pure paths](#pure-paths), which provide purely computational operations without I/O, and [concrete paths](#concrete-paths), which inherit from pure paths but also provide I/O operations.
	- ![pathlib inheritance diagram](https://docs.python.org/3.9/_images/pathlib-inheritance.png)
	- If you’ve never used this module before or just aren’t sure which class is right for your task, [`Path`](#pathlib.Path "pathlib.Path") is most likely what you need. It instantiates a [concrete path](#concrete-paths) for the platform the code is running on.
	- Pure paths are useful in some special cases; for example:
	- If you want to manipulate Windows paths on a Unix machine (or vice versa). You cannot instantiate a [`WindowsPath`](#pathlib.WindowsPath "pathlib.WindowsPath") when running on Unix, but you can instantiate [`PureWindowsPath`](#pathlib.PureWindowsPath "pathlib.PureWindowsPath").
	- You want to make sure that your code only manipulates paths without actually accessing the OS.
	- See also
	- [**PEP 428**](https://www.python.org/dev/peps/pep-0428): The pathlib module – object-oriented filesystem paths.
- ## Notes
	- `Path(a, b, c)` produces `a/b/c` or `a\b\c` depending on os
	-