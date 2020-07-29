#!/usr/bin/env python

# Add a CSV file as a table into <split>.db and <split>.tables.jsonl
# Call as:
#   python add_csv.py <split> <filename.csv>
# For a CSV file called data.csv, the table will be called table_data in the .db
# file, and will be assigned the id 'data'.
# All columns are treated as text - no attempt is made to sniff the type of value
# stored in the column.

import argparse, csv, json, os
import records

def get_table_name(table_id):
    return '{}'.format(table_id)

def csv_stream_to_sqlite(table_id, f, sqlite_file_name):
    db = records.Database('sqlite:///{}'.format(sqlite_file_name))
    cf = csv.DictReader(f, delimiter=',')
    # columns = [f'col{i}' for i in range(len(cf.fieldnames))]
    columns = cf.fieldnames
    simple_name = dict(zip(cf.fieldnames, columns))
    rows = [dict((simple_name[name], val) for name, val in row.items())
            for row in cf]
    types = {}
    for name in columns:
        good_float = 0
        bad_float = 0
        good_int = 0
        bad_int = 0
        for row in rows:
            val = row[name]
            try:
                float(val)
                good_float += 1
            except:
                bad_float += 1
            try:
                int(val)
                good_int += 1
            except:
                bad_int += 1
        if good_int >= 2 * bad_int and good_int >= good_float:
            types[name] = 'integer'
        elif good_float >= 2 * bad_float and good_float > 0:
            types[name] = 'real'
        else:
            types[name] = 'text'
    schema = ', '.join([f'{name} {types[name]}' for name in columns])
    tname = get_table_name(table_id)
    db.query(f'DROP TABLE IF EXISTS {tname}')
    db.query(f'CREATE TABLE {tname} ({schema})')
    ccolumns = [f':{name}' for name in columns]
    print(f'INSERT INTO {tname}({",".join(columns)}) VALUES({",".join(ccolumns)})')
    db.bulk_query(f'INSERT INTO {tname}({",".join(columns)}) VALUES({",".join(ccolumns)})',
                  rows)
    return True

def csv_to_sqlite(table_id, csv_file_name, sqlite_file_name):
    with open(csv_file_name) as f:
        return csv_stream_to_sqlite(table_id, f, sqlite_file_name)

def csv_stream_to_json(table_id, f, json_file_name):
    cf = csv.DictReader(f, delimiter=',')
    record = {}
    record['header'] = [(name or 'col{}'.format(i)) for i, name in enumerate(cf.fieldnames)]
    record['page_title'] = None
    record['types'] = ['text'] * len(cf.fieldnames)
    record['id'] = table_id
    record['caption'] = None
    record['rows'] = [list(row.values()) for row in cf]
    record['name'] = get_table_name(table_id)
    with open(json_file_name, 'a+') as fout:
        json.dump(record, fout)
        fout.write('\n')
    return record

def csv_to_json(table_id, csv_file_name, json_file_name):
    with open(csv_file_name) as f:
        csv_stream_to_json(table_id, f, json_file_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('split')
    parser.add_argument('file', metavar='file.csv')
    args = parser.parse_args()
    table_id = os.path.splitext(os.path.basename(args.file))[0]
    csv_to_sqlite(table_id, args.file, '{}.db'.format(args.split))
    csv_to_json(table_id, args.file, '{}.tables.jsonl'.format(args.split))
    print("Added table with id '{id}' (name '{name}') to {split}.db and {split}.tables.jsonl".format(
        id=table_id, name=get_table_name(table_id), split=args.split))

