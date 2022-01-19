import numpy as np
import tkinter.messagebox
import pandas as pd

def grnChooser2graph(grn_df):
    print(grn_df)
    cont = grn_df.values
    genes = np.unique(np.hstack((np.array(grn_df['regulator']).T,np.array(grn_df['target'])))).tolist()
    print('The number of gene is: ', len(genes))
    IM = np.zeros((len(genes), len(genes)))
    for edge in cont:
        row = genes.index(edge[0])
        col = genes.index(edge[1])
        if edge[2] == '+':
            IM[row, col] = 1
        elif edge[2] == '-':
            IM[row, col] = -1
        else:
            print('Unsupported regulatory relationship.')
    if IM.any() == 0:
        tkinter.messagebox.showwarning(title='Warning', message='The system contains 0 reaction!')
    return IM, len(genes), genes
