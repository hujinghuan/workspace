#!/usr/bin/python  
# -*- coding: utf-8 -*-  

'''
Created on 2016年12月1日

@author: Administrator
'''
import tushare as ts

df = ts.get_hist_data('000875')

df.to_csv(r'c:/day/000875.csv')