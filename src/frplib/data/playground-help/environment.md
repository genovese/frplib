# Overview

The `frplib` maintains an environment that governs
several features of the interface and the playground computations.
You can set these for a particular session or persistently
as the defaults for all your sessions.

## Persistent Configuration

The file `.frplib.toml` can contain settings for all `frplib`
configuration parameters. If it exists in an appropriate location,
these settings will be loaded by the playground and use as your
defaults.

The playground searches for the config file first in your
current working folder (where you are running the playground).
If it does not exist there, 
it looks next
in your home directory (`~/.frplib.toml` on Mac or Linux,
`~\.frplib.toml` or `$env:USERPROFILE\.frplib.toml` in Powershell, or
`%USERPROFILE%\.frplib.toml` in Windows CMD prompt).
If it does not exist there, it looks in your platform config directory
(`~/.config/frplib/.frplib.toml` on Linux,
`~/Library/Application Support/frplib/.frplib.toml` on macOS,
or `%APPDATA%\frplib\.frplib.toml` on Windows).

The playground will create a copy of the file for you
with your *current* settings.
Calling `environment.write_config()` at the playground
prompt, will print a copy of the file to your terminal,
and you can cut and paste it into any file you choose.
Alternatively, you can write directly to that file.
For example:
```
    with open('/Users/genovese/.frplib.toml', 'w') as file:
        environment.write_config(file)
```
will write the config to `/Users/genovese/.frplib.toml`.
Replace that with whatever file path is appropriate.


## Dark Mode

Call `environment.on_dark_mode()` at the playground prompt
to turn on a dark theme for the interface.

Call `environment.on_bright_mode()` at the playground prompt
to turn on a light theme for the interface. This is the playground default.

## Rich text display

Call `environment.off_ascii_only()` at the playground prompt
to turn on rich text formatting. This requires an ANSI-capable
terminal emulator, which should be the default on Mac and Linux
and for the [Windows Terminal](https://learn.microsoft.com/en-us/windows/terminal/) on Windows.
This is the playground default.

Call `environment.on_ascii_only()` at the playground prompt
to force ASCII-only display.

## Command Number View

Call `environment.on_command_number_in_prompt()` at the playground prompt
to display the current command number in every prompt string.

Call `environment.off_command_number_in_prompt()` at the playground prompt
to display the current command number in the status bar instead.
This is the playground default.

## Prompt String

The default playground prompt looks like 'playground> '.
You can change the tag (e.g., "playground") and the separator (e.g., "> ")
with `environment.set_prompt`

```
    environment.set_prompt('pgd')             # sets only the tag
    environment.set_prompt(sep='% ')          # sets only the separator
    environment.set_prompt('pgd', sep='% ')   # sets both
```

## Info System Interface

By default, the `info()` help system uses a dialog-based interface
to help you navigate through the hierarchy of topic documents.

Calling `environment.off_info_dialog()` at the playground prompt
will instead turn on a completion-based interface, using the playground's
completion mechanisms.

Calling `environment.on_info_dialog()` at the playground prompt
restores the default dialog system.
The dialog system is generally recommended, but ymmv.

## Info Pager

By default, the info() system will show you topic documents
with a pager that lets you see one screen at a time.
On systems with modern pagers (e.g., Mac and Linux),
`frplib` attempts to auto-detect their capabilities and
provide a better experience. This includes only engaging
the pager when the document is long and allowing rich
text formatting in the pager view.

For Windows users who do not have an up to date pager,
the info topic *Using the Playground* points you to an
easily downloadable pager that will fit the bill.
You can also turn off the pager facility.

Calling `environment.off_info_pager()` at the playground prompt
turns off the info-system pager.

Calling `environment.on_info_pager()` at the playground prompt
turns on the info-system pager.

## Numeric Display

Call `environment.set_max_denom(d)` at the playground prompt
with a *positive* integer, will set the maximum denominator
at which the playground will show a Kind weight as a fraction.
The default is set to 50.  Other useful settings are 99 and 999.

## Version

You can read the currrent `frplib` version, as a tuple (Major, Minor, Patch),
by looking at `environment.version`.

## Other Parameters

There are several other parameters that can be set, but most should
be left at their defaults unless you know what you are doing.
The only exceptions might be the complexity and evolution thresholds
for FRPs. For some intense calculations, it can be worth changing
these temporarily to keep `frplib` from doing extra work.
See the comments in the toml file.
