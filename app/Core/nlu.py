# %%
import re
import pickle
from typing import List, tuple , Optional
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

class NLU:

    def __init__(
            self,
            model_path: str = "chatbot_model.keras",
            words_path: str = "words.pkl",
            classes_path: str = "classes.pkl",
            threshold: float = 0.6
    ):
        self.model_path = model_path
        self.words_path = words_path
        self.classes_path = classes_path
        self.threshold = threshold

        self.lemmatizer = WordNetLemmatizer()
        self.words = []
        self.classes = []
        self.model = None

    def _load_vocabulary(self) -> None:
        with open(self.words_path, "rb") as f:
            self.words = pickle.load(f)
        with open(self.classes_path, "rb") as f:
            self.classes = pickle.load(f)

    def _bag_of_words(self, sentence:str) -> np.ndarray:
        self.model = load_model(self.model_path)

    def _clean_and_tokenize(self, sentence:str) -> List[str]:
        sentence = sentence.lower()
        sentence = re.sub(r"[^a-z0-9\s']", " ", sentence)
        tokens = nltk.word_tokenize(sentence)
        tokens = [self.lemmatizer.lemmatize(tok) for tok in tokens if tok.strip()]
        return tokens
    def _bag_of_words(self, sentence: str) -> np.ndarray:
        tokens = self._clean_and_tokenize(sentence)
        bag = np.zeros(len(self.words), dtype = np.float32)
        for i,w in enumerate(self.words):
            if w in tokens:
                bag[i] = 1.0
            return bag
    def predict_intents(self, sentence:str, threshold: Optional[float] = None) -> List[Tuple[str, float]]:
        if self.model is None or not self.words or not self.classes:
            return []
        
        thr = threshold if threshold is not None else self.threshold
        bow_vec = self._bag_of_words(sentence)
        bow_vec = np.expand_dims(bow_vec, axis = 0)

        preds = self.model.predict(bow_vec, verbose = 0)[0]
        results: List[tuple[str, float]] = []

        for idx, prob in enumerate(preds):
            if prob >= thr:
                intent_tag = self.classes[idx]
                results.append((intent_tag, float(prob)))

        results.sort(key =lambda x: x[1], reverse = True)
        return results
    def get_top_intent(self, sentence: str, threshold: Optional[float] = None) -> Tuple[Optional[str], float]:
        intents = self.predict_intents(sentence, threshold, threshold= threshold)
        if intents:
            return intents[0]
        return None, 0.0


