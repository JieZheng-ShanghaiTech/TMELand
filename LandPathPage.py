import tkinter.messagebox
import json
from tkinter.filedialog import asksaveasfile
import os
from HelperFunctions import *
from GRN_TME import *
from ODE_TME import *
import tkinter as tk

def fillAttTable(table,Global_w,params):
    n_atts = len(Global_w)
    weight_line = ['Frequency'] + list(Global_w)
    n_genes=len(params['Genes'])
    table.insert('', 0, text="", values=tuple(weight_line))
    for k in range(n_genes):
        table.insert('', k+1, text="", values=tuple([params['Genes'][k]]+[str(round(att[k],2)) for att in params['stablePoints']]),tags = (str(k%2),))

def showAtts(father,Global_w,params):
    n_atts=len(Global_w)
    column_names=['Genes']+['Att'+str(i) for i in range(1,n_atts+1)]
    attsWin=getPoppedWindow(father,width=400,height=300,title='Attractors Details')
    xx = tk.Scrollbar(attsWin, orient="horizontal")
    yy = tk.Scrollbar(attsWin, orient="vertical")
    table = ttk.Treeview(attsWin, columns=tuple(column_names),xscrollcommand=xx.set, yscrollcommand=yy.set)
    xx.pack(side="bottom", fill="x")
    yy.pack(side="right", fill="y")
    for name in column_names:
        table.heading(name, text=name)
    table['show'] = 'headings'

    xx.config(command=table.xview)
    yy.config(command=table.yview)

    for name in column_names:
        table.column(name, width=60)

    fillAttTable(table,Global_w,params)
    table.tag_configure('1', background='#cef3d9')
    table.tag_configure('0', background='#97edb2')
    table.pack(fill="both", expand=1)


def showTopView(canvas,axes):
    axes.view_init(azim=0, elev=90)
    canvas.draw()

def saveLand(loadModel,modelTop,modelDes,Global_sp,Global_sig,Global_w,savepath,pathsAction,default_params,ODEModelOdeCode,ODEModelJacCode):
    f = asksaveasfile(initialdir=os.getcwd() + './TME_models/', mode='w', defaultextension=".json")
    if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        f.close()
    else:
        f.close()
        fname = f.name  # path+name; os.path.basename(f.name) only name
        data = {}
        data['modelType'] = loadModel
        data['modelTopology']=modelTop
        data['modelDEs']=modelDes

        data['stablePoints'] = Global_sp.tolist()
        data['sigma'] = Global_sig.tolist()
        data['weight'] = Global_w.tolist()

        data['allpath'] = savepath
        data['pathAction'] = pathsAction

        data['defaultParams'] = changeNparray2List(default_params)
        data['ODEModelOdeCode'] = ODEModelOdeCode
        data['ODEModelJacCode']=ODEModelJacCode
        with open(fname, 'w') as outfile:
            json.dump(data, outfile)
        tkinter.messagebox.showinfo(title='Info', message='Save successfully!')

