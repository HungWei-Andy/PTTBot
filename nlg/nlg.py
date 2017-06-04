# -*- coding: utf-8 -*- 
import tensorflow as tf
import numpy as np
from collections import Counter
import os
from model import NLG, Config
from os.path import join, dirname, abspath

def read_dict(filename):
  words = []
  word2idx = {}
  with open(filename) as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
      words.append(line[:-1])
      word2idx[line[:-1]] = i
  return words, word2idx


cur_dir = dirname(abspath(__file__))
dict_file = join(cur_dir, 'dict.txt')
words, word2idx = read_dict(dict_file)


restore_path = os.path.join(cur_dir, 'models', 'model')

config = Config()
config.dict_size = len(words)
config.batch_size = 1
model = NLG(config)
model.build_runner(config.batch_size)

sess = tf.InteractiveSession()
sess.run(tf.global_variables_initializer())

saver = tf.train.Saver()
saver.restore(sess, restore_path)

def generate_template(action):
  result = []
  last_word = np.array([word2idx['<bos>']])
  state = None
  action = np.array([action])
  itera = 0
  while itera <= 40 and last_word != word2idx['<eos>']:
    itera += 1
    
    if state is None:
      pred, state, logits = sess.run([model.pred, model.state, model.logits], feed_dict={
                               model.x: last_word,
                               model.state_input: action + np.random.normal(loc=0, scale=config.noise_scale+0.1)
                             })
    else:
      pred, state, logits = sess.run([model.pred, model.state, model.logits], feed_dict={
                               model.x: last_word,
                               model.init_state: state
                             })
    result.append(words[pred[0]])
    last_word = pred
  if last_word == word2idx['<eos>']:
    result = result[:-1]
  return result

def fill_template(template, slots):
  state = slots['state']
  posts = slots['post']
  result = ''
  for i, word in enumerate(template):
    if word == '$posts': # replace posts
      result += '<br>\n'
      for i in range(min(len(posts), 20)):
        result += '(' + str(i) + ') '
        result += '<a href="'+posts[i]['link']+'">'+posts[i]['title']+'</a>'
        result += '<br>\n'
    
    elif word == '$board': # replace board
      if state is None or 'board' not in state:
        result += '(´･ω･`)'
      else:
        result += state['board']
    
    elif word == '$comment': # replace comment
      result += '<br>\n'
      for i in range(min(len(posts), 20)):
        if len(posts[i]['comment']) > 5:
          result += 'post '+str(i)+', 5th floor comment: '
          result += posts[i]['comment']['5'] + '<br>\n'
        else:
          result += 'post '+str(i)+', 1st floor comment: '
          result += posts[i]['comment']['1'] + '<br>\n'
      result += '<br>\n'
    
    elif word.isalpha():
      result += word + ' '
    
    else:
      result += word
  return result

def generate(action, slots):
  template = generate_template(action)
  return fill_template(template, slots)


print(generate(0, {'state': None, 'post': None}))
print('================================================')


if __name__ == '__main__':
  for i in range(9):
    print(i)
    print(generate(i, None))
