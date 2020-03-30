"""
https://towardsdatascience.com/calculating-string-similarity-in-python-276e18a7d33a
"""
import string
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords


STOPWORDS = stopwords.words('english')


def clean_string(text):
    text = ''.join([c for c in text if c not in string.punctuation])
    text = text.lower()
    text = ' '.join([word for word in text.split() if word not in STOPWORDS])
    return text


def cos_sims(sentences):
    cleaned = list(map(clean_string, sentences))

    vectorizer = CountVectorizer().fit_transform(cleaned)
    vectors = vectorizer.toarray()
    
    csim = cosine_similarity(vectors)

    return csim


def cos_sim_pair(s1, s2):
    csim = cos_sims([s1, s2])
    return csim[0][1]