def restoreLandscape(fig,canvas,data,e1,e2,e3,e4,l1,l2,e5,e6,e7,e8,tmax,pointInPath,l3,l4):
    # initial visualization
    with open(data, 'r') as fr:
        data = json.load(fr)
    TMEModelType = data['modelType']
    params = data['defaultParams']
    Global_sp = np.array(data['stablePoints'])
    Global_sig = np.array(data['sigma'])
    Global_w = np.array(data['weight'])
    # odeCode = data['odeCode']
    savepath = data['allpath']
    genes = params['Genes']

    # params setting
    e1.delete(0, tk.END)
    e2.delete(0, tk.END)
    e3.delete(0, tk.END)
    e4.delete(0, tk.END)
    l1.delete(0, tk.END)
    l2.delete(0, tk.END)
    e5.delete(0, tk.END)
    e6.delete(0, tk.END)
    e7.delete(0, tk.END)
    e8.delete(0, tk.END)
    tmax.delete(0, tk.END)
    pointInPath.delete(0, tk.END)
    l3.delete(0, tk.END)
    l4.delete(0, tk.END)

    e1.insert(0, params['cycle'])
    e2.insert(0, params['xmax'])
    e3.insert(0, params['Tfinal'])
    e4.insert(0, params['Diffusion'])
    e5.insert(0, params['y_min'][0])
    e6.insert(0, params['y_max'][0])
    e7.insert(0, params['y_min'][1])
    e8.insert(0, params['y_max'][1])
    l1['value'] = (params['Genes'])
    l2['value'] = (params['Genes'])
    l1.insert(0, params['Genes'][params['vari_spec'][0]])
    l2.insert(0, params['Genes'][params['vari_spec'][1]])
    if savepath!={}:
        tmax.insert(0, params['tmax'])
        pointInPath.insert(0, params['pointInPath'])
        l3['value'] = ([i for i in range(1, np.array(params['stablePoints']).shape[0] + 1)])  # attractors No. for selection of begin and end atts
        l4['value'] = ([i for i in range(1, np.array(params['stablePoints']).shape[0] + 1)])
        lastPath=list(savepath.keys())[-1]
        attbegin,attend=lastPath.split('-')
        l3.insert(0,attbegin)
        l4.insert(0,attend)

    # draw landscape
    xAxis, yAxis, P=None,None,None
    if TMEModelType == 'ODE':
        if len(Global_sp) == 0:
            tk.messagebox.showwarning(title='Warning', message='No steady points!')
        xAxis, yAxis, P, _ = ode_tme_draw_landscape(params,Global_sp,Global_sig,Global_w)
    elif TMEModelType == 'GRN' or TMEModelType == 'seq':
        if len(Global_sp) == 0:
            tk.messagebox.showwarning(title='Warning', message='No steady points!')
        xAxis, yAxis, P, _ = grn_tme_draw_landscape(params, Global_sp, Global_sig, Global_w)

    fig.clear()
    axes1 = fig.add_subplot(111, projection='3d')
    # print('initial P: ',self.P)
    tmp = axes1.plot_surface(xAxis, yAxis, P, cmap='jet', zorder=1)
    axes1.set_xlabel(genes[params['vari_spec'][0]])
    axes1.set_ylabel(genes[params['vari_spec'][1]])
    axes1.set_zlabel('U')
    # mark stable points
    steadyMarkers=Global_sp[:,params['vari_spec']]
    for i in range(len(steadyMarkers)):
        axes1.text(x=steadyMarkers[i][0], y=steadyMarkers[i][1], z=0, s=str(i + 1), c='red', size=12)

    fig.colorbar(tmp)
    canvas.draw()

    # draw path
    color_cnt = 0
    for i in data['allpath'].keys():
        color_cnt += 1
        pathi = np.array(data['allpath'][i])  # ith path
        pathx = pathi[params['vari_spec'][0]]
        pathy = pathi[params['vari_spec'][1]]
        pathz = np.zeros_like(pathx)
        num = pathx.shape[0]
        for i in range(num):
            # x grid
            for xx in range(100):
                if xx == 99:
                    idx = 99
                else:
                    if pathx[i] >= xAxis[0][xx] and pathx[i] <= xAxis[0][xx + 1]:
                        idx = xx
                        break
            # y grid
            for yy in range(100):
                if yy == 99:
                    idy = 99
                else:
                    if pathy[i] >= yAxis[yy][0] and pathy[i] <= yAxis[yy + 1][0]:
                        idy = yy
                        break
            # get P
            pathz[i] = np.array(P)[idy, idx]
        if color_cnt % 2 == 0:
            color_list = ['cyan']
        else:
            color_list = ['yellow']
        # random_color_index=random.randint(0,1)
        random_color_index = 0
        axes1.plot(pathx, pathy, pathz, c=color_list[random_color_index],zorder=3)  # z+2 to display it on the surface
        arrow_pos = int(len(pathx) / 3)
        axes1.plot(pathx[arrow_pos:arrow_pos + 1], pathy[arrow_pos:arrow_pos + 1],
                                 pathz[arrow_pos:arrow_pos + 1], c=color_list[random_color_index],
                                 marker='>', zorder=3)
        canvas.draw()
    return axes1
