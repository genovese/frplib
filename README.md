# frplib

[![PyPI - Version](https://img.shields.io/pypi/v/frplib.svg)](https://pypi.org/project/frplib)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/frplib.svg)](https://pypi.org/project/frplib)

-----

**frplib** is a library and application that provides a platform for instruction
on probability theory and statistics. It was written and designed for use in
my class Stat 218 Probability Theory for Computer Scientists.
The ideas represented by this library are described in detail in Part I of
my textbook [Probability Explained](docs/probex.pdf), currently in draft
form.

**Table of Contents**

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Resources](#resources)
- [License](#license)

## Installation

### Python installation is a prerequisite

`frplib` requires a modern Python installation to be installed, with `pip` included.
Versions 3.9+ will work, though 3.10+ is recommended. You can download and install
Python from [python.org](https://www.python.org/downloads/), though there may
be more convenient methods on your system (e.g., package managers
like homebrew, apt, yum).
A helpful and comprehensive tutorial for installing Python on Mac, Windows, and Linux
is available [here](https://realpython.com/installing-python/).

Note that your system may already have Python 3 installed. If so, you need to check
the version. If the version is suitable, you can use it as is.
If not, you will have to either upgrade it, if possible, or install a stand-alone version
for your use.

To check what version of Python you have, if any, you will need to open
a Terminal window (Mac), a Powershell window (Windows), or a xterm/terminal window (Linux)
and invoke one of the following commands
```
    python3 --version
    python --version
    py --version
```
The first is most likely what is needed on Mac and Linux,
the second most likely on Windows, and the third on some Windows installations.
See the tutorial referenced above for details.
(You can open a powershell window on Windows
from the Start menu or via the Windows key.)

On Mac, you can use the official installer, obtainable from 
[python.org](https://www.python.org/downloads/),
or use the [homebrew](https://brew.sh/) package manager.
The latter is a generally useful tool for managing software on your Mac
that I recommend. But either approach is fine.

On Windows, you can use the official installer from
[python.org](https://www.python.org/downloads/)
or the Microsoft Store Python package.
(If the latter, make sure you select the package from
the Python Software Foundation, which is *free*.)

On Ubuntu linux, you can either build Python from source
or use a package manager like `apt`.
For exaple, 
the following worked for me to get both Python and pip (version 3.11):
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11
sudo apt install python3.11-distutils
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
```

### Installing frplib

Once Python is installed, take note of what the `python` and `pip` commands
are for your system.
They might be `python3` and `pip3`
or `python` and `pip`
or even a specific version like `python3.12` and `pip3.12`.
(On one Windows machine, I also got `py` and `pip`.)

Given that, installing `frplib` is straightforward
by entering the following command (with your `pip` command)
at the terminal/shell/powershell prompt:

```console
pip install frplib
```

This will install the library and install the `frp` script from the terminal
command line. On Mac OS and Linux, the script will be installed in `/usr/local/bin`,
which should be available automatically in your path.
See below for the extra steps that may be needed on Windows.

Because we may be updating the library frequently, you will need to update
your installation at times. This can be done with a single command:

```console
pip install --upgrade frplib
```

again use the `pip` command that is appropriate to your installation.

Note that as described so far, we are installing the `frplib` globally,
so that you can access it anywhere.
You can also choose to install the library in a virtual environment
if you prefer.

#### Accessing the `frp` Script on Windows

On Windows, the location seems to depend on how you installed Python.
Try entering the command `frp --help` at the terminal prompt; if this displays
information about the market and playground subcommands, then you are ready to go.
See the next subsection if you are having trouble with this on Windows.

ATTN

While the scripts are not strictly necessary (see below), they are convenient.
If your system is not finding the scripts, you can forgo using them (there are
alternatives) or find the scripts and add them to the search list that the
system uses to find executable apps.  Results may vary among powershell,
wsl, and git-bash. The latter two should be easier, and the comments here
focus on powershell, which seems to be more popular among windows user.


In powershell (running as admin), you can enter the command

```
where python
```

to find the folder in which python is installed.
Substitute that path for [python-folder] in
```
python [python-folder]\Tools\scripts\win_add2path.py
```
and restart your powershell/terminal. The scripts should now be available.


### Running frp

The simplest way to run the app is to enter either `frp market` or `frp playground`
at the terminal command line prompt. You can get overview help by entering
`frp --help`. Further help is available from within the app. Use the
`help.` command in the market and `info()` in the playground.

The previous paragraph assumes that the scripts are available. If not,
you can always run the commands with

```console
python -m frplib market
python -m frplib playground
python -m frplib --help
```

using the `python` command for your installation.
These work identically to the scripts and are just longer to type.

If you need to check your version to make sure you are up to date,
enter one of

```console
frp --version
python -m frplib --version
```

at the terminal/shell/powershell prompt.


## Quick Start

There are two main sub-commands for interactive environments:

- `frp market` allows one to run demos simulating large batches of FRPs of arbitrary kind
   and to simulate the purchase of these batches to determine risk-neutral prices.
   
- `frp playground` is an enhanced Python REPL with frplib tools preloaded and special
   outputs, behaviours, and options to allow hands-on modeling with FRPs and kinds.

We will spend most of our time in the playground, which also offers functions
to reproduce market functionality.

In addition, you can use `frplib` functions and objects
directly in your Python code. Whereas the playground automatically
imports the commonly-used functions for easy use, in code, you
need to import the functions, objects, and data that you need
from various `frplib.*` modules.

Here is an example of what such imports might look like:

```python3
    from frplib.frps       import FRP, frp, conditional_frp
    from frplib.kinds      import Kind, kind, constant, either, uniform
    from frplib.statistics import statistic, __, Proj, Sum
```

imports useful objects for work FRPs, Kinds, and Statistics.

Entering `info('modules')` in the playground will give you
a list of available modules and a brief description.
Entering `info('object-index)` gives a table of the primary
objects and functions in `frplib` and the modules they
are found in.


## Resources

Built-in help `info` (specific to the playground) and `help` (Python built-in).

[Probability Explained](docs/probex.pdf)

The frplib [Cookbook](docs/frplib-cookbook.pdf) offers guidance on common tasks.

The frplib [Cheatsheet](docs/frplib-cheatsheet.pdf) provides a short
summary of the common methods, factories, combinators, and actions.


## License

`frplib` is distributed under the terms of the
[GNU Affero General Public License](http://www.gnu.org/licenses/) license.

Copyright (C) Christopher R. Genovese
