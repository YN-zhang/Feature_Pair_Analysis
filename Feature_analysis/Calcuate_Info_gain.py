
# coding: utf-8

# In[2]:


import csv
import math
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from scipy.stats import fisher_exact
from statistics import mean
import sys
#load the data set
listit = pd.read_csv(sys.argv[1]+'.csv',index_col=0)
print(listit.shape)

# BOTH
'''listit = pd.read_csv("./allselectedfeats/orangeFILT.csv",index_col=0)
print(listit.columns)
listit['class'] = 1.0
listit2 = pd.read_csv("./allselectedfeats/HiC-windowsFILT.csv",index_col=0)
print(listit2.columns)
listit2['class'] = -1.0
listit = listit.append(listit2)'''

#drop columns which are all zero
'''print(listit.shape)
listit = listit.loc[:, (listit != 0).any(axis=0)]
print(listit.shape)
#print(listit.shape,listit2.shape)
listit.head()'''


# # Calculate all 4 metrics

# In[3]:


def calcmetric(listit,fname):
    results = [["Feature","TP","FP","TN","FN","Accuracy","% Foreground","% Background","Info Gain","Fisher's Exact P-value","Enrichment/Depletion","Avg. Distance of Foreground Occurrence","Avg. Distance of Background Occurrence"]]
    #results = [["Feature","TP","FP","TN","FN","Accuracy","% Foreground","% Background","Info Gain","CART Phi","Fisher's Exact P-value","Chi-Squared P-value","Enrichment/Depletion"]]

    count = 0
    totalnum = len(listit.index)
    numfeats = len(listit.columns)
    #first find entropy of S
    numfore = 0
    numback = 0
    totalnum = len(listit.index)
    for ind,row in listit.iterrows():
        if(float(row['class']) == 1.0):
            numfore += 1
        else:
            numback += 1
    print(numfore,numback,totalnum)
    # entropy is zero if one outcome is certain to occur
    if(numback == 0 or numfore == 0):
        EntropyS = 0
    else:
        EntropyS = ((-numfore/totalnum)*math.log(numfore/totalnum,2)) - ((numback/totalnum)*math.log(numback/totalnum,2))
    resstep = listit.index[0].split("&")[0].split(":")[1].split("-")
    resstep = int((int(resstep[1])-int(resstep[0]))/2)
    for mut in listit.columns:
        if mut == 'class':
            continue
        count += 1
        dl = []
        numonright = len(listit.loc[listit[mut] == 1.0])
        numonleft = len(listit.loc[listit[mut] != 1.0])
        TP = len(listit.loc[(listit["class"] == 1.0) & (listit[mut] == 1.0)])
        # calculate distance between all window pairs which are TP
        gdl = [abs(int(x.split("&")[0].split(":")[1].split("-")[0])+resstep - int(x.split("&")[1].split(":")[1].split("-")[0])+resstep) for x in listit.loc[(listit["class"] == 1.0) & (listit[mut] == 1.0)].index]
        FP = len(listit.loc[(listit["class"] != 1.0) & (listit[mut] == 1.0)])
        hdl = [abs(int(x.split("&")[0].split(":")[1].split("-")[0])+resstep - int(x.split("&")[1].split(":")[1].split("-")[0])+resstep) for x in listit.loc[(listit["class"] != 1.0) & (listit[mut] == 1.0)].index]
        FN = len(listit.loc[(listit["class"] == 1.0) & (listit[mut] != 1.0)])
        TN = len(listit.loc[(listit["class"] != 1.0) & (listit[mut] != 1.0)])
        # make contingency table
        # format:
        #                 | CIMP-H | non-CIMP-H |
        #   --------------|--------|------------|
        #   occurring     |    #   |    #       |
        #   --------------|--------|------------|
        #   not occurring |    #   |    #       |
        df = pd.DataFrame([[TP,FP],[FN,TN]],columns=["cimp-h",'non-cimp-h'])
        # entropy is zero if one outcome is certain to occur
        if(FN == 0 or TN == 0):
            EntropyL = 0
        else:
            EntropyL = ((-FN/numonleft)*math.log(FN/numonleft,2)) - ((TN/numonleft)*math.log(TN/numonleft,2))
        # entropy is zero if one outcome is certain to occur
        if(TP == 0 or FP == 0):
            EntropyR = 0
        else:
            EntropyR = ((-TP/numonright)*math.log(TP/numonright,2)) - ((FP/numonright)*math.log(FP/numonright,2))
        infogain = EntropyS - (numonleft/totalnum)*EntropyL - (numonright/totalnum)*EntropyR
#        phival = (2*(numonleft/totalnum)*(numonright/totalnum)) * (abs((FN/numonleft)-(TP/numonright))+abs((TN/numonleft)-(FP/numonright)))
        tpperc = TP/numfore
        fpperc = FP/numback
        # "Feature","TP","FP","TN","FN","Accuracy","% Foreground","% Background","Info Gain","CART Phi","Fisher's Exact P-value","Chi-Squared P-value","Enrichment/Depletion"
        if len(gdl)>0:
            gamdist = mean(gdl)
        else:
            gamdist = 0
        if len(hdl)>0:
            hicdist = mean(hdl)
        else:
            hicdist = 0
        if fpperc == 0:
            tpperc = tpperc
            fpperc ==0
            enrich='Max'
        else:
            enrich=tpperc/fpperc
        results.append([mut,TP,FP,TN,FN,((TP+TN)/(TP+TN+FP+FN)),tpperc,fpperc,infogain,fisher_exact(df)[1],enrich,gamdist,hicdist])
        #results.append([mut,TP,FP,TN,FN,((TP+TN)/(TP+TN+FP+FN)),tpperc,fpperc,infogain,phival,fisher_exact(df)[1],chi2_contingency(df)[1],tpperc/fpperc])
    with open(""+fname,"w") as fun:
        writer = csv.writer(fun)
        writer.writerows(results)
    print("done! :)")


calcmetric(listit,sys.argv[1]+"pairfeatures.csv")

