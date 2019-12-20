#!/bin/bash

cd /
glove="glove.42B.300d"
mkdir -p IRNet/data
if [ ! -e IRNet/data/$glove.txt ]; then
  if [ ! -e cache/$glove.zip ]; then
    cd cache
    wget https://nlp.stanford.edu/data/wordvecs/$glove.zip
    cd ..
  fi
  if [ ! -e cache/$glove.txt ]; then
    cd cache
    unzip $glove.zip
    cd ..
  fi
  ln -s $PWD/cache/$glove.txt IRNet/data/$glove.txt
fi

mkdir -p IRNet/saved_model
if [ ! -e IRNet/saved_model/IRNet_pretrained.model ]; then
  if [ ! -e cache/IRNet_pretrained.model ]; then
    cd cache
    wget https://github.com/paulfitz/mlsql/releases/download/v0.1/IRNet_pretrained.model
    cd ..
  fi
  ln -s $PWD/cache/IRNet_pretrained.model IRNet/saved_model/IRNet_pretrained.model
fi
