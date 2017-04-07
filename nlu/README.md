# NLU: Bidirectional RNN

Here is the module of language understanding of the robot.

It contains three modules:

1. **Preprocessing** - build_dicts.py
    * Read the file 'training_data.csv' and build three dictionaries 'word_dict.txt', 'intent_dict.txt', 'label_dict.txt'.
        * 'word_dict.txt' is the dictionary of the input sentence where each word is a single character or a english word or a number.
        * 'intent_dict.txt' is the dictionary of the function names, e.g., find_post.
        * 'label_dict.txt' is the dictionary of the labels, e.g., board.

2. **Building RNN and training** - train_lm.py
3. **Testing the trained RNN** - run.py

## Training
To train the network, run 'train.sh'.
```
$ bash train.sh
```

## Testing
After the training, run 'test.sh' to input one sentence from command line and decode the sentence.
```
$ bash test.sh
```

## Pretrained-model
To use the pretrained model, please run 'download.sh' before testing:
```txt
$ bash download.sh
```

