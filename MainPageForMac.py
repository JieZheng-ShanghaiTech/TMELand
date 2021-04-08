# encoding=utf-8

import tkinter as tk
import tkinter.messagebox
from tkinter.filedialog import askopenfilename
from AboutFrame import *
from HelpFrame import *
from LandFrame import *
from InitialFrame import *
from GRN_TME import *
from ODE_TME import *
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import networkx as nx
import matplotlib.pyplot as plt
from HelperFunctions import *
import tkinter.messagebox
import json
import os
from matplotlib.lines import Line2D
import platform
import base64

'''
Main Page
'''
class MainPage(object):
    def __init__(self,master):
        self.root=master
        self.root.title('TMELand - A software to plot Waddington\'s landscape and paths based on the TME method')
        self.screenW=self.root.winfo_screenwidth()
        self.screenH=self.root.winfo_screenheight()
        self.winW=1400
        self.winH=720
        self.root.geometry('%dx%d+%d+%d'%(self.winW, self.winH, (self.screenW-self.winW)/2, (self.screenH-self.winH)/2)) # 居中
        if platform.system()=='Windows':
            self.root.iconbitmap(default="./resource/icon.ico")
        else:
            icon = PhotoImage(file='./resource/icon.gif')
            self.root.tk.call('wm', 'iconphoto', self.root._w, icon)
        self.createMainPage()
        self.params={}
        self.loadModel=''
    def createMainPage(self):
        # create all frames corresponding to all menus
        self.initialPage = InitialFrame(self.root, w=1300, h=700)
        self.modelPage=tk.Frame(self.root, width=1300, height=700)
        self.odeModelPage = tk.Frame(self.modelPage, width=1300, height=700)
        self.landPage = LandFrame(self.root, w=1300, h=700)
        self.helpPage = HelpFrame(self.root, w=1300, h=700)
        self.aboutPage = AboutFrame(self.root, w=1300, h=700)
        self.grnModelPage = tk.Frame(self.modelPage, width=1300, height=700)
        self.grnPage = tk.Frame(self.grnModelPage, width=1300, height=700)
        self.dynamicsSettingPage = tk.Frame(self.grnModelPage, width=1300, height=700)

        # # main menu bar
        # main_menubar = tk.Menu(self.root)
        # # Model menu
        # model_menu = tk.Menu(main_menubar, tearoff=0)
        # main_menubar.add_cascade(label='Open', menu=model_menu)
        # model_menu.add_command(label='Open ODE/SBML', command=self.showODEModel)
        # model_menu.add_command(label='Open Text', command=self.grnChooser) # only for GRN
        # model_menu.add_command(label='Open TME', command=self.tmeChooser)  # for saved models
        # # others menus
        # main_menubar.add_command(label='Model', command=self.showModelRelated)
        # main_menubar.add_command(label='Landscape & Path', command=self.showLand)
        # main_menubar.add_command(label='Help', command=self.showHelp)
        # main_menubar.add_command(label='About', command=self.showAbout)

        # Comment line 56-68 and uncomment the following part for MAC OS:
        # main menu bar
        main_menubar = tk.Menu(self.root)
        # Model menu
        model_menu = tk.Menu(main_menubar, tearoff=0)
        main_menubar.add_cascade(label='Open', menu=model_menu)
        model_menu.add_command(label='Open ODE/SBML', command=self.showODEModel)
        model_menu.add_command(label='Open TSV', command=self.grnChooser) # only for GRN
        model_menu.add_command(label='Open TME', command=self.tmeChooser)  # for saved models
        # others menus
        mv_menu = tk.Menu(main_menubar, tearoff=0)
        main_menubar.add_cascade(label='Model', menu=mv_menu)
        mv_menu.add_command(label='Model', command=self.showModelRelated)
        land_menu = tk.Menu(main_menubar, tearoff=0)
        main_menubar.add_cascade(label='Landscape & Path', menu=land_menu)
        land_menu.add_command(label='Landscape & Path', command=self.showLand)
        help_menu = tk.Menu(main_menubar, tearoff=0)
        main_menubar.add_cascade(label='Help', menu=help_menu)
        help_menu.add_command(label='Help', command=self.showHelp)
        about_menu = tk.Menu(main_menubar, tearoff=0)
        main_menubar.add_cascade(label='About', menu=about_menu)
        about_menu.add_command(label='About', command=self.showAbout)


        self.root['menu']=main_menubar

        self.initialPage.grid(row=0,column=0,sticky="n")

    def showModelRelated(self):
        self.modelPage.grid(row=0,column=0,sticky="n")
        self.initialPage.grid_forget()
        self.landPage.grid_forget()
        self.helpPage.grid_forget()
        self.aboutPage.grid_forget()

    def showODEModel(self): # ode and sbml model
        file = askopenfilename(initialdir=os.getcwd()+'./ODE_SBML_models/', title="Select ODE/SBML model",filetypes=[("ODE Files", "*.ode"),("SBML Files", "*.xml")])
        if file=='':
            self.initialPage.grid(row=0, column=0, sticky="n")
            tkinter.messagebox.showwarning(title='Warning', message='Please load a model file!')
        else:
            self.root.title('TMELand - '+os.path.basename(file))
            self.showModelRelated()
            self.grnModelPage.grid_forget()
            self.odeModelPage.grid(row=0, column=0, sticky="n")
            self.loadModel = 'ODE'
            self.landPage = LandFrame(self.root, w=1300, h=700)
            self.landPage.loadModel = self.loadModel
            self.landPage.fig.clear()
            self.landPage.fig.add_subplot(111, projection='3d')
            self.landPage.fig.canvas.draw_idle()
            self.landPage.Global_sp = np.array([])
            print('The loaded file is: ', file)
            assert '.xml' in file or '.ode' in file, 'Please check the loaded file for ODE model.'
            if ('.xml' not in file) and ('.ode' not in file):
                tkinter.messagebox.showerror(title='Error', message='Wrong loaded file!')
            try:
                # get grn figure by ODE functions
                if '.xml' in file:
                    odeShow, odeFunc, jacCode, odeParams = parseSBML(file)
                elif '.ode' in file:
                    odeShow, odeFunc, jacCode, odeParams = parseODE(file)
                self.landPage.odeCode = odeFunc
                self.landPage.jacCode = jacCode
                # store parameters for Landscape Page
                self.landPage.default_params['Sys_Dim'] = len(odeParams['genes'])
                self.landPage.default_params['Genes'] = odeParams['genes']
                self.landPage.l1['value'] = (odeParams['genes'])
                self.landPage.l2['value'] = (odeParams['genes'])
            except:
                print('No file be loaded or error.')
            # define ODE frame
            tk.Label(self.odeModelPage, text='Equations of the loaded ODE model', font=("Verdana", 12, "bold"),
                     pady=10).grid(row=0, column=0, pady=10, columnspan=3)
            odeShowFrame = tk.Frame(self.odeModelPage, bg='white', borderwidth=1)
            odeTxt = tk.Text(odeShowFrame, wrap=tk.NONE, font="Verdana 10", width=120, height=30, borderwidth=2)
            verScroll = tk.Scrollbar(odeShowFrame, orient='vertical', command=odeTxt.yview)
            horScroll = tk.Scrollbar(odeShowFrame, orient='horizontal', command=odeTxt.xview)
            odeTxt.config(yscrollcommand=verScroll.set, xscrollcommand=horScroll.set)
            odeTxt.grid(row=0, column=0, sticky="nsew")
            verScroll.grid(row=0, column=1, sticky="ns")
            horScroll.grid(row=1, column=0, sticky="ew")
            odeShowFrame.grid_rowconfigure(0, weight=1)
            odeShowFrame.grid_columnconfigure(0, weight=1)
            odeTxt.insert(tk.INSERT, odeShow)
            odeTxt.config(font="Verdana 10")
            odeShowFrame.grid(row=1, column=0, columnspan=3)


    def tmeChooser(self):
        file = askopenfilename(initialdir=os.getcwd()+'./TME_models/', title="Select TME model",filetypes=[("Json Files", "*.json")])
        if file=='':
            self.initialPage.grid(row=0, column=0, sticky="n")
            tkinter.messagebox.showwarning(title='Warning', message='Please load a model file!')
        else:
            self.root.title('TMELand - ' + os.path.basename(file))
            print('The loaded file is: ', file)
            assert '.json' in file, 'Please load the json format file for tme model.'
            if '.json' not in file:
                tkinter.messagebox.showerror(title='Error', message='Wrong loaded file!')
            # try:
            with open(file, 'r') as fr:
                data = json.load(fr)
            # self.initialPage.grid_forget()
            # self.modelPage.grid_forget()
            self.landPage.grid(row=0, column=0, sticky="n")
            # self.helpPage.grid_forget()
            # self.aboutPage.grid_forget()
            # left part
            self.landPage.loadModel=data['modelType']+'TME'
            self.landPage.default_params=data['defaultParams']
            self.landPage.Global_sp=np.array(data['stablePoints'])
            self.landPage.Global_sig=np.array(data['sigma'])
            self.landPage.Global_w=np.array(data['weight'])
            self.landPage.odeCode=data['odeCode']
            if 'allpath' in data.keys():
                self.landPage.savepath=data['allpath']

            self.landPage.e1.delete(0, END)
            self.landPage.e2.delete(0, END)
            self.landPage.e3.delete(0, END)
            self.landPage.e8.delete(0, END)
            self.landPage.e4.delete(0, END)
            self.landPage.e5.delete(0, END)
            self.landPage.e6.delete(0, END)
            self.landPage.e7.delete(0, END)
            self.landPage.l1.delete(0, END)
            self.landPage.l2.delete(0, END)
            self.landPage.e1.insert(0, data['defaultParams']['cycle'])
            self.landPage.e2.insert(0, data['defaultParams']['xmax'])
            self.landPage.e3.insert(0, data['defaultParams']['Tfinal'])
            self.landPage.e8.insert(0, data['defaultParams']['Diffusion'])
            self.landPage.e4.insert(0, data['defaultParams']['y_min'][0])
            self.landPage.e5.insert(0, data['defaultParams']['y_max'][0])
            self.landPage.e6.insert(0, data['defaultParams']['y_min'][1])
            self.landPage.e7.insert(0, data['defaultParams']['y_max'][1])
            self.landPage.l1['value'] = (data['defaultParams']['Genes'])
            self.landPage.l2['value'] = (data['defaultParams']['Genes'])
            self.landPage.l1.insert(0, data['defaultParams']['Genes'][data['defaultParams']['vari_spec'][0]])
            self.landPage.l2.insert(0, data['defaultParams']['Genes'][data['defaultParams']['vari_spec'][1]])
            # right part
            if 'allpath' in data.keys():
                # draw landscape and path
                self.landPage.fig.clear()
                self.landPage.axes1 = self.landPage.fig.add_subplot(111, projection='3d')

                if data['modelType'][:3] == 'GRN':
                    self.landPage.xAxis, self.landPage.yAxis, self.landPage.P, _ = grn_tme_draw_landscape(
                        data['defaultParams'], np.array(data['stablePoints']), np.array(data['sigma']),
                        np.array(data['weight']))
                elif data['modelType'][:3] == 'ODE':
                    self.landPage.xAxis, self.landPage.yAxis, self.landPage.P, _ = ode_tme_draw_landscape(
                        data['defaultParams'], np.array(data['stablePoints']), np.array(data['sigma']),
                        np.array(data['weight']))

                tmp = self.landPage.axes1.plot_surface(np.array(self.landPage.xAxis), np.array(self.landPage.yAxis),
                                                       np.array(self.landPage.P), cmap='jet', zorder=1)
                self.landPage.axes1.set_xlabel(data['defaultParams']['Genes'][data['defaultParams']['vari_spec'][0]])
                self.landPage.axes1.set_ylabel(data['defaultParams']['Genes'][data['defaultParams']['vari_spec'][1]])
                self.landPage.axes1.set_zlabel('U')

                steadyMarkers = []
                for i in np.array(data['defaultParams']['stablePoints']):
                    steadyMarkers.append(i[data['defaultParams']['vari_spec']].tolist())
                for i in range(len(steadyMarkers)):
                    self.landPage.axes1.text(x=steadyMarkers[i][0], y=steadyMarkers[i][1], z=0, s=str(i + 1), c='red',
                                             size=12)

                self.landPage.fig.colorbar(tmp)
                self.landPage.canvas.draw()
                # draw all paths
                color_cnt = 0
                for i in data['allpath'].keys():
                    color_cnt += 1
                    pathi = np.array(data['allpath'][i])  # ith path
                    pathx = pathi[data['defaultParams']['vari_spec'][0]]
                    pathy = pathi[data['defaultParams']['vari_spec'][1]]
                    pathz = np.zeros_like(pathx)
                    num = pathx.shape[0]
                    for i in range(num):
                        # x grid
                        for xx in range(100):
                            if xx == 99:
                                idx = 99
                            else:
                                if pathx[i] >= self.landPage.xAxis[0][xx] and pathx[i] <= self.landPage.xAxis[0][xx + 1]:
                                    idx = xx
                                    break
                        # y grid
                        for yy in range(100):
                            if yy == 99:
                                idy = 99
                            else:
                                if pathy[i] >= self.landPage.yAxis[yy][0] and pathy[i] <= self.landPage.yAxis[yy + 1][0]:
                                    idy = yy
                                    break
                        # get P
                        pathz[i] = np.array(self.landPage.P)[idy, idx]
                    if color_cnt % 2 == 0:
                        color_list = ['cyan']
                    else:
                        color_list = ['yellow']
                    # random_color_index=random.randint(0,1)
                    random_color_index = 0
                    self.landPage.axes1.plot(pathx, pathy, pathz, c=color_list[random_color_index],
                                             zorder=3)  # z+2 to display it on the surface
                    arrow_pos = int(len(pathx) / 3)
                    self.landPage.axes1.plot(pathx[arrow_pos:arrow_pos + 1], pathy[arrow_pos:arrow_pos + 1],
                                             pathz[arrow_pos:arrow_pos + 1], c=color_list[random_color_index],
                                             marker='>', zorder=3)
                    self.landPage.canvas.draw()
            else:
                # only draw landscape
                if data['modelType'][:3] == 'GRN':
                    self.landPage.xAxis, self.landPage.yAxis, self.landPage.P, _ = grn_tme_draw_landscape(
                        data['defaultParams'], np.array(data['stablePoints']), np.array(data['sigma']), np.array(data['weight']))
                elif data['modelType'][:3] == 'ODE':
                    self.landPage.xAxis, self.landPage.yAxis, self.landPage.P, _ = ode_tme_draw_landscape(
                        data['defaultParams'], np.array(data['stablePoints']), np.array(data['sigma']),
                        np.array(data['weight']))

                self.landPage.fig.clear()
                self.landPage.axes1 = self.landPage.fig.add_subplot(111, projection='3d')
                tmp = self.landPage.axes1.plot_surface(np.array(self.landPage.xAxis), np.array(self.landPage.yAxis),
                                                       np.array(self.landPage.P), cmap='jet', zorder=1)
                self.landPage.axes1.set_xlabel(data['defaultParams']['Genes'][data['defaultParams']['vari_spec'][0]])
                self.landPage.axes1.set_ylabel(data['defaultParams']['Genes'][data['defaultParams']['vari_spec'][1]])
                self.landPage.axes1.set_zlabel('U')

                steadyMarkers = []
                for i in np.array(data['defaultParams']['stablePoints']):
                    steadyMarkers.append(i[data['defaultParams']['vari_spec']].tolist())
                for i in range(len(steadyMarkers)):
                    self.landPage.axes1.text(x=steadyMarkers[i][0], y=steadyMarkers[i][1], z=0, s=str(i + 1), c='red',
                                             size=12)

                self.landPage.fig.colorbar(tmp)
                self.landPage.canvas.draw()


    # load model and default parameters: file chooser
    def grnChooser(self): # IM Hill_fn TM Act_Inh Degrade_rate y_max y_min vari_spec
        file = askopenfilename(initialdir=os.getcwd()+'./TSV_models/', title="Select Text model",filetypes=[("Text Files", "*.tsv")])
        if file=='':
            self.initialPage.grid(row=0, column=0, sticky="n")
            tkinter.messagebox.showwarning(title='Warning', message='Please load a model file!')
        else:
            self.root.title('TMELand - ' + os.path.basename(file))
            self.showGRNModel()
            self.loadModel='GRN'
            self.landPage = LandFrame(self.root, w=1300, h=700)
            self.landPage.loadModel = self.loadModel
            self.landPage.fig.clear()
            self.landPage.fig.add_subplot(111,projection='3d')
            self.landPage.fig.canvas.draw_idle()
            self.landPage.Global_sp=np.array([])
            print('The loaded file is: ',file)
            assert '.tsv' in file, 'Please load the tsv format file for Text model.'
            if '.tsv' not in file:
                tkinter.messagebox.showerror(title='Error', message='Wrong loaded file!')
            params={}
            # try:
            with open(file, 'r') as fread:
                # grn file -> IM matrix
                cont = fread.readlines()
                contLines = []
                genes = []
                G = nx.MultiDiGraph()
                pEdges = []
                nEdges = []
                for line in cont:
                    tmp = line.strip().split('\t')
                    genes.append(tmp[0])
                    genes.append(tmp[1])
                    contLines.append(tmp)
                genes = np.unique(genes).tolist()
                print('The number of gene is: ',len(genes))
                selfActGenes = set()
                selfInhGenes = set()
                G.add_nodes_from(genes)
                IM = np.zeros((len(genes), len(genes)))
                for edge in contLines:
                    row = genes.index(edge[0])
                    col = genes.index(edge[1])
                    if edge[2] == '+':
                        IM[row, col] = 1
                        pEdges.append((edge[0], edge[1]))
                        if row == col:
                            selfActGenes.add(edge[0])
                    elif edge[2] == '-':
                        IM[row, col] = -1
                        nEdges.append((edge[0], edge[1]))
                        if row == col:
                            selfInhGenes.add(edge[0])
                    else:
                        print('Unsupported regulatory relationship.')
                if IM.any()==0:
                    tkinter.messagebox.showwarning(title='Warning', message='The system contains 0 reaction!')
                selfActGenes = list(selfActGenes)
                selfInhGenes = list(selfInhGenes)
                # show grn by network visualization
                G.add_edges_from(pEdges)
                G.add_edges_from(nEdges)
                pos = nx.spring_layout(G,k=1,iterations=5)
                grnFig = plt.Figure(figsize=(12,6), dpi=100)
                grnAx = grnFig.add_subplot(111)
                nx.draw_networkx_nodes(G, pos, node_color='lightblue',ax=grnAx, label='no self-regulation', node_size=400)  # initial colors for all nodes
                nx.draw_networkx_nodes(G, pos, nodelist=selfActGenes,
                                       node_color='red',ax=grnAx, label='self-activation', node_size=400)  # self-active nodes with red colors
                nx.draw_networkx_nodes(G, pos, nodelist=selfInhGenes,
                                       node_color='black',ax=grnAx, label='self-inhibition', node_size=400)  # self-inhibited nodes with black colors
                nx.draw_networkx_labels(G, pos,ax=grnAx,font_size=14)
                nx.draw_networkx_edges(G, pos, edgelist=pEdges, edge_color='red', connectionstyle='arc3,rad=0.2',
                                       arrowsize=18,ax=grnAx, label='activation')
                nx.draw_networkx_edges(G, pos, edgelist=nEdges, edge_color='black', arrows=True,
                                       connectionstyle='arc3,rad=0.2', arrowsize=12,ax=grnAx,arrowstyle='-[', label='inhibition')

                def legend_entity(clr, shape, **kwargs):
                    if shape=='node':
                        return Line2D(range(1), range(1), color='white', marker='o', markerfacecolor=clr,**kwargs)
                    else: # 'edge'
                        return Line2D([0, 1], [0, 1], color=clr, **kwargs)
                # grnAx.legend(loc='upper right', fontsize='medium')
                grnAx.legend([legend_entity('black', 'node', markersize=13), legend_entity('red', 'node', markersize=13), legend_entity('lightblue', 'node', markersize=13), legend_entity('black','edge',lw=1), legend_entity('red','edge',lw=1)],['self-inhibition', 'self-activation', 'no self-regulation','inhibition','activation'], loc='upper right',fontsize='large')

                # show GRN frame
                tk.Label(self.grnPage, text='Visualization of the loaded model',font=("Verdana", 12, "bold")).grid(row=0, sticky='n',pady=10)
                GRN = FigureCanvasTkAgg(grnFig, self.grnPage)
                GRN.get_tk_widget().grid(row=1,sticky='ns')

                toolbar_frame=tk.Frame(self.grnPage)
                toolbar=NavigationToolbar2Tk(GRN,toolbar_frame)
                toolbar.update()
                toolbar_frame.grid(row=1,sticky='ws')
                # GRN._tkcanvas.grid()
                tk.Button(self.grnPage, text='Dynamics setting', command=self.showDynamicSetting).grid(row=2,sticky='s',pady=10)

            self.landPage.default_params['IM']=IM
            self.landPage.default_params['Sys_Dim'] = len(genes)
            self.landPage.default_params['Genes'] = genes
            self.landPage.l1['value']=(genes)
            self.landPage.l2['value']=(genes)
            # except:
            #     print('No file be loaded or error.')

    def showGRNModel(self):
        self.showModelRelated()
        self.grnModelPage.grid(row=0, column=0, sticky="n")
        self.grnPage.grid(row=0, column=0, sticky="n")
        self.dynamicsSettingPage.grid_forget()
        self.odeModelPage.grid_forget()

    def showDynamicSetting(self):
        equation = tk.StringVar()
        self.grnPage.grid_forget()
        self.dynamicsSettingPage.grid(row=0,column=0,sticky="n")
        def backToGRN():
            self.dynamicsSettingPage.grid_forget()
            self.grnPage.grid(row=0, column=0, sticky="n")
        tk.Button(self.dynamicsSettingPage, text='Show GRN', command=backToGRN).grid(row=0,columnspan=2,pady=10)
        tk.Label(self.dynamicsSettingPage, text='Dynamics (ODE) related parameters setting',font=("Verdana", 12, "bold")).grid(row=1,columnspan=2,pady=20)
        tk.Label(self.dynamicsSettingPage, text='Hill coefficient:').grid(row=2,column=0, pady=10, sticky='e',padx=20)
        e1=tk.Entry(self.dynamicsSettingPage, textvariable=tk.StringVar)
        e1.insert(0,'4')
        e1.grid(row=2, column=1, pady=10, sticky='w',padx=20)
        tk.Label(self.dynamicsSettingPage, text='Threshold:').grid(row=3, column=0, pady=10, sticky='e',padx=20)
        e2=tk.Entry(self.dynamicsSettingPage, textvariable=tk.StringVar)
        e2.insert(0, '0.7')
        e2.grid(row=3, column=1, pady=10, sticky='w',padx=20)
        tk.Label(self.dynamicsSettingPage, text='Activation:').grid(row=4, column=0, pady=10, sticky='e',padx=20)
        e3=tk.Entry(self.dynamicsSettingPage, textvariable=tk.StringVar)
        e3.insert(0, '1')
        e3.grid(row=4, column=1, pady=10, sticky='w',padx=20)
        tk.Label(self.dynamicsSettingPage, text='Inhibition:').grid(row=5, column=0, pady=10, sticky='e',padx=20)
        e4=tk.Entry(self.dynamicsSettingPage, textvariable=tk.StringVar)
        e4.insert(0, '0.5')
        e4.grid(row=5, column=1, pady=10, sticky='w',padx=20)
        tk.Label(self.dynamicsSettingPage, text='Degradation:').grid(row=6, column=0, pady=10, sticky='e',padx=20)
        e5=tk.Entry(self.dynamicsSettingPage, textvariable=tk.StringVar)
        e5.insert(0, '1')
        e5.grid(row=6, column=1, pady=10, sticky='w',padx=20)
        # tk.Label(self.dynamicsSettingPage, text='Diffusion:').grid(row=7, column=0, pady=10, sticky='e',padx=20)
        # e6=tk.Entry(self.dynamicsSettingPage, textvariable=tk.StringVar)
        # e6.insert(0, '0.005')
        # e6.grid(row=7, column=1, pady=10, sticky='w',padx=20)
        def autoODEGen():
            hill=int(e1.get()) # 2,3,4
            threshold=float(e2.get()) # 0-4
            act=float(e3.get()) # 0-4
            inh=float(e4.get()) # 0-4
            degrade=int(e5.get()) # 1
            # diffusion=float(e6.get())
            # store in parameters for TME method
            dim=self.landPage.default_params['Sys_Dim']
            self.landPage.default_params['Hill_fn']=abs(self.landPage.default_params['IM'])*hill
            self.landPage.default_params['TM'] = abs(self.landPage.default_params['IM']) * threshold
            actInh=np.zeros((dim, dim))
            for i in range(dim):
                for j in range(dim):
                    if self.landPage.default_params['IM'][i][j]==1:
                        actInh[i][j]=act
                    elif self.landPage.default_params['IM'][i][j]==-1:
                        actInh[i][j] = inh
                    else:
                        actInh[i][j] = 0
            self.landPage.default_params['Act_Inh']=actInh
            self.landPage.default_params['Degrade_rate'] = np.array([degrade]*dim)
            # self.landPage.default_params['Diffusion'] = diffusion
            # print(self.landPage.default_params)
            # Automatically ODE generation
            # equation.set('dx/dt=sum_x(act*x^hill/(x^hill+thresh^hill) or inh*thresh^hill/(x^hill+thresh^hill)) - degrade*x')
            tkinter.messagebox.showinfo(title='Info', message='Corresponding ODEs have been generated successfully!')
        tk.Button(self.dynamicsSettingPage, text='ODE generation', command=autoODEGen).grid(row=8, columnspan=2,pady=40)
        # tk.Label(self.dynamicsSettingPage, textvariable=equation, bg='white', fg='black', width=100, height=4).grid(row=9,columnspan=2, pady=100)

    def showLand(self):
        self.initialPage.grid_forget()
        self.modelPage.grid_forget()
        self.landPage.grid(row=0,column=0,sticky="n")
        self.helpPage.grid_forget()
        self.aboutPage.grid_forget()

    def showHelp(self):
        self.initialPage.grid_forget()
        self.modelPage.grid_forget()
        self.landPage.grid_forget()
        self.helpPage.grid(row=0,column=0,sticky="n")
        self.aboutPage.grid_forget()

    def showAbout(self):
        self.initialPage.grid_forget()
        self.modelPage.grid_forget()
        self.landPage.grid_forget()
        self.helpPage.grid_forget()
        self.aboutPage.grid(row=0,column=0,sticky="n")


'''
TME APP START
'''
main_window=tk.Tk()
main_window.grid_rowconfigure(0, weight=1)
main_window.grid_columnconfigure(0, weight=1)
MainPage(main_window)
main_window.mainloop()

'''
The GRN model refers to Delimited text format
'''