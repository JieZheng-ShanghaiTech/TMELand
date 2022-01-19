import numpy as np
from scipy.integrate import odeint
from matplotlib import cbook
from matplotlib import cm
from matplotlib.colors import LightSource
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import minimize
import scipy
import json
import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk
import platform
import base64
from PIL import Image, ImageTk


class Force():
    def __init__(self,params):
        self.IM = np.array(params['IM'])
        self.Hill_fn = np.array(params['Hill_fn'])
        self.TM = np.array(params['TM'])
        self.Act_Inh = np.array(params['Act_Inh'])
        self.Degrade_rate = params['Degrade_rate']
        self.Sys_Dim=params['Sys_Dim']

    def activate_Ha(self, gene, thres, activation, hill):
        Ha = activation * np.power(gene, hill) / (np.power(gene, hill) + np.power(thres, hill))
        return Ha

    def inhibit_Hr(self, gene, thres, inhibition, hill):
        Hr = inhibition * np.power(thres, hill) / (np.power(gene, hill) + np.power(thres, hill))
        return Hr

    def get_force(self, x, t):
        H = np.zeros((self.Sys_Dim, self.Sys_Dim, 1))  # need to take care of the 3D MATRIX is different in matlab

        for i in range(self.Sys_Dim):
            for j in range(self.Sys_Dim):
                if self.IM[i, j] == 1:
                    H[j, i] = self.activate_Ha(x[i], self.TM[i, j], self.Act_Inh[i, j], self.Hill_fn[i, j])
                if self.IM[i, j] == -1:
                    H[j, i] = self.inhibit_Hr(x[i], self.TM[i, j], self.Act_Inh[i, j], self.Hill_fn[i, j])

        F = np.zeros(self.Sys_Dim)

        for i in range(self.Sys_Dim):
            F[i] = np.sum(H[i, :, :]) - self.Degrade_rate[i] * x[i]  # dx/dt  F(i)=f(x[i]) 只有一个变量，没有其他变量
        # print(F)
        return F

    def get_odeEquations(self,x): # acquire the readable ODE form of equations
        H = np.empty((self.Sys_Dim, self.Sys_Dim),dtype=object)

        for i in range(self.Sys_Dim):
            for j in range(self.Sys_Dim):
                if self.IM[i, j] == 1:
                    H[j,i]=str(self.Act_Inh[i, j])+ '*'+ x[i]+'^'+str(self.Hill_fn[i, j]) +'/('+ x[i]+'^'+str(self.Hill_fn[i, j])+'+' + str(self.TM[i, j])+'^'+str(self.Hill_fn[i, j])+')'
                elif self.IM[i, j] == -1:
                    H[j, i] = str(self.Act_Inh[i, j])+ '*'+ str(self.TM[i, j])+'^'+str(self.Hill_fn[i, j]) +'/('+ x[i]+'^'+str(self.Hill_fn[i, j])+'+' + str(self.TM[i, j])+'^'+str(self.Hill_fn[i, j])+')'
                else:
                    H[j,i]=''

        F = np.empty(self.Sys_Dim,dtype=object)

        for i in range(self.Sys_Dim):
            tmp=H[i, :].tolist()
            while '' in tmp:
                tmp.remove('')
            F[i] = x[i]+'\'='+'+'.join(tmp)+'-'+str(self.Degrade_rate[i]) +'*' +x[i]  # dx/dt  F(i)=f(x[i]) 只有一个变量，没有其他变量
        return F


class Sigma(): # the covariance matrix of the gaussian distribution (steady state probability distribution)
    def __init__(self,params):
        self.IM = params['IM']
        self.Hill_fn = params['Hill_fn']
        self.TM = params['TM']
        self.Act_Inh = params['Act_Inh']
        self.Degrade_rate = params['Degrade_rate']
        self.Diffusion = params['Diffusion']
        self.Sys_Dim = params['Sys_Dim']

    def activate_Ha(self, gene, thres, activation, hill):
        Ha = activation * hill * np.power(thres, hill) * np.power(gene, hill - 1) / (np.power(np.power(thres, hill) + np.power(gene, hill), 2))
        return Ha

    def inhibit_Hr(self, gene, thres, inhibition, hill):
        Hr = -inhibition * hill * np.power(thres, hill) * np.power(gene, hill - 1) / (np.power(np.power(thres, hill) + np.power(gene, hill), 2))
        return Hr

    def get_sigma(self, stable):
        H0 = -1 * np.diag(self.Degrade_rate) * np.identity(self.Sys_Dim)
        H = np.zeros((self.Sys_Dim, self.Sys_Dim))
        for i in range(self.Sys_Dim):
            for j in range(self.Sys_Dim):
                if self.IM[i, j] == 1:
                    H[j, i] = self.activate_Ha(stable[i], self.TM[i, j], self.Act_Inh[i, j], self.Hill_fn[i, j])
                if self.IM[i, j] == -1:
                    H[j, i] = self.inhibit_Hr(stable[i], self.TM[i, j], self.Act_Inh[i, j], self.Hill_fn[i, j])

        H = H + H0
        P = np.zeros((np.power(self.Sys_Dim, 2), np.power(self.Sys_Dim, 2)))
        for i in range(self.Sys_Dim):
            P[i * self.Sys_Dim:i * self.Sys_Dim + self.Sys_Dim, i * self.Sys_Dim:i * self.Sys_Dim + self.Sys_Dim] = P[
                                                                                              i * self.Sys_Dim: i*self.Sys_Dim + self.Sys_Dim,
                                                                                              i * self.Sys_Dim:i * self.Sys_Dim + self.Sys_Dim] + H

        for m in range(self.Sys_Dim):
            for i in range(self.Sys_Dim):
                for j in range(self.Sys_Dim):
                    P[m * self.Sys_Dim + i, j * self.Sys_Dim + i] = P[m * self.Sys_Dim + i, j * self.Sys_Dim + i] + H[
                        m, j]

        B = np.zeros((np.power(self.Sys_Dim, 2), 1))
        for i in range(self.Sys_Dim):
            B[i * self.Sys_Dim + i] = -2 * self.Diffusion

        Sig = np.dot(np.linalg.inv(P), B) # P-1*B
        Sig = Sig.reshape(self.Sys_Dim, self.Sys_Dim)
        return Sig

