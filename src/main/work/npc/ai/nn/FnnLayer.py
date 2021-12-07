import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers


class FnnLayer(layers.Layer):

    def __init__(self, hiddenLayers, dropoutRate, name=None, **kwargs):
        super().__init__(name=name, **kwargs)

        self.hiddenLayers = hiddenLayers
        self.dropoutRate = dropoutRate
        self.model = None

    def build(self, inputShape):
        fnnLayers = []
        for units in self.hiddenLayers:
            fnnLayers.append(layers.BatchNormalization())
            fnnLayers.append(layers.Dropout(self.dropoutRate))
            fnnLayers.append(layers.Dense(units, activation=tf.nn.gelu, input_shape=inputShape))

        self.model = keras.Sequential(fnnLayers, name=self.name)

    def call(self, inputs, *args, **kwargs):
        return self.model(inputs)
