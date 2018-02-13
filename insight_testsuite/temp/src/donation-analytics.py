
# coding: utf-8

# In[19]:


import pandas as pd
import csv
import sys
from math import *
import random


# In[20]:


con_name = sys.argv[1]
percent_name = sys.argv[2]
output_path = sys.argv[3]


# In[21]:


def read_data(con_name, percent_name):
    '''
        input data
    '''
    colnames = ['CMTE_ID', 'AMNDT_IND', 'RPT_TP', 'TRANSACTION_PGI', 'IMAGE_NUM', 'TRANSACTION_TP', 'ENTITY_TP',
           'NAME', 'CITY', 'STATE', 'ZIP_CODE', 'EMPLOYER', 'OCCUPATION', 'TRANSACTION_DT', 'TRANSACTION_AMT',
           'OTHER_ID', 'TRAN_ID', 'FILE_NUM', 'MEMO_CD', 'MEMO_TEXT', 'SUB_ID']
    data = pd.read_csv(con_name, sep="|", header=None, names = colnames, dtype = str)
    with open(percent_name,'r') as f:
        percentile = f.read()
        percentile = percentile.strip()
        percentile = int(percentile)
    return data, percentile


# In[22]:


# wait for testing
def removed_data(data):
    d = data[data['OTHER_ID'].isnull()]
    lis = ['TRANSACTION_DT', 'ZIP_CODE', 'NAME', 'CMTE_ID', 'TRANSACTION_AMT']
    for i in lis:
        d = d[d[i].notnull()]
    return d

def subset_data(data, l):
    '''
    l: list of column names
    '''
    return data[l]


# In[23]:


def pair_dictionary(data):
    '''
        make dictionary of unique donors
    '''
    dic = {}
    for i in data.index:
        d = data.loc[i]
        key = (d['NAME'], d['ZIP_CODE'])
        if key in dic.keys():
            dic[key].append(i)
        else:
            dic[key] = [i]
    return dic


# In[24]:


def partial_result(data, dic):
    result = []
    repeat_amount = []
    year = 2019
    for i in dic.keys():
        n = len(dic[i])
        prior = False
        first_year = data.loc[dic[i][0]]['TRANSACTION_DT'][-4:]
        if n > 1:
            for j in xrange(len(dic[i])):
                lst = []
                tmp_data = data.loc[dic[i][j]]
                year = tmp_data['TRANSACTION_DT'][-4:]
                prior = int(year) - int(first_year) > 0
                if prior:
                    lst.append(tmp_data['CMTE_ID'])
                    zips = tmp_data['ZIP_CODE'][0:5]
                    lst.append(zips)
                    lst.append(year)
                    if j > 0:
                        repeat_amount.append(int(tmp_data['TRANSACTION_AMT']))
                    result.append(lst)
    return result, repeat_amount


# In[25]:


def select(repeat_amount, left, right, k):
    if right == left:
        return repeat_amount[left]
    pivot_index = random.randint(left, right)
    repeat_amount[left], repeat_amount[pivot_index] = repeat_amount[pivot_index], repeat_amount[left]
    i = left
    for j in xrange(left+1, right+1):
        if repeat_amount[j] < repeat_amount[left]:
            i += 1
            repeat_amount[i], repeat_amount[j] = repeat_amount[j], repeat_amount[i]
    repeat_amount[i], repeat_amount[left] = repeat_amount[left], repeat_amount[i]
    if k == i:
        return repeat_amount[i]
    elif k < i:
        return select(repeat_amount, left, i-1, k)
    else:
        return select(repeat_amount, i+1, right, k)


# In[31]:


def get_percentile(repeat_amount, p):
    n = len(repeat_amount)
    percent = ceil(n * p / 100.0)
    values = select(repeat_amount, 0, len(repeat_amount) - 1, percent - 1)
    return values


# In[27]:


def final_result(result, repeat_amount, values):
    summation = 0
    for i in xrange(len(result)):
        summation += repeat_amount[i]
        result[i].append(values)
        result[i].append(summation)
        result[i].append(i + 1)
    return result


# In[46]:


def repeat_donation(con_name, percent_name):
    data, percentile = read_data(con_name, percent_name)
    data = removed_data(data)
    lst = ['CMTE_ID','NAME','ZIP_CODE','TRANSACTION_DT', 'TRANSACTION_AMT','OTHER_ID']
    data = subset_data(data, lst)
    dic = pair_dictionary(data)
    result, repeat_amount = partial_result(data, dic)
    if len(repeat_amount) == 0: return []
    values = get_percentile(repeat_amount, percentile)
    result = final_result(result, repeat_amount, values)
    return result


# In[ ]:


result = repeat_donation(con_name, percent_name)
with open(output_path, 'w') as f:
    if len(result) == 0: f.write('')
    else:
        for i in result:
            for j in xrange(len(i)):
                if j < len(i) - 1:
                    f.write("%s|" % i[j])
                else:
                    f.write("%s\n" % i[j])