def grn_find_stable(params):
    all_stable = np.zeros((params['cycle'], params['Sys_Dim']))  # (300,3)
    force=Force(params)

    # print generated ode equations. You can use this to obtain inner generated equations.
    # You need a further editing because of some string problems.
    # grn_odes=force.get_odeEquations(params['Genes'])

    # progress bar setting
    progressWin=tk.Tk()
    progressWin.title('Drawing landscape progress bar')
    ww=300
    hh=70
    sw=progressWin.winfo_screenwidth()
    sh=progressWin.winfo_screenheight()
    progressWin.geometry('%dx%d+%d+%d'%(ww, hh, (sw-ww)/2, (sh-hh)/2))
    if platform.system() == 'Windows':
        progressWin.iconbitmap(default="./resource/icon.ico")
    else:
        # icon = tk.PhotoImage(file='1.gif')
        # progressWin.tk.call('wm', 'iconphoto', progressWin._w, icon)
        pass
    progressLand=ttk.Progressbar(progressWin)
    progressLand.pack(pady=20)
    progressLand['maximum']=100
    progressLand['value']=0
    numCnt=0
    for i in range(params['cycle']):
        numCnt = numCnt + 1
        progressLand['value']=int((numCnt/params['cycle'])*100)
        progressWin.update()
        x0 = params['xmax'] * np.random.rand(params['Sys_Dim'])    # initial point
        t = np.linspace(0, params['Tfinal'], num=100)    # time series
        result = odeint(force.get_force, x0, t)
        newest_x = result[-1]
        x = 100000000 * np.ones(params['Sys_Dim'])       # upper bound
        while np.linalg.norm(x - newest_x) > 1e-6:
            x = newest_x
            t = np.linspace(0, 10, num=100)
            result = odeint(force.get_force, x, t)  # 中间那个是x初值
            newest_x = result[-1]
        all_stable[i, :] = newest_x
    progressWin.destroy()
    # delete the points which are too similar
    for i in range(params['cycle'] - 1):
        for j in range(i + 1, params['cycle']):
            if np.linalg.norm(all_stable[j, :] - all_stable[i, :]) < 1e-6:
                all_stable[j] = all_stable[i]

    stable_points = np.unique(all_stable, axis=0)  # RETURN

    num = np.zeros((stable_points.shape[0], 2))  # count the number of stable points
    sigma = np.zeros((stable_points.shape[0], params['Sys_Dim'], params['Sys_Dim']))  # SIGMA  RETURN
    for i in range(stable_points.shape[0]):

        index=[]
        for j in range(all_stable.shape[0]):
            if all(stable_points[i]==all_stable[j]):
                index.append(j)

        num[i, 0] = i
        num[i, 1] = len(index)

        print("The stable points: ", stable_points[i], " repeat ", num[i, 1].astype(np.int), " times, ",
              " the location in the row xx is :\n", index)
        temp_sigma = Sigma(params)
        sigma[i] = temp_sigma.get_sigma(stable_points[i])
    # we can get all of the stable_points and their weight
    wei = num[:, 1] / params['cycle']  # RETURN
    return stable_points, sigma, wei

def grn_simulation(params):
    t = np.linspace(0, params['Tfinal'], num=100) # [1,2,3]
    results=[] # [[traj1],[traj2]]
    force=Force(params)
    for i in range(params['cycle']):
        x0 = params['xmax'] * np.random.rand(params['Sys_Dim'])    # initial point
        results.append(odeint(force.get_force, x0, t))
    return t,results

