# Using the Playground

The FRP playground is an interactive environment for building and
analyzing random systems. It runs a custom Python REPL
(Read-Eval-Print Loop) that is fully loaded with frplib functions
and tools and is designed to provide nice displays of the various
objects and results you produce.

The playground is invoked from the command line, typically by the command
```
    frp playground
```
After an introductory message, you will see the playground prompt `playground> `.
You enter expressions at the prompt and results of those expressions are
displayed afterwards.

The playground provides special display and error reporting to make
the experience more friendly. It also offers tools for navigating
your history and inspecting earlier results. The playground offers a
variety of configuration options; see the info topic
*Configuring the Playground Environment*.

## Entering Code in the Playground

Any valid Python code can be entered at the prompt, both expressions
and statements, including function and class definitions. Hitting
enter at the end of the line will submit and run the code,
displaying the result directly below.

When the code extends over multiple lines, lines after the first
will show a *continuation prompt* `...> ` to indicate this. Hitting
enter on the *last* line of the input or hitting Meta-enter (e.g.,
ESC then enter) with the cursor anywhere will run your code and
display the result. Before submitting, you can navigate through and
edit your code as described in the next section.

This works smoothly and conveniently, but there is one important
proviso. Modern terminal emulators including
[iTerm2](https://iterm2.com/), xterm, and the builtin Terminal on Macs;
[Windows Terminal](https://learn.microsoft.com/en-us/windows/terminal/) on Windows;
most terminal emulators on Linux; and the VS Code terminal support
something called "bracketed paste mode". If you run the playground
from these terminals, you can enter multiline code directly as
described above, either by typing or pasting. It will auto-indent
your code (or preserve indentation) and will allow you to navigate
through the code as described in the next section.

If when you enter multi-line code in playground, you see each line
entered separately, then your terminal either does not support
bracketed paste mode or it is turned off. In this case, you can hit
the function key F6 to turn on the playgrounds Paste Mode. Whether
Paste mode is on will show in the tool bar. Paste mode allows
multi-line input even in a terminal without bracketed paste mode.
Hitting F6 again will turn Paste mode off.

For Windows users, it is highly recommended that you
install the [Windows Terminal](https://learn.microsoft.com/en-us/windows/terminal/)
in which to run the playground.

## Navigating and History

In the playground, you can navigate using either arrow keys
or using C-n/C-p/C-f/C-b for down/up/right/left. (C- means hold the control
key and then hit the following key, so C-n means hold control and hit n.)

When you have entered code at the prompt but not yet submitted it, you can
navigate through your code and edit it as you like.
This includes multi-line code.

If you move up and down at the prompt (past your code), you will instead navigate
through your command history. You can move through previous commands
and hit enter to put that command at the prompt for editing. (Another enter is needed
to submit it.) This includes multi-line commands.

Sometimes when entering something at the prompt one hits up past the
code and into the history. Worry not, what you had entered is not
lost. Just move down again and it will be there.

You can also *search* through the history with C-r. When you hit
C-r, a search prompt appears. Type a pattern from a previous
command, and the playground will display the previous command
matching that pattern. You can continue to type (even backspace to
delete) to refine the pattern. Once you have the pattern you want,
you can hit C-r and C-s to search backward and forward for other
commands that match. Hitting enter will put that command at the
prompt ready for editing and submission. This works with multi-line
commands as well.

If you hit the function key F3, you go to a history screen where you
see -- and can navigate through -- all your previous commands.
Navigate to a command and hit space to mark it. Marked commands are
listed on the right half of the screen. Hitting space on a marked
line will unmark it, and remove it from the right side of the
screen. When you have commands marked that you like, hit enter, and
these commands will appear at the playground prompt, ready for
editing and submission.

Your history from all your sessions is saved in a history file.
On Mac and Linux, the history file is `~/.frp-playground-history`.
On windows, it is the current users profile directory,
which is typically `C:\Users\<Username>`,
so look in in `C:\Users\<Username>\.frp-playground-history`.

## Getting the Results of Previous Commands

The playground also remembers the results of every command.
For command number N (e.g., 17), the variable _N (e.g., _17)
holds the result value.

By default, the current command number is shown in brackets
on the left side of the toolbar (after "FRP Playground").
But if you use previous results frequently,
you may find it more convenient to include the command
number in the playground prompt.
See the info topic *Configuring the Playground Environment*
for how to do this.

## The Status Bar

By default, a status bar is displayed at the bottom of the screen.
This provides some information about the environment
(e.g., command number, shortcut style, mode)
and cues for function keys.

The function key F2 will open a menu that lets you configure various
additional features of the display. Navigate to the line you
want to change with up and down arrow keys
and use the right and left arrow keys to change the options,
hitting enter to save and exit.
Several features here that might be of interest include:

+ Displaying line number on multi-line input
+ Changing the code highlighting theme
+ Cursor style
+ Generating Auto-suggestions as you type
+ Enabling a pager for long output

and more.

## Getting Help

The playground has a built-in help system that is accessed through the function `info`.
Calling `info()` at the prompt opens an interactive search system over a hierarchical
collection of topics. You can navigate the search in two ways. First, you can move to
to an option (up and down arrow keys or C-n and C-p) and select it with Enter.
Second, you can type to do a fuzzy search; `info` will match all topics at the current
level that have the same characters you type in the same order (not necessarily adjacent).
Fuzzy search is case insensitive. Some nodes in the `info` hierarchy have *both*
associated info and child nodes with more specific info. In those cases, the current
node will be included on the list of options at the current level.

If you call `info` with a string, there are two possible outcomes.
If the string is an exact match for a topic (the topic labels along
the path in the info tree joined by '::'), `info` will open the info
document for that topic. Otherwise, it will open the interactive
search using your string as the intial fuzzy search key.

You can also call `info` on frply *objects*, which will display the info
document on the given object, if one exists, or delegate to the built-in
Python `help` otherwise.

The playground also includes a custom version of Python's built-in `help`.
When you call it on an frplib object, it will behave like `info`
by default if there is an associated info document or the built-in `help`
otherwise. You can force the latter by adding a second argument of `True`,
i.e., `help(obj, True)`.

The playground also includes functions `cookbook()`, `cheatsheet()`,
and `textbook()` that will open these helpful files in a PDF viewer
on your system.

### Paging for info and help

By default, info documents and help are run through a pager
to let you scroll long text easily. You can turn this on 
or off, both within a session and for your persistent configuration,
see *Configuring the Playground Environment*.

However, many standard pagers will operate even for short text documents,
which can be distracting. Some pagers have an option that gives a
more flexible behavior.

The pager `less`, available on Mac, Linux, and Windows is a good choice
for this. You can set the following either at your shell prompt or
in your bash or zsh init file:
```
    export PAGER='less -F'
```
This will cause `less` to skip the pager if the text is under one screen's worth,
which makes for a more pleasant workflow.


## Loading the Playground in a Script

You can import anything from the playground using the
`frplib.playground` module. For more formal code, it is recommended
that you import from specific frplib modules, but this shortcut is
convenient for quick scripts.

A helpful use case for this is to open a script file to keep any
code that you entered into the playground that you would like to
keep to run later. You can grab it after you run it from the screen,
from the history, or from the history file.
