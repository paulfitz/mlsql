#!/usr/bin/env python

# Turn this flag on to test just the server part of all this.
TRIAL_RUN = False


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
from src.rule import semQL

import shutil
import subprocess




###################################################################################
# Manual inference material
###################################################################################

import os
import pickle
import sqlite3
from pprint import pprint

import torch

from config import read_arguments_manual_inference
from intermediate_representation import semQL
from intermediate_representation.sem2sql.sem2SQL import transform
from intermediate_representation.sem_utils import alter_column0
from model.model import IRNet
from named_entity_recognition.api_ner.google_api_repository import remote_named_entity_recognition
from named_entity_recognition.pre_process_ner_values import pre_process, match_values_in_database
from preprocessing.process_data import process_datas
from preprocessing.utils import merge_data_with_schema
from spider import spider_utils
from spider.example_builder import build_example
from utils import setup_device, set_seed_everywhere

from spacy.lang.en import English

from termcolor import colored

import json
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
nlp = en_core_web_sm.load()

def _inference_semql(data_row, schemas, model):
    example = build_example(data_row, schemas)

    with torch.no_grad():
        results_all = model.parse(example, beam_size=1)
    results = results_all[0]
    # here we set assemble the predicted actions (including leaf-nodes) as string
    full_prediction = " ".join([str(x) for x in results[0].actions])

    prediction = example.sql_json['pre_sql']
    prediction['model_result'] = full_prediction

    return prediction, example


def _tokenize_question(tokenizer, question):
    # Create a Tokenizer with the default settings for English
    # including punctuation rules and exceptions

    question_tokenized = tokenizer(question)

    return [str(token) for token in question_tokenized]


def _get_entities(question):
    ner_results = remote_named_entity_recognition(row['question'])
    row['ner_extracted_values'] = ner_results['entities']

def _get_entities_local(question):
    doc = nlp(question)
    return [{'type': 'spacy_' + ent.label_, 'name': ent.text} for ent in doc.ents]

def _pre_process_values(row):
    row['ner_extracted_values'] = _get_entities_local(row['question'])

    extracted_values = pre_process(row)

    row['values'] = match_values_in_database(row['db_id'], extracted_values)

    return row


def _semql_to_sql(prediction, schemas):
    alter_column0([prediction])
    result = transform(prediction, schemas[prediction['db_id']])
    return result[0]


