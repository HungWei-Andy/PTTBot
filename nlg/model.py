import tensorflow as tf
import numpy as np

def make_cell(size, style='gru'):
  if style == 'lstm':
    return tf.contrib.rnn.BasicLSTMCell(size, forget_bias=1.0, state_is_tuple=True)
  if style == 'gru':
    return tf.contrib.rnn.GRUCell(size)

class Config(object):
  numsteps = 30
  hidden_size = 256
  mid_size = 50
  input_size = 256
  max_grad_norm = 5
  batch_size = 20
  epochs = 2000
  lr = 0.01
  noise_scale = 0.1

class NLG(object):
  def __init__(self, config):
    self.numsteps = config.numsteps
    self.hidden_size = config.hidden_size
    self.input_size = config.input_size
    self.dict_size = config.dict_size
    self.mid_size = config.mid_size
    self.max_grad_norm = config.max_grad_norm
    self._lr = config.lr

  def build_trainer(self, batch_size):
    self.x = tf.placeholder(tf.int32, shape=[batch_size, self.numsteps])
    self.y = tf.placeholder(tf.int32, shape=[batch_size, self.numsteps])
    self.loss_mask = tf.placeholder(tf.float32, shape=[batch_size, self.numsteps])
    self.state_input = tf.placeholder(tf.float32, shape=[batch_size])

    # build variables    
    with tf.variable_scope('variable') as scope:
      mid_w = tf.get_variable('mid_w', initializer=tf.random_normal([1, self.mid_size],0.0,0.01))
      mid_b = tf.get_variable('mid_b', initializer=tf.zeros([self.mid_size]))
      state_w = tf.get_variable('state_w', initializer=tf.random_normal([self.mid_size, self.hidden_size],0.0,0.01))
      state_b = tf.get_variable('state_b', initializer=tf.zeros([self.hidden_size]))
      output_w = tf.get_variable('output_w', initializer=tf.random_normal([self.hidden_size, self.dict_size], 0.0, 0.01))
      output_b = tf.get_variable('output_b', initializer=tf.zeros([self.dict_size]))
      input_w = tf.get_variable('input_w', initializer=tf.random_normal([self.dict_size, self.input_size], 0.0, 0.01))
      input_b = tf.get_variable('input_b', initializer=tf.random_normal([self.input_size], 0.0, 0.01))

    # prepare inputs
    with tf.device('/cpu:0'):
      inputs = tf.nn.embedding_lookup(input_w, self.x) + input_b
      print(inputs.shape)
      mid = tf.matmul(tf.reshape(self.state_input, [-1, 1]), mid_w) + mid_b
      state = tf.matmul(mid, state_w) + state_b
      print(state.shape)
    # build rnn
    cell = make_cell(self.hidden_size)
    
    scores = []
    preds = []
    print(state.shape)
    print(cell.zero_state(batch_size, tf.float32).shape)
    with tf.variable_scope("RNN"):
      for time_step in range(self.numsteps):
        print('building time_step '+str(time_step)+'...')
        if time_step > 0:
          tf.get_variable_scope().reuse_variables()
        (cell_output, state) = cell(inputs[:, time_step], state)
        logits = tf.matmul(cell_output, output_w) + output_b
        scores.append(logits)
        print(logits.shape)
        preds.append(tf.argmax(logits, axis=1))
    self.state = state
    self.scores = scores	
    self.preds = preds

    # build loss
    self.loss = loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
                                   logits = tf.stack(scores, axis=1), labels = self.y)
    print(self.loss.shape)
    self.loss = self.loss * self.loss_mask
    
    # build training operaions
    self.cost = cost = tf.reduce_mean(loss)
    self.train_op = tf.train.AdamOptimizer(learning_rate=self._lr).minimize(self.cost)

  def build_runner(self, batch_size):
    self.x = tf.placeholder(tf.int32, shape=[batch_size])
    self.state_input = tf.placeholder(tf.float32, shape=[batch_size])

    
    print(self.x.shape)
    print(self.state_input.shape)
    # build variables    
    with tf.variable_scope('variable') as scope:
      mid_w = tf.get_variable('mid_w', initializer=tf.random_normal([1, self.mid_size],0.0,0.01))
      mid_b = tf.get_variable('mid_b', initializer=tf.zeros([self.mid_size]))
      state_w = tf.get_variable('state_w', initializer=tf.random_normal([self.mid_size, self.hidden_size],0.0,0.01))
      state_b = tf.get_variable('state_b', initializer=tf.zeros([self.hidden_size]))
      output_w = tf.get_variable('output_w', initializer=tf.random_normal([self.hidden_size, self.dict_size], 0.0, 0.01))
      output_b = tf.get_variable('output_b', initializer=tf.zeros([self.dict_size]))
      input_w = tf.get_variable('input_w', initializer=tf.random_normal([self.dict_size, self.input_size], 0.0, 0.01))
      input_b = tf.get_variable('input_b', initializer=tf.random_normal([self.input_size], 0.0, 0.01))

    # prepare inputs
    with tf.device('/cpu:0'):
      inputs = tf.nn.embedding_lookup(input_w, self.x) + input_b
      print(inputs.shape)
      mid = tf.matmul(tf.reshape(self.state_input, [-1, 1]), mid_w) + mid_b
      self.init_state = tf.matmul(mid, state_w) + state_b

    # build rnn
    cell = make_cell(self.hidden_size)

    state = self.init_state
    with tf.variable_scope("RNN"):
      (cell_output, state) = cell(inputs, state)
      logits = tf.matmul(cell_output, output_w) + output_b
      self.logits = logits
      self.pred = tf.argmax(logits, axis=1)
    self.state = state