# %%
def multi_norm(x, x0, sigma, n):
    z = 1 / (np.power((2 * np.pi), (n / 2)) * np.power(np.linalg.det(sigma), (1 / 2))) * np.exp(
        -0.5 * np.dot(np.dot((x - x0), np.linalg.inv(sigma)), (x - x0).T))
    return z

def grn_tme_draw_landscape(params,sp, sig, w):
    y1 = np.linspace(params['y_min'][0], params['y_max'][0], 100)
    y2 = np.linspace(params['y_min'][1], params['y_max'][1], 100)
    x, y = np.meshgrid(y1, y2)
    z = np.zeros((x.shape[0], x.shape[0]))  # z axis in landscape
    P = np.zeros((x.shape[0], x.shape[0]))  # Pss
    for i in range(sp.shape[0]):
        vari_index = np.array(params['vari_spec']).tolist()
        sig_spec = np.array(sig[i, vari_index][:,vari_index])  # row col : vari_index
        mu_spec = np.array(sp[i, vari_index])
        for j in range(x.shape[0]):
            for n in range(x.shape[0]):
                point = np.array([x[j, n], y[j, n]])
                z[j, n] = multi_norm(point, mu_spec, sig_spec, 2)

        P = P + w[i] * z / params['cycle']  # 多个稳态分布的加权和
    P = P / sum(sum(P))  # norm
    temp = (10 ** (-50)) * np.ones((x.shape[0], x.shape[0]))
    for i in range(x.shape[0]):
        for j in range(x.shape[0]):
            P[i, j] = max(P[i, j], temp[i, j])
    P = -np.log(P)
    return x,y,P,sp

def grn_ss_path(start, ending, params):
    # shape: (dimension) X (pointInPath+1)
    initial_path = []
    for i in range(params['Sys_Dim']):
        temp = []
        for j in range(params['pointInPath'] + 1):
            temp.append(start[i] + (ending[i] - start[i]) * (j / 100))
        initial_path.append(temp)

    # initial_path: np.array  (dimension) X (pointInPath+1)
    initial_path = np.array(initial_path)
    initial_path = initial_path[:, 1:-1]

    # reshpe the start/ending to : ( dimension * 1)
    start = start.reshape(params['Sys_Dim'], 1)
    ending = ending.reshape(params['Sys_Dim'], 1)

    delt = params['tmax'] / params['pointInPath']

    # S(x)
    # x is the whole path without initial point and terminal point
    # this function is the target function that we want to minimize
    # after minimize this function-> x will become the path
    def S(x):

        x = x.reshape(params['Sys_Dim'], int(x.shape[0] / params['Sys_Dim']))
        whole_path = np.concatenate((start, x, ending), axis=1)

        interval_path = (whole_path[:, 1:] + whole_path[:, 0:-1]) / 2
        force = np.zeros((interval_path.shape[0], interval_path.shape[1]))

        for i in range(interval_path.shape[1]):
            x0 = interval_path[:, i]
            force0 = Force(params).get_force(x0, 0)
            force[:, i] = force0

        summand = np.sum(np.power(((whole_path[:, 1:] - whole_path[:, 0:-1]) / delt - force), 2),
                         axis=1)
        out = 0.5 * np.sum(summand * delt)

        return out

    # in minimize function, initial_path will become a 1-D array
    initial_path = initial_path.flatten()
    print('The progress of minimization for path:')
    res = minimize(S, initial_path, method='trust-constr', options={'maxiter': 300, 'verbose':2, 'disp': True})
    print('action (minimum objective value): ', res.fun)
    action=res.fun
    # path without start and end
    path = res.x.reshape(params['Sys_Dim'], int(res.x.shape[0] / params['Sys_Dim']))
    whole_path = np.concatenate((start, path, ending), axis=1)
    whole_path = whole_path.reshape(params['Sys_Dim'], params['pointInPath'] + 1)

    # others
    remesh_c=1e10
    if_remesh = 1
    qmin = 3
    delt = params['tmax'] / params['pointInPath']
    # monitor()
    w = np.sqrt(1 + remesh_c * np.sum(np.power(((whole_path[:, 1:] - whole_path[:, 0:-1]) / delt), 2), axis=0))
    # qfunc()
    q = np.max(w * delt) / np.min(w * delt)
    if if_remesh == 1 and q > qmin:
        alphak = np.insert(np.cumsum(w * delt / np.sum(w * delt)), 0, 0.)
        alphaold = np.linspace(0, 1, params['pointInPath'])  # need to search
        print(alphak)
        print(np.linspace(-2.5, 2.5, params['pointInPath']))
        Tnew = np.interp(alphaold, alphak, np.linspace(-2.5, 2.5, params['pointInPath'])) # 2.5???
        phi = scipy.interpolate.spline(np.linspace(-2.5, 2.5, params['pointInPath']), whole_path, Tnew)
        return phi,action
    else:
        return whole_path,action







