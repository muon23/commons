import warnings
from typing import TypeVar, Tuple, List, Union

import numpy as np


class CosineIndexer:
    CosineIndexer = TypeVar("CosineIndexer")

    class Node:
        Node = TypeVar("Node")

        def __init__(self, indexer, idx: int):
            Node = TypeVar("Node")

            self.indexer = indexer
            self.idx = idx
            self.nearer: Node = None
            self.farther: Node = None
            self.boundary = -1
            self.branchSize = 0

        def asRoot(self, nodes: List[Node]) -> Node:
            if not nodes:
                return self

            self.branchSize = len(nodes)

            indices = [n.idx for n in nodes]
            neighborIndices = self.indexer.neighbors[self.idx]
            neighborIndices = neighborIndices[np.isin(neighborIndices, indices)]

            mediumPosition = self.branchSize // 2
            mediumNeighbor = neighborIndices[mediumPosition]
            self.boundary = self.indexer.angles[self.idx][mediumNeighbor]

            nearer = list(filter(lambda n: n.idx in neighborIndices[:mediumPosition], nodes))
            if nearer:
                self.nearer = nearer[0].asRoot(nearer[1:])

            farther = list(filter(lambda n: n.idx in neighborIndices[mediumPosition:], nodes))
            if farther:
                self.farther = farther[0].asRoot(farther[1:])

            return self

        def find(self, vector: np.ndarray, norm: float) -> Tuple[Node, float]:

            nodeVector = self.indexer.vectors[self.idx]
            nodeNorm = self.indexer.norms[self.idx]
            # angle = float(CosineIndexer.getAngles(vector, nodeVector, norm, nodeNorm))
            angle = float(np.arccos(np.inner(vector, nodeVector) / (norm * nodeNorm)))

            if angle <= self.boundary:
                subNode, subAngle = self.nearer.find(vector, norm) if self.nearer else (None, np.pi)
            else:
                subNode, subAngle = self.farther.find(vector, norm) if self.farther else (None, np.pi)

            if subNode and subAngle < angle:
                return subNode, subAngle
            else:
                return self, angle

        def __str__(self):
            nearer = str(self.nearer) if self.nearer else ""
            farther = str(self.farther) if self.farther else ""
            if not nearer and not farther:
                return str(self.idx)
            return f"[{nearer}]({self.idx}:{self.boundary:4.2f})[{farther}]"

    def __init__(self, data: np.ndarray = None):
        self.dimensions: int = 0
        self.vectors, self.norms = self.__groom(data)
        self.angles = self.getAngles(self.vectors, self.vectors, self.norms, self.norms)
        self.neighbors = np.argsort(self.angles, axis=1)

        self.tree = self.Node(self, 0).asRoot(
            [self.Node(self, i) for i in range(1, len(self.vectors))]
        )

        self.lastSearchSpace = 0

    def __groom(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if len(data.shape) > 2:
            raise ValueError(f"Data must be a 2-dimensional matrix: {data.shape}")
        if len(data.shape) == 1:
            data = data.reshape(1, -1)

        if self.dimensions == 0:
            self.dimensions = data.shape[1]
        elif data.shape[1] != self.dimensions:
            raise ValueError(
                f"Attempt to add {data.shape[1]} dimension vectors to existing {self.dimensions} dimension data"
            )

        norms = np.linalg.norm(data, axis=1).reshape(-1, 1)

        return data, norms

    @classmethod
    def getAngles(cls, v1: np.ndarray, v2: np.ndarray, n1: Union[float, np.ndarray], n2: Union[float, np.ndarray]):

        if np.isscalar(n1):
            n1 = np.array([n1])
        if np.isscalar(n2):
            n2 = np.array([n2])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            angles = np.arccos(v1.dot(v2.T) / n1.dot(n2.T))
            return np.nan_to_num(angles)

    def add(self, data: np.ndarray) -> CosineIndexer:
        vectors, norms = self.__groom(data)

        ab = self.getAngles(vectors, self.vectors, norms, self.norms)
        bb = self.getAngles(vectors, vectors, norms, norms)

        self.vectors = np.concatenate((self.vectors, vectors))
        self.norms = np.concatenate((self.norms, norms))

        self.angles = np.concatenate((self.angles, ab.T), axis=1)
        abb = np.concatenate((ab, bb), axis=1)
        self.angles = np.concatenate((self.angles, abb))

        self.neighbors = np.argsort(self.angles, axis=1)

        self.tree = self.Node(self, 0).asRoot(
            [self.Node(self, i) for i in range(1, len(self.vectors))]
        )

        return self

    def find(self, vector: np.ndarray, k: int, accurate=False) -> List[int]:
        norm = np.linalg.norm(vector)
        nearest, alpha = self.tree.find(vector, norm)

        if not accurate:
            return self.neighbors[nearest.idx][:k]

        cohort = self.neighbors[nearest.idx]
        cohortAngles = self.angles[nearest.idx][cohort]
        beta = cohortAngles[k-1]
        limit = 2 * alpha + beta
        limitPosition = np.searchsorted(cohortAngles, limit, side="right")
        limitedCohortIndices = cohort[:limitPosition]
        limitedCohortVectors = self.vectors[limitedCohortIndices]
        limitedCohortNorms = self.norms[limitedCohortIndices]
        neighborAngles = self.getAngles(vector, limitedCohortVectors, norm, limitedCohortNorms)
        neighborAnglePositions = np.argsort(neighborAngles)[:k]

        np.set_printoptions(precision=4, linewidth=200)
        print(f"alpha={alpha}, beta={beta}, limit={limit}, pos={limitPosition}")
        print(f"cohort angles={cohortAngles}")
        print(f"neighbor angles={neighborAngles}")

        self.lastSearchSpace = limitPosition
        return limitedCohortIndices[neighborAnglePositions]

    def show(self):
        oldOptions = np.get_printoptions()
        np.set_printoptions(precision=4, linewidth=200)
        print("Vectors:")
        print(self.vectors)
        print("Angles:")
        print(self.angles)
        print("Nearest Neighbors:")
        print(self.neighbors)
        print("Tree:")
        print(self.tree)
        np.set_printoptions(**oldOptions)
