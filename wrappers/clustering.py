#!/bin/env python3
# -*- coding: utf-8 -*-

import math
from db import  load_database, load_zip
import vectors
import preprocessing_ru as pr


def area_affinity_clusters(area=1317, slice_date='2020-08-05', force=False):
    #Посчитать кластеры навыков для вакансий региона, используя Affinity Propagation
    clusters = {}
    skills_index = {}
    region_data = load_zip(f'./data/vacancies/{slice_date}.zip', f'{area}.json')
    #region_data = load_zip(f'C:/Users/phomi/PycharmProjects/curumir_1/data/vacancies/{slice_date}.zip', f'{area}.json')
    n_vacancies = len(region_data)
    threshold = math.ceil(n_vacancies*0.01)  # 10% порог от общего числа с округлением вверх

    for vacancy in region_data:
        for _skill in vacancy['key_skills']:
            skill = _skill['name']
            if skill not in skills_index:
                skills_index[skill] = [1, [vacancy['id']], ' '.join(pr.norm_preprocess(skill))]  # добавлена нормальная форма
            else:
                skills_index[skill][0] += 1
                skills_index[skill][1].append(vacancy['id'])  # здесь связывать навыки и id
    #print(skills_index)
    vector_data = f'./vectors/{area}.tsv'
    #vector_data = f'C:/Users/phomi/PycharmProjects/curumir_1/vectors/{area}.tsv'
    area_vectors = vectors.build_area_vectors(area, slice_date, skills_index, vector_data, threshold=threshold)
    clusters, centers, silhouette = vectors.calculate_affinity(area_vectors)

    # TODO: слегка костыльно это отдавать таким образом, но пока сгодится
    return (n_vacancies, threshold, clusters, centers, silhouette)


def area_affinity_clusters_de(area='Sachsen-Anhalt', slice_date='2020-03-07', force=False):
    #Посчитать кластеры навыков для вакансий региона, используя Affinity Propagation
    clusters = {}
    skills_index = {}
    region_data = load_database(f'./data/de/{slice_date}/{area}.json')

    n_vacancies = len(region_data)
    threshold = math.ceil(n_vacancies*0.01)  # 10% порог от общего числа с округлением вверх

    for vacancy in region_data:
        for skill in vacancy['key_skills']:
            if skill not in skills_index:
                skills_index[skill] = [1, [vacancy['id']]]
            else:
                skills_index[skill][0] += 1
                skills_index[skill][1].append(vacancy['id'])

    vector_data = f'./vectors/{area}.tsv'
    area_vectors = vectors.build_area_vectors_de(area, slice_date, skills_index, vector_data, threshold=threshold)
    clusters, centers, silhouette = vectors.calculate_affinity(area_vectors)

    # TODO: слегка костыльно это отдавать таким образом, но пока сгодится
    return (n_vacancies, threshold, clusters, centers, silhouette)


if __name__ == '__main__':
    vacancies_data = './data/vacancies/'
