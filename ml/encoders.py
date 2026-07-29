"""
Smoothed target (mean) encoding for high-cardinality categorical columns.

Why not one-hot: Product_ID (1,861 unique values), Customer_ID (793), and
City (529) are far too high-cardinality to one-hot encode without exploding
dimensionality. But a plain "average Sales per Product_ID" is dangerous:
many products appear only once or twice, so the model would just memorize
training rows and fail on new data (classic target leakage / overfitting).

Fix: shrinkage / smoothing. Each category's encoded value is a weighted
blend of its own group mean and the global mean, where the weight depends
on how many times that category was seen:

    encoded = (count * group_mean + smoothing * global_mean) / (count + smoothing)

A category seen many times (large count) ends up close to its own group
mean. A category seen once or never ends up close to the global mean
instead of an unreliable single data point.

CRITICAL: fit() must only ever be called on the training split. Calling it
on the full dataset (train+test together) leaks the test set's own Sales
values into the encoding used to predict it, which inflates evaluation
metrics and won't hold up on truly new data.
"""
