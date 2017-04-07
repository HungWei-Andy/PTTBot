from collections import Counter
import pandas as pd
import reader
import os

def build_dict(arr, filename, eos=True, unk=True):
    cnt = Counter()
    for word in arr.reshape(-1):
        if word != '<eos>':
            cnt[word] += 1

    dict_out = open(filename, 'w')
    if eos:
        dict_out.write('<eos>'+'\n')
    for idx, word in enumerate(list(cnt)):
        dict_out.write(word+'\n')
    if unk and '<unk>' not in cnt:
        dict_out.write('<unk>')
    dict_out.close()

sentences, labels, intents = reader.read_csv('./data/training_data.csv')
build_dict(sentences, './dict/word_dict.txt')
build_dict(labels, './dict/label_dict.txt')
build_dict(intents, './dict/intent_dict.txt', eos=False, unk=False)

