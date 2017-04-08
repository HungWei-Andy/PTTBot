#!/bin/bash
wget https://www.dropbox.com/s/4nztn154r9teqkm/intent_rnn.h5
wget https://www.dropbox.com/s/uj9ugeowi2wvwqt/label_rnn.h5
mkdir models
mv intent_rnn.h5 models
mv label_rnn.h5 models
