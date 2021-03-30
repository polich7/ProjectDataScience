#!/bin/env python3
# -*- coding: utf-8 -*-

import json
import io
import zipfile

def load_database(db_file):
    with open(db_file, 'r', encoding='utf-8') as db:
        return json.load(db)

def save_database(data, db_file, sort=False):
    with open(db_file, 'w', encoding='utf-8') as db:
        json.dump(data, db, ensure_ascii=False, indent=0, sort_keys=sort)


def load_zip(zip_file, db_file):
    with zipfile.ZipFile(zip_file) as zip_root:
        try:
            with io.TextIOWrapper(zip_root.open(db_file, mode='r'), encoding='utf-8') as db:
                return json.load(db)
        except KeyError:
            return []



