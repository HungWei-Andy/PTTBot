import pandas as pd

def read_dict(filename):
	fin = open(filename, 'r')
	words = fin.read().split()
	word_to_ids = dict(zip(words, range(len(words))))
	return words, word_to_ids

def read_csv(filename):
    df = pd.read_csv(filename, header=None).fillna('<eos>')
    sentences = df[::3].as_matrix()
    labels = df[1::3].as_matrix()
    intents = df[2::3][0].as_matrix()

    # replace unknown label
    for i, sentence in enumerate(sentences):
	    for j, word in enumerate(sentence):
		    if word != '<eos>' and labels[i, j] == '<eos>':
		        labels[i][j] = '<unk>' 

    return sentences, labels, intents