# encoding=utf-8
from libsbml import *
import numpy as np
import tkinter as tk
from tkinter import ttk
# from pyecharts.globals import SymbolType
import PIL.Image
import PIL.ImageTk
import os
import socket
# from psutil import process_iter
from signal import SIGTERM
'''
This part of code are partially referred to https://github.com/MCLand-NTU/MCLand/blob/master/MCLand_ver1.py. The specific referred
positions are marked with ###
'''

# sbml -> ODE grn, F functions (the given format of ODEs)
def parseSBML(file):
    odeParams={}
    odeShow=''
    odeCode=''
    jacCode=''
    reader=SBMLReader()
    docu=reader.readSBML(file)
    error=docu.getNumErrors()
    # assert error==0, 'The SBML file is parsed with errors.'
    docu=reader.readSBMLFromFile(file)
    model = docu.getModel()
    #################################################### Begin
    # The following section of code is adapted from Frank Bergmann Python code for using libSBML to convert SBML model
    # to ODE model for time course integration using scipy odeint
    variableNames=[]
    constants={}
    sbmlInitConds={}
    for i in range(model.getNumSpecies()):
        species=model.getSpecies(i)
        if species.getBoundaryCondition()==True:
            continue
        variableNames.append(species.getId())
    # print('variable names: ',variableNames)
    odeParams['genes']=variableNames
    jacCode = jacCode + 'from sympy import Matrix,symbols\n'
    jacCode = jacCode + 'import numpy as np\n'
    jacCode=jacCode+'global H\n'
    tmp_var_comma=''
    tmp_var_blank=''
    # x,y,...
    for i in variableNames:
        tmp_var_comma=tmp_var_comma+i+','
    # x y ...
    for i in variableNames:
        tmp_var_blank=tmp_var_blank+i+' '
    jacCode=jacCode+tmp_var_comma[:-1]+'=symbols("'+tmp_var_blank[:-1]+'")\n'
    jacCode=jacCode+'Y=Matrix([' + tmp_var_comma[:-1] + '])\n'

    sbmlCompartments=[]
    for i in range(model.getNumCompartments()):
        element=model.getCompartment(i)
        sbmlCompartments.append('{0} = {1}\n'.format(element.getId(), element.getSize()))
    # print('sbmlCompartments: ',sbmlCompartments)

    sbmlParameters=[]
    for i in range(model.getNumParameters()):
        element=model.getParameter(i)
        sbmlParameters.append('{0} = {1}\n'.format(element.getId(), element.getValue()))
    # print('sbmlParameters: ',sbmlParameters)

    sbmlRhs=[]
    sbmlReactions=[]
    variables={}
    for i in range(model.getNumSpecies()):
        # print('i: ',i)
        species=model.getSpecies(i)
        # print('species: ',species)
        if species.getBoundaryCondition() == True or (species.getId() in variables):
            # print('species id: ',species.getId())
            # print('species boundary condition: ',species.getBoundaryCondition())
            continue
        # initialization
        variables[species.getId()]=[]
    for i in range(model.getNumReactions()):
        reaction=model.getReaction(i)
        kinetics=reaction.getKineticLaw()
        sbmlReactions.append(str(reaction.getId())+'='+str(kinetics.getFormula()))
        for j in range(reaction.getNumReactants()):
            reactant=reaction.getReactant(j)
            species=model.getSpecies(reactant.getSpecies())
            if species.getBoundaryCondition()==True:
                continue
            if reactant.getStoichiometry() == 1.0:
                variables[species.getId()].append('-{0}'.format(reaction.getId()))
            else:
                variables[species.getId()].append('-({0})*{1}'.format(reactant.getStoichiometry(), reaction.getId()))
                # print('reaction ID: ',reaction.getId())
        for j in range(reaction.getNumProducts()):
            product=reaction.getProduct(j)
            species=model.getSpecies(product.getSpecies())
            if species.getBoundaryCondition() == True:
                continue
            if product.getStoichiometry() == 1.0:
                variables[species.getId()].append('{0}'.format(reaction.getId()))
            else:
                variables[species.getId()].append('({0})*{1}'.format(product.getStoichiometry(), reaction.getId()))

    variableList=list(variables.keys())
    correct_variableName = []
    # print('Reading reactions...')
    for i in range(len(variables.keys())):
        # print('variable index: ',i)
        # print('variable name: ',variableNames[i])
        sbmlRhs.append('d'+variableNames[i]+'/dt=')
        for eqn in variables[variableList[i]]:
            # print('equation: ',eqn)
            # print(variables[variableList[i]])
            sbmlRhs.append(' + ({0})'.format(eqn))

        # For constants where there is ode rhs is empty, set the ode rhs to 0.
        # and we need to set the constant based on their initialConcentration value.
        if len(variables[variableList[i]])==0:
            # first set the ode rhs to 0
            sbmlRhs.append('0')
            # set the constant based on their InitialConcentration
            element=model.getSpecies(i)
            constants[element.getId()]=element.getInitialAmount()
            # print('initial concentration: ',element.getInitialAmount())
        else: # 非常数变量
            correct_variableName.append(variableNames[i])

    # adjusting the stored format of the sbmlRhs
    dx_dt_index=[]
    index=0
    sbmlTmp=[]
    for i in sbmlRhs:
        if '/dt=' in i:
            dx_dt_index.append(index)
        index=index+1
    for i in range(len(dx_dt_index)):
        start = dx_dt_index[i]
        if i!=(len(dx_dt_index)-1):
            end=dx_dt_index[i+1]
        else:
            end = len(sbmlRhs)
        strTmp=''
        for ele_index in range(start+1,end):
            strTmp=strTmp+sbmlRhs[ele_index]
        sbmlTmp.append(strTmp)
    sbmlRhs=sbmlTmp # 将每个ODE方程的每一部分粘贴在一起
    # print('sbmlRhs: ',sbmlRhs)
    # print('correct_variableName: ',correct_variableName)

    variableNames=correct_variableName

    # This loop to add constants to the model object
    for i in range(model.getNumSpecies()):
        element=model.getSpecies(i)
        if element.getBoundaryCondition() == False:
            if element.getId() not in variableNames:
                constants[element.getId()]=element.getInitialConcentration()
            continue
        if element.isSetInitialConcentration():
            constants[element.getId()] = element.getInitialConcentration()
        else:
            constants[element.getId()] = element.getInitialAmount()

    # extract initial conditions
    for i in range(model.getNumSpecies()):
        element=model.getSpecies(i)
        sbmlInitConds[element.getId()]=element.getInitialConcentration()
    # print('initial conditions: ',sbmlInitConds)
    #################################################### End

    # show ODE code and differentiation of ODE code
    odeCode=odeCode+'from scipy.integrate import odeint\n'
    odeCode=odeCode+'import numpy as np\n'
    odeCode=odeCode+'def get_force(x,t):\n'
    for i in sbmlCompartments:
        odeCode=odeCode+'\t'+i.strip()+'\n'
        odeShow=odeShow+i.strip()+'\n'
    # global parameters
    for i in sbmlParameters:
        odeCode=odeCode+'\t'+i.strip()+'\n'
        odeShow=odeShow+i.strip()+'\n'
    for key in constants:
        odeCode=odeCode+'\t{0}={1}\n'.format(key,constants[key])
        odeShow=odeShow+'{0}={1}\n'.format(key,constants[key])
    for i in range(len(variableNames)):
        odeCode=odeCode+'\t{0}=x[{1}]\n'.format(variableNames[i],i)
    for i in sbmlReactions:
        odeCode=odeCode+'\t'+i.strip()+'\n'
        odeShow=odeShow+i.strip()+'\n'
    odeCode=odeCode+'\treturn np.array(['
    jacCode = jacCode + odeShow
    jacCode = jacCode + 'X=Matrix(['
    for i in range(len(sbmlRhs)):
        odeCode = odeCode + sbmlRhs[i] + ','
        odeShow=odeShow + 'd{0}/dt={1}\n'.format(odeParams['genes'][i],sbmlRhs[i])
        jacCode=jacCode+sbmlRhs[i] + ','
    odeCode=odeCode[:-1]+'])\n'
    jacCode = jacCode[:-1] + '])\n'
    jacCode = jacCode+'H=X.jacobian(Y).subs(['
    for i in range(len(odeParams['genes'])):
        jacCode=jacCode+'('+odeParams['genes'][i]+','+'stable[{0}]),'.format(i)
    jacCode = jacCode[:-1]+'])\n'
    jacCode = jacCode+'H=np.array(H)\n'

    return odeShow,odeCode,jacCode,odeParams

