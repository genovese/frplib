# Buckets and Balls Example Chapter 0 Section 8

from typing             import cast
from frplib.kinds       import Kind, QuantityType, conditional_kind, bayes, either

bucket = either(0, 1)
green_given_bucket = conditional_kind(cast(dict[QuantityType, Kind], {
    0: either(0, 1, 9),
    1: either(0, 1, 4)
}))

which_bucket_g = bayes(observed_y=1, x=bucket, y_given_x=green_given_bucket)
which_bucket_n = bayes(observed_y=0, x=bucket, y_given_x=green_given_bucket)