def _execute_query(sql, db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute(sql)
    result = cursor.fetchall()

    conn.close()

    return result

###################################################################################
# Manual inference material ends
###################################################################################






handle_request = None

import threading
thread = None
status = "Loading valuenet models, please wait"

app = Flask(__name__)
@app.route('/', methods=['POST'])
def run():
    if handle_request:
        return handle_request(request)
    else:
        return jsonify({"error": status}, 503)
def start():
    app.run(host='0.0.0.0', port=5050)

thread = None
if not(os.environ.get('AUTOEXIT')):
    thread = threading.Thread(target=start, args=())
    thread.daemon = True
    thread.start()

model = None
args = None

if not TRIAL_RUN:

    sys.argv = ['zing',
                '--model_to_load', '/valuenet_pretrained.pt',
                '--database', 'data',
                '--data_set', 'paulfitz',
                '--conceptNet', '/conceptNet']
    args = read_arguments_manual_inference()
    print(args)

    device, n_gpu = setup_device()
    set_seed_everywhere(args.seed, n_gpu)

    grammar = semQL.Grammar()
    model = IRNet(args, device, grammar)
    model.to(device)

    # load the pre-trained parameters
    model.load_state_dict(torch.load(args.model_to_load,map_location=torch.device('cpu')))
    model.eval()
    print("Load pre-trained model from '{}'".format(args.model_to_load))

    nlp = English()
    tokenizer = nlp.Defaults.create_tokenizer(nlp)

    with open(os.path.join(args.conceptNet, 'english_RelatedTo.pkl'), 'rb') as f:
        related_to_concept = pickle.load(f)

    with open(os.path.join(args.conceptNet, 'english_IsA.pkl'), 'rb') as f:
        is_a_concept = pickle.load(f)
    print('loaded all models')


def run_split(split):
    print(split)
    if not TRIAL_RUN:
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
    else:
        print("Trial run")
        with open(os.path.join(split, 'output.txt'), 'w') as f:
            f.write('trial run\n')
        with open(os.path.join(split, 'predict_lf.json'), 'w') as f:
            json.dump({'trial': 'run'}, f)
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
        csv_key = 'csv'
        if csv_key not in request.files:
            csv_key = 'csv[]'
        print(request.files)
        if csv_key not in request.files and not 'sqlite' in request.files:
            raise Exception('please include a csv file or sqlite file')
        if not 'q' in request.form:
            raise Exception('please include a q parameter with a question in it')
        csvs = request.files.getlist(csv_key)
        sqlite_file = request.files.get('sqlite')
        q = request.form['q']

        # brute force removal of any old requests
        if not TRIAL_RUN:
            subprocess.run([
                "bash",
                "-c",
                "rm -rf /cache/case_*"
            ])
        key = "case_" + str(uuid.uuid4())
        data_dir = os.path.join('/cache', key)
        os.makedirs(os.path.join(data_dir, 'data'), exist_ok=True)
        os.makedirs(os.path.join(data_dir, 'original', 'database', 'data'), exist_ok=True)
        print("Key", key)
        for csv in csvs:
            print("Working on", csv)
            table_id = os.path.splitext(csv.filename)[0]
            table_id = re.sub(r'\W+', '_', table_id)
            stream = io.StringIO(csv.stream.read().decode("UTF8"), newline=None)
            add_csv.csv_stream_to_sqlite(table_id, stream, os.path.join(data_dir, 'data',
                                                                        'data.sqlite'))
            stream.seek(0)
        if sqlite_file:
            print("Working on", sqlite_file)
            sqlite_file.save(os.path.join(data_dir, 'data', 'data.sqlite'))
        question_file = os.path.join(data_dir, 'question.json')
        tables_file = os.path.join(data_dir, 'tables.json')
        dummy_file = os.path.join(data_dir, 'dummy.json')
        add_question.question_to_json('data', q, question_file)

        row = {
            'question': q,
            'query': 'DUMMY',
            'db_id': args.database,
            'question_toks': _tokenize_question(tokenizer, q)
        }

        print(colored(f"question has been tokenized to : { row['question_toks'] }", 'cyan', attrs=['bold']))

        with open(dummy_file, 'w') as fout:
            fout.write('[]\n')

        subprocess.run([
            "python",
            "/spider/preprocess/get_tables.py",
            data_dir,
            tables_file,
            dummy_file
        ])

        # valuenet expects different setup to irnet
        shutil.copyfile(tables_file, os.path.join(data_dir, 'original', 'tables.json'))
        database_path = os.path.join(data_dir, 'original', 'database', 'data',
                                     'data.sqlite')
        shutil.copyfile(os.path.join(data_dir, 'data', 'data.sqlite'),
                        database_path)
        
        schemas_raw, schemas_dict = spider_utils.load_schema(data_dir)

        data, table = merge_data_with_schema(schemas_raw, [row])

        pre_processed_data = process_datas(data, related_to_concept, is_a_concept)

        pre_processed_with_values = _pre_process_values(pre_processed_data[0])

        print(f"we found the following potential values in the question: {row['values']}")

        prediction, example = _inference_semql(pre_processed_with_values, schemas_dict, model)

        print(f"Results from schema linking (question token types): {example.src_sent}")
        print(f"Results from schema linking (column types): {example.col_hot_type}")

        print(colored(f"Predicted SemQL-Tree: {prediction['model_result']}", 'magenta', attrs=['bold']))
        print()
        sql = _semql_to_sql(prediction, schemas_dict)

        print(colored(f"Transformed to SQL: {sql}", 'cyan', attrs=['bold']))
        print()
        result = _execute_query(sql, database_path)

        print(f"Executed on the database '{args.database}'. Results: ")
        for row in result:
            print(colored(row, 'green'))

        message = {
            "split": key,
            "result": {
                "sql": sql.strip(),
                "answer": result
            }
        }
        code = 200
    except Exception as e:
        message = { "error": str(e) }
        code = 500
    if debug:
        message['base'] = base
    return jsonify(message), code

handle_request = handle_request0

if thread:
    thread.join()
