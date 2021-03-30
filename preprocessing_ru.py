from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import pymorphy2
import re

morph = pymorphy2.MorphAnalyzer()  # russian morphanalyzer
stemmer = SnowballStemmer("russian")  # russian stemmer
stop_words = stopwords.words("russian")  # russian stopwords


def stemm_preprocess(text):  # стемминг
    text1 = re.sub(r'[;/)(?!\.:,""«»\s]', ' ', text) # Remove the punctuations
    tokens = word_tokenize(text1)  # tokenization
    tokens = [word.lower() for word in tokens if not word in stop_words]  # Remove stopword and make lower case
    tokens = [stemmer.stem(word) for word in tokens]  # stemming
    return tokens


def norm_preprocess(text):  # нормализация при помощи морфологического анализатора
    ls = list()
    text1 = re.sub(r'[;/)(?!\.:,""«»\s]', ' ', text) # Remove the punctuations
    tokens = word_tokenize(text1)  # tokenization
    tokens = [word.lower() for word in tokens if not word in stop_words]  # Remove stopword and make lower case
    words=[]
    for word in tokens:
        p = morph.parse(word)[0]  # normal form
        words.append(p.normal_form)
    return words

# словарь для ковертации наименований вакансий для приведения к единой форме
dict = {'web':'веб', 'вэб':'веб', '1с':'1c', '1 с':'1c', '1 c':'1c', 'с++':'c++', 'с ++':'c++', 'c ++':'c++'}


def entity_change(t, dictionary):  # конвертация синонимов в самое популярное название
    for key, value in dictionary.items():
        if key in t:
            t = t.replace(key, value)
    return t

useless_words=['программист', 'разработчик', 'младший', 'старший', 'middle', 'senior', 'junior', 'стажер', 'ведущий']
def vacancy_name_proc (name):  # обработка наименований вакансий для функции оценки, убирает неинформативные слова,
                               # лишние символы
    name = name.replace('-', ' ')
    name1 = re.sub(r'[;/)(?!\.:,""«»\s]', ' ', name)  # Remove the punctuations
    tokens = word_tokenize(name1)  # tokenization
    tokens = [word.lower() for word in tokens ]
    tokens = [word for word in tokens if word not in useless_words]
    name1 = ' '.join(tokens)
    for item in useless_words:
        name=name1.replace(str(item),'')
    name=name.strip()
    return name

if __name__ == '__main__':

    text = 'Умный! разработчик Программист python))'
    check = "Программист 1 С/ С#, старший Web-программист, вэб-программист"
    print(vacancy_name_proc(entity_change(vacancy_name_proc(check), dict)))
    # print(stemm_preprocess(text))
    #print(norm_preprocess(text))

