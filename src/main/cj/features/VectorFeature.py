from typing import Optional, Tuple, List

import numpy as np
from pandas import DataFrame

from cj.features.Feature import Feature


class VectorFeature(Feature):

    def __init__(
            self,
            column: str,
            normalize: str = None,
            none: Optional[float] = 0.0,
            padding: Optional[float] = None,
    ):

        if normalize and normalize not in ["full", "column", "length"]:
            raise NotImplementedError(f"Unsupported normalization method {normalize}")

        self.column = column
        self.normalize = normalize
        self.none = none
        self.padding = padding

    def extract(self, *args: DataFrame) -> Tuple[np.ndarray, List[str]]:
        for df in args:
            if self.column not in df.columns:
                raise KeyError(f"Column {self.column} is not in {list(df.columns)}")

        vectorSizes = set()
        for df in args:
            vectorSizes = vectorSizes.union(df[self.column].apply(lambda x: len(x)).unique())
        width = max(vectorSizes)

        if len(vectorSizes) == 1:
            self.padding = None
        elif self.padding is None:
            raise ValueError(f"Vector sizes vary ({', '.join([str(x) for x in vectorSizes])}), padding required")

        results = []
        for df in args:
            values = np.array(df[self.column].to_list())

            if self.padding is not None:
                values = np.array([row + [self.padding] * (width - len(row)) for row in values])

            if self.none:
                values = np.nan_to_num(values, nan=self.none)

            results.append(np.expand_dims(values, axis=0))

        results = np.concatenate(results, axis=0)

        if self.normalize == "length":
            norm = np.linalg.norm(results, axis=2)
            norm = np.expand_dims(norm, axis=2)
            results = results / norm

        elif self.normalize == "column":
            maxValue = np.max(results, axis=1)
            minValue = np.min(results, axis=1)
            valueRange = maxValue - minValue
            results = (results - minValue) / valueRange

        elif self.normalize == "full":
            maxValue = np.max(results)
            minValue = np.min(results)
            valueRange = maxValue - minValue
            results = (results - minValue) / valueRange

        return results, [f"{self.column}_{i}" for i in range(width)]
