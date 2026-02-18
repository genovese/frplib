# Changelog

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

