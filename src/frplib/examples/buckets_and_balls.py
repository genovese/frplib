"""Buckets and Balls Example 8.11

Exports
-------
+ bucket
+ green_given_bucket
+ which_bucket_g
+ which_bucket_n

"""

from frplib.kinds import conditional_kind, bayes, choice

bucket = choice(0, 1)
green_given_bucket = conditional_kind({
    0: choice(1, 0, 9),
    1: choice(1, 0, 4)
})

which_bucket_g = bayes(observed_y=1, x=bucket, y_given_x=green_given_bucket)
which_bucket_n = bayes(observed_y=0, x=bucket, y_given_x=green_given_bucket)
