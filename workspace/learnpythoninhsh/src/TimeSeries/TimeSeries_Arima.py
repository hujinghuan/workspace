#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import pandas as pd
import numpy as np
from scipy import  stats
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.graphics.api import qqplot
from numpy.numarray.numerictypes import Float64

dta=[10930,10318,10595,10972,7706,6756,9092,10551,9722,10913,11151,8186,6422, 
6337,11649,11652,10310,12043,7937,6476,9662,9570,9981,9331,9449,6773,6304,9355, 
10477,10148,10395,11261,8713,7299,10424,10795,11069,11602,11427,9095,7707,10767, 
12136,12812,12006,12528,10329,7818,11719,11683,12603,11495,13670,11337,10232, 
13261,13230,15535,16837,19598,14823,11622,19391,18177,19994,14723,15694,13248, 
9543,12872,13101,15053,12619,13749,10228,9725,14729,12518,14564,15085,14722, 
11999,9390,13481,14795,15845,15271,14686,11054,10395]
dta=np.array(dta,dtype=np.float)


dta=pd.Series(dta)
dta.index = pd.Index(sm.tsa.datetools.dates_from_range('2001','2090')) #应该是2090，不是2100
dta.plot(figsize=(12,8))
#plt.show() # 在Scala IDE要输入这个命令才能显示图片

fig = plt.figure(figsize=(12,8))
ax1= fig.add_subplot(111)
diff1 = dta.diff(1)
diff1.plot(ax=ax1)
#plt.show()

diff1= dta.diff(1) #我们已经知道要使用一阶差分的时间序列，之前判断差分的程序可以注释掉 //原文有错误应该是diff1= dta.diff(1)，而非dta= dta.diff(1)
fig = plt.figure(figsize=(12,8))
ax1=fig.add_subplot(211)
fig = sm.graphics.tsa.plot_acf(dta,lags=40,ax=ax1)
ax2 = fig.add_subplot(212)
fig = sm.graphics.tsa.plot_pacf(dta,lags=40,ax=ax2)
#plt.show()


#arma_mod70 = sm.tsa.ARMA(dta,(7,0)).fit()
#print(arma_mod70.aic,arma_mod70.bic,arma_mod70.hqic)
#arma_mod30 = sm.tsa.ARMA(dta,(0,1)).fit()
#print(arma_mod01.aic,arma_mod01.bic,arma_mod01.hqic)
#arma_mod71 = sm.tsa.ARMA(dta,(7,1)).fit()
#print(arma_mod71.aic,arma_mod71.bic,arma_mod71.hqic)
arma_mod80 = sm.tsa.ARMA(dta,(8,0)).fit()
#print(arma_mod80.aic,arma_mod80.bic,arma_mod80.hqic)


resid = arma_mod80.resid

fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(211)
fig = sm.graphics.tsa.plot_acf(resid.values.squeeze(), lags=40, ax=ax1)
ax2 = fig.add_subplot(212)
fig = sm.graphics.tsa.plot_pacf(resid, lags=40, ax=ax2)
#plt.show()

print(sm.stats.durbin_watson(resid.values))

fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)
ax = resid.plot(ax=ax);
#plt.show()

print(stats.normaltest(resid))
fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)
fig = qqplot(resid, line='q', ax=ax, fit=True)
#plt.show()

r,q,p = sm.tsa.acf(resid.values.squeeze(), qstat=True)
data = np.c_[range(1,41), r[1:], q, p]
table = pd.DataFrame(data, columns=['lag', "AC", "Q", "Prob(>Q)"])
print(table.set_index('lag'))

predict_dta = arma_mod80.predict('2090', '2100', dynamic=True)
print(predict_dta)

fig, ax = plt.subplots(figsize=(12, 8))
ax = dta.ix['2000':].plot(ax=ax)
fig = arma_mod80.plot_predict('2090', '2100', dynamic=True, ax=ax, plot_insample=False)
plt.show()
