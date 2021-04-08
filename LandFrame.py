import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
import matplotlib.pyplot as plt
from GRN_TME import *
from ODE_TME import *
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.messagebox
from tkinter.filedialog import *
import pickle
from matplotlib import cm
import random
import numpy as np
import os
import json
from HelperFunctions import changeNparray2List
import time
# import resource

class LandFrame(tk.Frame):
    def __init__(self,master,w,h):
        tk.Frame.__init__(self,master,width=w,height=h)
        self.root=master
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.leftFrame=tk.Frame(self,width=650,height=700,highlightbackground='black',
                                     highlightcolor='black', highlightthickness=1)
        self.rightFrame=tk.Frame(self,width=650,height=700)
        self.moreAttInfoFrameL=tk.Frame(self,width=650,height=700)
        self.moreAttInfoFrameR = tk.Frame(self, width=650, height=700)
        self.default_params={}
        self.e1 = tk.Entry(self.leftFrame, textvariable=tk.StringVar())
        self.e2 = tk.Entry(self.leftFrame, textvariable=tk.StringVar())
        self.e3 = tk.Entry(self.leftFrame, textvariable=tk.StringVar())
        self.e8 = tk.Entry(self.leftFrame, textvariable=tk.StringVar()) # for diffusion
        self.e4 = tk.Entry(self.leftFrame, textvariable=tk.StringVar(), width=8)
        self.e5 = tk.Entry(self.leftFrame, textvariable=tk.StringVar(), width=8)
        self.e6 = tk.Entry(self.leftFrame, textvariable=tk.StringVar(), width=8)
        self.e7 = tk.Entry(self.leftFrame, textvariable=tk.StringVar(), width=8)
        self.l1 = ttk.Combobox(self.leftFrame)
        self.l2 = ttk.Combobox(self.leftFrame)
        self.odeCode=''
        self.jacCode=''
        self.loadModel=''
        self.fig=Figure()
        self.axes1= None
        self.axes2 = None
        self.canvas = FigureCanvasTkAgg(self.fig, self.rightFrame)
        self.xAxis=np.zeros((100,100)) # landscape x y z axis
        self.yAxis=np.zeros((100,100))
        self.P=np.zeros((100,100))
        self.createLandPage()
        self.Global_sp=np.array([]) # denote weather have generated landscape and save steady info
        self.Global_sig=np.array([])
        self.Global_w=np.array([])
        self.savepath={} # save all path, key is from attractor - to attractor
        self.pathsAction={}
        self.drawPathCnt=0 # control path color

    def createLandPage(self):
        # nSeries=
        # geneMax =
        # time=
        # lowerBoundary=
        # upperBoundary=

        # left
        self.leftFrame.grid(row=0, column=0, padx=20, pady=60, ipadx=2, sticky='ns')
        self.rightFrame.grid(row=0, column=1, padx=20, pady=60, sticky='ns')
        # left frame setting
        tk.Label(self.leftFrame, text='Parameters Setting', font=("Helvetica", 10)).grid(row=0, sticky='we',columnspan=3)
        tk.Label(self.leftFrame, text='Number of series:').grid(row=1, sticky='W', pady=10)

        self.e1.insert(0, 500)
        self.e1.grid(row=1, column=1, sticky='E', columnspan=2)
        tk.Label(self.leftFrame, text='Gene max value:').grid(row=2, sticky='W', pady=10)

        self.e2.insert(0, 1)
        self.e2.grid(row=2, column=1, sticky='E', columnspan=2)
        tk.Label(self.leftFrame, text='Time:').grid(row=3, sticky='W', pady=10)

        self.e3.insert(0, 1000)
        self.e3.grid(row=3, column=1, sticky='E', columnspan=2)

        tk.Label(self.leftFrame, text='Diffusion:').grid(row=4, sticky='W', pady=10)
        self.e8.insert(0, 0.005)
        self.e8.grid(row=4, column=1, sticky='E', columnspan=2)

        tk.Label(self.leftFrame, text='Min:').grid(row=6, column=1, sticky='w',padx=10)

        self.e4.insert(0, 0)
        self.e4.grid(row=7, column=1, sticky='w',padx=10)
        tk.Label(self.leftFrame, text='Max:').grid(row=6, column=2, sticky='w')

        self.e5.insert(0, 3)
        self.e5.grid(row=7, column=2, sticky='w') # marker1 bound: e4; e5

        self.e6.insert(0, 0)
        self.e6.grid(row=8, column=1, sticky='w', pady=5,padx=10)
        self.e7.insert(0, 3)
        self.e7.grid(row=8, column=2, sticky='w', pady=5) # marker2 bound: e6; e7

        tk.Label(self.leftFrame, text='Visualization markers:').grid(row=6, sticky='W')
        self.l1.grid(row=7, column=0, sticky='w', padx=5)
        self.l2.grid(row=8, column=0, sticky='w', padx=5, pady=5)
        def updateByMarkers():
            marker1 = self.l1.get()
            marker2 = self.l2.get()
            marker1_lb = float(self.e4.get())
            marker1_ub = float(self.e5.get())
            marker2_lb = float(self.e6.get())
            marker2_ub = float(self.e7.get())

            genes = self.default_params['Genes']
            self.default_params['vari_spec'] = np.array([genes.index(marker1), genes.index(marker2)])
            self.default_params['y_min'] = np.array([marker1_lb,marker2_lb])
            self.default_params['y_max'] = np.array([marker1_ub,marker2_ub])
            if self.loadModel[:3] == 'GRN':
                self.xAxis, self.yAxis, self.P, self.default_params['stablePoints'] = grn_tme_draw_landscape(
                self.default_params, self.Global_sp, self.Global_sig, self.Global_w)
            elif self.loadModel[:3] == 'ODE':
                self.xAxis, self.yAxis, self.P, self.default_params['stablePoints'] = ode_tme_draw_landscape(
                    self.default_params, self.Global_sp, self.Global_sig, self.Global_w)
            self.fig.clear()
            self.axes1 = self.fig.add_subplot(111, projection='3d')
            # print('update P: ',self.P)
            tmp=self.axes1.plot_surface(self.xAxis, self.yAxis, self.P, cmap='jet',zorder=1)
            self.axes1.set_xlabel(genes[self.default_params['vari_spec'][0]])
            self.axes1.set_ylabel(genes[self.default_params['vari_spec'][1]])
            self.axes1.set_zlabel('U')

            steadyMarkers = []
            for i in np.array(self.default_params['stablePoints']):
                steadyMarkers.append(i[np.array(self.default_params['vari_spec'])].tolist())
            for i in range(len(steadyMarkers)):
                self.axes1.text(x=steadyMarkers[i][0], y=steadyMarkers[i][1], z=0, s=str(i + 1), c='red', size=12)

            self.fig.colorbar(tmp)
            self.canvas.draw()

            # add paths when landscape is be updated if there are paths (only for same markers)
            if self.savepath!={}:
                color_cnt = 0
                for i in self.savepath.keys():
                    color_cnt += 1
                    pathi = np.array(self.savepath[i])  # ith path
                    pathx = pathi[self.default_params['vari_spec'][0]]
                    pathy = pathi[self.default_params['vari_spec'][1]]
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
                    self.axes1.plot(pathx, pathy, pathz, c=color_list[random_color_index],
                                             zorder=3)  # z+2 to display it on the surface
                    arrow_pos = int(len(pathx) / 3)
                    self.axes1.plot(pathx[arrow_pos:arrow_pos + 1], pathy[arrow_pos:arrow_pos + 1],
                                             pathz[arrow_pos:arrow_pos + 1], c=color_list[random_color_index],
                                             marker='>', zorder=3)
                    self.canvas.draw()

        tk.Button(self.leftFrame, text='Update', command=updateByMarkers).grid(row=10, sticky='w', pady=50, padx=50,
                                                                           columnspan=3)
        def saveLand():
            f = asksaveasfile(initialdir=os.getcwd()+'./TME_models/',mode='w', defaultextension=".json")
            if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
                f.close()
            else:
                f.close()
                fname = f.name # path+name; os.path.basename(f.name) only name
                data = {}
                data['modelType'] = self.loadModel
                data['stablePoints'] = self.Global_sp.tolist()
                data['sigma'] =self.Global_sig.tolist()
                data['weight'] =self.Global_w.tolist()
                data['defaultParams'] = changeNparray2List(self.default_params)
                data['odeCode']=self.odeCode
                with open(fname, 'w') as outfile:
                    json.dump(data, outfile)
                tkinter.messagebox.showinfo(title='Info', message='Save successfully!')
        tk.Button(self.leftFrame, text='Save landscape', command=saveLand).grid(row=10, sticky='e', pady=50, padx=50,
                                                                               columnspan=3)

        # right
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, self.rightFrame)
        toolbar.update()
        toolbar.pack(side=tk.TOP, pady=2, padx=5, ipadx=5)
        self.canvas._tkcanvas.pack(pady=2, padx=10, ipadx=5, side=tk.TOP, fill=tk.BOTH, expand=True)

        tk.Button(self.rightFrame, text='Draw path', command=self.drawPath).pack(side=LEFT, padx=130, pady=5)
        def savePath():
            f = asksaveasfile(initialdir=os.getcwd()+'./TME_models/',mode='w', defaultextension=".json")
            if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
                f.close()
            else:
                f.close()
                fname = f.name # path+name; os.path.basename(f.name) only name
                data = {}
                data['modelType'] = self.loadModel
                data['stablePoints'] = self.Global_sp.tolist()
                data['sigma'] = self.Global_sig.tolist()
                data['weight'] = self.Global_w.tolist()

                data['allpath'] = self.savepath
                data['pathAction']=self.pathsAction
                data['defaultParams'] = changeNparray2List(self.default_params)
                data['odeCode'] = self.odeCode
                with open(fname, 'w') as outfile:
                    json.dump(data, outfile)
                tkinter.messagebox.showinfo(title='Info', message='Save successfully!')
        tk.Button(self.rightFrame, text='Save path', command=savePath).pack(side=RIGHT, padx=130, pady=5)

        def drawLandscape():
            import time
            tstart = time.time()
            if self.loadModel[-3:]=='TME':
                tkinter.messagebox.showerror(title='Error', message='Not support recompute landscape for TME model!')

            else:
                self.savepath = {}
                print(self.loadModel)
                nSeries = int(self.e1.get())
                geneMax = int(self.e2.get())
                time = int(self.e3.get())
                diffusion = float(self.e8.get())
                # m1lb = float(self.e4.get())
                # m1ub = float(self.e5.get())
                # m2lb = float(self.e6.get())
                # m2ub = float(self.e7.get())
                marker1 = self.l1.get()
                # marker2 = self.l2.get()

                # store in parameters
                self.default_params['cycle'] = nSeries
                self.default_params['xmax'] = geneMax
                self.default_params['Tfinal'] = time
                self.default_params['Diffusion'] = diffusion
                genes = self.default_params['Genes']
                if marker1 == '':  # for resimulation. If no input, use default, else, use last input by user
                    self.default_params['y_min'] = np.array([0, 0])  # by default
                    self.default_params['y_max'] = np.array([3, 3])
                    self.default_params['vari_spec'] = np.array([0, 1])  # by default, only using above parameters

                # draw landscape
                # tk.Label(self.rightFrame, image=img).grid(row=0, column=0, sticky='wens')
                if self.loadModel == 'ODE':
                    self.Global_sp, self.Global_sig, self.Global_w = ode_find_stable(self.default_params, self.odeCode,
                                                                                     self.jacCode)
                    if len(self.Global_sp)==0:
                        tk.messagebox.showwarning(title='Warning', message='No steady points!')
                    self.xAxis, self.yAxis, self.P, self.default_params['stablePoints'] = ode_tme_draw_landscape(
                        self.default_params, self.Global_sp, self.Global_sig, self.Global_w)
                elif self.loadModel == 'GRN':
                    self.Global_sp, self.Global_sig, self.Global_w = grn_find_stable(self.default_params)
                    if len(self.Global_sp)==0:
                        tk.messagebox.showwarning(title='Warning', message='No steady points!')
                    self.xAxis, self.yAxis, self.P, self.default_params['stablePoints'] = grn_tme_draw_landscape(
                        self.default_params, self.Global_sp, self.Global_sig, self.Global_w)

                self.fig.clear()
                self.axes1 = self.fig.add_subplot(111, projection='3d')
                # print('initial P: ',self.P)
                tmp = self.axes1.plot_surface(self.xAxis, self.yAxis, self.P, cmap='jet', zorder=1)
                self.axes1.set_xlabel(genes[self.default_params['vari_spec'][0]])
                self.axes1.set_ylabel(genes[self.default_params['vari_spec'][1]])
                self.axes1.set_zlabel('U')

                # mark stable points
                steadyMarkers = []
                for i in self.default_params['stablePoints']:
                    steadyMarkers.append(i[self.default_params['vari_spec']].tolist())
                for i in range(len(steadyMarkers)):
                    self.axes1.text(x=steadyMarkers[i][0], y=steadyMarkers[i][1], z=0, s=str(i + 1), c='red', size=12)

                self.fig.colorbar(tmp)
                self.canvas.draw()
            import time
            tend = time.time()
            print('The consuming time of a landscape is: '+str(tend-tstart)+' s')
            # mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0
            # print('The max consuming memory of a landscape is: '+str(mem)+' MB')


        tk.Button(self.leftFrame, text='Draw', command=drawLandscape).grid(row=5, sticky='we', pady=50, padx=120, columnspan=3)

    def drawPath(self):
        attractorNum=np.array(self.default_params['stablePoints']).shape[0]
        if attractorNum==0:
            tk.messagebox.showwarning(title='Warning', message='No attractor!')
        elif attractorNum==1:
            tk.messagebox.showwarning(title='Warning', message='Only one attractor, no path!')
        else:
            # 弹出窗口参数设置
            settingWin=tk.Toplevel(self)
            ww=380
            hh=230
            sw=settingWin.winfo_screenwidth()
            sh=settingWin.winfo_screenheight()
            settingWin.geometry('%dx%d+%d+%d'%(ww, hh, (sw-ww)/2, (sh-hh)/2))
            settingWin.title('Drawing path setting')
            tmax = tk.StringVar()
            pointInPath = tk.StringVar()
            tk.Label(settingWin, text='Time range:').grid(row=1, column=0, sticky='W', pady=10)
            e1 = tk.Entry(settingWin, textvariable=tmax)
            e1.insert(0, 5)
            e1.grid(row=1, column=1, sticky='E')
            tk.Label(settingWin, text='Points number:').grid(row=2, column=0, sticky='W', pady=10)
            e2 = tk.Entry(settingWin, textvariable=pointInPath)
            e2.insert(0, 20)
            e2.grid(row=2, column=1, sticky='E')
            tk.Label(settingWin, text='Beginning attractor:').grid(row=6, column=0, sticky='W', pady=10)
            tk.Label(settingWin, text='Ending attractor:').grid(row=7, column=0, sticky='W', pady=10)
            l1 = ttk.Combobox(settingWin)
            l2 = ttk.Combobox(settingWin)
            attlist=[]
            for i in range(1,attractorNum+1):
                attlist.append(i) # 为attractor编号，1...
            l1['value'] = (attlist)
            l2['value'] = (attlist)
            l1.grid(row=6, column=1, sticky='E')
            l2.grid(row=7, column=1, sticky='E')
            # draw path between specific attractors on the landscape
            def backendDrawPath():
                tstart=time.time()
                self.drawPathCnt+=1 # control path color
                self.default_params['tmax']=int(e1.get())
                self.default_params['pointInPath']=int(e2.get())
                start=int(l1.get()) # begin attractor
                end=int(l2.get()) # end attractor
                if self.loadModel[:3]=='ODE':
                    path,action=ode_ss_path(np.array(self.default_params['stablePoints'][start-1]),np.array(self.default_params['stablePoints'][end-1]),self.default_params,self.odeCode)
                elif self.loadModel[:3]=='GRN':
                    path,action=grn_ss_path(np.array(self.default_params['stablePoints'][start-1]),np.array(self.default_params['stablePoints'][end-1]),self.default_params)
                attbeginend=str(start)+'-'+str(end)
                print(attbeginend+'Transfer path:',path)
                self.savepath[attbeginend]=path.tolist() # save one trajectory for all variables, but save landscape for two variables
                self.pathsAction[attbeginend]=action
                # show on the landscape
                pathx=path[self.default_params['vari_spec'][0]]
                pathy=path[self.default_params['vari_spec'][1]]
                pathz=np.zeros_like(pathx)
                num=pathx.shape[0]
                # print('path P: ',self.P)
                for i in range(num):
                    # x grid
                    for xx in range(100):
                        if xx==99:
                            idx=99
                        else:
                            if pathx[i]>=self.xAxis[0][xx] and pathx[i]<=self.xAxis[0][xx+1]:
                                idx=xx
                                break
                    # y grid
                    for yy in range(100):
                        if yy==99:
                            idy=99
                        else:
                            if pathy[i]>=self.yAxis[yy][0] and pathy[i]<=self.yAxis[yy+1][0]:
                                idy=yy
                                break
                    # get P

                    pathz[i]=self.P[idy,idx] # !!! pay attention
                if self.drawPathCnt%2==0:
                    color_list=['cyan']
                else:
                    color_list = ['yellow']
                # random_color_index=random.randint(0,1)
                random_color_index = 0
                # self.axes1.plot_surface(pathx, pathy, self.P, c=color_list[random_color_index],zorder=3) # z+2 to display it on the surface
                self.axes1.plot(pathx, pathy, pathz, c=color_list[random_color_index],zorder=3)  # z+2 to display it on the surface
                arrow_pos=int(len(pathx)/3)
                # self.axes1.plot_surface(pathx[arrow_pos:arrow_pos+1], pathy[arrow_pos:arrow_pos+1], self.P, c=color_list[random_color_index], marker='>',zorder=3)
                self.axes1.plot(pathx[arrow_pos:arrow_pos + 1], pathy[arrow_pos:arrow_pos + 1],pathz[arrow_pos:arrow_pos + 1], c=color_list[random_color_index], marker='>', zorder=3)

                self.canvas.draw()
                settingWin.destroy()

                tend = time.time()
                print('The consuming time of a path is: ' + str(tend - tstart) + ' s')
                # mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0
                # print('The max consuming memory of a path is: ' + str(mem) + ' MB')



            tk.Button(settingWin, text='Draw', command=backendDrawPath).grid(row=9, sticky='we', pady=20, padx=160,
                                                                               columnspan=2)




