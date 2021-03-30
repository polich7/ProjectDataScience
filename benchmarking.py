import math
from db import  load_zip
import vectors
import preprocessing_ru as pr
import pandas as pd
import nltk


label_numbers={}

def vacancy_name_comparison(dict):  # функция оценки кластеров по названиям
    for id_0, (x, value1) in enumerate(dict.items()):
        for id_1, (y, value2) in enumerate(dict.items()):
            if id_0<id_1:
                if len(x)!=0 and len(y)!=0:#enumerate - получать индекс - 2 цикл # стрипнуть строку в момент препроцессинга. здесь не проверять на пробелы
                    item_0 = ' {} '.format(x)
                    item_1 = ' {} '.format(y)
                    print(item_0, item_1)
                    if len(item_0)>=len(item_1):
                        if item_0.find(item_1)!= -1:
                            if item_1.strip() not in label_numbers:
                                label_numbers[item_1.strip()] = value1+value2
                            else:
                                label_numbers[item_1.strip()] += value1
                    else:
                        if item_1.find(item_0.strip())!= -1:
                            if item_0.strip() not in label_numbers:
                                label_numbers[item_0.strip()] = value1+value2
                            else:
                                label_numbers[item_0.strip()] += value2
    return label_numbers
#print(vacancy_name_comparison(vacancy_name))

all_skill = pd.read_excel(f'C:/Users/phomi/PycharmProjects/curumir_1/data/skill.xls', sheet_name='Sheet1', nrows=3731, usecols='A', index_col=None)

def skills_norm_dict():  # создание словаря формата: {нормальная форма навыка:навык}
    skills_dict = {}
    for item in all_skill['skill']:
        if ' '.join(pr.norm_preprocess(item)) not in skills_dict:
            skills_dict[' '.join(pr.norm_preprocess(item))]=item
    return(skills_dict)

skills_dict=skills_norm_dict()


def extract_metadata_rus(area=1061, slice_date='2020-03-05'): # выделение навыков из описания вакансий
    skills_dict = skills_norm_dict()
    region_data = load_zip(f'C:/Users/phomi/PycharmProjects/curumir_1/data/vacancies/{slice_date}.zip', f'{area}.json')
    skills_index_1={}
    for vacancy in region_data:
        ls = pr.norm_preprocess(vacancy['description'])
        for number in range(5):
            number += 1
            for gram in nltk.ngrams(ls, number):
                for key, value in skills_dict.items():
                    if (key == ' '.join(gram)):
                        if key not in skills_index_1:
                            skills_index_1[key] = [1, [vacancy['id']], value]
                        else:
                            skills_index_1[key][0] += 1
                            if vacancy['id'] not in skills_index_1[key][1]:
                                skills_index_1[key][1].append(vacancy['id'])
    return skills_index_1
#print(extract_metadata(area=1061, slice_date='2020-03-05'))


def clusters_evaluation(area=1317, slice_date='2020-08-05', force=False):

    vacancy_name_region = {}

    clusters = {}
    skills_index = {}
    #region_data = load_zip(f'./data/vacancies/{slice_date}.zip', f'{area}.json')
    region_data = load_zip(f'C:/Users/phomi/PycharmProjects/curumir_1/data/vacancies/{slice_date}.zip', f'{area}.json')
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

    #vector_data = f'./vectors/{area}.tsv'
    vector_data = f'C:/Users/phomi/PycharmProjects/curumir_1/vectors/{area}.tsv'
    area_vectors = vectors.build_area_vectors(area, slice_date, skills_index, vector_data, threshold=threshold)
    clusters, centers, silhouette = vectors.calculate_affinity(area_vectors)
    # оценка отсюда
    for i in skills_index.values():
        for key, value in clusters.items():
            if i[2] == ' '.join(pr.norm_preprocess(key)) and value==4:  # если нормальная форма совпала в выделенных навыках и в навыках кластера
                for vacancy in region_data:
                    for item in i[1]:  # смотрим все id вакансий, которые есть у навыка из кластера
                        if item == vacancy['id']:  # если в регионе есть такой id
                            if pr.entity_change(pr.vacancy_name_proc(vacancy['name']), pr.dict) not in vacancy_name_region.keys():  # то создаем словарь {id вакансии: обработанное имя вакансии}
                                vacancy_name_region[pr.entity_change(pr.vacancy_name_proc(vacancy['name']),pr.dict)] = 1
                            else:
                                vacancy_name_region[pr.entity_change(pr.vacancy_name_proc(vacancy['name']),pr.dict)] += 1


    evaluation_names=(vacancy_name_comparison(vacancy_name_region))  # считаем сколько раз встречается каждое наименование. Потенциально косяк здесь

    if (max(evaluation_names.values())>max(vacancy_name_region.values())):
        print(max(evaluation_names.values())/sum(vacancy_name_region.values()))  # самое популярное название на кол-во вакансий
    else:
        print(max(vacancy_name_region.values())/sum(vacancy_name_region.values()))
    return evaluation_names
print(clusters_evaluation(area=1317, slice_date='2020-08-05', force=False))
# берем центр кластера, смотрим в каких вакансиях он есть, берем названия этих вакансий