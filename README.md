# frplib

[![PyPI - Version](https://img.shields.io/pypi/v/frplib.svg?cacheSeconds=300)](https://pypi.org/project/frplib)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/frplib.svg?cacheSeconds=300)](https://pypi.org/project/frplib)

-----

**frplib** is a library and application that provides a platform for
probabilistic computing. It is designed for teaching probability
theory and statistics, particularly for my course Stat 218
Probability Theory for Computer Scientists at Carnegie Mellon
University. The ideas represented by this library are described in
detail in Part I of my textbook [Probability Explained](src/frplib/data/probex.pdf), 
which is nearing completion. The software also has modules that let
you work through and experiment with every significant example in
the book.

**frplib** is built on top of [Python](https://www.python.org) and
provides both a library for use in your Python code and an
interactive environment for simulating and analyzing random systems.
It focuses primarily on *finite* random systems as a means to
building the central concepts and tools fo probability theory.

ATTN
Two principle abstractions underlie the software.
An *FRP* (Fixed Random Payoff) is a device that represents


**Table of Contents**

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Resources](#resources)
- [License](#license)

## Installation

### Python installation is a prerequisite

`frplib` requires **Python 3.10 or later** with `pip` included. 
Python 3.10 through 3.14 are officially supported.
You can download and install Python from
[python.org](https://www.python.org/downloads/),
though there may be more convenient methods on your system
(e.g., package managers like homebrew, apt, yum).
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
The first is most likely what is needed on Mac and Linux. On Windows, try `py` first
(see [Windows notes](#windows-notes) below for why it's the more reliable choice), then
`python`.
(You can open a powershell window on Windows
from the Start menu or via the Windows key.)

On Mac, you can use the official installer, obtainable from
[python.org](https://www.python.org/downloads/),
or use the [homebrew](https://brew.sh/) package manager.
The latter is a generally useful tool for managing software on your
Mac that I highly recommend, but see the [note](#note-on-pip-install) on `pip install`
restrictions below, which apply to Homebrew's Python.

On Windows, you can use the official installer from
[python.org](https://www.python.org/downloads/)
or the Microsoft Store Python package.
(If the latter, make sure you select the package from
the Python Software Foundation, which is *free*.)
See [Windows notes](#windows-notes) below — the process is easier than it used to be.

On Ubuntu or other Debian-based Linux, a stock `apt install python3` already satisfies
the 3.10+ requirement on any currently supported release (Ubuntu 22.04+, Debian 12+). If
you're on an older release whose system Python is too old, you can add a newer version
via the deadsnakes PPA, e.g. for Python 3.12:

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv
python3.12 -m ensurepip --upgrade
```

(The old `curl .../get-pip.py` and `python3.x-distutils` steps are no longer needed —
`ensurepip`, bundled with Python itself, takes care of it, and `distutils` no longer
exists as of Python 3.12.)

While you're at it, `sudo apt install pipx` is worth doing now — see below.

### Other software worth installing (while you're at it)

TL;DR A good terminal emulator, a modern pager like `less`, and the
Python package installer `pipx` are highly worth installing.


The `frplib` playground offers a nicer experience with a modern terminal emulator
that can display rich text, colors, and formatting
and with a configurable pager. A modern terminal app
makes it super easy to enter and edit multi-line code in the playground.

On Mac, the built-in Terminal app does fine, but I suggest
the fully featured [Iterm2](https://iterm2.com/), which is easy to install
and highly performant.

On Linux, most available terminal emulators have the functionality we need,
and less will be installed by default in most distributions.

The VS Code terminal also supports all we need.

On Windows, I highly suggest installing the
[Windows Terminal](https://learn.microsoft.com/en-us/windows/terminal/).
It offers a vastly better command-line experience compared to the classic Powershell/cmd
console. It is small, free and can be installed
from either the previous link or the Microsoft Store.

For Windows users, [jftuga/less-Windows](https://github.com/jftuga/less-Windows)
is a standalone GNU version of the pager `less` that is compiled for
Windows 10/11 with no dependencies, and which supports these
capabilities. It's packaged for winget, so it can be installed with:
```
  winget install jftuga.less
```

Finally, on all platforms, the [`pipx`](https://pipx.pypa.io/)` Python installer
s a valuable addition to your toolkit, especially essential for certain
Python installations. See this [note](#note-on-pip-install).

### Two ways to use `frplib`, and why it matters

`frplib` is both a command-line app (the `frp` script, giving you `market` and
`playground`) and a library you can `import` in your own code (e.g., for homework or
your own experiments). **Plan on setting up both**. For the course, you need to
be able to 

- Run **`frp market` / `frp playground` from anywhere**, which you get when installing with
  **pipx**, as described below. It keeps `frplib` in its own isolated environment and puts only the
  `frp` command on your path.
- **Import `frplib` modules in your own scripts or notebooks**, which requires a separate
  **virtual environment**, as described below. The isolation pipx gives makes it less
  convenient to use its environment in your own code.

The two installs are independent and don't conflict with each other, so just do both,
one after the other, as below. (If you're sure you only need one of the two — say, you're
not planning to write any code that imports `frplib` modules — then it's fine to skip the
other section.)

#### Note on pip install

Recent changes to Python ([PEP 668](https://peps.python.org/pep-0668/))
impact global installation of packages for OS-managed Pythons. On
Linux distributions and on Homebrew's Python for Macs, a plain `pip
install frplib` will likely fail with an error mentioning
`externally-managed-environment`. This is because your OS package
manager (`apt`, `brew`, ...) manages that Python installation, and
pip refuses to modify it directly, even with `--user`. **Don't** use
the `--break-system-packages` flag some error messages suggest; it
defeats the protection PEP 668 is there to provide. Use `pipx` or a
venv instead. Both sidestep the restriction entirely because neither
touches the OS-managed Python directly.

If you installed Python yourself from
[python.org](https://www.python.org/downloads/), or via `pyenv`,
this restriction does not apply, and a plain `pip install` should
work fine.

### Installing the app with pipx (recommended for `frp`)

[`pipx`](https://pipx.pypa.io/) installs a Python application into its own private
environment and exposes just its command(s) on your `PATH` — exactly what you want for
a CLI tool like `frp`, and it works the same way whether or not your Python is
externally managed.

Install pipx once, using whichever of these matches your setup:

```console
# Debian/Ubuntu, or Mac with Homebrew
sudo apt install pipx      # or: brew install pipx
pipx ensurepath

# Any Python from python.org, or pyenv (Mac, Windows, Linux)
python3 -m pip install --user pipx     # use `py` in place of `python3` on Windows
python3 -m pipx ensurepath
```

The `ensurepath` adds pipx's own bin directory to your `PATH`. **Open a new terminal window**
for that change to take effect, then install `frplib`:

```console
pipx install frplib
```

To update `frplib` later:
```console
pipx upgrade frplib
```
Either way, you should now be able to run:

```console
frp --help
```

### Installing the library in a virtual environment

To import `frplib` modules in your own code, the idiomatic Python way
is install it into a virtual environment (called a venv for short)
in your current project, rather than system wide.
For example, you can create such a venv in the folder containing
your course work, and then activate it when working with `frplib`.

The standard workflow looks like the following.
In a terminal, change to the folder where you want to work.

  1. Create the venv. *You only need to do this once.
  ```console
  python3 -m venv myproject-env         # create the venv (use `py` on Windows)
  ```
  Give the venv a name that is meaningful to you. (`myproject-env` is just an example.)

  2. Activate the venv. *Do this whenever you want to work the library*.
     The command differs by shell:
     ```console
     source myproject-env/bin/activate      # Mac/Linux, bash or zsh
     myproject-env\Scripts\activate         # Windows, PowerShell or cmd
     ```
     Again, this assumes you are in your project directory/folder when
     you issue the commands.

     Your prompt should now show `(myproject-env)`. Install `frplib` into it:

  3. Install any packages you want to use when this environment is active.
     *Do this as needed*. The environment remembers what you install.
     ```console
     pip install frplib
     ```
And now, you can import `frplib` modules in scripts you run from this same terminal, or select
this venv as the interpreter/kernel in your editor or Jupyter. When you're done,
the `deactivate` command closes it. You'll need to `activate` again each time you open a new
terminal to keep working with `frplib`.

> **Tip:** rather than making a fresh venv per assignment, it's often easier to keep one
> standing "baseline" venv with `frplib` (and any other libraries you use regularly)
> installed, and just `activate` it whenever you want to do casual, interactive work.
> I keep such venvs in `~/.local/venvs` to have a standard location, but you can
> put them where you like.
>
> When working on larger projects, it is recommended to use a dedicated venv
> for the project and all its dependencies to make your build and runs reproducible.

### Windows notes

If you already have Python installed on Windows from earlier (e.g., a class, a
tutorial, it came with something else), you don't need to reinstall it — everything
below works with what you already have as long as it meets the version requirement.

Two important steps for Windows users:

1. **Install [Windows Terminal](https://learn.microsoft.com/en-us/windows/terminal/) first.**
   It offers a much better command-line experience than the classic Powershell/cmd
   console (including multi-line editing, tabs, sane copy-paste, resizing that doesn't break).
   It is small, it is free, and it is easy to install, either from the previous link
   or from the Microsoft Store. Everything below assumes you're
   working in the Windows Terminal (or an equivalent), in a Powershell tab.

2. **Use `py` to invoke Python** (Try `py --version` now!)
   The python.org installer puts the `py` launcher in `C:\Windows`, so
   it's *always* on your `PATH`, regardless of whether you checked
   "Add python.exe to PATH" during setup. Using `python` / `python3`
   will only work if that box was checked. Because it works no
   matter how your Python was installed or configured `py` is the
   more reliable choice.

   The one exception is the Microsoft Store Python package, which has no `py`
   launcher — use `python` instead, which the Store puts on your `PATH` for you. (If
   `py --version` just failed, this is almost certainly your situation.) Store Python
   has one more quirk worth knowing about, once we get to installing `frp` below.

Given the above, the recommended route for getting the `frp` app on Windows is:
```console
py -m pip install --user pipx
py -m pipx ensurepath
```
Close and reopen your terminal, and then do:
```console
pipx install frplib
frp --help
```
This works cleanly even for Microsoft Store Python, which, unlike the python.org
installer, puts python on `PATH` but not in the Scripts folder where pip-installed
commands like frp land. The `pipx ensurepath` finds and adds that folder for you, so you
don't need to hunt for it yourself.

#### Fallback option: installing with plain pip and fixing PATH manually

If you'd rather not use pipx — e.g., you did a plain `pip install frplib` and `frp` isn't
found at the terminal — you can add the right folder to `PATH` yourself. Start a
Powershell window with administrator privileges (search for Powershell in the Start
menu, right-click, "Run as administrator").

First, find where your Python packages are installed. Enter (using your `py`/`python`
command):
```
py -m site
```
This shows a couple of file paths, `USER_BASE` and `USER_SITE` — you want the former.
For instance, this might be something like `C:\Program Files\Python312`
or `C:\Users\yourname\AppData\Python\Python312`.
Whatever it is, you want the `Scripts` subfolder of that directory.

A slightly less clean alternative is to enter
```
pip show frplib
```
This will spit out some text; look for a line that starts with `Location:`,
which will contain another path that looks like
`C:\Program Files\Python312\Lib\site-packages`.
You want the part of this without the `\Lib\site-packages`,
which we will call your `USER_BASE` below.

Next, check that the `Scripts` folder exists and has the
`frp` script in it. Enter at the powershell prompt for instance
```
dir C:\Users\yourname\AppData\Python\Python312\Scripts
```
using your `USER_BASE` instead. You should see an `frp` entry in the
list. The pathname that you used in this command, we will write
as `C:\...\Scripts` but you should *replace it with the one you just used* in what follows.
If you do not see a `frp` entry, make sure that you are
using the same version of python with which you installed `frplib`.

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
Finally, check the new path with
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
come in for help. Python itself also offers a tool to try, if all else fails.
Once you have located the Python folder as described above, you can substitute
that path for [python-folder] in the following command
```
python [python-folder]\Tools\scripts\win_add2path.py
```
and restart your powershell/terminal. The scripts should now be available.

### Running frp

The simplest way to run the `frp` app is to enter either `frp playground` or `frp market` 
at the terminal command line prompt. This uses the script that was installed
by pipx (or by pip, if it's on your path). You can get overview help by entering
`frp --help`. Further help is available from within the app. Use the
`help.` command in the market and `info()` in the playground, as described below.

If you need to check your version to make sure you are up to date,
enter one of
```console
frp --version
```
at the terminal/shell/powershell prompt.

You can run `frp playground --dark` to start in a dark theme.
You can set dark mode as a persistent preference so that you do not
need the `--dark`.
See the info topic *Configuring the Playground Environment*
for how to do this.

#### If `frp` is not on your path...

The previous paragraph assumes that the `frp` script is on your path.
If not, you can always run the commands with
```console
python -m frplib playground
python -m frplib market
python -m frplib --help
```
using the `python` command for your installation (`py` on Windows).
This should be run after activating
whichever venv you installed `frplib` into. These work identically to the
script and are just longer to type.

If you need to check your version to make sure you are up to date,
enter one of
```console
python -m frplib --version
```
at the terminal/shell/powershell prompt.


## Quick Start

There are two main sub-commands for interactive environments:

- `frp playground` is an enhanced Python REPL with frplib tools preloaded and special
   outputs, behaviours, and options to allow hands-on modeling with FRPs and kinds.

- `frp market` allows one to run demos simulating large batches of FRPs of arbitrary kind
   and to simulate the purchase of these batches to determine risk-neutral prices.
   
We will spend most of our time in the playground, which also offers functions
to reproduce market functionality.

Both commands provide an environment in which you can enter commands or code,
move back and forth (e.g., with arrow keys or Control-/Control-n) to edit lines and to recall
earlier commands in your history.  You can also search backward in the
history with Control-r, which recalls matching previous commands and lets
you select from them.
You can also see the entire history by hitting the F3 function key.
In the playground, you can use any `frplib` or Python construct. Python code works
as in the Python repl. If you enter multiline constructs, like function definitions,
the playground lets you move around and edit your input. Enter the multiline code
by creating a blank line and hitting return.
Use `quit()` to exit the playground and `quit.` to exit the market.
See the info topic *Using the Playground* for more.

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
Entering `info('object-index')` gives a table of the primary
objects and functions in `frplib` and the modules they
are found in.

For quick scripts, you can import any object available in the playground
from the `frplib.playground` module,
e.g., `from frplib.playground import *`.


## Resources

There are a variety of resources to help you learn how to use `frplib`,
both interactively and in code.

+ The key ideas and lots of examples are given in Part I of the textbook
  [Probability Explained](src/frplib/data/probex.pdf).
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
  You can view or grab the PDF for the book with the `textbook()` command
  in the playground.

+ The frplib [Cookbook](src/frplib/data/frplib-cookbook.pdf) offers recipes for common tasks,
  on which you can build.

  You can view or grab the PDF for the cookbook with the `cookbook()` command
  in the playground.

+ The frplib [Cheatsheet](src/frplib/data/frplib-cheatsheet.pdf) provides a short
  summary of the common methods, factories, combinators, and actions.

  You can view or grab the PDF for the cheatsheet with the `cheatsheet()` command
  in the playground.

And in addition, there is a built-in help system in the playground and the market.
In the market, enter `help.` including the period.  This will summarize the
available help commands, which are fairly straightforward.

In the playground, you can access help in (at least) five ways.
First, the playground function `info` is an interface to built-in documention.
Enter `info()` at the prompt to start an interactive search through the hiearchcy
of info documents.
Second, for any topic, you pass that as a string to `info` to see the
documentation on that topic.
(Nested topics are separated by `::`.)
If the topic is a match, its info document will be displayed;
otherwise, it starts the search with the given string as a fuzzy search key.
Third, most `frplib` will display information about themselves
when passed to `info`,
and many like Statistics or factories will display information about themselves
when you print them.
For instance,
```
playground> Sum
A Monoidal Statistic 'Sum' that returns the sum of all the components of the given value. It expects a tuple and returns a scalar.
```
Fourth, the playground installs a custom version of Python's built-in `help` command.
For many `frplib` objects this will display their info documents
and will otherwise delegate to the built-in help.
To force the built-in help, pass `True` as the second argument, e.g.,
`help(obj, True)`.
Finally, the playground will show you the signatures
of functions as you type (when you enter the opening parenthis).
It will also give you dynamic completion of names as you type
them, making it easier to locate the function or data you want to use.


## License

`frplib` is distributed under the terms of the
[GNU Affero General Public License](http://www.gnu.org/licenses/) license.

Copyright (C) Christopher R. Genovese
