# Builtin Constants

Several constants are pre-defined in `frplib`. They are automatically
loaded into the playground and can be imported into your own code.


+ `infinity` :: the quantity that represents positive infinity

   (Available in the module `frplib.statistics` and `frplib.playground`)

+ `Pi` :: high-precision quantity approximating pi

   (Available in the module `frplib.statistics` and `frplib.playground`)

+ `nothing` :: an object representing a missing value. Its primary
      use case is as a default value for padding a tuple to a common
      dimension when no more semantically meaningful value is available. 
      (See combinators `Keep` and `MaybeMap` for examples). Arithmetic
      operations of numbers with `nothing` always produce `nothing`.

   (Available in the module `frplib.numeric` and `frplib.playground`)
