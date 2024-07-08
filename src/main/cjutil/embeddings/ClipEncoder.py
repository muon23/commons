import logging
from typing import Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from cjutil.embeddings.TextEncoder import TextEncoder


class ClipEncoder(TextEncoder):
    def __init__(self, modelName: str = 'clip-ViT-B-32-multilingual-v1'):
        self.modelName = modelName
        # TODO: sentence_transformers no longer compatible with torch-1.13.1.  Consider using OpenAI's CLIP
        self.clip = SentenceTransformer(self.modelName)
        logging.info(f"CLIP model {self.modelName} loaded")

    def encode(self, text: str) -> Optional[np.ndarray]:
        return self.clip.encode([text]).reshape(1, -1)
