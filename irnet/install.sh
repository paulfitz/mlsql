#!/bin/bash

set -e

if [ ! -e venv ]; then
  virtualenv -ppython3 venv
fi

source venv/bin/activate

if [ ! -e WikiSQL ]; then
  git clone https://github.com/salesforce/WikiSQL
  cd WikiSQL
  git checkout 7080c898e13d82395c85e2c2c1de3c914801f4d8
  cd ..
fi

if [ ! -e spider ]; then
  git clone https://github.com/taoyds/spider
  cd spider
  git checkout 0b0c9cad97e4deeef1bc37c8435950f4bdefc141
  cd ..
fi

if [ ! -e IRNet ]; then
  git clone https://github.com/microsoft/IRNet
  cd IRNet
  git checkout 72df5c876f368ae4a1b594e7a740ff966dbbd3ba
  cd ..
fi

if [ ! -e irnet_conceptNet.zip ]; then
  wget https://github.com/paulfitz/mlsql/releases/download/v0.1/irnet_conceptNet.zip
fi
