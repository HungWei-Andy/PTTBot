import keras
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM

class LSTMForwardRNN(object):
  def __init__(self, config):
    self.model = Sequential()
    self.model.add(Embedding(voc_size, config.input_size))
    self.model.add(LSTM(config.hidden_size))
    self.model.add(Dense(intent_dict_size, activation='softmax'))

class LSTMBidirectionRNN(object):
  def __init__(self, config):
    self.left = Sequential()
    self.left.add(Embedding(voc_size, config.input_size))
    self.left.add(LSTM(config.hidden_size))
    

