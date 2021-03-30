from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
import re

stop_words = stopwords.words("english")  # russian stopwords

lemma = WordNetLemmatizer()  # Lemmatize
porter_stemmer = PorterStemmer()  # stemmer

def stemm_preprocess(text):
    text1 = re.sub(r'[;/)(?!\.:,""«»\s]', ' ', text) # Remove the punctuations
    tokens = word_tokenize(text1)  # tokenization
    tokens = [word.lower() for word in tokens if not word in stop_words]  # Remove stopword and make lower case
    tokens = [porter_stemmer.stem(word) for word in tokens ] # stemming

    return tokens

def lemm_preprocess(text):

    text1 = re.sub(r'[;/)(?!\.:,""«»\s]', ' ', text) # Remove the punctuations
    tokens = word_tokenize(text1)  # tokenization
    tokens = [word.lower() for word in tokens if not word in stop_words]  # Remove stopword and make lower case
    tokens = [lemma.lemmatize(word, pos="v") for word in tokens]
    tokens = [lemma.lemmatize(word, pos="n") for word in tokens]
    return tokens


if __name__ == '__main__':

    text = "what where which when how hello, my name  can't is Polina I or can't liked shouldn't dogs and cats are first two second won't"

    print(stemm_preprocess(text))
    print(lemm_preprocess(text))
