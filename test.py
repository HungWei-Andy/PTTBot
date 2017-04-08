# -*- coding:utf-8 -*-
from __future__ import print_function
import os
import nlu.reader as reader
import logging
from keras.models import load_model
from kp.knowledge_provider import KnowledgeProvider  
import time 
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

# load dictionary
word_dict, word_to_ids = reader.read_dict('nlu/dict/word_dict.txt')
label_dict, label_to_ids = reader.read_dict('nlu/dict/label_dict.txt')
intent_dict, intent_to_ids = reader.read_dict('nlu/dict/intent_dict.txt')

# load intent rnn and label rnn
intent_rnn = load_model('nlu/models/intent_rnn.h5')
label_rnn = load_model('nlu/models/label_rnn.h5')

#set database path
DATABASE_PATH = 'kp/database/merged_file.json'
kp = KnowledgeProvider(DATABASE_PATH)
keyword_dict = {'爆':100,'紫爆':100,'紫':100,'西斯':'sex','八卦':'Gossiping', 'gossiping': 'Gossiping', 'nba': 'NBA'
               ,'NBA':'NBA','JOKE':'joke', 'lol': 'LOL'}

#print(u'西斯')
#print(str('西斯'))

def keyword_translate(request, keyword_dict):
    req = request

    for key,val in keyword_dict.iteritems():
        if req['board'] == key:
            req['board'] = val

    for k,v in req['push'].iteritems():
        for key,val in keyword_dict.iteritems():
            if v == key:
                req['push'][k] = val
                print (val)
    return req


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
                words.append(word.lower())
            else:
                word += chs[i]
                word += chs[i + 1]
                word += chs[i + 2]
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

        # repack the label into a dictionary
        request = {
            'function':None,
            'board':None,
            'title':None,
            'author':None,
            'content':None,
            'comment':{'state':None,'message':None,'id':None,'date':None},
            'push':{'all':None,'score':None,'g':None,'b':None,'n':None},
            'date':None,
            'ip':None
        }

        request['function'] = intent_dict[intents]
        # print ('1')
        # print (request)
        i = j = 0
        while i < labels.shape[0]:
            label = label_dict[labels[i]]
            if label != '<eos>' and label != '<unk>':
                word = words[i]
                j = i + 1
                while label_dict[labels[j]] == label and j < labels.shape[0]:
                    word += words[j]
                    j += 1
                i = j

                if label == 'score':
                    request['push']['score'] = word
                else:
                    request[label] = word
            else:
                i += 1
        # print ('2')
        # print (request)

        '''
        knowledge provider(backend database)
        '''
        req = keyword_translate(request, keyword_dict)
        # print ('request' + str(request))
        # print ('req' + str(req))
        kp.query(req)

except Exception as e:
    print (e)
    logging.warning('穴穴你使用我們PTTBOT，愛你 <3')
