from nltk.tokenize import word_tokenize
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from scipy.sparse import hstack
import nltk
import joblib
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import gc
import scipy.sparse as sp

# Descargar stopwords si es necesario
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('stopwords')



# Función para vectorizar las columnas de texto
def preprocess_and_vectorize(df, vectorizers=None):
    if vectorizers is None:
        vectorizers = {}

    X_text_vectorized = None

    # Procesar columna por columna
    for col in df.columns:
        if col in vectorizers:
            # Usar vectorizador existente
            vectorizer = vectorizers[col]
            X_col_vectorized = vectorizer.transform(df[col])
        else:
            # Crear nuevo vectorizador si no existe
            vectorizer = TfidfVectorizer(stop_words=stopwords.words('spanish'), min_df=1)
            vectorizer.fit(df[col])
            X_col_vectorized = vectorizer.transform(df[col])
            vectorizers[col] = vectorizer

        # Concatenar las matrices en una sola (si es la primera, inicializarla)
        if X_text_vectorized is None:
            X_text_vectorized = X_col_vectorized
        else:
            X_text_vectorized = sp.hstack([X_text_vectorized, X_col_vectorized])

        gc.collect()  # Liberar memoria después de cada columna

    return X_text_vectorized





