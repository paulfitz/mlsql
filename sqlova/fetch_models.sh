#!/bin/bash

set -e

function fetch_model() {
  target="$1"
  url="$2"
  if [ ! -e "$target" ]; then
    which wget && {
      wget -O "$target" "$url"
    } || {
      which curl && {
        curl -L "$url" > "$target"
      } || {
        echo "Please fetch $url"
        echo "And place it in $target"
        exit 1
      }
    }
    echo "Downloaded $1"
  else
    echo "Have $1 already, not downloading"
  fi
}

mkdir -p pretrained

fetch_model pretrained/model_bert_best.pt \
  https://github.com/naver/sqlova/releases/download/SQLova-parameters/model_bert_best.pt

fetch_model pretrained/model_best.pt \
  https://github.com/naver/sqlova/releases/download/SQLova-parameters/model_best.pt
