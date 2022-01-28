# encoding=utf-8
import os
import tkinter as tk
import tkinter.messagebox
from tkinter.filedialog import askopenfilename,askopenfilenames
import pandas as pd
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import networkx as nx
import matplotlib.pyplot as plt
import tkinter.messagebox
import json
import time
import platform
import webbrowser
import PIL.Image
import PIL.ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
# from pyecharts import options as opts
# from pyecharts.charts import Graph
# from cefpython3 import cefpython as cef
# from pyecharts.globals import SymbolType
# from pyecharts import options as opt
import scipy
import webbrowser
from jaal import Jaal
from multiprocessing import Process,Value
import resource

from AboutPage import *
from InputPage import *
from HelperFunctions import *
from SeqPage import *
from LandPathPage import *
from GRN_TME import *
from ODE_TME import *
from ModelPage import *

'''
Main Page
'''

class MainPage(object):
    def __init__(self,master):
        # layout
        self.root=master
        self.root.title('TMELand - A software to plot Waddington\'s landscape and paths based on the TME method')
        self.screenW=self.root.winfo_screenwidth()
        self.screenH=self.root.winfo_screenheight()
        self.winW=450
        self.winH=400
        self.root.geometry('%dx%d+%d+%d'%(self.winW, self.winH, (self.screenW-self.winW)/2, (self.screenH-self.winH)/2)) # 居中
        if platform.system()=='Windows':
            self.root.iconbitmap(default="./resource/icon.ico")
        else:
            icon = PIL.ImageTk.PhotoImage(file='./resource/icon.gif')
            self.root.tk.call('wm', 'iconphoto', self.root._w, icon)
        # DS init
        self.params={}
        self.inputChoice=tk.StringVar()
        self.loadModelType='' # four types: ODE(SBML), GRN, seq, TME
        self.TMEModelType=''
        self.loadModelToplogy=pd.DataFrame() # store model GRN topology: from to sign weight
        self.loadModelDEs=pd.DataFrame() # store model GRN DEs, params and ODEs
        self.loadModelPaths={'ODE':'','GRN':'','TME':'','seq_expr':'','seq_time':'','seq_gnames':'','seq_cnames':''}
        self.ODEModelOdeCode=''
        self.ODEModelJacCode=''
        self.Global_sp=None
        self.Global_sig=None
        self.Global_w=None
        self.savepath={}
        self.pathsAction={}
        self.landAxes=None
        self.drawPathCnt = 0  # control path color
        self.simu_t, self.simu_results=None,None
        self.subnetGenes=[]
        # widget
        self.createMainPage()

    def deleteContent(self):
        self.params = {}
        self.loadModelType = ''  # four types: ODE(SBML), GRN, seq, TME
        self.TMEModelType = ''
        self.loadModelToplogy = pd.DataFrame()  # store model GRN topology: from to sign weight
        self.loadModelDEs = pd.DataFrame()  # store model GRN DEs, params and ODEs
        self.loadModelPaths = {'ODE': '', 'GRN': '', 'TME': '', 'seq_expr': '', 'seq_time': '', 'seq_gnames': '',
                               'seq_cnames': ''}
        self.ODEModelOdeCode = ''
        self.ODEModelJacCode = ''
        self.Global_sp = None
        self.Global_sig = None
        self.Global_w = None
        self.savepath = {}
        self.pathsAction = {}
        self.drawPathCnt = 0  # control path color
        self.subnetGenes = []

    def createMainPage(self):

        # main menu bar
        main_menubar = tk.Menu(self.root)

        # menu for MAC OSX
        help_menu = tk.Menu(main_menubar, tearoff=0)
        main_menubar.add_cascade(label='Help', menu=help_menu)
        help_menu.add_command(label='Help', command=self.showHelp)
        about_menu = tk.Menu(main_menubar, tearoff=0)
        main_menubar.add_cascade(label='About', menu=about_menu)
        about_menu.add_command(label='About', command=self.showAbout)

        self.root['menu']=main_menubar

        # Main Page layout
        img=get_img('./resource/arrow_down.png',20,20)
        topo=get_img('./resource/topology.png',25,25)
        edit=get_img('./resource/edit.png',30,30)
        des=get_img('./resource/des.png',25,25)
        model_frame=tk.Frame(self.root,width=390,height=100)
        tk.Button(self.root, text='Input', font=('normal', 14, 'bold'),bg = "white", fg = "black", command=self.openInputWindow).pack(fill="both",padx=30,ipady=5,pady=10)
        l1=tk.Label(self.root, image=img)
        l1.image=img # a tk bug, must reassign here
        l1.pack()
        tk.Button(self.root, text='GRN Model', font=('normal', 14, 'bold'),bg = "white", fg = "black").pack(fill="both",padx=30,ipady=5)
        l2 = tk.Label(model_frame, image=topo)
        l2.image = topo  # a tk bug, must reassign here
        l3 = tk.Label(model_frame, image=edit)
        l3.image = edit  # a tk bug, must reassign here
        l4 = tk.Label(model_frame, image=des)
        l4.image = des  # a tk bug, must reassign here
        l2.grid(row=0,column=0)
        l3.grid(row=0,column=1)
        l4.grid(row=0,column=2)
        tk.Button(model_frame,text='GRN topology', font=('normal', 10),bg = "white", fg = "black", command=self.GRNToplogy).grid(row=1,column=0,padx=5)
        tk.Button(model_frame,text='Topology editing', font=('normal', 10),bg = "white", fg = "black", command=lambda: self.topologyEditing(self.root)).grid(row=1,column=1,padx=5)
        tk.Button(model_frame,text='DE-based GRN', font=('normal', 10), bg="white", fg="black",command=lambda: self.GRNDEs(self.root,4,0.7,1,1,0.5,1)).grid(row=1,column=2,padx=5)
        model_frame.pack(fill="both",padx=30,pady=10)
        l2=tk.Label(self.root, image=img)
        l2.image=img
        l2.pack()
        tk.Button(self.root, text='Dynamics Simulation', font=('normal', 14, 'bold'),bg = "white", fg = "black", command=self.openSimulationWindow).pack(fill="both",padx=30,ipady=5,pady=10)
        l3=tk.Label(self.root, image=img)
        l3.image=img
        l3.pack()
        tk.Button(self.root, text='Landscape & Path', font=('normal', 14, 'bold'),bg = "white", fg = "black", command=self.openLandscapePathWindow).pack(fill="both",padx=30,ipady=5,pady=10)


    def showHelp(self):
        webbrowser.open(url='https://github.com/JieZheng-ShanghaiTech/TMELand/blob/main/TMELand%20Manual.pdf',new=1,autoraise=True)

        # sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
        # cef.Initialize()
        # cef.CreateBrowserSync(url="https://github.com/JieZheng-ShanghaiTech/TMELand/blob/main/TMELand%20Manual.pdf",
        #                       window_title="TMELand User Manual")
        # cef.MessageLoop()

    def showAbout(self):
        # poped window setting
        about=getPoppedWindow(father=self.root,width=500,height=300,title='About TMELand')
        tk.Message(about, text=getAboutContent(), font=("Verdana", 10), justify=tk.LEFT, highlightbackground='black',
                   highlightcolor='black', highlightthickness=1).pack(pady=5)
    def openInputWindow(self):
        def uploadODE():
            if self.inputChoice.get() == '':
                tkinter.messagebox.showwarning(title='Warning', message='Please choose a model type!')
            else:
                self.deleteContent()
                self.loadModelType = self.inputChoice.get()
                print("The loaded model type is:", self.loadModelType)
                file = askopenfilename(initialdir=os.getcwd() + './ODE_SBML_models/', title="Select a ODE/SBML model",
                                       filetypes=[("ODE Files", "*.ode"), ("SBML Files", "*.xml")])
                self.loadModelPaths['ODE'] = file
                # parse
                if self.loadModelPaths['ODE'] == '':
                    tkinter.messagebox.showwarning(title='Warning', message='Please upload a model file!')
                else:
                    self.root.title('TMELand - ' + os.path.basename(self.loadModelPaths['ODE']))
                    print('The loaded model name is:', os.path.basename(self.loadModelPaths['ODE']))
                    # parse ODE: Obtain DEs-related
                    if '.xml' in self.loadModelPaths['ODE']:
                        odeShow, odeFunc, jacCode, odeParams = parseSBML(self.loadModelPaths['ODE'])
                    elif '.ode' in self.loadModelPaths['ODE']:
                        odeShow, odeFunc, jacCode, odeParams = parseODE(self.loadModelPaths['ODE'])
                    self.ODEModelOdeCode = odeFunc
                    self.ODEModelJacCode = jacCode
                    self.params['Sys_Dim'] = len(odeParams['genes'])
                    self.params['Genes'] = odeParams['genes']
                    lines = odeShow.split('\n')
                    lines = [line.split('=') for line in lines]
                    self.loadModelDEs = pd.DataFrame(lines)
                    # parse ODE: Obtain GRN topology
                    v1.set(os.path.basename(file)) # once uploaded file display in the label, it means successful.


        def uploadTSV():
            if self.inputChoice.get() == '':
                tkinter.messagebox.showwarning(title='Warning', message='Please choose a model type!')
            else:
                self.deleteContent()
                self.loadModelType = self.inputChoice.get()
                print("The loaded model type is:", self.loadModelType)
                file = askopenfilename(initialdir=os.getcwd() + './TSV_models/', title="Select a Text model",
                                       filetypes=[("Text Files", "*.tsv")])
                self.loadModelPaths['GRN'] = file
                # parse
                if self.loadModelPaths['GRN'] == '':
                    tkinter.messagebox.showwarning(title='Warning', message='Please upload a model file!')
                else:
                    self.root.title('TMELand - ' + os.path.basename(self.loadModelPaths['GRN']))
                    print('The loaded model name is:', os.path.basename(self.loadModelPaths['GRN']))
                    # parse GRN: Obtain GRN topology
                    self.loadModelToplogy = pd.read_csv(self.loadModelPaths['GRN'], sep='\t',
                                                        names=['regulator', 'target', 'func'])
                    self.loadModelToplogy.insert(loc=len(self.loadModelToplogy.columns),column='weight',value=[1.0]*len(self.loadModelToplogy.index))
                    self.params['IM'], self.params['Sys_Dim'], self.params['Genes'] = grnChooser2graph(
                        self.loadModelToplogy)
                    # parse GRN: Obtain GRN DEs
                    v2.set(os.path.basename(file))


        def uploadTME():
            if self.inputChoice.get() == '':
                tkinter.messagebox.showwarning(title='Warning', message='Please choose a model type!')
            else:
                self.deleteContent()
                self.loadModelType = self.inputChoice.get()
                print("The loaded model type is:", self.loadModelType)
                file = askopenfilename(initialdir=os.getcwd() + './TME_models/', title="Select a TME model",
                                       filetypes=[("Json Files", "*.json")])
                self.loadModelPaths['TME'] = file
                # parse
                if self.loadModelPaths['TME'] == '':
                    tkinter.messagebox.showwarning(title='Warning', message='Please upload a model file!')
                else:
                    self.root.title('TMELand - ' + os.path.basename(self.loadModelPaths['TME']))
                    print('The loaded model name is:', os.path.basename(self.loadModelPaths['TME']))
                    v3.set(os.path.basename(file))
                    # parse TME JSON data
                    with open(self.loadModelPaths['TME'], 'r') as fr:
                        data = json.load(fr)
                    self.TMEModelType = data['modelType']
                    self.loadModelToplogy=pd.DataFrame(data['modelTopology'],columns=['regulator', 'target', 'func','weight'])
                    self.loadModelDEs=pd.DataFrame(data['modelDEs'])
                    self.params = data['defaultParams']
                    self.Global_sp = np.array(data['stablePoints'])
                    self.Global_sig = np.array(data['sigma'])
                    self.Global_w = np.array(data['weight'])
                    self.ODEModelOdeCode = data['ODEModelOdeCode']
                    self.ODEModelJacCode = data['ODEModelJacCode']
                    self.savepath = data['allpath']
                    if self.TMEModelType=='GRN' or self.TMEModelType=='seq':
                        self.params['IM'] = np.array(self.params['IM'], dtype=int)
                        self.params['Hill_fn'] = np.array(self.params['Hill_fn'], dtype=float)
                        self.params['TM'] = np.array(self.params['TM'], dtype=float)
                        self.params['Act_Inh'] = np.array(self.params['Act_Inh'], dtype=float)
                        self.params['Degrade_rate'] = np.array(self.params['Degrade_rate'], dtype=float)
                    self.params['y_min']=np.array(self.params['y_min'],dtype=float)
                    self.params['y_max'] = np.array(self.params['y_max'], dtype=float)
                    self.params['vari_spec'] = np.array(self.params['vari_spec'], dtype=float)



        def uploadSeq_expr():
            if self.inputChoice.get() == '':
                tkinter.messagebox.showwarning(title='Warning', message='Please choose a model type!')
            else:
                self.deleteContent()
                self.loadModelType = self.inputChoice.get()
                print("The loaded model type is:", self.loadModelType)
                file = askopenfilename(initialdir=os.getcwd() + './scRNAseq_models/',title="Select gene expression data",filetypes=[("TXT Files", "*.txt")])
                self.loadModelPaths['seq_expr'] = file
                # parse
                if self.loadModelPaths['seq_expr'] == '':
                    tkinter.messagebox.showwarning(title='Warning', message='Please upload a expression file!')
                else:
                    self.root.title('TMELand - ' + os.path.basename(self.loadModelPaths['seq_expr']))
                    print('The loaded expression file is:', os.path.basename(self.loadModelPaths['seq_expr']))
                    v4.set(os.path.basename(file))

        def uploadSeq_time():
            if self.inputChoice.get() == '':
                tkinter.messagebox.showwarning(title='Warning', message='Please choose a model type!')
            else:
                file = askopenfilename(initialdir=os.getcwd() + './scRNAseq_models/', title="Select time-series data",
                                       filetypes=[("TXT Files", "*.txt")])
                self.loadModelPaths['seq_time'] = file
                # parse
                print('The loaded time file is:', os.path.basename(self.loadModelPaths['seq_time']))
                v5.set(os.path.basename(file))

        def uploadSeq_gnames():
            if self.inputChoice.get() == '':
                tkinter.messagebox.showwarning(title='Warning', message='Please choose a model type!')
            else:
                file = askopenfilename(initialdir=os.getcwd() + './scRNAseq_models/', title="Select gene names",
                                       filetypes=[("TXT Files", "*.txt")])
                self.loadModelPaths['seq_gnames'] = file
                self.params['Genes'] = np.loadtxt(self.loadModelPaths['seq_gnames'], dtype=str).tolist()
                print(self.params['Genes'])
                # parse
                print('The loaded gene-name file is:', os.path.basename(self.loadModelPaths['seq_gnames']))
                v6.set(os.path.basename(file))

        def uploadSeq_cnames():
            if self.inputChoice.get() == '':
                tkinter.messagebox.showwarning(title='Warning', message='Please choose a model type!')
            else:
                file = askopenfilename(initialdir=os.getcwd() + './scRNAseq_models/', title="Select cell names",
                                       filetypes=[("TXT Files", "*.txt")])
                self.loadModelPaths['seq_cnames'] = file
                # parse
                print('The loaded cell-name file is:', os.path.basename(self.loadModelPaths['seq_cnames']))
                v7.set(os.path.basename(file))

        file_img=tk.PhotoImage(file="./resource/icon.gif") # to be added
        inputWin=getPoppedWindow(father=self.root,width=480,height=550,title='Input')
        f1 = getFrame(inputWin, 480, 40, 'black', 'black', 1)
        f2 = getFrame(inputWin, 480, 40, 'black', 'black', 1)
        f3 = getFrame(inputWin, 480, 40, 'black', 'black', 1)
        f4 = getFrame(inputWin, 480, 40, 'black', 'black', 1)
        r1 = tk.Radiobutton(f1, text='ODE/SBML', variable=self.inputChoice, value='ODE')
        r2 = tk.Radiobutton(f2, text='TSV', variable=self.inputChoice, value='GRN')
        r3 = tk.Radiobutton(f3, text='scRNA-seq', variable=self.inputChoice, value='seq')
        r4 = tk.Radiobutton(f4, text='TME', variable=self.inputChoice, value='TME')
        f1.pack(side="top", fill="both", padx=50, ipady=5, pady=10)
        f2.pack(side="top", fill="both", padx=50, ipady=5, pady=10)
        f3.pack(side="top", fill="both", padx=50, ipady=5, pady=10)
        f4.pack(side="top", fill="both", padx=50, ipady=5, pady=10)

        r1.grid(row=0,column=0,sticky='w')
        tk.Label(f1, text='file:').grid(row=1,column=0,padx=10,sticky="w")
        v1=tk.StringVar()
        tk.Label(f1, textvariable=v1,bg="white",width=12).grid(row=1, column=1,padx=10)
        tk.Button(f1,text="upload file",command=uploadODE).grid(row=1,column=2,padx=10,sticky="e")

        r2.grid(row=0, column=0, sticky='w')
        tk.Label(f2, text='file:').grid(row=1, column=0, padx=10,sticky="w")
        v2 = tk.StringVar()
        tk.Label(f2, textvariable=v2,bg="white",width=12).grid(row=1, column=1,padx=10)
        tk.Button(f2, text="upload file", command=uploadTSV).grid(row=1, column=2,padx=10,sticky="e")

        r3.grid(row=0, column=0, sticky='w')
        tk.Label(f3, text='Expression:').grid(row=1, column=0, padx=10,pady=2,sticky="w")
        v4 = tk.StringVar()
        tk.Label(f3, textvariable=v4,bg="white",width=12).grid(row=1, column=1,padx=10,pady=2)
        tk.Button(f3, text="upload file", command=uploadSeq_expr).grid(row=1, column=2,padx=10,pady=2,sticky="e")
        tk.Label(f3, text='Time-series:').grid(row=2, column=0,  padx=10,pady=2,sticky="w")
        v5 = tk.StringVar()
        tk.Label(f3, textvariable=v5,bg="white",width=12).grid(row=2, column=1,padx=10,pady=2)
        tk.Button(f3, text="upload file", command=uploadSeq_time).grid(row=2, column=2,padx=10,pady=2,sticky="e")
        tk.Label(f3, text='Gene names:').grid(row=3, column=0, padx=10,pady=2,sticky="w")
        v6 = tk.StringVar()
        tk.Label(f3, textvariable=v6,bg="white",width=12).grid(row=3, column=1,padx=10,pady=2)
        tk.Button(f3, text="upload file", command=uploadSeq_gnames).grid(row=3, column=2,padx=10,pady=2,sticky="e")
        tk.Label(f3, text='Cell names:').grid(row=4, column=0, padx=10,pady=2,sticky="w")
        v7 = tk.StringVar()
        tk.Label(f3, textvariable=v7,bg="white",width=12).grid(row=4, column=1,padx=10,pady=2)
        tk.Button(f3, text="upload file", command=uploadSeq_cnames).grid(row=4, column=2,pady=2,padx=10,sticky="e")
        tk.Button(f3, text="scRNA-seq Analysis", command=lambda: self.seqAnalysis(inputWin)).grid(row=5, column=1, pady=3)
        tk.Button(f3, text="GRN Inference", command=lambda: self.grnInference(inputWin)).grid(row=6,  column=1, pady=3)

        r4.grid(row=0, column=0, sticky='w')
        tk.Label(f4, text='file:').grid(row=1, column=0,padx=10,sticky="w")
        v3 = tk.StringVar()
        tk.Label(f4, textvariable=v3,bg="white",width=12).grid(row=1, column=1,padx=10)
        tk.Button(f4, text="upload file", command=uploadTME).grid(row=1, column=2,padx=10,sticky="e")
        # tk.Button(inputWin, text='Submit', font=('normal', 14, 'bold'),bg = "white", fg = "black", command=self.parseData).pack(side="bottom",padx=50,ipady=5,pady=10)

    def callJall(self):
        # Jaal implementation
        node_df = pd.DataFrame(self.params['Genes'], columns=['id'])
        edge_df = self.loadModelToplogy.copy(deep=True)
        edge_df.columns = ['from', 'to', 'sign', 'weight']
        # edge_df.loc[:, 'label'] = edge_df.loc[:, 'weight'].astype(str) # show edge weight on the graph
        port = 8050

        # launch a process to serve as server
        def subProcessLaunchGraph(edge_df, node_df, mess):
            mess.value = 1
            Jaal(edge_df, node_df).plot(directed=True, vis_opts={'height': '600px',  # change height
                                                                 'interaction': {'hover': True},
                                                                 # turn on-off the hover
                                                                 'physics': {'stabilization': {'iterations': 100}}})

        mess = Value('I', 0)
        proc = Process(target=subProcessLaunchGraph, args=(edge_df, node_df, mess))
        proc.start()
        # proc.join()
        while True:
            if mess.value == 1:
                webbrowser.open("http://127.0.0.1:" + str(port) + "/", new=1, autoraise=True)
                break

    def GRNToplogy(self):
        if self.loadModelType=='ODE' or (self.loadModelType=='TME' and self.TMEModelType=='ODE'):
            tk.messagebox.showerror(title='Error', message="TMELand doesn't support topology parsing for ODE-based GRN models currently!")
        else:
            # check the port
            if checkPort(8050):
                # pop a window ask whether kill the cresponding process
                askWin = getPoppedWindow(father=self.root, width=230, height=130, title='Port Problem')
                tk.Message(askWin,
                           text="TMELand detects port 8050 has been taken, would you want to end that process immediately?",
                           bg="white", justify=tk.LEFT,
                           highlightbackground='black', width=200,
                           highlightcolor='black', highlightthickness=1).grid(row=0, columnspan=2, padx=10, pady=10)

                def yes():
                    killPort(8050)
                    self.callJall()
                    askWin.destroy()

                tk.Button(askWin, text="Yes", command=yes).grid(row=1, column=0, padx=10, pady=10)

                def no():
                    tk.messagebox.showwarning(title='Warning',
                                              message="Please end the process on port 8050 to get the latest data!")
                    askWin.destroy()

                tk.Button(askWin, text="No", command=no).grid(row=1, column=1, padx=10, pady=10)
            else:
                self.callJall()


        # pyecharts implementation
        # # graph visualization setting
        # node_size=30
        # edge_terminal=10
        #
        # nodes=[]
        # for gene in self.params['Genes']:
        #     nodes.append({"name": gene, "symbolSize": node_size,"itemStyle": {"normal": {"color": getNodeColor(gene,grn)}}})
        #
        # links = []
        # for i in range(len(grn)):
        #     links.append(opts.GraphLink(source=grn[i][0], target=grn[i][1],symbol_size=edge_terminal,linestyle_opts=opts.LineStyleOpts(color=func2color(grn[i][2]),width=1, curve=0.3)))
        #
        # c = (
        #         Graph(init_opts=opts.InitOpts(width="1000px", height="600px"))
        #         .add(series_name="",
        #              nodes=nodes,
        #              links=links,
        #              repulsion=8000,
        #              edge_symbol=[None, 'arrow'],
        #              is_selected=True,
        #              is_focusnode=True,
        #              is_roam=True,
        #              is_draggable=True,
        #              layout="force",
        #              )
        #         .set_global_opts(title_opts=opts.TitleOpts(title="GRN Topology"),
        #                          legend_opts=opts.LegendOpts(orient="vertical", pos_left="2%", pos_top="20%"),
        #                          toolbox_opts=opts.ToolboxOpts(is_show=True),
        #                          tooltip_opts=opts.TooltipOpts(is_show=True))
        #         .render("./resource/GRN.html")
        # )
        # # pop a cefpython realized window
        # # sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
        # # cef.Initialize()
        # # cef.CreateBrowserSync(url="file:///./resource/GRN.html",
        # #                       window_title="GRN Topology")
        # # cef.MessageLoop()
        #
        # # the above is only work on Win, so below
        # webbrowser.open("file:///"+os.getcwd()+'/resource/GRN.html',new=1,autoraise=True)


    def topologyEditing(self,father):
        if self.loadModelType == 'ODE' or (self.loadModelType == 'TME' and self.TMEModelType == 'ODE'):
            tk.messagebox.showerror(title='Error',message="TMELand doesn't support topology editing for ODE-based GRN models currently!")
        else:
            editWin=getPoppedWindow(father=father,width=400,height=580,title='GRN Topology Editing')
            # modify self.loadModelToplogy
            nodeFrame=getFrame(editWin, 360, 200, 'black', 'black', 1)
            edgeFrame=getFrame(editWin, 360, 200, 'black', 'black', 1)
            # node frame
            tk.Label(editWin,text="Node").pack(pady=10)
            nodeFrame.pack()
            tk.Label(nodeFrame, text="Gene name:").grid(row=0, column=0, sticky="w",pady=5,padx=5)
            geneEntry=tk.Entry(nodeFrame, textvariable=tk.StringVar)
            geneEntry.grid(row=0,column=1,sticky="e",pady=5,padx=5)
            l1_f = tk.Frame(nodeFrame)
            l1_f.grid(row=3, column=1, sticky="e", pady=5, padx=5)
            l1 = tk.Listbox(l1_f, height=3)
            l2 = ttk.Combobox(edgeFrame)
            l4 = ttk.Combobox(edgeFrame)
            def addGene(g):
                if g in self.params["Genes"]:
                    tk.messagebox.showerror(title='Error', message=g+' already in the list!')
                else:
                    self.params["Genes"].append(g)
                    # update list choice
                    edit_fill(l1, self.params["Genes"])
                    l2['value'] = tuple(self.params["Genes"])
                    l4['value'] = tuple(self.params["Genes"])
            def delGene(g):
                if g in np.unique(self.loadModelToplogy[['regulator','target']].values): # check whether it evolved in the edges of GRN
                    tk.messagebox.showerror(title='Error', message=g + ' evolved in the regulation of other genes!')
                else:
                    if g in self.params["Genes"]:
                        self.params["Genes"].remove(g)
                        # update list choice
                        edit_fill(l1, self.params["Genes"])
                        l2['value'] = tuple(self.params["Genes"])
                        l4['value'] = tuple(self.params["Genes"])
                    else:
                        tk.messagebox.showerror(title='Error', message=g + ' not in the list!')
            tk.Button(nodeFrame,text="Add node",command=lambda: addGene(geneEntry.get())).grid(row=1,column=0,sticky="w",pady=5,padx=20)
            tk.Button(nodeFrame,text="Delete node",command=lambda: delGene(geneEntry.get())).grid(row=1, column=1, sticky="e",pady=5,padx=20)
            tk.Label(nodeFrame, text="Genes list search:").grid(row=2, column=0, sticky="w",pady=5,padx=5)

            l1.pack(side=tk.LEFT, fill=tk.BOTH)
            edit_fill(l1, self.params["Genes"])
            s1 = tk.Scrollbar(l1_f)
            s1.pack(side=tk.RIGHT, fill=tk.BOTH)
            l1.config(yscrollcommand=s1.set)
            s1.config(command=l1.yview)
            e1=tk.Entry(nodeFrame,bg="white",fg="blue")
            e1.grid(row=2, column=1, sticky="e",pady=5,padx=5)
            e1.bind('<KeyRelease>', lambda eve1: edit_search(eve1,self.params["Genes"],l1))
            # edge frame
            tk.Label(editWin, text="Edge").pack(pady=10)
            edgeFrame.pack()
            tk.Label(edgeFrame, text="Source:").grid(row=0, column=0, sticky="w",padx=5,pady=5)
            l2.grid(row=0, column=1, sticky="e",padx=5,pady=5)
            l2['value'] = tuple(self.params["Genes"])
            tk.Label(edgeFrame, text="Relationship:").grid(row=1, column=0, sticky="w",padx=5,pady=5)
            l3 = ttk.Combobox(edgeFrame)
            l3.grid(row=1, column=1, sticky="e",padx=5,pady=5)
            l3['value'] = tuple(['+','-'])
            tk.Label(edgeFrame, text="Target:").grid(row=2, column=0, sticky="w",padx=5,pady=5)
            l4.grid(row=2, column=1, sticky="e",padx=5,pady=5)
            l4['value'] = tuple(self.params["Genes"])
            l5_f = tk.Frame(edgeFrame)
            l5_f.grid(row=5, column=1, sticky="e", padx=5, pady=5)
            l5 = tk.Listbox(l5_f, height=3)
            def addEdge(s,func,t): # add/modify edge
                if not self.loadModelToplogy.loc[(self.loadModelToplogy['regulator'] == s) & (self.loadModelToplogy['target']==t)].empty:
                    id = self.loadModelToplogy.loc[(self.loadModelToplogy['regulator'] == s) & (self.loadModelToplogy['target'] == t)].index
                    if self.loadModelToplogy.loc[id, 'func'].values[0]==func:
                        tk.messagebox.showerror(title='Error', message=s + func + t + ' already in the list!')
                    else:
                        self.loadModelToplogy.loc[id, 'func'] = func
                        tk.messagebox.showinfo(title='Info',message='You have changed relationship from ' + s + ' to ' + t + ' as ' + func + '!')
                        edit_fill(l5, dataFrame2comboboxList(self.loadModelToplogy))
                else:
                    self.loadModelToplogy=self.loadModelToplogy.append([{'regulator': s, 'target': t, 'func': func}], ignore_index=True)
                    edit_fill(l5, dataFrame2comboboxList(self.loadModelToplogy))
            def delEdge(s,func,t):
                if self.loadModelToplogy.loc[(self.loadModelToplogy['regulator'] == s) & (self.loadModelToplogy['target']==t)&(self.loadModelToplogy['func']==func)].empty:
                    tk.messagebox.showerror(title='Error', message=s+func+t + ' not in the list!')
                else:
                    id = self.loadModelToplogy.loc[(self.loadModelToplogy['regulator'] == s) & (self.loadModelToplogy['target'] == t) & (self.loadModelToplogy['func']==func)].index
                    self.loadModelToplogy = self.loadModelToplogy.drop(index=id)
                    edit_fill(l5, dataFrame2comboboxList(self.loadModelToplogy))
            tk.Button(edgeFrame, text="Add edge", command=lambda: addEdge(l2.get(),l3.get(),l4.get())).grid(row=3, column=0, sticky="w",padx=20,pady=5)
            tk.Button(edgeFrame, text="Delete edge", command=lambda: delEdge(l2.get(),l3.get(),l4.get())).grid(row=3, column=1, sticky="e",padx=20,pady=5)
            tk.Label(edgeFrame, text="Edges list search:").grid(row=4, column=0, sticky="w",padx=5,pady=5)
            l5.pack(side=tk.LEFT,fill=tk.BOTH)
            edit_fill(l5, dataFrame2comboboxList(self.loadModelToplogy))
            s2 = tk.Scrollbar(l5_f)
            s2.pack(side=tk.RIGHT, fill=tk.BOTH)
            l5.config(yscrollcommand=s2.set)
            s2.config(command=l5.yview)
            e5=tk.Entry(edgeFrame,bg="white",fg="blue")
            e5.grid(row=4, column=1, sticky="e", pady=5, padx=5)
            e5.bind('<KeyRelease>', lambda eve2: edit_search(eve2, dataFrame2comboboxList(self.loadModelToplogy), l5))
            def submitEditGRN():
                # call grnChooser2graph to update params
                self.params['IM'], self.params['Sys_Dim'], self.params['Genes'] = grnChooser2graph(self.loadModelToplogy)
                tk.messagebox.showinfo(title='Info', message='GRN topology editing successfully!')
            tk.Button(editWin,text="OK",font=('normal', 14, 'bold'),bg = "white", fg = "black",command=submitEditGRN).pack(pady=20)

    def autoODEGen(self,father,win,hill, threshold, act, self_act, inh, degrade):
        hill = int(hill)  # 2,3,4
        threshold = float(threshold)  # 0-4
        act = float(act)  # 0-4
        self_act=float(self_act)
        inh = float(inh)  # 0-4
        degrade = int(degrade)  # 1
        # store in parameters for TME method
        dim = self.params['Sys_Dim']
        self.params['Hill_fn'] = abs(self.params['IM']) * hill
        self.params['TM'] = abs(self.params['IM']) * threshold
        actInh = np.zeros((dim, dim))
        for i in range(dim):
            for j in range(dim):
                if self.params['IM'][i][j] == 1:
                    if i==j: # self activation
                        actInh[i][j] = self_act
                    else:
                        actInh[i][j] = act
                elif self.params['IM'][i][j] == -1:
                    actInh[i][j] = inh
                else:
                    actInh[i][j] = 0
        self.params['Act_Inh'] = actInh
        self.params['Degrade_rate'] = np.array([degrade] * dim)
        # Automatically ODE generation
        force = Force(self.params)
        grn_odes = force.get_odeEquations(self.params['Genes'])
        odes=[]
        for i in range(len(self.params['Genes'])):
            odes.append([self.params['Genes'][i]+'\'',grn_odes[i]])
        self.loadModelDEs=pd.DataFrame(odes)
         # update below DEs frame by destroy original window and open a new one
        win.destroy() # not elegant to update, destroy first then create
        self.GRNDEs(father,hill, threshold, act, self_act, inh, degrade)



    def GRNDEs(self,father,v1,v2,v3,v4,v5,v6): # initialization and reconstruction used to show params
        GRNDEsWin=getPoppedWindow(father=father,width=600,height=440,title='DEs Described GRN')
        coeFrame = getFrame(GRNDEsWin, 600, 100, 'black', 'black', 1)
        desFrame = getFrame(GRNDEsWin, 600, 300, 'black', 'black', 1)
        # coefficients frame
        if self.loadModelType=='GRN' or self.loadModelType=='seq':
            tk.Label(GRNDEsWin, text="DEs coefficients configuration").pack(padx=20,pady=5)
            coeFrame.pack(padx=20,pady=5,fill="both")
            tk.Label(coeFrame, text='Hill coefficient:').grid(row=0,column=0,sticky='WE')
            e1 = tk.Entry(coeFrame, textvariable=tk.StringVar,width=8)
            e1.delete(0, 'end')
            e1.insert(0, str(v1))
            e1.grid(row=0, column=1,sticky='WE')
            tk.Label(coeFrame, text='Threshold:').grid(row=0, column=2,sticky='WE')
            e2 = tk.Entry(coeFrame, textvariable=tk.StringVar,width=8)
            e2.delete(0, 'end')
            e2.insert(0, str(v2))
            e2.grid(row=0, column=3,sticky='WE')
            tk.Label(coeFrame, text='Activation:').grid(row=0, column=4,sticky='WE')
            e3 = tk.Entry(coeFrame, textvariable=tk.StringVar,width=8)
            e3.delete(0, 'end')
            e3.insert(0, str(v3))
            e3.grid(row=0, column=5,sticky='WE')
            tk.Label(coeFrame, text='Self activation:').grid(row=1, column=0, sticky='WE')
            e4 = tk.Entry(coeFrame, textvariable=tk.StringVar, width=8)
            e4.delete(0, 'end')
            e4.insert(0, str(v4))
            e4.grid(row=1, column=1, sticky='WE')
            tk.Label(coeFrame, text='Inhibition:').grid(row=1,column=2,sticky='WE')
            e5 = tk.Entry(coeFrame, textvariable=tk.StringVar,width=8)
            e5.delete(0, 'end')
            e5.insert(0, str(v5))
            e5.grid(row=1, column=3,sticky='WE')
            tk.Label(coeFrame, text='Degradation:').grid(row=1, column=4,sticky='WE')
            e6 = tk.Entry(coeFrame, textvariable=tk.StringVar,width=8)
            e6.delete(0, 'end')
            e6.insert(0, str(v6))
            e6.grid(row=1, column=5,sticky='WE')
            tk.Button(coeFrame, text='OK',command=lambda: self.autoODEGen(father,GRNDEsWin,e1.get(),e2.get(),e3.get(),e4.get(),e5.get(),e6.get()),width=6).grid(row=5,column=2,columnspan=2,sticky='WE', pady=5)
        # DEs frame
        tk.Label(GRNDEsWin, text="Differential equations").pack(padx=20, pady=5)
        desFrame.pack(padx=20,pady=5,fill="both")
        showDEsDescribedGRN(desFrame,self.loadModelDEs)
        # def updateDEs(table): update odes functionality hasn't been implemented
        #     new_odes=table.model.data
        #     self.loadModelDEs=dict2odesdf(new_odes)
        # tk.Button(GRNDEsWin, text='Update DEs',command=lambda: updateDEs(table)).pack(padx=20, pady=20)

    def doSimulation(self, fig, canvas, e1, e2, e3, l1):
        nSeries = int(e1)
        geneMax = int(e2)
        inp_time = int(e3)

        # store in parameters
        self.params['cycle'] = nSeries
        self.params['xmax'] = geneMax
        self.params['Tfinal'] = inp_time
        genes = self.params['Genes']

        # draw landscape
        if self.loadModelType == 'ODE' or (self.loadModelType=='TME' and self.TMEModelType=='ODE'):
            self.simu_t, self.simu_results = ode_simulation(self.params, self.ODEModelOdeCode,self.ODEModelJacCode)
        elif self.loadModelType == 'GRN' or self.loadModelType == 'seq' or (self.loadModelType=="TME" and (self.TMEModelType=='GRN' or self.TMEModelType=='seq')):
            self.simu_t, self.simu_results = grn_simulation(self.params)

        fig.clear()
        axes1 = fig.add_subplot(111)
        traj = np.array(self.simu_results[0])  # the first trajectory by default
        for id,g in enumerate(genes):
            axes1.plot(self.simu_t, traj[:,id], label=g)
        axes1.set_xlabel('time')
        axes1.set_ylabel('expression level')
        axes1.legend()
        canvas.draw()

        l1['value'] = ([i for i in range(1, 1 + nSeries)])

    def doSimulationAnalysis(self):
        traj=np.array(self.simu_results[0]) # the distance of last two points
        if np.linalg.norm(traj[-1,:] - traj[-2,:]) <= 1e-6:
            tkinter.messagebox.showinfo(title='Info', message='The model has converged!')
        else:
            tkinter.messagebox.showinfo(title='Info', message='The model hasn\'t converged, please change parameters!')

    def doSimulationUpdate(self,fig,canvas,traj_no):
        index=int(traj_no)-1
        fig.clear()
        axes1 = fig.add_subplot(111)
        traj = np.array(self.simu_results[index])
        for id, g in enumerate(self.params['Genes']):
            axes1.plot(self.simu_t, traj[:, id], label=g)
        axes1.set_xlabel('time')
        axes1.set_ylabel('expression level')
        axes1.legend()
        canvas.draw()

    def openSimulationWindow(self):
        simuWin=getPoppedWindow(father=self.root,width=780,height=480,title='Simulation')
        leftFrame = tk.Frame(simuWin, width=350, height=480)
        rightFrame = tk.Frame(simuWin, width=380, height=480)
        leftFrame.grid(row=0, column=0)
        rightFrame.grid(row=0, column=1)

        fig = Figure(figsize=(5,5))
        canvas = FigureCanvasTkAgg(fig, rightFrame)
        """
        Left Frame
        """
        initFrame = getFrame(leftFrame, 300, 500, 'black', 'black', 1)
        updateFrame = getFrame(leftFrame, 300, 500, 'black', 'black', 1)
        l1 = ttk.Combobox(updateFrame, width=8)
        # initialization setting
        tk.Label(leftFrame, text="Parameters setting").pack(padx=20, pady=5)
        initFrame.pack(padx=20, pady=5, fill="both")
        tk.Label(initFrame, text='Number of series:', width=16).grid(row=0, column=0, sticky='W',pady=10)
        e1 = tk.Entry(initFrame, textvariable=tk.StringVar(), width=14)
        e1.insert(0, 20)
        e1.grid(row=0, column=1, sticky='E', padx=10,pady=10)
        tk.Label(initFrame, text='Gene max value:', width=16).grid(row=1, column=0, sticky='W',pady=10)
        e2 = tk.Entry(initFrame, textvariable=tk.StringVar(), width=14)
        e2.insert(0, 1)
        e2.grid(row=1, column=1, sticky='E', padx=10,pady=10)
        tk.Label(initFrame, text='Time:', width=16).grid(row=2, column=0, sticky='W',pady=10)
        e3 = tk.Entry(initFrame, textvariable=tk.StringVar(), width=14)
        e3.insert(0, 200)
        e3.grid(row=2, column=1, sticky='E', padx=10,pady=10)
        tk.Button(initFrame, text='Simulation', width=7,
                  command=lambda: self.doSimulation(fig, canvas, e1.get(), e2.get(), e3.get(),l1)).grid(
            row=4, column=0, sticky='WE', pady=30,padx=15)
        tk.Button(initFrame, text='Analysis', width=7,
                  command=self.doSimulationAnalysis).grid(
            row=4, column=1, sticky='WE', pady=30,padx=15)
        tk.Label(leftFrame, text="Update trajectory").pack(padx=20, pady=5)
        updateFrame.pack(padx=20, pady=5, fill="both")
        tk.Label(updateFrame, text='Trajectory:').grid(row=0, column=0, sticky='W',pady=10)
        l1.grid(row=0, column=2, sticky='E', padx=10,pady=10)
        tk.Button(updateFrame, text='Update', width=9,
                  command=lambda: self.doSimulationUpdate(fig,canvas,l1.get())).grid(row=1, column=1, sticky='WE', pady=30,padx=5)

        """
        Right Frame
        """
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True,pady=10)

        toolbar = NavigationToolbar2Tk(canvas, rightFrame)
        toolbar.update()
        toolbar.pack(side=tk.TOP, pady=2, padx=5, ipadx=5)
        canvas._tkcanvas.pack(pady=10, padx=10, ipadx=5, side=tk.TOP, fill=tk.BOTH, expand=True)


    def drawLandscape(self,fig,canvas,nSeries,geneMax,inp_time,diffusion,l3,l4):
        tstart = time.time()
        # self.savepath = {}
        nSeries = int(nSeries)
        geneMax = int(geneMax)
        inp_time = int(inp_time)
        diffusion = float(diffusion)

        # store in parameters
        self.params['cycle'] = nSeries
        self.params['xmax'] = geneMax
        self.params['Tfinal'] = inp_time
        self.params['Diffusion'] = diffusion
        genes = self.params['Genes']
        # use default visualization-related params
        self.params['y_min'] = np.array([0, 0])  # by default
        self.params['y_max'] = np.array([3, 3])
        self.params['vari_spec'] = np.array([0, 1])  # by default, only using above parameters

        # draw landscape
        # tk.Label(self.rightFrame, image=img).grid(row=0, column=0, sticky='wens')
        if self.loadModelType == 'ODE' or (self.loadModelType=='TME' and self.TMEModelType=='ODE'):
            self.Global_sp, self.Global_sig, self.Global_w = ode_find_stable(self.params, self.ODEModelOdeCode,self.ODEModelJacCode)
            if len(self.Global_sp) == 0:
                tk.messagebox.showwarning(title='Warning', message='No steady points!')
            self.xAxis, self.yAxis, self.P, self.params['stablePoints'] = ode_tme_draw_landscape(self.params, self.Global_sp, self.Global_sig, self.Global_w)
        elif self.loadModelType == 'GRN' or self.loadModelType == 'seq' or (self.loadModelType=='TME' and (self.TMEModelType=='GRN' or self.TMEModelType=='seq')):
            self.Global_sp, self.Global_sig, self.Global_w = grn_find_stable(self.params)
            if len(self.Global_sp) == 0:
                tk.messagebox.showwarning(title='Warning', message='No steady points!')
            self.xAxis, self.yAxis, self.P, self.params['stablePoints'] = grn_tme_draw_landscape(
                self.params, self.Global_sp, self.Global_sig, self.Global_w)

        fig.clear()
        axes1 = fig.add_subplot(111, projection='3d')
        # print('initial P: ',self.P)
        tmp = axes1.plot_surface(self.xAxis, self.yAxis, self.P, cmap='jet', zorder=1)
        axes1.set_xlabel(genes[self.params['vari_spec'][0]])
        axes1.set_ylabel(genes[self.params['vari_spec'][1]])
        axes1.set_zlabel('U')

        # mark stable points
        steadyMarkers = []
        for i in self.params['stablePoints']:
            steadyMarkers.append(i[self.params['vari_spec']].tolist())
        for i in range(len(steadyMarkers)):
            axes1.text(x=steadyMarkers[i][0], y=steadyMarkers[i][1], z=0, s=str(i + 1), c='red', size=12)

        fig.colorbar(tmp)
        canvas.draw()
        # tend = time.time()
        # print('The consuming time of a landscape is: ' + str(tend - tstart) + ' s')
        # mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0
        # print('The max consuming memory of a landscape is: '+str(mem)+' MB')
        self.landAxes=axes1 # be used for drawing path
        l3['value']=([i for i in range(1,np.array(self.params['stablePoints']).shape[0]+1)]) # attractors No. for selection of begin and end atts
        l4['value'] = ([i for i in range(1,np.array(self.params['stablePoints']).shape[0]+1)])

    def updateByMarkers(self,fig,canvas,marker1,marker2,marker1_lb,marker1_ub,marker2_lb,marker2_ub,l3,l4): # 考虑有没有必要放在主文件里
        marker1_lb = float(marker1_lb)
        marker1_ub = float(marker1_ub)
        marker2_lb = float(marker2_lb)
        marker2_ub = float(marker2_ub)
        genes = self.params['Genes']
        self.params['vari_spec'] = np.array([genes.index(marker1), genes.index(marker2)])
        self.params['y_min'] = np.array([marker1_lb, marker2_lb])
        self.params['y_max'] = np.array([marker1_ub, marker2_ub])
        if self.loadModelType == 'GRN' or self.loadModelType == 'seq' or (self.loadModelType=='TME' and (self.TMEModelType=='GRN' or self.TMEModelType=='seq')):
            self.xAxis, self.yAxis, self.P, self.params['stablePoints'] = grn_tme_draw_landscape(
                self.params, self.Global_sp, self.Global_sig, self.Global_w)
        elif self.loadModelType == 'ODE' or (self.loadModelType=='TME' and self.TMEModelType=='ODE'):
            self.xAxis, self.yAxis, self.P, self.params['stablePoints'] = ode_tme_draw_landscape(
                self.params, self.Global_sp, self.Global_sig, self.Global_w)
        fig.clear()
        axes1 = fig.add_subplot(111, projection='3d')
        # print('update P: ',self.P)
        tmp = axes1.plot_surface(self.xAxis, self.yAxis, self.P, cmap='jet', zorder=1)
        axes1.set_xlabel(genes[self.params['vari_spec'][0]])
        axes1.set_ylabel(genes[self.params['vari_spec'][1]])
        axes1.set_zlabel('U')

        steadyMarkers = []
        for i in np.array(self.params['stablePoints']):
            steadyMarkers.append(i[np.array(self.params['vari_spec'])].tolist())
        for i in range(len(steadyMarkers)):
            axes1.text(x=steadyMarkers[i][0], y=steadyMarkers[i][1], z=0, s=str(i + 1), c='red', size=12)

        fig.colorbar(tmp)
        canvas.draw()
        self.landAxes=axes1
        l3['value'] = ([i for i in range(1, np.array(self.params['stablePoints']).shape[
            0] + 1)])  # attractors No. for selection of begin and end atts
        l4['value'] = ([i for i in range(1, np.array(self.params['stablePoints']).shape[0] + 1)])

        # add paths when landscape is be updated if there are paths (only for same markers)
        if self.savepath != {}:
            color_cnt = 0
            for i in self.savepath.keys():
                color_cnt += 1
                pathi = np.array(self.savepath[i])  # ith path
                pathx = pathi[self.params['vari_spec'][0]]
                pathy = pathi[self.params['vari_spec'][1]]
                pathz = np.zeros_like(pathx)
                num = pathx.shape[0]
                for i in range(num):
                    # x grid
                    for xx in range(100):
                        if xx == 99:
                            idx = 99
                        else:
                            if pathx[i] >= self.xAxis[0][xx] and pathx[i] <= self.xAxis[0][xx + 1]:
                                idx = xx
                                break
                    # y grid
                    for yy in range(100):
                        if yy == 99:
                            idy = 99
                        else:
                            if pathy[i] >= self.yAxis[yy][0] and pathy[i] <= self.yAxis[yy + 1][0]:
                                idy = yy
                                break
                    # get P
                    pathz[i] = np.array(self.P)[idy, idx]
                if color_cnt % 2 == 0:
                    color_list = ['cyan']
                else:
                    color_list = ['yellow']
                # random_color_index=random.randint(0,1)
                random_color_index = 0
                axes1.plot(pathx, pathy, pathz, c=color_list[random_color_index],
                                zorder=3)  # z+2 to display it on the surface
                arrow_pos = int(len(pathx) / 3)
                axes1.plot(pathx[arrow_pos:arrow_pos + 1], pathy[arrow_pos:arrow_pos + 1],
                                pathz[arrow_pos:arrow_pos + 1], c=color_list[random_color_index],
                                marker='>', zorder=3)
                canvas.draw()


    def backendDrawPath(self,fig,canvas,tmax,pointInPath,att1,att2):
        attractorNum = np.array(self.params['stablePoints']).shape[0]
        if attractorNum == 0:
            tk.messagebox.showwarning(title='Warning', message='No attractor!')
        elif attractorNum == 1:
            tk.messagebox.showwarning(title='Warning', message='Only one attractor, no path!')
        else:
            tstart = time.time()
            self.drawPathCnt += 1  # control path color
            self.params['tmax'] = int(tmax)
            self.params['pointInPath'] = int(pointInPath)
            start = int(att1)  # begin attractor
            end = int(att2)  # end attractor
            if self.loadModelType == 'ODE' or (self.loadModelType=='TME' and self.TMEModelType=='ODE'):
                path, action = ode_ss_path(np.array(self.params['stablePoints'][start - 1]),
                                           np.array(self.params['stablePoints'][end - 1]), self.params,
                                           self.ODEModelOdeCode)
            elif self.loadModelType == 'GRN' or self.loadModelType == 'seq' or (self.loadModelType=='TME' and (self.TMEModelType=='GRN' or self.TMEModelType=='seq')):
                path, action = grn_ss_path(np.array(self.params['stablePoints'][start - 1]),
                                           np.array(self.params['stablePoints'][end - 1]), self.params)
            attbeginend = str(start) + '-' + str(end)
            print(attbeginend + 'Transfer path:', path)
            self.savepath[attbeginend] = path.tolist()  # save one trajectory for all variables, but save landscape for two variables
            self.pathsAction[attbeginend] = action
            # show on the landscape
            pathx = path[self.params['vari_spec'][0]]
            pathy = path[self.params['vari_spec'][1]]
            pathz = np.zeros_like(pathx)
            num = pathx.shape[0]
            # print('path P: ',self.P)
            for i in range(num):
                # x grid
                for xx in range(100):
                    if xx == 99:
                        idx = 99
                    else:
                        if pathx[i] >= self.xAxis[0][xx] and pathx[i] <= self.xAxis[0][xx + 1]:
                            idx = xx
                            break
                # y grid
                for yy in range(100):
                    if yy == 99:
                        idy = 99
                    else:
                        if pathy[i] >= self.yAxis[yy][0] and pathy[i] <= self.yAxis[yy + 1][0]:
                            idy = yy
                            break
                # get P

                pathz[i] = self.P[idy, idx]  # !!! pay attention
            if self.drawPathCnt % 2 == 0:
                color_list = ['cyan']
            else:
                color_list = ['yellow']
            # random_color_index=random.randint(0,1)
            random_color_index = 0
            # self.axes1.plot_surface(pathx, pathy, self.P, c=color_list[random_color_index],zorder=3) # z+2 to display it on the surface
            self.landAxes.plot(pathx, pathy, pathz, c=color_list[random_color_index],
                            zorder=3)  # z+2 to display it on the surface
            arrow_pos = int(len(pathx) / 3)
            # self.axes1.plot_surface(pathx[arrow_pos:arrow_pos+1], pathy[arrow_pos:arrow_pos+1], self.P, c=color_list[random_color_index], marker='>',zorder=3)
            self.landAxes.plot(pathx[arrow_pos:arrow_pos + 1], pathy[arrow_pos:arrow_pos + 1], pathz[arrow_pos:arrow_pos + 1],
                            c=color_list[random_color_index], marker='>', zorder=3)

            canvas.draw()
            # tend = time.time()
            # print('The consuming time of a path is: ' + str(tend - tstart) + ' s')
            # mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0
            # print('The max consuming memory of a path is: ' + str(mem) + ' MB')

    def openLandscapePathWindow(self):
        landPathWin=getPoppedWindow(father=self.root,width=910,height=640,title='Epigenetic Landscape and Kinetic Path')
        leftFrame=tk.Frame(landPathWin,width=300, height=650)
        rightFrame=tk.Frame(landPathWin,width=550, height=650)
        leftFrame.grid(row=0,column=0)
        rightFrame.grid(row=0,column=1)

        fig = Figure(figsize=(6,6))
        canvas = FigureCanvasTkAgg(fig, rightFrame)
        """
        Left Frame
        """
        initFrame = getFrame(leftFrame, 300, 40, 'black', 'black', 1)
        updFrame = getFrame(leftFrame, 300, 40, 'black', 'black', 1)
        ptyFrame = getFrame(leftFrame, 300, 40, 'black', 'black', 1)
        pathFrame = getFrame(leftFrame, 300, 40, 'black', 'black', 1)

        l3 = ttk.Combobox(pathFrame, width=10)
        l4 = ttk.Combobox(pathFrame, width=10)
        # initialization setting
        tk.Label(leftFrame,text="Initialization setting").pack(padx=20,pady=5)
        initFrame.pack(padx=20,pady=5,fill="both")
        tk.Label(initFrame, text='Number of series:').grid(row=0,column=0, sticky='W')
        e1 = tk.Entry(initFrame, textvariable=tk.StringVar(),width=12)
        e1.insert(0, 500)
        e1.grid(row=0, column=2, sticky='E',padx=10)
        tk.Label(initFrame, text='Gene max value:').grid(row=1, column=0,sticky='W')
        e2 = tk.Entry(initFrame, textvariable=tk.StringVar(),width=12)
        e2.insert(0, 1)
        e2.grid(row=1, column=2, sticky='E',padx=10)
        tk.Label(initFrame, text='Time:').grid(row=2, column=0,sticky='W')
        e3 = tk.Entry(initFrame, textvariable=tk.StringVar(),width=12)
        e3.insert(0, 1000)
        e3.grid(row=2, column=2, sticky='E',padx=10)
        tk.Label(initFrame, text='Diffusion:').grid(row=3, column=0,sticky='W')
        e4 = tk.Entry(initFrame, textvariable=tk.StringVar(),width=12)
        e4.insert(0, 0.005)
        e4.grid(row=3, column=2, sticky='E',padx=10)
        tk.Button(initFrame, text='Draw', width=9,command=lambda: self.drawLandscape(fig,canvas,e1.get(),e2.get(),e3.get(),e4.get(),l3,l4)).grid(row=4, column=1,sticky='WE',pady=5)

        # update landscape
        tk.Label(leftFrame, text="Update landscape").pack(padx=20,pady=5)
        updFrame.pack(padx=20,pady=5,fill="both")
        tk.Label(updFrame, text='Visualization markers:').grid(row=0, sticky='W')
        tk.Label(updFrame, text='Min:').grid(row=0, column=1, sticky='w')
        tk.Label(updFrame, text='Max:').grid(row=0, column=2, sticky='w')
        l1,l2 = ttk.Combobox(updFrame,width=12),ttk.Combobox(updFrame,width=12)
        l1['value']=(self.params['Genes'])
        l2['value']=(self.params['Genes'])
        l1.grid(row=1, column=0, sticky='w',padx=2)
        l2.grid(row=2, column=0, sticky='w',padx=2)
        e5 = tk.Entry(updFrame, textvariable=tk.StringVar(),width=10)
        e5.insert(0, 0)
        e5.grid(row=1, column=1, sticky='w',padx=2)
        e6 = tk.Entry(updFrame, textvariable=tk.StringVar(),width=10)
        e6.insert(0, 3)
        e6.grid(row=1, column=2, sticky='w',padx=2)  # marker1 bound: e5; e6
        e7 = tk.Entry(updFrame, textvariable=tk.StringVar(),width=10)
        e7.insert(0, 0)
        e7.grid(row=2, column=1, sticky='w',padx=2)
        e8 = tk.Entry(updFrame, textvariable=tk.StringVar(),width=10)
        e8.insert(0, 3)
        e8.grid(row=2, column=2, sticky='w',padx=2)  # marker2 bound: e7; e8
        tk.Button(updFrame, text='Update', command=lambda: self.updateByMarkers(fig,canvas,l1.get(),l2.get(),e5.get(),e6.get(),e7.get(),e8.get(),l3,l4),width=9).grid(row=3,column=1,sticky='WE',pady=5,padx=2)

        # landscape property
        tk.Label(leftFrame, text="Landscape properties").pack(padx=20,pady=5)
        ptyFrame.pack(padx=20,pady=5,fill="both")
        tk.Button(ptyFrame, text='Show attractors', command=lambda: showAtts(landPathWin,self.Global_w,self.params)).grid(row=0, sticky='WE',pady=5,padx=2)
        tk.Button(ptyFrame, text='Show top view', command=lambda: showTopView(canvas,self.landAxes)).grid(row=0, column=1, sticky='WE',pady=5,padx=2)

        # kinetic path calculation
        tk.Label(leftFrame, text="Kinetic path calculation").pack(padx=20,pady=5)
        pathFrame.pack(padx=20,pady=5,fill="both")
        tk.Label(pathFrame, text='Time range:').grid(row=0, column=0, sticky='W')
        tmax = tk.Entry(pathFrame, textvariable=tk.StringVar(),width=10)
        tmax.insert(0, 5)
        tmax.grid(row=0, column=2, sticky='E')
        tk.Label(pathFrame, text='Points number:').grid(row=1, column=0, sticky='W')
        pointInPath = tk.Entry(pathFrame, textvariable=tk.StringVar(),width=10)
        pointInPath.insert(0, 20)
        pointInPath.grid(row=1, column=2, sticky='E')
        tk.Label(pathFrame, text='Beginning attractor:').grid(row=2, column=0, sticky='W')
        tk.Label(pathFrame, text='Ending attractor:').grid(row=3, column=0, sticky='W')
        l3.grid(row=2, column=2, sticky='E')
        l4.grid(row=3, column=2, sticky='E')
        tk.Button(pathFrame, text='Draw', command=lambda: self.backendDrawPath(fig,canvas,tmax.get(),pointInPath.get(),l3.get(),l4.get()) ,width=9).grid(row=4, column=1, sticky='we', pady=5)
        """
        Right Frame
        """
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, rightFrame)
        toolbar.update()
        toolbar.pack(side=tk.TOP, pady=2, padx=5, ipadx=5)
        canvas._tkcanvas.pack(pady=2, padx=10, ipadx=5, side=tk.TOP, fill=tk.BOTH, expand=True)
        tk.Button(rightFrame, text='Save result', command=lambda: saveLand(self.loadModelType,self.loadModelToplogy.values.tolist(),self.loadModelDEs.values.tolist(),self.Global_sp,self.Global_sig,self.Global_w,self.savepath,self.pathsAction,self.params,self.ODEModelOdeCode,self.ODEModelJacCode)).pack(side=tk.BOTTOM)

        if self.loadModelType=='TME':
            self.landAxes=restoreLandscape(fig,canvas,self.loadModelPaths['TME'],e1,e2,e3,e4,l1,l2,e5,e6,e7,e8,tmax,pointInPath,l3,l4)

    def seqAnalysis(self,father):
        seqAnalysisWin=getPoppedWindow(father=father,width=660,height=540,title='scRNA-seq Analysis')
        visualization_choice = tk.Frame(seqAnalysisWin, width=300, height=100)
        visualization_choice.pack()
        tk.Label(visualization_choice, text='Visualization:').grid(row=0, column=0, pady=10,padx=5)
        visualization_plots = ttk.Combobox(visualization_choice)
        visualization_plots['value'] = (['dimensionality reduction (pca)', 'clustering', 'trajectory inference'])
        visualization_plots.grid(row=0, column=1, pady=10,padx=5)
        tk.Label(visualization_choice, text='Color:').grid(row=0, column=2, pady=10,padx=5)
        colors=ttk.Combobox(visualization_choice)
        colors['value'] = (self.params['Genes']+['cell label','clustering'])
        colors.grid(row=0, column=3, pady=10,padx=5)

        fig = Figure(figsize=(5,5))
        canvas = FigureCanvasTkAgg(fig, seqAnalysisWin)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, anchor='s',fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, seqAnalysisWin)
        toolbar.update()
        toolbar.pack(side=tk.TOP, anchor='s',pady=2, padx=5, ipadx=5)
        canvas._tkcanvas.pack(pady=2, padx=30, ipadx=5, side=tk.TOP, anchor='s',fill=tk.BOTH, expand=True)

        tk.Button(visualization_choice, text="Draw",command=lambda: visualAnalyzeData(canvas,fig,visualization_plots.get(),colors.get(),self.loadModelPaths)).grid(row=0,column=4,pady=10,padx=5)

    def grnInference(self,father):
        GRNInfAlg=tk.StringVar()
        grnInfWin=getPoppedWindow(father=father,width=385,height=490,title='Automatically GRN Inference')
        tk.Radiobutton(grnInfWin, text='Use SCODE', variable=GRNInfAlg, value='SCODE').grid(row=0,column=0,padx=10,pady=10,sticky='W')
        seq_norm_var = tk.IntVar()
        seq_norm = tk.Checkbutton(grnInfWin, text='seq normalization', variable=seq_norm_var, onvalue=1, offvalue=0)
        seq_norm.grid(row=1,column=0,padx=10,sticky='W')
        paramFrame=getFrame(grnInfWin, 300, 40, 'black', 'black', 1)
        paramFrame.grid(row=2,columnspan=3,padx=20,pady=10,sticky="we")
        filterFrame=getFrame(grnInfWin, 300, 40, 'black', 'black', 1)
        filterFrame.grid(row=4,columnspan=3,padx=20,pady=10,sticky="we")
        # tk.Radiobutton(grnInfWin, text='Use PoLoBag', variable=GRNInfAlg, value='PoLoBag').grid(row=3, column=0, padx=10,pady=10, sticky='W')
        # paramFrame2=getFrame(grnInfWin, 300, 40, 'black', 'black', 1)
        # paramFrame2.grid(row=4,columnspan=3,padx=20,pady=10,sticky="we")
        # SCODE frame
        tfnum,pnum,cnum,maxite,repeat = tk.StringVar(),tk.StringVar(),tk.StringVar(),tk.StringVar(),tk.StringVar()
        tk.Label(paramFrame, text='tfnum:').grid(row=0, column=0,sticky="we",pady=5,padx=10)
        e1 = tk.Entry(paramFrame, textvariable=tfnum,width=12)
        if self.loadModelPaths['seq_gnames']!='':
            e1.insert(0, len(self.params['Genes']))
        e1.grid(row=0, column=1,sticky="we",pady=5,padx=10)
        tk.Label(paramFrame, text='pnum:').grid(row=1, column=0,sticky="we",pady=5,padx=10)
        e2 = tk.Entry(paramFrame, textvariable=pnum,width=12)
        e2.insert(0, 2)
        e2.grid(row=1, column=1,sticky="we",pady=5,padx=10)
        tk.Label(paramFrame, text='cnum:').grid(row=2, column=0,sticky="we",pady=5,padx=10)
        e3 = tk.Entry(paramFrame, textvariable=cnum,width=12)
        if self.loadModelPaths['seq_cnames']!='':
            e3.insert(0, len(np.loadtxt(self.loadModelPaths['seq_cnames'],dtype=str)))
        e3.grid(row=2, column=1,sticky="we",pady=5,padx=10)
        tk.Label(paramFrame, text='maxite:').grid(row=3, column=0,sticky="we",pady=5,padx=10)
        e4 = tk.Entry(paramFrame, textvariable=maxite,width=12)
        e4.insert(0, 100)
        e4.grid(row=3, column=1,sticky="we",pady=5,padx=10)
        tk.Label(paramFrame, text='repeat:').grid(row=4, column=0, sticky="we", pady=5, padx=10)
        e5 = tk.Entry(paramFrame, textvariable=repeat, width=12)
        e5.insert(0, 10)
        e5.grid(row=4, column=1, sticky="we", pady=5, padx=10)
        # PoLobag frame
        # n12, n22, nm, nb, alpha = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(),tk.StringVar()
        # tk.Label(paramFrame2, text='n12:').grid(row=0, column=0)
        # e5 = tk.Entry(paramFrame2, textvariable=n12,width=7)
        # e5.insert(0, 0.5)
        # e5.grid(row=0, column=1)
        # tk.Label(paramFrame2, text='n22:').grid(row=0, column=2)
        # e6 = tk.Entry(paramFrame2, textvariable=n22,width=7)
        # e6.insert(0, 3.5)
        # e6.grid(row=0, column=3)
        # tk.Label(paramFrame2, text='nM:').grid(row=0, column=4)
        # e7 = tk.Entry(paramFrame2, textvariable=nm,width=7)
        # e7.insert(0, 0.5)
        # e7.grid(row=0, column=5)
        # tk.Label(paramFrame2, text='nB:').grid(row=1, column=0)
        # e8 = tk.Entry(paramFrame2, textvariable=nb,width=7)
        # e8.insert(0, 500)
        # e8.grid(row=1, column=1)
        # tk.Label(paramFrame2, text='alpha:').grid(row=1, column=2)
        # e9 = tk.Entry(paramFrame2, textvariable=alpha,width=7)
        # e9.insert(0, 0.1)
        # e9.grid(row=1, column=3)

        tk.Label(filterFrame, text='Subnetwork genes:').grid(row=7, column=0,sticky="w",pady=5,padx=5)
        v1 = tk.StringVar()
        tk.Label(filterFrame, textvariable=v1, bg="white",width=10).grid(row=7, column=1,pady=5,sticky="w")

        def uploadSubnet():
            file = askopenfilename(initialdir=os.getcwd()+ './scRNAseq_models/', title="Select subnetwork genes",
                                   filetypes=[("TXT Files", "*.txt")])
            v1.set(os.path.basename(file))
            self.subnetGenes=getSubnetGenes(file)
        tk.Button(filterFrame, text="upload file", command=uploadSubnet).grid(row=7, column=2, sticky="w",pady=5,padx=5)
        tk.Label(filterFrame, text='Top edges number:').grid(row=6, column=0,pady=5,sticky="w",padx=5)
        ratio=tk.StringVar()
        threshold = tk.Entry(filterFrame,textvariable=ratio,width=8)
        threshold.grid(row=6, column=1,pady=5,sticky="w",padx=5)

        def grnGenerationFunc(expr, time, grn_inference, params, geneNamesDir,seq_norm): # cause need put GRN model into global variables
            if grn_inference == "":
                # 未选择方法，弹出警告
                tk.messagebox.showwarning(title='Warning', message='Unselected a GRN inference method!')

            if grn_inference == "SCODE":
                # parse params
                params_dic = {}
                tfnum = params[0].get()
                pnum = params[1].get()
                cnum = params[2].get()
                maxite = params[3].get()
                repeat=params[4].get()

                # call SCODE
                new_expr_path=expr
                if seq_norm==1: # norm expr
                    expr_data=np.loadtxt(expr,delimiter='\t')
                    new_expr=scipy.stats.zscore(expr_data,axis=1)
                    new_expr_path=os.path.dirname(expr)+'/norm_expr.txt'
                    np.savetxt(new_expr_path,new_expr,delimiter='\t')
                # callSCODE(new_expr_path, time, './Inferred_GRN/SCODE', tfnum, pnum, cnum, maxite)
                callSCODEAvg(new_expr_path, time, './Inferred_GRN', tfnum, pnum, cnum, maxite,repeat)
                # from edge and scores
                if not os.path.exists('./Inferred_GRN/' + 'meanA.txt'):
                    tk.messagebox.showerror(title='Error', message='SCODE calculation failed!')
                else:
                    formGRNTopology('./Inferred_GRN/' + 'meanA.txt', './Inferred_GRN/' + 'GRN-scores.txt', geneNamesDir)
                    tkinter.messagebox.showinfo(title='Info', message='GRN generation successfully!')
            # if grn_inference=="PoLoBag":
            #     n12 = float(params[4].get())
            #     n22 = float(params[5].get())
            #     nm = float(params[6].get())
            #     nb = int(params[7].get())
            #     alpha=float(params[8].get())
            #
            #     # call PoLoBag
            #     callPoLoBag(expr,'./Inferred_GRN/PoLoBag/'+'result_network.txt',n12,n22,nm,nb,alpha)

        tk.Button(grnInfWin,text="GRN generation",command=lambda: grnGenerationFunc(self.loadModelPaths['seq_expr'],self.loadModelPaths['seq_time'],GRNInfAlg.get(),[e1,e2,e3,e4,e5],self.loadModelPaths['seq_gnames'],seq_norm_var.get())).grid(row=3,columnspan=3,padx=10,pady=10)
        def grnFilterFunc(subnetGenes,inp_threshold):
            # filter genes and acquire scores for thresholds
            # scoresFilePath = ""
            # if grn_inference == "SCODE":
            scoresFilePath = './Inferred_GRN/' + 'GRN-scores.txt'
            # else:
            #     scoresFilePath = './Inferred_GRN/PoLoBag/' + 'result_network.txt'

            if not os.path.exists(scoresFilePath):
                tk.messagebox.showerror(title='Error', message='form GRN edge scores failed!')
            else:
                # subnetwork first
                edge_scores = np.loadtxt(scoresFilePath, delimiter='\t', dtype=str)
                weights=edge_scores[:,2].tolist()
                weights=[abs(float(i)) for i in weights]
                self.loadModelToplogy = pd.DataFrame(edge_scores, columns=['regulator', 'target', 'func'])
                # weights=(weights-np.min(weights))/(np.max(weights)-np.min(weights)) # min-max standard
                self.loadModelToplogy.insert(loc=len(self.loadModelToplogy.columns), column='weight', value=weights)
                # print("subnet genes:", subnetGenes)
                if subnetGenes != []:
                    ids = self.loadModelToplogy.loc[(self.loadModelToplogy['regulator'].isin(subnetGenes)) & (
                        self.loadModelToplogy['target'].isin(subnetGenes))].index
                    self.loadModelToplogy = self.loadModelToplogy.iloc[ids]

                # threshold then
                keep_num = inp_threshold
                self.loadModelToplogy = self.loadModelToplogy[:keep_num]
                for i in self.loadModelToplogy.index:
                    self.loadModelToplogy.loc[i,'func'] = '+' if float(self.loadModelToplogy.loc[i,'func']) >= 0 else '-'

                self.params['IM'], self.params['Sys_Dim'], self.params['Genes'] = grnChooser2graph(
                    self.loadModelToplogy)
                self.loadModelToplogy.to_csv(os.path.dirname(scoresFilePath) + '/GRN-topology.tsv', sep=',',
                                             index=False)
                tkinter.messagebox.showinfo(title='Info', message='GRN filtering successfully!')
                print("The inferred GRN topology has been generated at " + os.path.dirname(
                    scoresFilePath) + "'/GRN-topology.tsv'")

        tk.Button(grnInfWin,text="GRN filtering",command=lambda: grnFilterFunc(self.subnetGenes,int(ratio.get()))).grid(row=5,columnspan=3,padx=10,pady=10)


'''
TME APP START
'''
main_window=tk.Tk()
main_window.grid_rowconfigure(0, weight=1)
main_window.grid_columnconfigure(0, weight=1)
MainPage(main_window)
main_window.mainloop()
# cef.Shutdown()

'''
The GRN model refers to Delimited text format
'''