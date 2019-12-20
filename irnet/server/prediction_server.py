#!/usr/bin/env python

import sys
sys.path.insert(0, '/IRNet')
sys.path.insert(0, '/server')

import argparse
import json
import os

from flask import Flask, request
from flask import jsonify
import io
import uuid
import re

import add_csv
import add_question

import torch
from src import args as arg
from src import utils
from src.models.model import IRNet
from src.rule import semQL

import shutil

handle_request = None

import threading
thread = None
status = "Loading irnet model, please wait"

app = Flask(__name__)
@app.route('/', methods=['POST'])
def run():
    if handle_request:
        return handle_request(request)
    else:
        return jsonify({"error": status}, 503)
def start():
    app.run(host='0.0.0.0', port=5050)
thread = threading.Thread(target=start, args=())
thread.daemon = True
thread.start()

import subprocess
subprocess.run(["bash", "/server/download.sh"])
subprocess.run(["python", "/server/setup_nltk.py"])

sys.argv = ['zing',
            '--dataset', 'fake',
            '--glove_embed_path', '/cache/glove.42B.300d.txt',
            '--epoch',  '50',
            '--beam_size', '5',
            '--seed', '90',
            '--save', '/tmp/save_name',
            '--embed_size', '300',
            '--sentence_features',
            '--column_pointer',
            '--hidden_size', '300',
            '--lr_scheduler',
            '--lr_scheduler_gammar', '0.5',
            '--att_vec_size', '300',
            '--batch_size', '1',
            '--load_model', '/cache/IRNet_pretrained.model']
arg_parser = arg.init_arg_parser()
args = arg.init_config(arg_parser)
print(args)
grammar = semQL.Grammar()
model = IRNet(args, grammar)
if args.cuda: model.cuda()
print('load pretrained model from %s'% (args.load_model))
pretrained_model = torch.load(args.load_model,
                              map_location=lambda storage, loc: storage)
import copy
pretrained_modeled = copy.deepcopy(pretrained_model)
for k in pretrained_model.keys():
    if k not in model.state_dict().keys():
        del pretrained_modeled[k]

model.load_state_dict(pretrained_modeled)

model.word_emb = utils.load_word_emb(args.glove_embed_path)
print('loaded all models')

import json

def run_split(split):
    print(split)
    args.dataset = split
    sql_data, table_data, val_sql_data,\
        val_table_data = utils.load_dataset(args.dataset, use_small=args.toy)
    json_datas, sketch_acc, acc = utils.epoch_acc(model, args.batch_size, val_sql_data, val_table_data,
                                                  beam_size=args.beam_size)
    print('Sketch Acc: %f, Acc: %f' % (sketch_acc, acc))
    with open(os.path.join(split, 'predict_lf.json'), 'w') as f:
        json.dump(json_datas, f)
    subprocess.run([
        "python",
        "./sem2SQL.py",
        "--data_path",
        split,
        "--input_path",
        os.path.join(split, 'predict_lf.json'),
        "--output_path",
        os.path.join(split, 'output.txt')
    ], cwd="/IRNet")
    results = {}
    with open(os.path.join(split, 'output.txt'), 'r') as f:
        results["sql"] = f.read().strip()
    with open(os.path.join(split, 'predict_lf.json'), 'r') as f:
        results["interpretation"] = json.load(f)
    message = {
        "split": split,
        "result": results
    }
    return message

def serialize(o):
    if isinstance(o, int64):
        return int(o)

def handle_request0(request):
    debug = 'debug' in request.form
    base = ""
    try:
        if not 'csv' in request.files:
            raise Exception('please include a csv file')
        if not 'q' in request.form:
            raise Exception('please include a q parameter with a question in it')
        csv = request.files['csv']
        q = request.form['q']
        table_id = os.path.splitext(csv.filename)[0]
        table_id = re.sub(r'\W+', '_', table_id)

        # brute force removal of any old requests
        subprocess.run([
            "rm",
            "-rf",
            "/cache/case_*"
        ])
        stream = io.StringIO(csv.stream.read().decode("UTF8"), newline=None)
        key = "case_" + str(uuid.uuid4())
        data_dir = os.path.join('/cache', key)
        os.makedirs(os.path.join(data_dir, 'data'), exist_ok=True)
        add_csv.csv_stream_to_sqlite(table_id, stream, os.path.join(data_dir, 'data',
                                                                    'data.sqlite'))
        stream.seek(0)
        question_file = os.path.join(data_dir, 'question.json')
        tables_file = os.path.join(data_dir, 'tables.json')
        dummy_file = os.path.join(data_dir, 'dummy.json')
        add_question.question_to_json('data', q, question_file)
        with open(dummy_file, 'w') as fout:
            fout.write('[]\n')

        subprocess.run([
            "python",
            "/spider/preprocess/get_tables.py",
            data_dir,
            tables_file,
            dummy_file
        ])
        subprocess.run([
            "bash",
            "./run_me.sh",
            question_file,
            tables_file,
            os.path.join(data_dir, 'dummy2.json')
        ], cwd="/IRNet/preprocess")
        shutil.copyfile(question_file, os.path.join(data_dir, 'dev.json'))
        shutil.copyfile(question_file, os.path.join(data_dir, 'train.json'))
        message = run_split(data_dir)
        code = 200
    except Exception as e:
        message = { "error": str(e) }
        code = 500
    if debug:
        message['base'] = base
    return jsonify(message), code

handle_request = handle_request0
thread.join()
