#!/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from scipy.spatial.distance import pdist, squareform
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import AffinityPropagation
from sklearn import metrics

from db import load_database, save_database, load_zip
skills = {}

def build_area_vectors(area: str, slice_date: str, skills_index: dict, filename='./skills_vectors.tsv', threshold=5) -> list:
    '''
        Построение n-мерного вектора для каждого навыка.
        n — общее количество вакансий в базе.
        :param threshold — минимальное число вакансий, чтобы навык был учтен
    '''
    vectors = []
    vacancies = []
    #vacancies += load_zip(f'./data/vacancies/{slice_date}.zip', f'{area}.json')
    vacancies += load_zip(f'C:/Users/phomi/PycharmProjects/curumir_1/data/vacancies/{slice_date}.zip', f'{area}.json')
    n = len(vacancies)
    skills = [key for key, value in skills_index.items() if value[0] >= threshold]
    for i in range(len(skills)):
        skill = skills[i]
        vectors.append([skill])
        for j in range(n):
            vacancy = vacancies[j]
            key_skills = [item['name'] for item in vacancy['key_skills']]
            if skill in key_skills:
                vectors[i].append(1)
            else:
                vectors[i].append(0)
    return vectors

# TODO: довольно костыльно прикрученный расчет векторов для регионов
def build_area_vectors_de(area: str, slice_date: str, skills_index: dict, filename='./skills_vectors.tsv', threshold=5) -> list:
    '''
        Построение n-мерного вектора для каждого навыка.
        n — общее количество вакансий в базе.
        :param threshold — минимальное число вакансий, чтобы навык был учтен
    '''
    vectors = []
    vacancies = []
    vacancies += load_database(f'./data/de/{slice_date}/{area}.json')
    n = len(vacancies)
    skills = [key for key, value in skills_index.items() if value[0] >= threshold]
    for i in range(len(skills)):
        skill = skills[i]
        vectors.append([skill])
        for j in range(n):
            vacancy = vacancies[j]
            if skill in vacancy['key_skills']:
                vectors[i].append(1)
            else:
                vectors[i].append(0)
    return vectors

def build_distance_matrix(vectors):
    data = pd.DataFrame.from_records(vectors).set_index(0)
    matrix = pd.DataFrame(squareform(pdist(data, metric='cosine')), columns=data.index, index=data.index)

    plt.figure(figsize=(40,40))
    sns.heatmap(matrix, annot=False, cmap="coolwarm",fmt='.2f', linewidths=.05)
    plt.show()
    return matrix


def calculate_affinity(vectors: list, verbose=False) -> dict:
    data = pd.DataFrame.from_records(vectors).set_index(0)

    matrix = squareform(pdist(data, metric='cosine'))# квадратичная матрица по метрике

    delta = 4 # delta is a free parameter representing the width of the Gaussian kernel. - эмпиричекси
    similarity_matrix = np.exp(- matrix ** 2 / (2. * delta ** 2))# матрица схожести

    affinity = AffinityPropagation(affinity='precomputed', verbose=True)# precomputed-уже посичтана матрица схожести
    affinity.fit(similarity_matrix)# стандартный метод
    cluster_centers = affinity.cluster_centers_indices_  # возвращает индексы центров кластеров, поэтому можно соотнести с лейблами потом
    labels = affinity.labels_

    # TODO: Вот этот кусок хорошо бы засунуть в функцию, а то каждый раз перепечатываю
    clusters = {}
    skills = data.index.tolist()
    n_skills = len(skills)# сколько скилов
    n_clusters = len(cluster_centers)

    readable_centers = [skills[i] for i in cluster_centers] # индексы центра в слова

    silhouette_score = metrics.silhouette_score(similarity_matrix, labels, metric='cosine')
    print(f"Silhouette Coefficient: {silhouette_score:5f}\n")


    for i in range(len(skills)):
        clusters[skills[i]] = int(labels[i])  # потом мы сериализуем это в JSON, а он не знает типы из NumPy
    if verbose:
        print('N of skills:', n_skills)
        print('N of clusters:', n_clusters)
        for j in range(n_clusters):
            print([key for key, value in clusters.items() if value == j])
    print(clusters)
    return clusters, readable_centers, silhouette_score


if __name__ == '__main__':
    vacancies_data = './data/vacancies/'


