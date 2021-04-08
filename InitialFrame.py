import tkinter as tk
from tkinter import *

class InitialFrame(tk.Frame):
    def __init__(self,master,w,h):
        tk.Frame.__init__(self,master,width=w,height=h)
        self.root=master
        self.createInitialPage()

    def createInitialPage(self):
        # initial show page
        main_title = tk.Label(self, text='Quick Cooking Page', font=("Verdana", 12, "bold"))
        # will be replaced by more advanced rich text display
        # https://stackoverflow.com/questions/35733300/how-to-show-markdown-format-text-in-tkinter
        main_title.pack(pady=5)
        welcome = tk.Label(self, text='Welcome to the TMELand, here\'s a quick tutorial:', font=('Verdana', 10), justify=tk.LEFT)
        welcome.pack(pady=5)
        txtShow=tk.StringVar()
        quick_cooking='1. Info: TMELand is used to plot Waddington\'s epigenetic landscape and ' \
                      'state transition paths between attractors using TME method.\n\n' \
                      '2. Input: The TMELand supports TSV, ODE, SBML, and TME files:\n\n' \
                      '    TSV: TSV (Tab-separated values) stores the interaction relationship among nodes ' \
                      'in gene regulatory network, activation is +, inhibition is -. ' \
                      'Please refer to ' \
                      'the ./TSV_models/ to find an example.\n\n' \
                      '    ODE: ODE (XPPAUT ODE) refers to .ode format, which is a set of ODE equations. ' \
                      'Please refer to ' \
                      'the ./ODE_SBML_models/ to find an example.\n\n' \
                      '    SBML: You can also provide your self-define ODE functions by SBML' \
                      'format. TMELand supports SBML models come from BioModels website.\n\n' \
                      '    TME: TME is a self-define format to save computed model. After ' \
                      'you construct landscape only or landscape with paths, you can save it ' \
                      'as a TME model for next reloading.\n\n'\
                      '3. Main functions:\n\n' \
                      '    Model visualization: After loading your models, you can obtain ' \
                      'the parsed and visualized results of your models.\n\n' \
                      '    Drawing landscape: After defining your models, you can draw ' \
                      'the landscape.\n\n' \
                      '    Drawing state transition path: After drawing the landscape, you can draw transition ' \
                      'paths between any two attractors.'

        txtShow.set(quick_cooking)
        txt=tk.Message(self,textvariable=txtShow,font=('Verdana', 10),justify=tk.LEFT,bg='white',highlightbackground='black',
                                     highlightcolor='black', highlightthickness=1)
        txt.pack(pady=5)
