#!/bin/bash
wget https://www.dropbox.com/s/xe1omytsq37x5fm/data.zip

unzip data.zip
rm data.zip

mv models nlu/
mv database kp/
