# -*- coding: utf-8 -*- 
#from __future__ import print_function
import os
import nlu.reader as reader

import logging
from keras.models import load_model
import time 
import json
import logging
import pandas
import dateutil.parser
import sys
import random
import operator
from copy import deepcopy

#python sys default decode method: ascii
#so change sys decode from ascii to utf-8 done ! No Error Fxck u
reload(sys)
sys.setdefaultencoding('utf-8')

"""
Classic cart-pole system implemented by Rich Sutton et al.
Copied from https://webdocs.cs.ualberta.ca/~sutton/book/code/pole.c
"""
import logging
import math
import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
import time
from simulated_user.simulated_user import  user_semantic

import nlg.nlg as nlg

# load dictionary
word_dict, word_to_ids = reader.read_dict('nlu/dict/word_dict.txt')
label_dict, label_to_ids = reader.read_dict('nlu/dict/label_dict.txt')
intent_dict, intent_to_ids = reader.read_dict('nlu/dict/intent_dict.txt')

# load intent rnn and label rnn
print('loading NLU')
intent_rnn = load_model('nlu/models/intent_rnn.h5')
label_rnn = load_model('nlu/models/label_rnn.h5')
print('loaded NLU')

#set database path
DATABASE_PATH = 'kp/database/sex.json'
keyword_dict = {'爆':100,'紫爆':100,'紫':100,'西斯':'sex','八卦':'Gossiping','NBA':'NBA','JOKE':'joke'}
logger = logging.getLogger(__name__)



import numpy as np
import gym

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.agents.sarsa import SarsaAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory
import time
from envs.env_pttbot import Env_PTTBot 
from keras.models import load_model

import nlg.nlg as nlg


ENV_NAME = 'PTTBot'

env = Env_PTTBot()
nb_actions = env.action_space.n

# Next, we build a very simple model.
model = Sequential()
model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(nb_actions))
model.add(Activation('linear'))
print(model.summary())

#############################
##            DQN          ##
#############################

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=50000, window_length=1)
policy = BoltzmannQPolicy()

# del(model)
# model = load_model('PTTBot_model.h5')
dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=10, target_model_update=1e-2, policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])
dqn.load_weights('dqn_{}_weights.h5f'.format(ENV_NAME))

