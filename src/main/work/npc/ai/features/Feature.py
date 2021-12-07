from abc import ABC, abstractmethod

import numpy as np
from pandas import DataFrame
from typing import List, Tuple


class Feature(ABC):

    @abstractmethod
    def extract(self, *args: DataFrame) -> Tuple[np.ndarray, List[str]]:
        pass
