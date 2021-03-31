#!/bin/env python3
# -*- coding: utf-8 -*-

import flask
import os
import wrappers.clustering as clustering
import preprocessing_ru as pr
import json
PROJECT = 'Curumir'

app = flask.Flask(PROJECT)
app.debug = True

regions = {}
regions_de = [
    'Baden-Württemberg', 'Bayern', 'Berlin', 'Brandenburg', 'Bremen', 'Hamburg', 'Hessen', 'Mecklenburg-Vorpommern', 
    'Niedersachsen', 'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland', 'Sachsen', 'Sachsen-Anhalt', 'Schleswig-Holstein', 'Thüringen'
]

vacancies = []

vacancy_data = {}

@app.route('/')
def index():
    return flask.render_template('clusters.html')

@app.route('/finder')
def finder():
    return flask.render_template('finder.html')


@app.route('/country', methods=['GET'])
def get_country_data():
    country = flask.request.args['c']
    if country == 'ru':
        return flask.jsonify(
            {code: regions[code] for code in sorted(regions, key=int)}, 
            sorted([arc[:-4] for arc in os.listdir('./data/vacancies/')]))
    elif country == 'de':
        return flask.jsonify(
            {index: region for index, region in enumerate(regions_de)}, 
            sorted([arc for arc in os.listdir('./data/de/')]))
    else:
        return []

@app.route('/clusters', methods=['GET'])
def get_area_clusters():
    country = flask.request.args['country']
    area = int(flask.request.args['area'])
    date = flask.request.args['date']
    if country == 'ru':
        area_clusters = list(clustering.area_affinity_clusters(area, date))
    else:
        area_de = regions_de[area]
        area_clusters = list(clustering.area_affinity_clusters_de(area_de, date))
    clusters = area_clusters[2]
    ready_clusters = []
    for j in range(len(area_clusters[3])): # сортировка для читаемых скиллов
        ready_clusters.append(sorted([key for key, value in clusters.items() if value == j]))
    area_clusters[2] = ready_clusters
    return flask.jsonify(area_clusters)


@app.route('/context', methods=['GET'])
def get_skill_context():
    context_skills_prep=[]
    '''Отдаем кластеры, содержащие введенные пользователем компетенции'''
    country = flask.request.args['country']
    area = int(flask.request.args['area'])
    date = flask.request.args['date']
    context_skills = str(flask.request.args['skills']).split(',')
    for item in context_skills:  # нормализация введенных навыков
        context_skills_prep.append(' '.join(pr.norm_preprocess(item)))
    if country == 'ru':
        area_clusters = list(clustering.area_affinity_clusters(area, date))
    else:
        area_de = regions_de[area]
        area_clusters = list(clustering.area_affinity_clusters_de(area_de, date))
    clusters = area_clusters[2]
    ready_clusters = []
    for j in range(len(area_clusters[3])):
        ready_clusters.append(sorted([key for key, value in clusters.items() if value == j]))
    ready_clusters = list(filter(lambda cluster: any([skill for skill in cluster if ' '.join(pr.norm_preprocess(skill)) in context_skills_prep]), ready_clusters))  # сравнение норм. форм
    area_clusters[2] = ready_clusters  # наверное, не надо отдавать прям все, но этим займусь в ближайшее время
    return flask.jsonify(area_clusters)

if __name__ == "__main__":
    with open('./data/regions.json', 'r', encoding='utf-8') as f:
        regions= json.load(f)


    app.run(host='0.0.0.0', port=9001)
