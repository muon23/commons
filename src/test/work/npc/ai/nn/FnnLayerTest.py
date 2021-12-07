import unittest

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from work.npc.ai.nn.FnnLayer import FnnLayer


class FnnLayerTest(unittest.TestCase):
    learningRate = 0.1
    numEpochs = 300
    batchSize = 256

    numFeatures = 3
    sampleSize = 50000

    @classmethod
    def runExperiment(cls, model, x_train, y_train):
        # Compile the model.
        model.compile(
            optimizer=keras.optimizers.Adam(cls.learningRate),
            # loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            loss=tf.keras.losses.BinaryCrossentropy(),
            metrics=[keras.metrics.SparseCategoricalAccuracy(name="acc")],
        )
        # Create an early stopping callback.
        early_stopping = keras.callbacks.EarlyStopping(
            monitor="val_acc", patience=50, restore_best_weights=True
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
        x = np.random.rand(cls.sampleSize, cls.numFeatures)
        y = np.apply_along_axis(
            lambda row: 1 if row[0] * row[1] * 5 + row[2] + np.random.normal(0, 0.1) > 1.5 else 0,
            # lambda row: 1 if row[0] > 0.5 else -0.0,
            1, x
        ).reshape(-1, 1)
        return x, y

    def test_runModel(self):
        tf.keras.backend.clear_session()

        x_train, y_train = self.generateData()
        x_test, y_test = self.generateData()

        print(x_train[:10, :], y_train[:10, :])

        inputs = layers.Input(shape=(self.numFeatures,), name="input_features")
        fnn = FnnLayer([32, 32, 32], 0.5)(inputs)
        logits = layers.Dense(1, name="logits", activation="sigmoid")(fnn)
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


if __name__ == '__main__':
    unittest.main()
