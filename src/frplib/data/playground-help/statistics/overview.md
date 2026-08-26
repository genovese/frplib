# Statistics

A **statistic** is a function that takes and returns values.
It represents some operation or data-processing algorithm that
we will apply to our data. We use statistics for many purposes,
most importantly for embodying questions that we want to answer
with the data that we measure from a random system.

In `frplib`, a statistic is a special object that is callable as
a function. These objects can be used in transformations and other
operations. They can be queried for the types/dimensions of values
they accept and return. And they can be combined to form new
statistics.

There are several ways to make statistics in `frplib`:

1. Using **built-in statistics**, of which there are many.
See the *Statistics::Built-Ins* topic in the info tree.
A simple example of a built-in statistic is `Sum` that
sums the components of its input.

2. Using a **statistic factory** which makes statistics that meet
desired specifications. These are functions that take a specification
and return a statistic to serve a particular purpose.
A simple example of a statistic factory is `Constantly` which takes
a value and returns a statistic that always yields that value.

3. Using a **statistic combinator** to combine several statistics
into a new statistic. A simple example of a statistic combinator
is `Chain` which chains together two or more statistics, feeding
the output of one to the input of the next.

4. Defining a **custom statistic** in code. See the
*Statistics::Defining Custom Statistics* info document for detail.

A **condition** is a special case of a statistic that returns
a "Boolean" value. In `frplib`, we use a scalar tuple <0> for false
and <1> for true. Conditions are used to test whether a value
has certain features.
