import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

class HelpFrame(tk.Frame):
    def __init__(self,master,w,h):
        tk.Frame.__init__(self,master,width=w,height=h)
        self.root=master
        self.createHelpPage()

    def createHelpPage(self):
        main_title = tk.Label(self, text='Detailed User Manual', font=("Verdana", 12, "bold"), width=20, height=2)
        # will be replaced by more advanced rich text display
        # https://stackoverflow.com/questions/35733300/how-to-show-markdown-format-text-in-tkinter
        main_title.grid(row=0,column=0,pady=5)

        quick_cooking = '1. Info: TMELand is used to plot Waddington\'s epigenetic landscape and ' \
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
                      '    Drawing landscape: To draw a landscape, there are three steps:\n\n' \
                      '        1. Form ODE equations (only need for TSV models): by \'Dynamics setting\' button to generate ODE equations. \n\n' \
                      '        2. Draw: this step includes simulation and default visualization (the first two marker genes and visualization range is from 0 to 3), and corresponding to \'Draw\' button.\n\n'\
                      '        3. Update: you can adjust the marker genes and range to update the landscape by \'Update\' button; Once you make sure your visualization parameters, if you need change model related parameters, you only ' \
                        'need to click \'Draw\' button without reupdate; Update is also worked for TME model. You can update landscape shape after load a TME model. \n\n' \
                      '    Drawing transition path: After drawing the landscape, you can draw state transition ' \
                      'path between two attractors by specify time range, granularity, beginning and ending attractors; You can also draw path after load a TME model; Update landscape will keep paths. \n\n\n\n\n' \
                        '######For more details, please refer to the User Manual.######'


        helpInfoFrame = tk.Frame(self, bg='white', borderwidth=1)
        helpTxt = tk.Text(helpInfoFrame, wrap=tk.WORD, font="Verdana 10", width=100, height=15, borderwidth=2)
        verScroll = tk.Scrollbar(helpInfoFrame, orient='vertical', command=helpTxt.yview)
        # horScroll = tk.Scrollbar(helpInfoFrame, orient='horizontal', command=helpTxt.xview)
        helpTxt.config(yscrollcommand=verScroll.set) # , xscrollcommand=horScroll.set
        helpTxt.grid(row=0, column=0, sticky="nsew")
        verScroll.grid(row=0, column=1, sticky="ns")
        # horScroll.grid(row=1, column=0, sticky="ew")
        helpInfoFrame.grid_rowconfigure(0, weight=1)
        helpInfoFrame.grid_columnconfigure(0, weight=1)
        helpTxt.insert(tk.INSERT, quick_cooking)

        # helpTxt.insert(tk.END, '\n')
        # img = tk.PhotoImage(file="./resource/quick_tutorial.gif")
        # helpTxt.image_create(tk.END, image=img)  # Example 1
        # helpTxt.window_create(tk.END, window=tk.Label(helpTxt, image=img))  # Example 2

        helpTxt.config(font="Verdana 10")
        helpInfoFrame.grid(row=1,column=0,pady=5)



        sec_title = tk.Label(helpInfoFrame, text='Operation Pipeline', bg='white', font=("Verdana", 11), width=20, height=2)
        sec_title.grid(row=2,column=0,pady=5)
        fig = Image.open('./resource/quick_tutorial.JPG')
        fig_resize = fig.resize((800,250))
        render = ImageTk.PhotoImage(fig_resize)
        img = Label(helpInfoFrame, image=render)
        img.image = render
        img.grid(row=3,column=0,pady=5)