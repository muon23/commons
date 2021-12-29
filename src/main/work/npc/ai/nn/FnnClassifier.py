from typing import List, Union

import dill
import pandas as pd
import tensorflow as tf
from pandas import DataFrame
from tensorflow import keras
from tensorflow.keras import layers, callbacks

from work.npc.ai.features.Feature import Feature
from work.npc.ai.nn.ClassifierFactory import ClassifierFactory
from work.npc.ai.nn.ClassifierModel import ClassifierModel
from work.npc.ai.nn.FnnLayer import FnnLayer


class FnnClassifierModel(ClassifierModel):

    def __init__(
            self,
            features: List[Feature],
            labels: List[Feature],
            hiddenLayers: List[int],
            **kwargs
    ):
        super().__init__(features, labels)

        self.hiddenLayers = hiddenLayers
        self.dropoutRate = kwargs.get("dropoutRate", 0.0)
        self.checkpointFile = kwargs.get("checkpointFile")
        self.verbose = kwargs.get("verbose", 1)
        self.patience = kwargs.get("patience", 10)
        self.epochs = kwargs.get("epochs", 300)
        self.outputActivation = kwargs.get("outputActivation", None)

        self.model: keras.Model = None
        self.labelNames = None

    def build(self, inputUnits: int, outputUnits: int):
        tf.keras.backend.clear_session()

        if not self.outputActivation:
            self.outputActivation = "softmax" if outputUnits > 1 else "sigmoid"

        inputs = layers.Input(shape=(inputUnits,), name="input_features")
        fnn = FnnLayer(hiddenLayers=self.hiddenLayers, dropoutRate=self.dropoutRate, name="fnn")(inputs)
        outputs = layers.Dense(outputUnits, name="output_labels", activation=self.outputActivation)(fnn)
        self.model = keras.Model(inputs=inputs, outputs=outputs, name="fnn_model")

        self.model.compile(
            optimizer="adam",
            loss=tf.keras.losses.BinaryCrossentropy(),
            metrics=[
                tf.metrics.BinaryAccuracy(),
                tf.metrics.Precision(),
                tf.metrics.Recall(),
                tf.metrics.AUC(),
            ]
        )

    def train(self, data: DataFrame) -> None:
        featureData, featureNames = self.features.extract(data)
        featureData = featureData[0]
        inputUnits = len(featureNames)

        labelData, self.labelNames = self.labels.extract(data)
        labelData = labelData[0]
        outputUnits = len(self.labelNames)

        if not self.model:
            self.build(inputUnits, outputUnits)

        checkpoint = callbacks.ModelCheckpoint(
            filepath=self.checkpointFile,
            save_best_only=True,
            save_weights_only=True,
            verbose=self.verbose
        ) if self.checkpointFile is not None else None

        early_stop = callbacks.EarlyStopping(
            monitor="loss", mode="min", verbose=self.verbose, patience=self.patience
        )

        cb = [early_stop]
        if checkpoint is not None:
            cb.append(checkpoint)

        self.model.fit(
            featureData, labelData,
            epochs=self.epochs, callbacks=cb,
            verbose=self.verbose
        )

    def evaluate(self, data: DataFrame) -> dict:
        if not self.model:
            raise RuntimeError("Model has not yet built nor trained")

        featureData, featureNames = self.features.extract(data)
        featureData = featureData[0]

        labelData, labelNames = self.labels.extract(data)
        labelData = labelData[0]

        result = self.model.evaluate(
            featureData, labelData,
            verbose=1 if self.verbose > 0 else 0
        )

        return dict(zip(self.model.metrics_names, result))

    def classify(self, data: DataFrame) -> DataFrame:
        if not self.model:
            raise RuntimeError("Model has not yet trained")

        featureData, featureNames = self.features.extract(data)
        featureData = featureData[0]

        predictions = self.model.predict(featureData)

        return pd.DataFrame(predictions, columns=self.labelNames)

    def show(self, what: str = None) -> None:
        if not self.model:
            raise RuntimeError("Number of features and labels unknown.  (Call build() or train() first)")

        self.model.summary()

    def save(self, fileName: str):
        self.model.save(fileName)

        # Nullify self.model since it has trouble serialize
        temp = self.model
        self.model = None

        with open(f"{fileName}/{FnnClassifier.MODEL_FILE_NAME}", "wb") as fd:
            dill.dump(self, fd)

        self.model = temp   # Recover model and MD5


class FnnClassifier(ClassifierFactory):
    MODEL_FILE_NAME = "fnn_classifier_model.dil"

    @classmethod
    def of(
            cls,
            features: Union[Feature, List[Feature]],
            labels: Union[Feature, List[Feature]],
            **kwargs
    ) -> ClassifierModel:
        hiddenLayers = kwargs.get("hiddenLayers", None)
        if not hiddenLayers:
            raise ValueError(f"Missing FNN layer specifications (hiddenLayers=[<list of layer widths>] required)")

        if isinstance(features, Feature):
            features = [features]

        if isinstance(labels, Feature):
            labels = [labels]

        return FnnClassifierModel(features, labels, **kwargs)

    @classmethod
    def load(cls, fileName: str) -> ClassifierModel:
        with open(f"{fileName}/{cls.MODEL_FILE_NAME}", "rb") as fd:
            model = dill.load(fd)
            model.model = tf.keras.models.load_model(fileName)

        return model

