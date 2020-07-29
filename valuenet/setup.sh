#!/bin/bash

set -e

if [ ! -e valuenet ]; then
  git clone https://github.com/paulfitz/valuenet -b mlsql_tweaks
fi

source venv/bin/activate
pip install -r /requirements.txt
python -m spacy download en_core_web_sm 

sed -i "s/	/        /g" spider/preprocess/get_tables.py 
sed -i "s/print \(.*\)/print(\1)/" spider/preprocess/get_tables.py 
sed -i "s/prev_/#prev_/" spider/preprocess/get_tables.py 
sed -i "s/cur_/#cur_/" spider/preprocess/get_tables.py 
sed -i "s/if df in ex_tabs.*/if False:/" spider/preprocess/get_tables.py 

sed -i "s/open(file_name)/open(file_name, 'r', encoding='utf=8')/" IRNet/src/utils.py
sed -i "s/(total)/(max(total,0.00001))/g" IRNet/src/utils.py
sed -i "s/^                continue/                print('continue')/" IRNet/src/utils.py

if [ ! -e IRNet/preprocess/conceptNet ]; then
  unzip irnet_conceptNet.zip
  ln -s $PWD/conceptNet IRNet/preprocess/conceptNet
  cd IRNet/preprocess
  sed -i 's/\r//g' run_me.sh
  cd ../..
fi

mkdir -p cache
