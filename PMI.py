# -*- coding: utf-8 -*-
import math, pyprind, json
from pymongo import MongoClient

class PMI(object):
    """docstring for PMI"""
    def __init__(self, uri=None):
        self.client = MongoClient(uri)
        self.db = self.client['nlp']
        self.Collect = self.db['pmi']
            
    def search_word_freq(self, keyword):
        result = self.Collect.find({'key':keyword}, {'freq':1, '_id':False}).limit(1)
        if result.count()==0:
            return 1
        return result[0]['freq']

    def checkHasPMI(self, keyword):
        result = self.Collect.find({'key':keyword}, {'freq':1, 'value':1, '_id':False}).limit(1)
        if result.count() == 0:
            return False
        elif list(result)[0]['value'] == []:
            return False
        return True

    def getWordFreqList(self):
        result = {}
        for i in self.db['kcm'].find():
            keyword = i['key']
            for correlationTermsArr in i['value']:
                corTermCount = correlationTermsArr[1]

                # accumulate keyword'c frequency.
                result[keyword] = result.setdefault(keyword, 0) + corTermCount

        return result.items()

    def build(self):
        import pymongo
        self.Collect.remove({})

        # read frequency file and insert into MongoDB. 
        # with format {key:'中興大學', freq:100, value:[]}
        result = []
        for keyword, amount in self.getWordFreqList():
            result.append({'key':keyword, 'freq':amount, 'value':[]})

        self.Collect.insert(result)
        self.Collect.create_index([("key", pymongo.HASHED)])

    def get(self, keyword, amount):
        # return PMI value of this keyword
        # if doesn't exist in MongoDB, then query for 1000 PMI kcm for this specific keyword.

        if self.checkHasPMI(keyword):
            return list(self.Collect.find({'key':keyword}, {'value':1, '_id':False}).limit(1))[0]['value'][:amount]
        else:
            keyword_freq = self.search_word_freq(keyword)
            result = []

            cursor = self.db['kcm'].find({'key':keyword}, {'value':1, '_id':False}).limit(1)
            if cursor.count() == 0:
                return []
            for kcm_pair in list(cursor)[0]['value']:

                # PMI = log2(p(x, y)/p(x)*p(y)) 
                # frequency of total keyword = 154451970
                # p(x, y) = frequency of (x, y) / frequency of total keyword.
                # p(x) = frequency of x / frequency of total keyword.
                value=(math.log10( int(kcm_pair[1]) * 154451970  /(float(keyword_freq) * int(self.search_word_freq(kcm_pair[0]))  )) / math.log10(2))

                # this equation is contributed by 陳聖軒. 
                # contact him with facebook: https://www.facebook.com/henrymayday
                value*=(math.log10(int(self.search_word_freq(kcm_pair[0])))/math.log10(2))
                result.append((kcm_pair[0], value))

            result = sorted(result, key = lambda x: -x[1])
            self.Collect.update({'key':keyword}, {'$set':{'value':result}})
            return result[:amount]

if __name__ == '__main__':
    p = PMI()
    p.build()
    print(p.get("綠委", 10))