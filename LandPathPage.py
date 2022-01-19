import tkinter.messagebox
import json
from tkinter.filedialog import asksaveasfile
import os
from HelperFunctions import *

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

def saveLand(loadModel,Global_sp,Global_sig,Global_w,savepath,pathsAction,default_params,odeCode):
    f = asksaveasfile(initialdir=os.getcwd() + './TME_models/', mode='w', defaultextension=".json")
    if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        f.close()
    else:
        f.close()
        fname = f.name  # path+name; os.path.basename(f.name) only name
        data = {}
        data['modelType'] = loadModel
        data['stablePoints'] = Global_sp.tolist()
        data['sigma'] = Global_sig.tolist()
        data['weight'] = Global_w.tolist()

        data['allpath'] = savepath
        data['pathAction'] = pathsAction
        data['defaultParams'] = changeNparray2List(default_params)
        data['odeCode'] = odeCode
        with open(fname, 'w') as outfile:
            json.dump(data, outfile)
        tkinter.messagebox.showinfo(title='Info', message='Save successfully!')