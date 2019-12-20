#!/usr/bin/env python

# Add a line of json representing a question into <split>.jsonl
# Call as:
#   python add_question.py <split> <table id> <question>
#
# This utility is not intended for use during training.  A dummy label is added to the
# question to make it loadable by existing code.
#
# For example, suppose we downloaded this list of us state abbreviations:
#   https://vincentarelbundock.github.io/Rdatasets/csv/Ecdat/USstateAbbreviations.csv
# Let's rename it as something short, say "abbrev.csv"
# Now we can add it to a split called say "playground":
#   python add_csv.py playground abbrev.csv
# And now we can add a question about it to the same split:
#   python add_question.py playground abbrev "what state has ansi digits of 11"
# The next step would be to annotate the split:
#   python annotate_ws.py --din $PWD --dout $PWD --split playground
# Then we're ready to run prediction on the split with predict.py

import argparse, csv, json

import json
import nltk
import sys

nltk.download('punkt')

def encode_question(db_id, question):
    question_toks = nltk.word_tokenize(question)
    result = [{
        "db_id": db_id,
        "query": "SELECT count(*) FROM something",
        "question": question,
        "question_toks": question_toks,
        "sql": {
            "except": None,
            "from": {
                "conds": [],
                "table_units": [
                    [
                        "table_unit",
                        1
                    ]
                ]
            },
            "groupBy": [],
            "having": [],
            "intersect": None,
            "limit":  None,
            "orderBy": [],
            "select": [
                False,
                [
                    [
                        1,
                        [
                            0,
                            [
                                0,
                                0,
                                False
                            ],
                            None
                        ]
                    ]
                ]
            ],
            "union": None,
            "where": [
                [
                    False,
                    1,
                    [
                        0,
                        [
                            0,
                            1,
                            False
                        ],
                        None
                    ],
                    1.0,
                    None
                ]
            ]
        }
    }]
    return result

def question_to_json(table_id, question, json_file_name):
    record = encode_question(table_id, question)
    with open(json_file_name, 'w') as fout:
        json.dump(record, fout)
        fout.write('\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('split')
    parser.add_argument('table_id')
    parser.add_argument('question', type=str, nargs='+')
    args = parser.parse_args()
    json_file_name = '{}.jsonl'.format(args.split)
    question_to_json(args.table_id, " ".join(args.question), json_file_name)
    print("Added question (with dummy label) to {}".format(json_file_name))