class PTTBot(object): 
    def __init__(self, dqn):
        self.dqn = dqn
        #######################
        #  PTTBot  parameter  #
        #######################
        self.nb_actions = 8
        self.nb_states = 4
        self.count = 0
        #declare number of action
        self.action_space = spaces.Discrete(self.nb_actions)
        #state limit
        self.observation_space = spaces.Box(np.array([0,0,0,0],dtype='float32'), np.array([7,1,1,1],dtype='float32'))

        self._seed()
        self.viewer = None
        self.function_dict = {'inform_title': 0, 'request_author':1,'inform_Noneed':2,'request_post':3,'request_board':4,'inform_push':5,'inform_board':6}

        self.states = {}
        self.states_rl_input = None
        self.filtered_posts = []
        self.state_init = {
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
        self.request = self.state_init
        self.kp = KnowledgeProvider(DATABASE_PATH)

        self.steps_beyond_done = None
        self.done = False
        self.reward = 0

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]
    #############################################
    ##  Agent give an action                   ##
    ##  then env give next state, reward, done ##
    #############################################
    def process(self, sentence):
        ####################
        ##   Preprocess   ## 
        ####################
        if sentence == None:
            sentence = '你是笨蛋嗎'

        ##########################
        ##          NLU         ##
        ##########################
        print('[User Say]: ' + sentence)
        self.request = nlu2req(sentence)
        self.request = keyword_translate(self.request, keyword_dict)

        ##########################
        ##           DST        ## 
        ##########################
        # update states
        self.states, self.filtered_posts = self.kp.query(self.request)
        self.states_rl_input = self.dic2array(self.states)

        ################################
        ##  Dialogue Policy: DQN      ## 
        ################################
        action = self.dqn.forward(self.states_rl_input)
        
        print('[count] ->>' + str(self.count))
        print('[action] ->>' + str(action))
        print('self.states:' + str(self.states))
        print('[function ; title ; board ; score]')
        print('self.states_rl_input' + str(self.states_rl_input))
        print('self.filtered_posts:' + str(len(self.filtered_posts)))
        
        ####################
        ##   Action NLG   ## 
        ####################
        reply = nlg.generate(action, {'state': self.states, 'post': self.filtered_posts})
        print('[ChatBot Say :]:'+reply)

        return reply

    def _reset(self):
        print('===============')
        print('====  Reset  ====')
        print('===============')
        self.request = self.state_init
        self.states =  {}
        self.states_rl_input = self.np_random.uniform(low=-0.05, high=0.05, size=(self.nb_states ,))
        self.filtered_posts = []
        self.state_init = {
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
        self.kp.reset()
        self.simulated_user = user_semantic()

        return np.array(self.states_rl_input)


    def dic2array(self,states):
        state_array = np.array([0]*self.nb_states )
        function_value = 0
        if 'function' in states:
           # print('******** function in states **********')
           function_value = self.function_dict[states['function']]
        state_array[0] = int(function_value)


        if 'title' in states:
            # print('******** title in states **********')
            state_array[1] = 1
        if 'board' in states:
            # print('******** board in states **********')
            state_array[2] = 1
        if 'push' in states:
            # print('******** score in states **********')
            state_array[3] = 1

        return state_array.astype(dtype='float32')

class KnowledgeProvider:
    #request for per sentence
    request = {} 

    #store overall context intent ; context means this function will stay how long not to be substitube
    dialogue_state = {'turns':0}
    filtered_posts=[]
    DATABASE_PATH =''
    DATABASE =[]


    def __init__(self,database_path):
        self.DATABASE_PATH = database_path
        try:
            with open(self.DATABASE_PATH) as f:
                self.DATABASE = json.load(f)
            logging.info('Database load successfully !')
        except:
            logging.warning('The database is not exist : ' + str(self.DATABASE_PATH))

        self.states = {}

    # def dialogue_state_update(self,request):
    #   for k,v in request.iteritmes():


    #Dialogue State Update
    def query(self,request):
        self.request = deepcopy(request)
        #update dualogue states
        self.states.update(self.extract_slot(self.request))
        self.filtered_posts = self.DATABASE
        self.find_strategy(self.states)
        return self.states, self.filtered_posts

    def reset(self):
        self.states = {}
        self.request = {}

    def decode_utf8(self,string):
        return string.decode('utf-8').encode('utf-8')

    # filter post via dialogue state
    def find_strategy(self,request):
        # Strategy of finding posts
        for k,v in request.iteritems():

            if k == 'board':
                self.filtered_posts = filter(lambda posts: posts[k] == v, self.filtered_posts)          
            elif k == 'title':
                #find request keyword in database title
                self.filtered_posts = filter(lambda posts: self.decode_utf8(v) in self.decode_utf8(posts[k]), self.filtered_posts)
                a=0
            elif k == 'author':
                self.filtered_posts = filter(lambda posts: self.decode_utf8(v) in self.decode_utf8(posts[k]), self.filtered_posts)              

            elif k == 'content':
                a=0
            elif k == 'comment':
                a=0
            elif k == 'push':
                for key,val in request[k].iteritems():
                    if key=='all':
                        self.filtered_posts = filter(lambda posts: posts[k][key] >= val, self.filtered_posts)
                    elif key=='score':
                        self.filtered_posts = filter(lambda posts: posts[k][key] >= val, self.filtered_posts)
                    elif key=='good':
                        self.filtered_posts = filter(lambda posts: posts[k][key] >= val, self.filtered_posts)               
                    elif key=='bad':
                        self.filtered_posts = filter(lambda posts: posts[k][key] >= val, self.filtered_posts)
                    elif key=='none':
                        self.filtered_posts = filter(lambda posts: posts[k][key] >= val, self.filtered_posts)
                    else:
                        self.filtered_posts = filter(lambda posts: posts[k][key] >= val, self.filtered_posts)

            elif k == 'date':
                a=0
            elif k == 'ip':
                a=0
            else:
                a=0
 
    #remove user request which value is None, in other words, remain useful slot
    def extract_slot(self, request):        
        request_tmp = request

        for key, val in list(request_tmp.iteritems() ):
            if key == 'comment'  or key =='push':
                for k,v in list(request_tmp[key].iteritems()) :
                    if v is None:
                        del request_tmp[key][k]
                if request_tmp[key] =={}:
                    del request_tmp[key]
            else:
                if val is None:
                    del request_tmp[key]

        return request_tmp

def nlu2req(sentence):
    # split the sentence
    i = 0
    words = []
    chs = list(sentence)
    while i < len(chs):
        word = ''
            
        if chs[i].isdigit() or chs[i].isalpha():
            while i < len(chs) and (chs[i].isdigit() or chs[i].isalpha()):
                word += chs[i]
                i += 1
            words.append(word)
        else:
            word += chs[i]
            word += chs[i + 1]
            word += chs[i + 2]
            words.append(word)
            i += 3

    # turn words into vectors
    if len(words) == 1:
        words.append(words[0])
    X = [word_to_ids[word] if word in word_dict else word_to_ids['<unk>'] for word in words ]

    # predict the result
    intents = intent_rnn.predict_classes(X)[-1]
    labels = label_rnn.predict_classes(X).reshape(-1)

    # print the result
    print(intent_dict[intents])
    for i in range(labels.shape[0]-1):
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
            while j < labels.shape[0]  and label_dict[labels[j]] == label:
                word += words[j]
                j += 1
            i = j

            if label == 'score':
                request['push']['score'] = word
            else:
                request[label] = word
        else:
            i += 1
    return request

# e.g Turn 爆 into 100
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
