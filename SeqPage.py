import scanpy as sc
import numpy as np
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import os

from GrnGeneration.SCODE.CallSCODE import *
# from GrnGeneration.PoLoBag.PoLoBag import callPoLoBag

def visualAnalyzeData(canvas,fig,analysisMethod,color,paths):
    fig.clear()
    axes = fig.add_subplot(111)
    # sc setting
    sc.settings.verbosity = 3
    sc.set_figure_params(dpi=100, color_map='viridis_r')
    sc.logging.print_header()

    # load data, store in AnnData
    adata = sc.AnnData(X=np.loadtxt(paths['seq_expr']).T)
    adata.var_names = np.loadtxt(paths['seq_gnames'],dtype=str).tolist()
    adata.obs_names = np.loadtxt(paths['seq_cnames'],dtype=str).tolist()
    adata.obs['cell_name'] = np.loadtxt(paths['seq_cnames'],dtype=str).tolist()
    # print(adata)
    # print(adata.to_df())
    # print(adata.obs.columns)
    if color == 'cell label':
        color = 'cell_name'
    if analysisMethod == "clustering":  # based on leiden
        sc.pp.neighbors(adata, knn=True)  # two params
        sc.tl.leiden(adata, key_added='clustering')  # by default, using Leiden graph clustering
        sc.tl.umap(adata)
        sc.pl.umap(adata, color=color, ax=axes, show=False)
    if analysisMethod == 'trajectory inference':
        sc.pp.neighbors(adata, knn=True)  # two params
        sc.tl.louvain(adata, resolution=1.0, key_added='clustering')
        sc.tl.paga(adata, groups='clustering')
        sc.pl.paga(adata, color=color, ax=axes, show=False)
    if analysisMethod == 'dimensionality reduction (pca)':
        sc.tl.pca(adata, svd_solver='arpack')
        if color != 'clustering':
            sc.pl.pca(adata, color=color, ax=axes, show=False)
        else:
            tk.messagebox.showwarning(title='Warning',
                                      message='dimensionality reduction visualization not support clustering!')

    canvas.draw()


