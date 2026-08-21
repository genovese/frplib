# Overview

**frplib** is a library and interactive environment for probabilistic programming. It lets you build complex random systems, simulate them, and analyze them to answer interesting questions about their behavior. The software is tightly coupled with the text *Probability Explained* and has modules that lets you work through and experiment with every significant example in the book.

The focus of *frplib* is primarily on *finite* random systems. There are two principle abstractions underlying the software. An *FRP* (Fixed Random Payoff) is a device that represents an observable random quantity. An FRP produces a random value at some point during the random system's evolution, and that value is thereafter fixed for all time. Its value is what we observe and measure for the random quantity the FRP represents.

At any point, our knowledge about the FRP's value -- and our predictions of its value based on that knowledge -- is captured by its *Kind*. Finding an FRP's Kind lets us make predictions and decisions *before* we observe the FRP's value.

Both FRPs and Kinds can be operated on with a common set of four operations called the **Big 3+1**:

+ Tranforming with Statistics
+ Building with Joins
+ Constraining with Observations
+ Predicting with Expectations

These four operations and one principle (the Likelihood Principle) give us all tools we need to derive probability theory and statistics for finite systems and beyond.

When frplib is used as a library, you can import frplib tools and functions into Python code or scripts that carry out your calculations. When used as an interactive environment, you explore, compute, and display the objects and results of your calculations. The frplib **playground** is an enhanced Python REPL (Read-Evaluate-Print-Loop) that is preloaded with the frplib resources and that provides nice interactive output and help for frplib functions, objects, and data.

