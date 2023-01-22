from typing import List, Tuple

import numpy as np
from pandas import DataFrame

from cj.features.Feature import Feature


class FeatureExtractor:

    def __init__(self, features: List[Feature]):
        self.features = features

    def addFeatures(self, features: List[Feature]):
        self.features.extend(features)

    def extract(self, *args: DataFrame) -> Tuple[np.ndarray, List[str]]:
        results = []
        featureNames = []
        for ff in self.features:
            values, names = ff.extract(*args)
            results.append(values)
            featureNames += names

        return np.concatenate(results, axis=2), featureNames



