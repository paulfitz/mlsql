#!/bin/bash

set -o errexit
set -o errtrace
set -o pipefail
set -e

trap 'cleanup' EXIT
trap 'echo "Exiting on SIGINT"; exit 1' INT
trap 'echo "Exiting on SIGTERM"; exit 1' TERM

PIDS=()

cleanup() {
  kill "${PIDS[@]}"
  wait "${PIDS[@]}"
  exit 0
}

cd /opt/corenlp/src
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer &
PIDS+=($!)

# corenlp should be up before we start serving sqlova, or we could
# fail to annotate a request.
while ! wget http://localhost:9000 < /dev/null > /dev/null 2>&1; do
  echo Waiting for nlp server
  sleep 1
done

cd /opt/sqlova
python3 ./predict.py \
              --bert_type_abb uL \
              --model_file pretrained/model_best.pt \
              --bert_model_file pretrained/model_bert_best.pt \
              --bert_path support \
              --data_path /opt/sqlova \
              --result_path /opt/sqlova &
PIDS+=($!)

wait "${PIDS[@]}"
