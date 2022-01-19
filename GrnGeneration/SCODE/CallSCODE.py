# encoding=utf-8
'''
Author: ZhuLin
'''

import subprocess
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve, roc_curve, auc, accuracy_score, f1_score, precision_score, recall_score,auc
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import PrecisionRecallDisplay
from sklearn.metrics import RocCurveDisplay
import sys


# 对于要调用的文件要import进来，但是该文件是R，只能从调用的位置开始访问
def callSCODE(fdata, ftime, diry, tfnum, pnum, cnum, maxite):
    subprocess.call(['Rscript', 'GrnGeneration/SCODE/SCODE.R', fdata, ftime, diry, tfnum, pnum, cnum, maxite])
    print("SCODE generated finished")

def callSCODEAvg(fdata, ftime, diry, tfnum, pnum, cnum, maxite, rep):
    subprocess.call(['ruby', 'GrnGeneration/SCODE/run_R.rb', fdata, ftime, diry, tfnum, pnum, cnum, maxite, rep])
    print("SCODE Avg generated finished")

# callSCODE('SCODE/bio_data/expr.txt','SCODE/bio_data/time.txt','SCODE/bio_data' ,'35', '4' ,'92', '100')
# callSCODEAvg(fdata='./mCAD-2000-1/expr.txt',ftime='./mCAD-2000-1/time.txt',diry='./mCAD-2000-1' ,tfnum='5', pnum='6' ,cnum='2000', maxite='100',rep='5')
# callSCODEAvg(fdata='./VSC-2000-1/expr.txt',ftime='./VSC-2000-1/time.txt',diry='./VSC-2000-1' ,tfnum='8', pnum='10' ,cnum='2000', maxite='100',rep='5')
# callSCODEAvg(fdata='./HSC-2000-1/expr.txt',ftime='./HSC-2000-1/time.txt',diry='./HSC-2000-1' ,tfnum='11', pnum='2' ,cnum='2000', maxite='100',rep='5')
# callSCODEAvg(fdata='./GSD-2000-1/expr.txt',ftime='./GSD-2000-1/time.txt',diry='./GSD-2000-1' ,tfnum='19', pnum='2' ,cnum='2000', maxite='100',rep='5')
# callSCODE('./data2/exp_train.txt','./data2/time_train.txt','./data2' ,'100', '4' ,'356', '100')
'''
data: data
gene: 100
cell: 356
dr: 4
ite: 100
'''
# indata=np.loadtxt('SCODE/data/exp_train.txt',dtype=float) # 100x356 (gene x cell)
# print('indata shape:',indata.shape)
# intime=np.loadtxt('SCODE/data/time_train.txt',dtype=float) # 356x2 (cell)
# print('intime shape:',intime.shape)
# ####
# import matplotlib.pyplot as plt
# plt.scatter([i for i in range(356)],intime[:,1],alpha=0.6)
# plt.show()
# ####
# outA=np.loadtxt('SCODE/out/A.txt',dtype=float) # 100x100 (gene x gene)
# print('outA shape',outA.shape)

def formODEs(A_dir,oup_dir): # input is coefficients matrix A and output is odes file
    A=np.loadtxt(A_dir,dtype=float)
    n,_=A.shape
    print('The number of genes is: ',n)
    gene_names=[]
    for i in range(1,n+1):
        gene_names.append('gene'+str(i))
    with open(oup_dir,'a+') as oup_file:
        for i in range(n):
            coefficients=A[i]
            line='gene'+str(i+1)+'\'='
            for j in range(n):
                coefficients[j]=np.around(coefficients[j],1)
                if coefficients[j]>0:
                    line+=('+'+str(coefficients[j])+'*gene'+str(j+1))
                elif coefficients[j]<0:
                    line+=(str(coefficients[j])+'*gene'+str(j+1))
                else:
                    continue
            line=line.replace('=+','=',1)
            oup_file.write(line+'\n')
    print(oup_dir+" generated finished")

# formODEs('bio_data/A.txt', './ODE_SBML_models/' + 'ES_MEFData.ode')

def digit2label(weight):
    """
    map weight value into +/- regulatory function
    """
    if weight>0:
        return 1
    elif weight==0:
        return 0
    else:
        return -1

