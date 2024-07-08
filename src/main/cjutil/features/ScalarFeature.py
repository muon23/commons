from typing import Tuple, Union, List, Optional

import numpy as np
from pandas import DataFrame

from cjutil.features.Feature import Feature


class ScalarFeature(Feature):
    def __init__(
            self,
            columns: Union[str, List[str]],
            normalize: Union[bool, Tuple[float, float]] = False,
            none: Optional[float] = 0.0,
    ):
        self.columns = columns if isinstance(columns, list) else [columns]
        self.none = none
        self.normalize = normalize

    def extract(self, *args: DataFrame) -> Tuple[np.ndarray, List[str]]:
        for df in args:
            if not set(self.columns).issubset(df.columns):
                raise KeyError(f"Some of {self.columns} are not in {list(df.columns)}")

        results = []
        for df in args:
            values = df[self.columns].to_numpy()
            if self.none:
                values = np.nan_to_num(values, nan=self.none)

            if self.normalize:
                lower, upper = 0, 1 if isinstance(self.normalize, bool) else self.normalize
                minValue = np.min(values, axis=0)
                maxValue = np.max(values, axis=0)
                valueRange = maxValue - minValue
                values = (values - minValue) / valueRange * (upper - lower) + lower

            results.append(np.expand_dims(values, axis=0))

        results = np.concatenate(results, axis=0)

        return results, self.columns

