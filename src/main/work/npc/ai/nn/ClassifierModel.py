from abc import ABC, abstractmethod
from typing import List

from pandas import DataFrame

from work.npc.ai.features.Feature import Feature
from work.npc.ai.features.FeatureExtractor import FeatureExtractor


class ClassifierModel(ABC):
    def __init__(self, features: List[Feature], labels: List[Feature]):
        self.features = FeatureExtractor(features)
        self.labels = FeatureExtractor(labels)

    @abstractmethod
    def train(self, data: DataFrame) -> None:
        pass

    @abstractmethod
    def evaluate(self, data: DataFrame) -> dict:
        pass

    @abstractmethod
    def classify(self, data: DataFrame) -> DataFrame:
        pass

    @abstractmethod
    def show(self, what: str = None) -> None:
        pass

    @abstractmethod
    def save(self, fileName: str):
        pass