# ODE -> ODE grn, F functions (the given format of ODEs)
def parseODE(file):
    odeParams={}
    odeShow=''
    odeCode=''
    jacCode=''
    paramsCode=[]
    paramsNames=[]
    paramsValues=[]
    geneNo=0
    geneODEs=[]
    geneNames=[]
    odeExps=[] # ode right part
    constants=[]
    initConds={}
    #################################################### Begin
    with open(file,'r') as fr:
        cnt=fr.readlines()
        for line in list(cnt):
            if line[0]=='#' or line[0]=='@':
                cnt.remove(line)
        for line in list(cnt):
            if line.find('par')==0:
                par_line=line
                par=par_line.split(None,1)[1]
                par_code=par.replace(',',';')

                strr=par_code.replace(';','').split()
                for exp in strr:
                    parName,parValue=exp.split('=')
                    paramsNames.append(parName)
                    paramsValues.append(parValue)
                paramsCode.append(par_code)
            if line.find("'")>0:
                geneNo=geneNo+1
                geneODEs.append(line)
                varName=line.split('=')[0].replace("'",'')
                geneNames.append(varName)

                odeExp=line.split('=')[1].replace('\n','')
                odeExp=odeExp.replace('^','**')
                odeExps.append(odeExp)
            if line.find('/dt')>0:
                geneNo+=1
                geneODEs.append(line)
                varName=line.split('=')[0]
                varName=varName.split('/')[0]
                varName=list(varName).pop(0)
                varName=''.join(varName)
                geneNames.append(varName)

                odeExp=line.split('=')[1].replace('\n','')
                odeExp=odeExp.replace('^','**')
                odeExps.append(odeExp)
            if line.find('const')==0:
                const=line
                const=const.split(None,1)[1]
                constants.append(const)
            if line.find('init')==0:
                init_line=line
                init=init_line.split(None,1)[1]
                strr=init.replace(',','').split()
                for i in strr:
                    initName,initValue=i.split('=')
                    initConds[initName]=initValue
    #################################################### End
    # define returned variables
    if len(paramsCode)>0:
        odeShow=odeShow+'parameters:\n'
        for i in paramsCode:
            odeShow=odeShow+i
        odeShow=odeShow+'\n'
    if len(constants)>0:
        odeShow = odeShow + '\n'
        for i in constants:
            odeShow=odeShow+i
        odeShow = odeShow + '\n'
    for i in geneODEs:
        odeShow=odeShow+i

    # print(geneNames)
    odeParams['genes']=geneNames

    jacCode = jacCode + 'from sympy import Matrix,symbols\n'
    jacCode = jacCode + 'import numpy as np\n'
    jacCode=jacCode+'global H\n'
    tmp_var_comma = ''
    tmp_var_blank = ''
    # x,y,...
    for i in geneNames:
        tmp_var_comma = tmp_var_comma + i + ','
    # x y ...
    for i in geneNames:
        tmp_var_blank = tmp_var_blank + i + ' '
    jacCode = jacCode + tmp_var_comma[:-1] + '=symbols("' + tmp_var_blank[:-1] + '")\n'
    jacCode = jacCode + 'Y=Matrix([' + tmp_var_comma[:-1] + '])\n'
    # ODE code and Jac code
    odeCode = odeCode + 'from scipy.integrate import odeint\n'
    odeCode = odeCode + 'import numpy as np\n'
    odeCode = odeCode + 'def get_force(x,t):\n'

    for i in range(len(paramsNames)):
        odeCode = odeCode + '\t' + paramsNames[i]+'='+paramsValues[i] + '\n'
        jacCode=jacCode+paramsNames[i]+'='+paramsValues[i] + '\n'
    for i in constants:
        odeCode = odeCode + '\t{0}\n'.format(i)
        jacCode=jacCode+'{0}\n'.format(i)
    for i in range(len(geneNames)):
        odeCode = odeCode + '\t{0}=x[{1}]\n'.format(geneNames[i], i)
    for i in range(len(odeExps)):
        odeCode = odeCode + '\t' + 'R'+str(i+1)+'='+odeExps[i] + '\n'
        jacCode=jacCode+'R'+str(i+1)+'='+odeExps[i] + '\n'
    odeCode = odeCode + '\treturn np.array(['
    jacCode = jacCode + 'X=Matrix(['
    for i in range(len(geneNames)):
        odeCode = odeCode + 'R' + str(i+1) + ','
        jacCode = jacCode + 'R' + str(i+1) + ','
    odeCode = odeCode[:-1] + '])\n'
    jacCode = jacCode[:-1] + '])\n'
    jacCode = jacCode + 'H=X.jacobian(Y).subs(['
    for i in range(len(odeParams['genes'])):
        jacCode = jacCode + '(' + odeParams['genes'][i] + ',' + 'stable[{0}]),'.format(i)
    jacCode = jacCode[:-1] + '])\n'
    jacCode = jacCode + 'H=np.array(H)\n'

    return odeShow, odeCode, jacCode, odeParams

