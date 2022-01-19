import tkinter as tk
import numpy as np
from tkinter import ttk
import pandas as pd
from tkintertable import TableCanvas, TableModel


def odesdf2dict(des):
    odes=des.values
    column_names=['Gene','Equation']
    res={}
    for i in range(odes.shape[0]):
        res[str(i+1)]={column_names[0]:odes[i,0],column_names[1]:odes[i,1]}
    return res

def dict2odesdf(dic):
    res=[]
    for i in range(len(dic)):
        line=dic[str(i+1)]
        res.append([line['Gene'],line['Equation']])
    return pd.DataFrame(np.array(res))




def showDEsDescribedGRN(father,des):
    column_names = ['Gene','Equation']
    xx = tk.Scrollbar(father, orient="horizontal")
    yy = tk.Scrollbar(father, orient="vertical")
    table = ttk.Treeview(father, columns=tuple(column_names), xscrollcommand=xx.set, yscrollcommand=yy.set)
    xx.pack(side="bottom", fill="x")
    yy.pack(side="right", fill="y")
    for name in column_names:
        table.heading(name, text=name)
    table['show'] = 'headings'

    xx.config(command=table.xview)
    yy.config(command=table.yview)

    table.column('Gene', width=70)
    table.column('Equation', width=600)

    n_des=des.values.shape[0]
    for k in range(n_des):
        table.insert('', k , text="", values=tuple(des.values[k]))


    # based on tktable developed
    # data = odesdf2dict(des)
    # xx = tk.Scrollbar(father, orient="horizontal")
    # yy = tk.Scrollbar(father, orient="vertical")
    # table = TableCanvas(father, data=data,
    #                     cellwidth=200,cellbackgr='#e3f698',
    #                     thefont=('Arial', 12), rowheight=25,rowheaderwidth=30,
    #                     rowselectedcolor='yellow', read_only=False,width=20000,xscrollcommand=xx.set, yscrollcommand=yy.set)
    #
    #
    # table.show()
    # return table

    table.pack(fill="both", expand=1)