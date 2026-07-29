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

import pandas as pd
from typing import Optional


class SmoothedTargetEncoder:
    def __init__(self, smoothing: float = 10.0):
        """
        Args:
            smoothing: higher = more shrinkage toward the global mean for
                rare categories. 10 means a category needs roughly 10+
                occurrences before it's trusted close to its own mean.
        """
        self.smoothing = smoothing
        self.mapping_: Optional[pd.Series] = None
        self.global_mean_: Optional[float] = None
        self.column: Optional[str] = None

    def fit(self, df: pd.DataFrame, column: str, target: pd.Series) -> "SmoothedTargetEncoder":
        """Fit on TRAINING DATA ONLY."""
        self.column = column
        self.global_mean_ = float(target.mean())

        stats = target.groupby(df[column]).agg(["mean", "count"])
        smoothing = self.smoothing
        self.mapping_ = (
            (stats["count"] * stats["mean"] + smoothing * self.global_mean_)
            / (stats["count"] + smoothing)
        )
        return self

    def transform(self, df: pd.DataFrame) -> pd.Series:
        if self.mapping_ is None:
            raise RuntimeError("Encoder must be fit() before transform()")
        # Categories not seen during fit (new products/customers/cities at
        # inference time) fall back to the global mean.
        return df[self.column].map(self.mapping_).fillna(self.global_mean_)

    def fit_transform(self, df: pd.DataFrame, column: str, target: pd.Series) -> pd.Series:
        self.fit(df, column, target)
        return self.transform(df)

    def to_dict(self) -> dict:
        """For saving alongside the model (pickle-friendly plain dict)."""
        return {
            "column": self.column,
            "smoothing": self.smoothing,
            "global_mean": self.global_mean_,
            "mapping": self.mapping_.to_dict() if self.mapping_ is not None else {},
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SmoothedTargetEncoder":
        enc = cls(smoothing=d["smoothing"])
        enc.column = d["column"]
        enc.global_mean_ = d["global_mean"]
        enc.mapping_ = pd.Series(d["mapping"])
        return enc