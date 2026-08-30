# The Big 3+1

The **Big 3+1** refers to the four operations from which
we derive essentially all the probabilistic calculations.

+ Tranforming with Statistics

  A statistic is just a function that maps values (i.e., tuples of numbers)
  to values (tuples of numbers). Whenever we want to transform, summarize, or extract
  a feature from our data, we define a statistic that does the job.
  Whenever we apply an algorithm to process or analyze our data, we are
  using a statistic.

  We can use statistics to *transform* FRPs and Kinds.
  We transform an FRP by *applying the statistic to the FRP's value*,
  producing a new but related FRP. We transform
  a Kind by *applying the statistic to each possible value of the Kind*
  (i.e., the leaf nodes) and then combining branches that
  map to the same value in the transformed tree, adding their
  weights.

  We use statistics to **express and answer questions**.
  The statistic describes the steps we will take to extract the desired
  information from the data, *before those data are available*.
  Each feature FRP is derived by transforming the Data FRP
  with a statistic that represents one of our questions.
  The values of feature these FRPs will answer those questions,
  and our goal is to predict their values (or compute their Kinds)
  as accurately as possible to guide our decisions and actions.

+ Building with Joins

  We use joins **to build a model by combining simpler parts**.
  When a system can most easily be described as a combination of
  smaller parts, think about using a join.
  The join operation is the only one of the Big 3+1 that can
  inject new randomness into a system.

+ Constraining with Obervations

  We use observations to **update our knowledge and predictions with new information**.
  An observation is a constraint that some specific observable condition
  is *known to be true*, either because we actually observed that condition or
  because we are considering the hypothetical in which we observe it.

  When we constrain a Kind with an observation, we simply *erase all the branches that are inconsistent with the condition*.
  This gives us a new Kind, which in canonical
  form simply re-normalizes the weights of the remaining branches by the total weight
  of branches that are consistent with the condition.

  If you want to update your knowledge or predictions for some known information,
  use an observation.

+ Predicting with Expectations

  We use the risk-neutral price
  **to compute our best prediction of an FRP's value**,
  which we call its **expectation**. The expectation of an FRP
  reflects a "typical" value that is "close" in some sense to what
  the FRP will produce.

  From their definition as risk-neutral prices, expectations inherit
  many useful properties, and from these properties, we can deduce
  how to compute the expectation of an FRP from its Kind. Computing
  expectations is often the target of our analysis because
  predictions can guide our behavior and decisions in the context of
  the system we are studying.
