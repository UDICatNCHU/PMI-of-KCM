# -*- coding: utf-8 -*-
import math, requests, pyprind, json
from pymongo import MongoClient

class PMI(object):
    """docstring for PMI"""
    client = MongoClient()
    db = client['nlp']
    Collect = db['pmi']
    def __init__(self, uri=None):
        PMI.client = MongoClient(uri)
    # @classmethod
    # def from_string(cls, date_as_string):
    #     day, month, year = map(int, date_as_string.split('-'))
    #     date1 = cls(day, month, year)
    #     return date1
            
    @classmethod
    def search_word_freq(cls, keyword):
        result = cls.Collect.find({'key':keyword}, {'freq':1, '_id':False}).limit(1)
        if result.count()==0:
            return 1
        return result[0]['freq']

    @classmethod
    def checkHasPMI(cls, keyword):
        result = cls.Collect.find({'key':keyword}, {'freq':1, 'value':1, '_id':False}).limit(1)
        if result.count() == 0:
            return False
        elif list(result)[0]['value'] == []:
            return False
        return True

    def build(self):
        import pymongo
        self.Collect.remove({})

        self.wordfreqfile=open("cht.modelWordlist_countingCombine",'r')
        # read frequency file and insert into MongoDB. 
        # with format {key:'中興大學', freq:100, value:[]}
        result = []
        for line in self.wordfreqfile:
            line=line.split()
            if(len(line)==2):
                result.append({'key':line[0], 'freq':line[1], 'value':[]})
                # [line[0]]=int(line[1])
            else:
                raise Exception('dd')

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

            for kcm_pair in json.loads(requests.get('http://api.udic.cs.nchu.edu.tw/api/kcm', {'keyword':keyword, 'lang':'cht', 'num':1000}).text):

                # PMI = log2(p(x, y)/p(x)*p(y)) 
                # frequency of total keyword = 154451970
                # p(x, y) = frequency of (x, y) / frequency of total keyword.
                # p(x) = frequency of x / frequency of total keyword.
                print(kcm_pair)
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
    # p.build()
    print(p.get('蔡英文', 10))
    