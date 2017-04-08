# -*- coding: utf-8 -*-
from __future__ import print_function
import logging
import os
import reader
from keras.models import load_model
from kp import knowledge_provider

# load dictionary
word_dict, word_to_ids = reader.read_dict('./dict/word_dict.txt')
label_dict, label_to_ids = reader.read_dict('./dict/label_dict.txt')
intent_dict, intent_to_ids = reader.read_dict('./dict/intent_dict.txt')

# load intent rnn and label rnn
intent_rnn = load_model('./models/intent_rnn.h5')
label_rnn = load_model('./models/label_rnn.h5')



try:
    while(1):
        # read sentence from command line
        print('\nPlease Input a sentence: ', end='')
        sentence = raw_input()

        # split the sentence
        i = 0
        words = []
        chs = list(sentence)
        while i < len(chs):
            word = ''
            
            if chs[i].isdigit() or chs[i].isalpha():
                while (chs[i].isdigit() or chs[i].isalpha()) and i < len(chs):
                    word += chs[i]
                    i += 1
                words.append(lower(word))
            else:
                word += chs[i]
                word += chs[i+1]
                word += chs[i+2]
                words.append(word)
                i += 3

        # turn words into vectors
        X = [word_to_ids[word] if word in word_dict else word_to_ids['<unk>'] for word in words ]

        # predict the result
        intents = intent_rnn.predict_classes(X)[-1]
        labels = label_rnn.predict_classes(X).reshape(-1)

        # print the result
        print(intent_dict[intents])
        for i in range(labels.shape[0]):
            print(words[i] + label_dict[labels[i]])

except:
        logging.warning('你問太多問題囉,真受不了你')
