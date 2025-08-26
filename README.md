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

While having a short-hand for the `frp` script is not strictly
necessary, it is very convenient. If your system is not finding the
scripts, you can forgo using them or find the scripts and add them
to the search list that the system uses to find executable apps, as
described below. Results may vary among powershell, wsl, and
git-bash. The latter two should be easier, and the comments here
focus on powershell, which seems to be more popular among windows
user.

On Windows, the location of the `frp` script depends on how you installed Python.
To make this easy to use, you want to ensure that Powershell will be able to find
it without any extra effort on your part.

Start a Powershell window with administrator privileges.
This should be an option in the Start menu when you search for Powershell.

Before proceeding further, try entering the command 
```
frp --help
``` 
at the powershell prompt. 
If this displays
information about the market and playground subcommands, then 
no further action is needed.
If instead it gives an error message, we need to tell powershell how to find
`frp`. We will do that by updating your `PATH` environment variable.

First, we need to find where your python packages are installed.
There are two approaches to try, both should work fine.
At the prompt, enter
```
python -m site
```
again using your python command (e.g., `python3`).
This should show to file paths, `USER_BASE` and `USER_SITE`,
you want the former.
For instance, this might be something like `C:\Program Files\Python312`
or `C:\Users\yourname\AppData\Python\Python312`.
Whatever it is, you want the `Scripts` subfolder of that directory.

A slightly less clean alternative is to enter
```
pip show frplib
```
This will spit out some text, look for a line that starts with `Location:`,
which will contain another path that looks like
`C:\Program Files\Python312\Lib\site-packages`.
You want the part of this without the `\Lib\site-packages`,
which we will call your `USER_BASE` below.

Next, we want to check that the `Scripts` folder exists and has the
`frp` script in it.
Enter at the powershell prompt for instance
```
dir C:\Users\yourname\AppData\Python\Python312\Scripts
```
using your `USER_BASE` instead. You should see an `frp` entry in the
list. The pathname that you used in this command, we will write
as `C:\...\Scripts` but you should *replace it with the one you just used* in what follows.
If you do not see a `frp` entry, in this `dir` command,
make sure that you are using the same version of python with which you installed
`frplib`. If so, it might be a good idea to come ask for help.

Given that you see the `frp` script in that `dir` command, we will now
add it to the path that powershell searches for programs.
For this, it is important that you started powershell with Administrator privileges.
As a check against any problems, we will print out the current path with
```
$env:Path
```
for comparison later, so keep this in view.
Next, enter the following, **being sure to include the `;` before the scripts path** as below
*and* replacing `C:\...\Scripts` with **your actual path**:
```
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\...\Scripts", "Machine")
```
Finally, check that the new path with
```
[Environment]::GetEnvironmentVariable("Path", "Machine")
```
You should see the Scripts folder you just added at the end,
and the rest should look like what you had before.

You have to restart your Powershell for the changes in your path
to take effect. So start a new Powershell window and you should now
be able to run `frp`. Try:
```
frp playground
```
to check.

If you have any questions or troubles with this, do not hesitate to
come in for help. Sometimes Python itself offers a tool to do this,
if all else fails. Once you have located the Python folder as
described above, you can substitute that path for [python-folder] in
the following command
```
python [python-folder]\Tools\scripts\win_add2path.py
```
and restart your powershell/terminal. The scripts should now be available.


### Running frp

The simplest way to run the `frp` app is to enter either `frp market` or `frp playground`
at the terminal command line prompt. This uses the script that was installed
with `frplib`. You can get overview help by entering
`frp --help`. Further help is available from within the app. Use the
`help.` command in the market and `info()` in the playground, as described below.

The previous paragraph assumes that the `frp` script is in your path. 
If not, you can always run the commands with

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

Both commands provide an environment in which you can enter commands or code,
move back and forth (e.g., with arrow keys or Control-/Control-n) to edit lines and to recall
earlier commands in your history.  You can also search backward in the
history with Control-r, which recalls matching previous commands and lets
you select from them.
You can also see the entire history by hitting the F3 function key.
In the playground, you can any `frplib` or Python construct. Python code works
as in the Python repl. If you enter multiline constructs, like function definitions,
the playground lets you move around and edit your input. Enter the multiline code
by creating a blank line and hitting return.
Use `quit()` to exit the playground and `quit.` to exit the market.

In addition to the interactive environments, you can use `frplib` functions and objects
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

There are a variety of resources to help you learn how to use `frplib`,
both interactively and in code.
The main user guide is in Part I of the textbook
[Probability Explained](docs/probex.pdf).
This develops all the key concepts and has loads of examples.
All the major examples in the book have associated modules
in the `frplib.examples` submodule.
For example:
```
from frplib.examples.monty_hall import (
    door_with_prize, chosen_door, got_prize_door_initially
)
```
imports the listed data and functions associated with the Monty Hall example
in Chapter 1. 
Instead of listing particular items,
you can load all the exported symbols in the module with
```
from frplib.examples.monty_hall import *
```

The frplib [Cookbook](docs/frplib-cookbook.pdf) offers recipes for common tasks,
on which you can build.

The frplib [Cheatsheet](docs/frplib-cheatsheet.pdf) provides a short
summary of the common methods, factories, combinators, and actions.

And in addition, there is a built-in help system in the market and in the playground.
In the market, enter `help.` including the period.  This will summarize the
available help commands, which are fairly straightforward.

In the playground, you can access help in four ways.
The playground function `info` is an interface to built-in documention.
Enter `info()` at the prompt to see an overview of available topics.
For any topic, you pass that as a string to `info` to see the
documentation on that topic.
Nested topics are separated by `::`. For instance, `info('kinds::factories::uniform')`
gives information on the `uniform` Kind factory, which is three levels deep.
A few special topics are `info('overview')` for some general orientation;
`info('modules')` lists all the `frplib` modules with brief descriptions of each;
and `info('object-index')` lists all the major `frplib` functions
and objects and the module to which they belong.

Second, some objects, like Statistics, will display information about themselves
when you print them.
For instance,
```
playground> Sum
A Monoidal Statistic 'sum' that returns the sum of all the components of the given value. It expects a tuple and returns a scalar.
```
Also, Python has a built-in `help` command
that will provide useful information about `frplib` objects,
especially the functions.
The help on the functions shows how they are used
and what they return.

Finally, the playground will show you the signatures
of functions as you type (when you enter the opening parenthis).
It will also give you dynamic completion of names as you type
them, making it easier to locate the function or data you want to use.


You can 
Built-in help `info` (specific to the playground) and `help` (Python built-in).



The frplib [Cookbook](docs/frplib-cookbook.pdf) offers guidance on common tasks.



## License

`frplib` is distributed under the terms of the
[GNU Affero General Public License](http://www.gnu.org/licenses/) license.

Copyright (C) Christopher R. Genovese
