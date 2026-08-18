# Changelog

## 0.2.13 - 2026-08-17

This is a transitional release that introduces some significant
new features but also prepares the ground for a several
new features, a significant internal architecture change,
and a terminology change in keeping with the latest version
of the text.

### Changed

- Support for Python 3.9 has been dropped and support for 3.14 added.

- weighted_as Kind factory now repeats the last weight
  given if too few weights are supplied, or uses
  all 1s if no weights are supplied.

- arbitrary Kind factory defaults to None for the names

- Started transition of language (mixture -> join, conditional
  constraint -> observation, ...) but this is an ongoing effort.

- as_quantity now raises an exception if given an object
  that cannot be converted

### Added

- Kind procedures with the @kind decorator on a generator
  This provides a procedural way to define Kinds.
  See the built-in documentation.

- FRP procedures with the @frp decorator on a generator
  This provides a procedural way to define FRPs.
  See the built-in documentation.

- The summaries returned by FRP.sample now have a transform method
  for transforming the values by a statistic. Also added property
  .summary for a read-only view of the underlying frequency data and
  .values_seen() to get a set of all the values in the table.

- New interactive info system with hierarchical, fuzzy search.
  (NOTE: The info database has not yet been fully updated.)

- Custom help function for the playground REPL

  Objects with a __frplib_help__ attribute use that attribute to
  generate the help text. If it is a method of the object, it is
  called with no arguments and should return a renderable object
  (rich.console.RenderableType -- which includes Panel, Table,
  Markdown, Group -- or a string). If it is a string, it is assumed
  to be a markdown formatted string and is output to the console
  accordingly. If it is another renderable type, it is printed
  directly. Other objects with a __doc__ attribute have a cleaned
  version

- Support for config file .frplib.toml which allows
  persistent setting of preferences for the environment,
  especially for the playground.

- Added choice Kind factory as a replacement for either,
  which is deprecated

- frplib.playground module makes it easy to load the full
  playground imports within a script
  
- Command number is now visible in the mode line, with an
  environment option to put it in the prompt instead
  
- Intelligent handling of IndexErrors and KeyErrors with
  better messages and explain_error() function for more
  details.

- Numeric display parameters and FRP threshhold parameters
  are now in the environment and can be set in the config file.

- Factory decorators for Kinds, FRPs, Statistics, and Conditions
  These wrap functions in a factory object that provide nicer
  self documentation at the repl, provide some robustness
  in return values (e.g., Kind returned from FRP factory is
  automatically converted), and the decorators also
  clearly signal intention for the function which increases
  clarity.

- new exception type FactoryError for users in factory functions


### Fixed

- Resampling with given operator is more proper and non-fresh FRP
  and better checking of inconsistent conditions when possible. In
  the rare case in which a pre-check is not possible,
  non-termination will happen with an inconsistent condition, but
  user interrupt will be caught with a suitable message.

- Error in loading symbols into the playground. This bug was latent
  and first had an impact in this version, but the problem is
  fixed.
  
- FRP.sample can now handle symbolic values

- Handles new ptpython version for PlaygroundRepl error handling

- Updates and fixes in roulette example code

- Many docstring and minor fixes

## 0.2.12 - 2025-10-08

### Changed

- Applying E to a conditional Kind/FRP returns an object
  whose 'raw' component is the conditional expectation
  as a *statistic*. So, E(ckF).raw is the same
  as ckF.expecdtation.
  
### Added

