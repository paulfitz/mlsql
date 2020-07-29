#!/bin/bash

cp -r /maintain/example_data/ /valuenet/data/paulfitz
cd /
source venv/bin/activate

if [ ! -e valuenet_pretrained.pt ]; then
  wget https://github.com/paulfitz/mlsql/releases/download/v0.1/valuenet_pretrained.pt
fi

(
echo "import nltk"
echo "nltk.download('averaged_perceptron_tagger')"
) | python

cd /valuenet
PYTHONPATH=/valuenet/src python /server/prediction_server.py
