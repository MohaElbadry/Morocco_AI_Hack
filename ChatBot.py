import json
import pickle
import random

import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

class Chat:
    def __init__(self,intents,words,classes,model):
        self.intents = intents 
        self.words = words
        self.classes = classes
        self.model = model
        
    def clean_up_sentence(self,sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
        return sentence_words
    
    def bag_of_words(self,sentence):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(self.words)
        for w in sentence_words :
            for i,word in enumerate(self.words):
                if word == w:
                    bag[i] = 1
        return np.array(bag)
    
    def predict_class(self,sentence):
        bow = self.bag_of_words(sentence)
        res = self.model.predict(np.array(np.array([bow])))[0]
        ERROR_THRESHOLD  = 0.25
        results = [[i,r] for i , r in enumerate(res) if r > ERROR_THRESHOLD]
        
        results.sort(key=lambda x: x[1],reverse=True)
        return_list = []
        
        for r in results:
            return_list.append({'intent':self.classes[r[0]],'probabilty':r[1]})
        return return_list
    
    def get_respoonse(self,message):
        intents_list,intents_json = self.predict_class(message),self.intents
        if len(intents_list)==0:
            tag = 'fallback'
        else:
            if intents_list[0]['probabilty'] < 0.9:
                tag = 'fallback'
            else:
                tag = intents_list[0]['intent']
        print(intents_list)
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if i['tag'] == tag:
                result = random.choice(i['responses'])
        return result,tag
    