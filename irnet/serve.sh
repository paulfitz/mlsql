#!/bin/bash

source venv/bin/activate
PYTHONPATH=$PWD/IRNet:$PWD/server:$PYTHONPATH python server/prediction_server.py