def changeNparray2List(dic):
    for i in dic.keys():
        if isinstance(dic[i],np.ndarray):
            dic[i]=dic[i].tolist()
    return dic

def getPoppedWindow(father,width,height,title):
    settingWin = tk.Toplevel(father)
    ww = width
    hh = height
    sw = settingWin.winfo_screenwidth()
    sh = settingWin.winfo_screenheight()
    settingWin.geometry('%dx%d+%d+%d' % (ww, hh, (sw - ww) / 2, (sh - hh) / 2))
    settingWin.title(title)
    return settingWin

def getFrame(father,width,height,highlightbackground,highlightcolor,highlightthickness):
    frame = tk.Frame(father, width=width, height=height, highlightbackground=highlightbackground,
                              highlightcolor=highlightcolor, highlightthickness=highlightthickness)
    return frame

def func2color(func):
    if func=='+':
        return "red"
    elif func=='-':
        return "black"
    else:
        return None

def getNodeColor(gene,grn):
    grn=grn.tolist()
    if [gene,gene,'+'] in grn:
        return "#FF0000" # self activation
    if [gene, gene, '-'] in grn:
        return "#000000" # self inhibition
    return "#4169E1"  # non self regulation

def get_img(path,w,h):
    img = PIL.Image.open(path)
    img = img.resize((w,h), PIL.Image.ANTIALIAS)
    img = PIL.ImageTk.PhotoImage(img)
    return img

def dataFrame2comboboxList(df):
    rs=df.values.tolist()
    rs=[r[0]+" "+r[2]+" "+r[1] for r in rs]
    return rs

def edit_search(ety,listt,l):
    inp = ety.widget.get()
    if inp == '':
        data = listt
    else:
        data = []
        for item in listt:
            if inp.lower() in item.lower():
                data.append(item)
    edit_fill(l,data)

def edit_fill(l,data):
    l.delete(0, 'end')
    for item in data:
        l.insert('end', item)

def getSubnetGenes(path):
    data=np.loadtxt(path,dtype=str)
    data=[line.strip() for line in data]
    return data

def killPort(port):
    os.system("kill -9 $(lsof -t -i:"+str(port)+")")


def checkPort(port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1',int(port)))
        s.shutdown(2)
        return True # be taken
    except:
        return False # not be taken
