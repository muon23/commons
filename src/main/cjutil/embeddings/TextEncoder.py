from abc import ABC, abstractmethod
from typing import Optional

import numpy as np


class TextEncoder(ABC):

    @abstractmethod
    def encode(self, text: str) -> Optional[np.ndarray]:
        pass
