#!/bin/bash

function run() {
  echo " "
  echo "=================================================="
  echo "$2"
  curl -F "csv=@$1.csv" -F "q=$2" localhost:5050
}

run iris "how many setosa rows are there"
run iris "what is the average petal width for virginica"
run iris "what is the longest sepal for versicolor"
run bridges "how long is throgs neck"
run bridges "who designed the george washington"
run bridges "how many bridges are there"
run bridges "how many bridges are designed by O. H. Ammann"
run bridges "which bridges are longer than 2000"
run bridges "how many bridges are longer than 2000"
run bridges "what is the shortest length"
