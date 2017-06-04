from os import environ
import os, sys
import agent_server

####################### Server ################################
from flask import Flask
app = Flask(__name__)

from time import gmtime, strftime
log_file = os.path.join('log', strftime('%Y-%m-%d_%H-%M-%S.txt', gmtime()))
logerr_file = os.path.join('logerr', strftime('%Y-%m-%d_%H-%M-%S.txt', gmtime()))
log = open(log_file, 'w')
logerr = open(logerr_file, 'w')
sys.stdout = log
sys.stderr = logerr

pttbot = agent_server.PTTBot(agent_server.dqn)

@app.route('/')
def home():
	print('in homepage')
	with open('index.html') as f:
		homepage = f.read()
	return homepage, 200

@app.route('/query/<sentence>')
def query(sentence):
	global pttbot
        sentence = sentence.decode('utf-8').encode('utf-8')
	if sentence == 'reset':
		pttbot._reset()
		res = 'PTTBot has been reset!'
	else:
		res = pttbot.process(sentence)	
	print('in query:', sentence)
	return res, 200

from os import environ

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', '140.112.251.159')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
