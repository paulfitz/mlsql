#!/bin/bash

set -e

function check_running() {
  which docker || {
    echo "Please install docker"
    exit 1
  }
  if [ ! "$(docker ps -q -f name=sqlova)" ]; then
    echo "sqlova not running"
    exit 1
  fi
}

function run_in_docker() {
  docker exec -it sqlova "$@"
}
