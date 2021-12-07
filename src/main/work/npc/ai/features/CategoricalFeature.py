import numpy as np
import pandas as pd
from pandas import DataFrame, CategoricalDtype
from typing import List, Tuple

from work.npc.ai.features.Feature import Feature


class CategoricalFeature(Feature):
    def __init__(self, column: str):
        self.column = column

    def extract(self, *args: DataFrame) -> Tuple[np.ndarray, List[str]]:
        for df in args:
            if self.column not in df.columns:
                raise KeyError(f"Column {self.column} is not in {list(df.columns)}")

        categories = set()
        for df in args:
            categories = categories.union(set(df[self.column]))
        categories = list(categories)
        categories.sort()

        results = []
        for df in args:
            df[self.column].astype(CategoricalDtype(categories))
            results.append(np.expand_dims(pd.get_dummies(df[self.column]).to_numpy(), axis=0))

        results = np.concatenate(results, axis=0)

        return results, [f"{self.column}_{c}" for c in categories]

