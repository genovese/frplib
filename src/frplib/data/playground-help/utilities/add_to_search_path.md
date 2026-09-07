# add_to_search_path

Calling `add_to_search_path(d1, ...)` takes one or more
(valid) directory names as strings and adds those directories
to the playgrounds import search path.

This makes it easier to import python code from other locations.

Example:
```
    pgd> add_to_search_path('/Users/joe/extra-src')
    pgd> from extras import *
```
with the file `extras.py` in the directory `'/Users/joe/extra-src'`.
