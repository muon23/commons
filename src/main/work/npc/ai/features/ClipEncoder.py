from typing import Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from work.npc.ai.features.TextEncoder import TextEncoder


class ClipEncoder(TextEncoder):
    def __init__(self, modelName: str = 'clip-ViT-B-32-multilingual-v1'):
        self.modelName = modelName
        self.clip = SentenceTransformer(self.modelName)

    def encode(self, text: str) -> Optional[np.ndarray]:
        return self.clip.encode([text]).reshape(1, -1)