- (EXPERIMENTAL) Enabled the operation stat // knd,
  where knd is a Kind and stat is a compatible statistic.
  This represents the averaging of the statistic
  by the Kind, E(knd ^ stat) as raw value.

  The primary utility of this is that it makes

  (ck // knd).expectation = ck.expectation // knd

  for a conditional Kind ck, giving a nice expression
  of the conditining operator in terms of expectations.
  This is good.

  The downside is muddying the types of the operators
  and (internally) complicating module import.

  This should not be counted on for future versions
  until it can be fully considered.

- New statistic IndexOf searches for a value
  as a contiguous sub-value of another tuple,
  returning the first starting index if so,
  or -1 if none.
  
  The condition Contains tests whether this
  search is successful.

- New statistic Freqs computes the (nothing-padded)
  tuple of frequencies for a tuple in descending
  order.

- The VecTuple.pad_to class method pads (or truncates)
  a tuple out to a specified length with a given
  value (nothing by default).

- Info documentation for the new statistics

- Some new tests

### Fixed

- Unary negation of symbolic quantities is implemented.
  This was inadvertently omitted in earlier versions.

- Several docstrings improved

## 0.2.11 - 2025-09-23

### Changed

- The `.expectation` of Kinds, FRPs, conditional Kinds,
  and conditional FRPs are now *properties* and do not
  require ()s. Moreover, for conditional Kinds and
  conditional FRPs, the result is now a **statistic**,
  which can be evaluated or used as a transform.

- Unfolding of Kinds with symbolic weights or values
  is now fully supported.

- Using `frp(cKind)` and `conditional_kind(cFRP)` now works.
  Although not strictly logical, it fits convenient usage
  to convert a conditional Kind to a conditional FRP or
  conditional FRP to a conditional Kind, and it mimics
  the previously legal `kind(cFRP)` and `conditional_frp(cKind)`.

- `statistics.tuple_safe` accepts a `convert` argument,
  allowing it to be used for more than statistics.

- New methods and better documentation for `random_graphs` example.

- environment now includes numeric output parameters; these
  are not yet fully used but will be in an upcoming release.

- Assorted documentation and types improved.

- Tests added for new and existing features.

### Added 

- Conditional Kinds and Conditional FRPs from decorated functions
  can now destructure their arguments and infer their codimension
  just like statistics can. Specifically, if given more than one
  argument (include *args), the names given are assigned the
  corresponding component of the input tuple. As always, the
  true input to the function is a single tuple, but this
  eliminates the need to explicitly unpack.

  For example, we might write
  ```python
  @conditional_kind
  def foo(a, b, c):
      return uniform(a, a + b, a + c)
  ```
  instead of
  ```python
  @conditional_kind(codim=3)
  def foo(value):
      a, b, c = value
      return uniform(a, a + b, a + c)
  ```

- Kinds can now be dumped to and loaded from files, to make
  it possible to avoid repeating computation. The methods
  are `k.dump(filepath)` and `Kind.load(filepath)`.

- Kinds and FRPs now have entropy properties
  
- Conditional Kinds and Conditional FRPs now have
  a `conditional_entropy` property which returns
  the (pointwise) conditional entropy as a **statistic**.

- `average_conditional_entropy` and `mutual_information`
  methods now exist in `frplib.frps` and are automatically
  loaded into the playground.

### Fixed

- empty Kinds now mix properly with 0-dimensional conditional Kinds

- log(0) calculation when mixing with FRP.empty corrected

- Typo fix in message from pull request #2 (thanks to aj255l)

- Edited github workflow to account for bug in Click 0.8.3

- Minor style issues and 

## 0.2.10 - 2025-09-03

### Changed

- Changed the typing for conditional Kinds to eliminate some
  spurious mypy warnings.

- Assorted documentation improvements

- Added several tests

### Added

- The `^` operator now accepts a vector tuple on the left and a statistic
  on the right, so `v ^ phi` is equivalent to `phi(v)`, mirroring what
  works with FRPs and Kinds.
  
## 0.2.9 - 2025-09-02

### Changed

- Changed the typing for conditional Kinds to eliminate some
  spurious mypy warnings.

- Assorted documentation improvements

- Added several tests

### Changed

- Extensive additions and fixes to `random_images` example.

- Assorted documentation improvements

- Many tests added

### Added

- `fold` and `fold` utilities
  
### Fixed

- Arithmetic operators now more properly compute the dimension
  of the resulting statistics that they combine.

- Added proper formatting for `nothing` values in tuples,
  so nothing tuples display properly.

- `nothing`s show up properly in `FRP.sample` and `Market.demo`

- Codims/dims added to `six_of_one` example

- Fixed slice handling in projections to give the correct
  dimension when it is possible to infer it (i.e., when
  the slice is not length dependent)

