# Serializing Kinds

`frplib` allows you to save a Kind to a file and disk and read it back in later sessions.
This is useful if you generating the Kind takes a long time or lots of computation.
You can make it, save it, and then reuse it at will.

If `k` is a Kind,

+ `k.dump(path)` saves the Kind in an internal format to a file at path `path`, which should be
  a string or a `Path` object (from Python standard library `pathlib`).

+ `Kind.load(path)` reads a Kind from the file at the specified path and returns it.
  The `path` should be a string or `Path` object pointing to the file on your computer's
  file system.
  
+ `k.serialize()` prints a string representation of the Kind in sexp format. See info
  on the function `kind` for detail on that format.
