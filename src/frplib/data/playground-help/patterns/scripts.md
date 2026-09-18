# Writing Quick Scripts

`frplib` is designed to be used both interactively (with the playground and market)
and in your code by importing various functions and objects as needed.
But it can also be used for quick scripting.

To that end, the `frplib.playground` module is useful as it defines all the
objects that are loaded by default into the playground environment.
If you start a script with 
```
    from frplib.playground import *
```
then you can code in a file as you would in the playground.

This is particularly useful for recording the steps you took in
the playground for running later and for quick calculations.

You can of course use it for any code, but as a matter of practice
for long-lived code, we prefer to explicitly load in the objects
we want to use. You can do that from `frplib.playground` or,
more typically, from the modules that contain the objects.
See info documents *Object Index* and *Module Index* to find
that correspondence.
