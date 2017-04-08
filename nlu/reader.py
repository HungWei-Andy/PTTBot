import pandas as pd
import numpy as np

def read_dict(filename):
    fin = open(filename, 'r')
    words = fin.read().split()
    fin.close()
    word_to_ids = dict(zip(words, range(len(words))))
    return words, word_to_ids

def read_csv(filename, tolower=True):
    df = pd.read_csv(filename, header=None).fillna('<eos>')
    sentences = df[::3].as_matrix().astype(np.str)
    labels = df[1::3].as_matrix().astype(np.str)
    intents = df[2::3][0].as_matrix().astype(np.str)

    if tolower:
        sentences = np.char.lower(sentences)
        labels = np.char.lower(labels)
        intents = np.char.lower(intents)

    # replace unknown label
    for i, sentence in enumerate(sentences):
	    for j, word in enumerate(sentence):
		    if word != '<eos>' and labels[i, j] == '<eos>':
		        labels[i][j] = '<unk>' 

    return sentences, labels, intents
