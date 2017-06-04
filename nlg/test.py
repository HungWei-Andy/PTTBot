# -*- coding: utf-8 -*-
import nlg
import nltk
from train import read_input

testing_epoch = 500

def evaluate(sentences, gts, style='max'):
  score = 0
  for i in range(len(gts)):
    smooth = nltk.translate.bleu_score.SmoothingFunction()
    bleu_score = nltk.translate.bleu_score.sentence_bleu(sentences, gts[i], smoothing_function=smooth.method2)

    if style == 'max':
      score = max(score, bleu_score)
    elif style == 'avg':
      score += bleu_score
    else:
      error('no this type of evaluation')
  
  if style == 'avg':
    score /= 1.0*len(gts)
  return score

def main():
  # read groundtruths
  test_data = read_input('template_test.txt')
  
  # run evaluation
  f = open('test_score.txt', 'w')
  for i in range(9):
    print('testing on label '+str(i))
    sentences = []
    for cnt in range(testing_epoch):
      sentences.append(nlg.generate_template(i))
    
    max_bleu_score = evaluate(sentences, test_data[i], style='max')
    average_bleu_score = evaluate(sentences, test_data[i], style='avg')
    f.write(str(i)+'\n')
    f.write('max: '+str(max_bleu_score)+'\n')
    f.write('avg: '+str(average_bleu_score)+'\n')

if __name__ == '__main__':
  main()