def posneg2label(symbol):
    if symbol=='+':
        return 1
    else:
        return -1

def formGRNTopology(A_dir,oup_dir,gene_names_dir): # 将预测的A中的值写进来,并且按照score的绝对值进行排序
    """
    :param A_dir: matrix A directory
    :param oup_dir: output path
    :param gene_names_dir: a text file contains a list of gene names
    :return:
    """
    A=np.loadtxt(A_dir,dtype=float)
    n, _ = A.shape
    with open(gene_names_dir,'r') as fr:
        gene_names=fr.readlines()
    gene_names=[gene.strip() for gene in gene_names]
    oup=[]

    for i in range(n):
        for j in range(n):
            func = A[i, j]  # digit2label()
            oup.append([gene_names[j],gene_names[i],float(func)])

    oup.sort(key=lambda x:abs(x[2]),reverse=True)
    with open(oup_dir,'w') as f:
        for i in range(len(oup)):
            f.write(oup[i][0]+'\t'+oup[i][1]+'\t'+str(oup[i][2])+'\n')
    print(oup_dir + " generated finished")



# formGRNTopology('/Users/zhulin/Desktop/TMELand_reconstruction_1.0/Inferred_GRN/SCODE/A.txt','/Users/zhulin/Desktop/TMELand_reconstruction_1.0/Inferred_GRN/SCODE/score.txt' ,'/Users/zhulin/Desktop/TMELand_reconstruction_1.0/scRNAseq_models/GUO2010/48-gene/SCODE_genes.txt')

# def normalization(data):
#     _range = np.max(data) - np.min(data)
#     return (data - np.min(data)) / _range



def evaluation1(oup,ref):
    """
    TP: + -> +
    TN: - -> -
    FP: - -> +
    FN: + -> -
    在ground truth中将没有的边其值都置为0，去掉所有自调控的关系，然后进行evaluation，这样比较数据集的大小就是n(n-1)
    """
    oup_dic,ref_dic={},{}
    with open(oup,'r') as fr1:
        for row in fr1.readlines():
            line=row.strip().split('\t')
            if line[0]==line[1]: # drop self-regulation
                continue
            oup_dic[line[0]+'-'+line[1]]=int(line[2])
    with open(ref,'r') as fr2:
        for row in fr2.readlines()[1:]:
            line=row.strip().split(',')
            if line[0]==line[1]: # drop self-regulation
                continue
            ref_dic[line[0]+'-'+line[1]]=posneg2label(line[2])
    preds,trues=[],[]
    for pair in oup_dic.keys():
        preds.append(oup_dic[pair])
        if pair not in ref_dic.keys():
            trues.append(0)
        else:
            trues.append(ref_dic[pair])
    print(len(preds))
    print(len(trues))

    print("oup_dic:",oup_dic)
    print("ref_dic:",ref_dic)
    print("preds:",preds)
    print("trues:",trues)

    acc=accuracy_score(trues,preds)
    print("acc:",acc)

    f1=f1_score(trues,preds,average=None)
    print("f1:",f1)

    recall=recall_score(trues,preds,average=None)
    print("recall:",recall)

    precision=precision_score(trues,preds,average=None)
    print("precision:",precision)

    # p,r,_=precision_recall_curve(trues,preds)
    # pr_auc=auc(r,p)
    # print("pr_auc:",pr_auc)
    # PrecisionRecallDisplay(precision=p,recall=r).plot()
    #
    # fpr,tpr,_=roc_curve(trues,preds)
    # roc_auc=auc(fpr,tpr)
    # print("roc_auc:",roc_auc)
    # RocCurveDisplay(fpr=fpr,tpr=tpr,roc_auc=roc_auc).plot()
    # plt.show()






# evaluation('./mCAD-2000-1/mCAD-2000-1-score.tsv','./mCAD-2000-1/refNetwork.csv')
# evaluation1('./VSC-2000-1/VSC-2000-1-score.tsv','./VSC-2000-1/refNetwork.csv')
# evaluation('./HSC-2000-1/HSC-2000-1-score.tsv','./HSC-2000-1/refNetwork.csv')
# evaluation('./GSD-2000-1/GSD-2000-1-score.tsv','./GSD-2000-1/refNetwork.csv')