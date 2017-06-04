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

###################
##            DQN          ##
###################

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=50000, window_length=1)
policy = BoltzmannQPolicy()

# del(model)
# model = load_model('PTTBot_model.h5')
dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=10, target_model_update=1e-2, policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])
dqn.load_weights('dqn_{}_weights.h5f'.format(ENV_NAME))

# Okay, now it's time to learn something! We visualize the training here for show, but this
# slows down training quite a lot. You can always safely abort the training prematurely using
# Ctrl + C.
dqn.fit(env, nb_steps=10000, visualize=True, verbose=2)


# After training is done, we save the final weights.
dqn.save_weights('dqn_{}_weights.h5f'.format(ENV_NAME), overwrite=True)


# dqn.load_weights('dqn_PTTBot_weights.h5f')
# Finally, evaluate our algorithm for 5 episodes.
dqn.test(env, nb_episodes=5, visualize=True)


###################
##          SARSA        ##
###################
# sarsa = SarsaAgent(model=model, nb_actions=nb_actions, nb_steps_warmup=10, policy=policy)
# sarsa.compile(Adam(lr=1e-3), metrics=['mae'])
# sarsa.fit(env, nb_steps=50000, visualize=True, verbose=2)
