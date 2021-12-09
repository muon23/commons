import os
import unittest

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from work.npc.ai.features.CategoricalFeature import CategoricalFeature
from work.npc.ai.features.ScalarFeature import ScalarFeature
from work.npc.ai.nn.FnnClassifier import FnnClassifier
from work.npc.ai.nn.FnnLayer import FnnLayer


class FnnClassifierTest(unittest.TestCase):
    learningRate = 0.1
    numEpochs = 300
    batchSize = 256

    numFeatures = 3
    sampleSize = 50000

    outputDir = "../../../../../../output/FnnClassifierTest"

    @classmethod
    def runExperiment(cls, model, x_train, y_train):
        # Compile the model.
        model.compile(
            # optimizer=keras.optimizers.Adam(cls.learningRate),
            optimizer="adam",
            # loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            loss=tf.keras.losses.BinaryCrossentropy(),
            # metrics=[keras.metrics.SparseCategoricalAccuracy(name="acc")],
            metrics=[
                tf.metrics.BinaryAccuracy(),
                tf.metrics.Precision(),
                tf.metrics.Recall(),
                tf.metrics.AUC(),
            ],
        )
        # Create an early stopping callback.
        # early_stopping = keras.callbacks.EarlyStopping(
        #     monitor="val_acc", patience=50, restore_best_weights=True
        # )

        early_stopping = keras.callbacks.EarlyStopping(
            monitor="loss", mode="min", patience=50
        )

        # Fit the model.
        history = model.fit(
            x=x_train,
            y=y_train,
            epochs=cls.numEpochs,
            batch_size=cls.batchSize,
            validation_split=0.15,
            callbacks=[early_stopping],
        )

        return history

    @classmethod
    def generateData(cls):
        def makeY(row):
            if row[0] > 0.75:
                return 0 if row[1] + row[2] > 1 else 1
            else:
                return 2 if row[0] - 2 * row[1] < 0 else 3

        x = np.random.rand(cls.sampleSize, cls.numFeatures)
        y = np.apply_along_axis(makeY, 1, x)
        yy = np.zeros((y.size, y.max()+1))
        yy[np.arange(y.size), y] = 1
        return x, yy

    def test_runModel(self):
        tf.keras.backend.clear_session()

        x_train, y_train = self.generateData()
        # x_test, y_test = self.generateData()

        print(x_train[:10, :], y_train[:10, :])

        inputs = layers.Input(shape=(self.numFeatures,), name="input_features")
        fnn = FnnLayer([32, 32, 32], 0.5)(inputs)
        logits = layers.Dense(4, name="logits", activation="sigmoid")(fnn)
        model = keras.Model(inputs=inputs, outputs=logits, name="testModel")

        model.summary()

        self.runExperiment(model, x_train, y_train)

        result = model.predict([
            [0.5, 0.5, 0.5],
            [0.4, 0.4, 0.4],
            [0.6, 0.4, 0.6],
            [0, 0, 0],
            [1, 1, 1],
        ])
        print(result)

        self.assertEqual(True, True)  # add assertion here

    def test_fnnClassifier(self):
        outputFile = self.outputDir + "/test_fnnClassifier"
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)

        def makeY(row):
            if row[0] > 0.75:
                return 0 if row[1] + row[2] > 1 else 1
            else:
                return 2 if row[0] - 2 * row[1] < 0 else 3

        df = pd.DataFrame(np.random.rand(self.sampleSize, self.numFeatures), columns=list("abc"))
        df["y"] = df.apply(makeY, axis=1)
        print(df)

        train = df.sample(frac=0.8)
        valid = df.drop(train.index)

        classifier = FnnClassifier.of(
            ScalarFeature(["a", "b", "c"]),
            CategoricalFeature("y"),
            hiddenLayers=[32, 32, 32, 4]
        )

        classifier.train(train)
        classifier.show()
        classifier.evaluate(valid)

        data = pd.DataFrame([
            [0.8, 0.5, 0.6],
            [0.9, 0.1, 0.2],
            [0.5, 0.1, 0.1],
            [0.2, 0.5, 0.1],
        ], columns=list("abc"))
        data["y"] = data.apply(makeY, axis=1)

        predicted = classifier.classify(data)
        data = pd.concat([data, predicted], axis=1)
        print(data)

        classifier.save(outputFile)
        classifier2 = FnnClassifier.load(outputFile)
        classifier2.show()
        predicted2 = classifier2.classify(data)

        self.assertTrue(predicted.equals(predicted2))


if __name__ == '__main__':
    unittest.main()
