#!/bin/bash

. utils.sh

if [[ -z "$1" ]]; then
  echo "Please supply split name"
  exit 1
fi

check_running
./fetch_models.sh

run_in_docker python /opt/sqlova/annotate_ws.py --split "$1" --din /share --dout /share
run_in_docker python /opt/sqlova/predict.py --split "$1" \
              --bert_type_abb uL \
              --model_file /share/pretrained/model_best.pt \
              --bert_model_file /share/pretrained/model_bert_best.pt \
              --bert_path /share/support \
              --data_path /share \
              --result_path /share
