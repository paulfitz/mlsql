#!/bin/bash

. utils.sh

check_running

run_in_docker python /opt/sqlova/add_question.py "$@"
