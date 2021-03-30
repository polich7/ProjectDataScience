#!/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import datetime
import logging

# https://github.com/hhru/api/blob/master/docs/vacancies.md — доки по API вакансий

API = 'https://api.hh.ru'
skills = {}
total_vacancies = {}


def load_regions():
    with open('./data/regions.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_regions_map():
    with open('./data/regions_map.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_totals():
    with open('./data/found.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_skills():
    with open('./data/skills.json', 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':
    logging.basicConfig(filename=f'hh_{datetime.date.today().isoformat()}.log', level=logging.INFO)
    vacancies_data = './data/vacancies/'
    check_date = datetime.date.today().isoformat()
    if not os.path.exists(vacancies_data+check_date):
        os.mkdir(vacancies_data+check_date)
    regions = load_regions()


