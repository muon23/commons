from abc import ABC, abstractmethod

from typing import TypeVar, List

from cjutil.features.CategoricalFeature import CategoricalFeature
from cjutil.features.Feature import Feature


class ClassifierFactory(ABC):
    ClassifierModel = TypeVar("ClassifierModel")

    @classmethod
    @abstractmethod
    def of(cls, features: List[Feature], labels: List[CategoricalFeature], **kwargs) -> ClassifierModel:
        pass

    @classmethod
    @abstractmethod
    def load(cls, fileName: str) -> ClassifierModel:
        pass
