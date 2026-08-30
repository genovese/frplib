# The Market

Access to the FRP Marketplace functionality through the `Market` object.
`Market` has methods `buy`, `compare`, `demo`, and `show` that
gives access to the full range of Marketplace functionality in
the playground.

+ `Market.demo`

   The market's demo command is used to study the values of a large
   batch of activated FRPs. The designated FRPs are activated and a
   table summarizing their values is displayed, along with the kind
   that all these FRPs share.
    
   The syntax of the command is
   ``` 
     Market.demo(count, kind_spec)
   ``` 
   Here, `count` is a positive integer (like 1000); you can use _ as
   a separator between blocks of three digits. And, `kind_spec`
   defines a Kind, and can be anything accepted by the function
   `kind` to produce a Kind.
   
   The output table shows the distinct values produced by the
   batch, the counts of how many FRPs have each value, and
   the percentage of the FRPs having each value.
    
+ `Market.buy`

   The market's buy command is used to set prices for FRPs of a
   particular kind. In particular, it can be used to estimate the
   risk-neutral prices of FRPs and kinds.
    
   The syntax of the command is
   ```
     Market.buy(count, prices, kind_spec)
   ```
   Here, `count` is a positive integer (like 1000); you can use _ as a
   separator between blocks of three digits. Also, `prices` is a
   Python list of floating-point numbers. And, `kind_spec`
   defines a Kind, and can be anything accepted by the function `kind`
   to produce a Kind.
    
   The output includes a display of the specified kind and a table
   summarizing the purchases. The table has one row per specified
   price, in order, and shows the price per unit, the total net
   payoff from the purchase of all the FRPs, and the net payoff per
   unit.


+ `Market.compare`

   The market's compare command is used to examine demos from two
   kinds, side-by-side (so to speak). The output is similar to that of
   the demo command, but there is a kind display and summary for each
   of the specified kinds.
    
   The syntax for the command is
   ```
     Market.compare(count, kind_spec1, kind_spec2)
   ```
   Here, `count` is a positive integer (like 1000); you can use _ as
   a separator between blocks of three digits. And, `kind_spec1`
   and `kind_spec2` define Kinds, and can be anything accepted by the function
   `kind` to produce a Kind.

+ `Market.show`

   The market's show command is used to display the kind tree
   specified by the kind input format. The syntax is
   `Market.show(kind_spec)`. This is not very helpful in the
   playground, which can display Kinds in several ways already.
   (See *Kinds::Displaying Kinds*.)
