import tensorflow as tf
import numpy as np
from collections import Counter
import os
from model import NLG, Config

def str2array(s):
  i = 0
  result = []
  while i < len(s):
    if not s[i].isalnum() and s[i] != '$': # alphbet and number
      result.append(s[i:i+3])
      i += 3
    else: # Chinese characters
      j = i+1
      while j < len(s) and (s[j].isalnum() or s[j] == '$'):
        j += 1
      result.append(s[i:j])
      i = j
    
    # skip spaces
    while i < len(s) and s[i].isspace():
      i += 1
  return np.array(result)

def read_input(filename):
  # read in raw data
  with open(filename) as f:
    lines = [line[:-1].split(', ') for line in f]

  # turn each line into a pair of label and word array
  result = {}
  for line in lines:
    label = int(line[0])
    if label not in result:
      result[label] = []
    result[label].append(str2array(line[1]))
  return result

def build_dict(str_data, filename):
  # counting
  cnt = Counter()
  cnt['<bos>'] += 1
  cnt['<eos>'] += 1
  for key in str_data:
    for line in str_data[key]:
      for word in line:
        cnt[word] += 1

  # prepare words and word2idx
  words = list(cnt)
  word2idx = {}
  for i in range(len(words)):
    word2idx[words[i]] = i

  # write to file
  with open(filename, 'w') as f:
    for word in words:
      f.write(word)
      f.write('\n')
  return word2idx, words

def trans_dict(word2idx, str_data):
  actions = []
  sentences = []
  for key in str_data:
    for line in str_data[key]:
      indices = []
      for word in line:
        indices.append(word2idx[word])
      sentences.append(np.array(indices))
      actions.append(key)
  return np.array(actions), np.array(sentences)

if __name__ == '__main__':
  # prepare training data
  str_data = read_input('template.txt')
  word2idx, words = build_dict(str_data, 'dict.txt')
  actions, sentences = trans_dict(word2idx, str_data)

  # build model
  config = Config()
  config.dict_size = len(words)
  model = NLG(config)
  model.build_trainer(config.batch_size)

  # pad zeros and prepare mask
  mask = np.zeros([len(actions), config.numsteps])
  xs = []
  ys = []
  for i, sentence in enumerate(sentences):
    mask[i, :sentence.shape[0]] = 1
    xs.append(np.r_[word2idx['<bos>'], sentence, word2idx['<eos>'], np.zeros(config.numsteps-sentence.size-2)])
    ys.append(np.r_[sentence, word2idx['<eos>'], np.zeros(config.numsteps-sentence.size-1)])
  xs = np.stack(xs)
  ys = np.stack(ys)
  
  # add noises to actions
  noises = np.random.normal(loc=0, scale=config.noise_scale, size=actions.shape)
  actions = actions + noises
  with open('noise.txt', 'w') as f:
    for noise in noises:
      f.write(str(noise))
      f.write('\n')

  # run training
  sess = tf.InteractiveSession()
  saver = tf.train.Saver()

  idxs = np.arange(config.epochs*config.batch_size).reshape(config.epochs, config.batch_size) % len(actions)
  np.random.shuffle(idxs)

  sess.run(tf.global_variables_initializer())
  print idxs.shape, config.epochs

  f = open('train_loss.txt', 'w')
  for epoch in range(config.epochs):
    idx = idxs[epoch]
    _, cost, scores = sess.run([model.train_op, model.cost, model.scores],
                       feed_dict={
                         model.x: xs[idx].reshape(config.batch_size, -1),
                         model.y: ys[idx].reshape(config.batch_size, -1),
                         model.loss_mask: mask[idx].reshape(config.batch_size, -1),
                         model.state_input: actions[idx]
                       })
    f.write(str(cost)+'\n')
    f.flush()
    print('epoch '+str(epoch)+' cost: '+str(cost))
    print(np.mean(scores))
  f.close()
  #saver.save(sess, os.path.join('models', 'model'))
