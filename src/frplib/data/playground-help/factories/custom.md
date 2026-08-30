# Custom Factories

For defining factories for Kinds, FRPs, Statistics, and Conditions,
`frplib` defines several decorators:

+ `@kind_factory`
+ `@frp_factory`
+ `@statistic_factory`
+ `@condition_factory`

These decorators are attached to the factory function itself, the
function that returns a Kind, FRP, Statistic, or Condition.
Recall that a factory function is just a function that returns
an object specified by the functions parameters.

The advantages of using these decorators include

+ clearly marking the intent of the function;

+ improving the factory's documentation and usability
  in code, and especially in the playground.
  
See info documents
*Kinds::Custom Kind Factories*,
*FRPs::Custom FRP Factories*, and
*Statistics::Custom Statistic and Condition Factories*
for examples and more detail.
This is also illustrated in the textbook.
