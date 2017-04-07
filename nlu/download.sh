#!/bin/bash
wget https://www.dropbox.com/s/esv9jhz8dh67ikw/intent_rnn.h5
wget https://www.dropbox.com/s/8ivyulw0zm1i1fk/label_rnn.h5
mkdir models
mv intent_rnn.h5 models
mv label_rnn.h5 models
