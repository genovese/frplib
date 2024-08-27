# frplib

[![PyPI - Version](https://img.shields.io/pypi/v/frplib.svg)](https://pypi.org/project/frplib)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/frplib.svg)](https://pypi.org/project/frplib)

-----

**frplib** is a library and application that provides a platform for instruction
on probability theory and statistics. It was written and designed for use in
my class Stat 218 Probability Theory for Computer Scientists.
The ideas represented by this library are described in detail in the draft chapter
in [docs](docs/chapter0.pdf).

**Table of Contents**

- [Installation](#installation)
- [Quick Start](#quick-start)
- [User Guide](#user-guide)
- [License](#license)

## Installation

### Python installation is a prerequisite

`frplib` requires a modern Python installation to be installed, with `pip` included.
Versions 3.9+ will work, though 3.10+ is recommended. You can download and install
Python from [here](https://www.python.org/downloads/), though your system may
have a package manager (like homebrew, apt, yum) that makes this even more
convenient.

On Ubuntu linux, the following worked for me to get both Python and pip:

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11
sudo apt install python3.11-distutils
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
```

### Installing frplib

Once Python is installed, it should be sufficient to enter the following command
at a terminal/shell/powershell prompt:

```console
pip install frplib
```

This will install the library and install the `frp` script from the terminal
command line. On Mac OS and Linux, these scripts were installed in `/usr/local/bin`,
which should be available automatically.
On Windows, the location seems to depend on how you installed Python.
Try entering the command `frp --help` at the terminal prompt; if this displays
information about the market and playground subcommands, then you are ready to go.
See the next subsection if you are having trouble with this on Windows.

Because we will be updating the library frequently, you will need to update
your installation at times. This can be done with a single command:

```console
pip install --upgrade frplib
```


### Finding the Scripts on Windows

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
you can run the commnds with

```console
python -m frplib market
python -m frplib playground
python -m frplib --help
```

These work identically to the scripts and are just longer to type.

If you need to check your version to make sure you are up to date,
enter one of

```console
frp --version
python -m frplib --version
```

at the terminal prompt.


## Quick Start

There are two main sub-commands:

- `frp market` allows one to run demos simulating large batches of FRPs of arbitrary kind
   and to simulate the purchase of these batches to determine risk-neutral prices.
   
- `frp playground` is an enhanced Python REPL with frplib tools preloaded and special
   outputs, behaviours, and options to allow hands-on modeling with FRPs and kinds.

More Coming Soon...

## User Guide

Coming Soon...

## License

`frplib` is distributed under the terms of the
[GNU Affero General Public License](http://www.gnu.org/licenses/) license.

Copyright (C) Christopher R. Genovese
