import keras
import reader
import random
import numpy as np
import os
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, Bidirectional
from keras.layers.wrappers import TimeDistributed

class Config(object):
    max_timestep = 50
    input_size = 256
    intent_hidden_size = 100
    label_hidden_size = 200
    intent_epoch = 10
    label_epoch = 20
    batch_size = 256
    train_sample_num = 8200

def words2vec(words, word_to_ids):
    vec = []
    for word in words:
        vec.append(word_to_ids[word])
    return vec

def int2onehot(arr, maxlen):
    ori_shape = arr.shape
    res_shape = ori_shape + (maxlen,)
    
    oned_arr = arr.reshape(-1)
    res = []
    for i in range(len(oned_arr)):
        res.append([0 for _ in range(maxlen)])
        res[i][oned_arr[i]] = 1
    return np.array(res).reshape(res_shape)

def main():
    config = Config()

    # import dictionaries
    word_dict, word_to_ids = reader.read_dict('./dict/word_dict.txt')
    label_dict, label_to_ids = reader.read_dict('./dict/label_dict.txt')
    intent_dict, intent_to_ids = reader.read_dict('./dict/intent_dict.txt')
    
    voc_size = len(word_dict)
    label_dict_size = len(label_dict)
    intent_dict_size = len(intent_dict)

    # import csv
    sentences, labels, intents = reader.read_csv('./data/training_data.csv')
    
    # turn training data into indices
    sentence_vecs = []
    label_vecs = []
    for sentence in sentences:
        sentence_vecs.append(words2vec(sentence, word_to_ids))
    for label in labels:
        label_vecs.append(words2vec(label, label_to_ids))
    intent_vecs = words2vec(intents, intent_to_ids)

    X = pad_sequences(sentence_vecs, maxlen=config.max_timestep)
    Y_label = int2onehot(pad_sequences(np.array(label_vecs), maxlen=config.max_timestep), label_dict_size)
    Y_intent = int2onehot(np.array(intent_vecs), intent_dict_size)
    
    # split into train and test sets
    train_idxs = random.sample(range(len(intent_vecs)), config.train_sample_num)
    test_idxs = [i for i in range(len(Y_intent)) if i not in train_idxs]
        
    X_train = X[train_idxs]
    Y_label_train = Y_label[train_idxs]
    Y_intent_train = Y_intent[train_idxs]

    X_test = X[test_idxs]
    Y_label_test = Y_label[test_idxs]
    Y_intent_test = Y_intent[test_idxs]


    # build intent rnn
    config = Config()
    intent_rnn = Sequential()
    intent_rnn.add(Embedding(voc_size, config.input_size))
    intent_rnn.add(LSTM(config.intent_hidden_size, return_sequences=False))
    intent_rnn.add(Dense(intent_dict_size, activation='softmax'))
    intent_rnn.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(X_train.shape, Y_intent_train.shape)
    intent_rnn.fit(X_train, Y_intent_train,
        epochs=config.intent_epoch, batch_size=config.batch_size, shuffle=True, validation_split=0.05)
    intent_rnn.save(os.path.join('models', 'intent_rnn.h5'))
    score = intent_rnn.evaluate(X_test, Y_intent_test, batch_size=config.batch_size)
    print('Intent RNN testing score: ', score)

    label_rnn = Sequential()
    label_rnn.add(Embedding(voc_size, config.input_size))
    label_rnn.add(Bidirectional(LSTM(config.label_hidden_size, return_sequences=True)))
    label_rnn.add(TimeDistributed(Dense(label_dict_size, activation='softmax')))
    label_rnn.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    label_rnn.fit(X_train, Y_label_train,
        epochs=config.label_epoch, batch_size=config.batch_size, shuffle=True, validation_split=0.05)
    label_rnn.save(os.path.join('models', 'label_rnn.h5'))
    score = label_rnn.evaluate(X_test, Y_label_test, batch_size=config.batch_size)
    print('Label RNN testing score: ', score)

if __name__ == '__main__':
    main()
