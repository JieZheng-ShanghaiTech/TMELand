import tkinter as tk
import tkinter.messagebox

class NewModelFrame(tk.Frame):
    def __init__(self,master,w,h):
        tk.Frame.__init__(self,master,width=w,height=h)
        self.root=master
        self.askCreateWayFrame = tk.Frame(self, height=300, width=500, bg='white', highlightbackground='black',
                                     highlightcolor='black', highlightthickness=1)
        self.graphFrame=tk.Frame(self,width=900,height=500)
        self.createNewModelPage()

    def createNewModelPage(self):
        # tk.Label(self,text='new model page').pack()
        self.askCreateWayFrame.grid(row=0,column=0)
        optionVar=tk.IntVar()
        tk.Label(self.askCreateWayFrame, text='Choose a way to create the new model:', bg='white', font=('TkDefaultFont', 14)).grid(row=0,column=0)
        option1 = tk.Radiobutton(self.askCreateWayFrame, text='ODE', bg='white', font=('TkDefaultFont', 13), variable=optionVar, value=1, command=self.createFromODE)
        option1.grid(row=1,column=0)
        option2 = tk.Radiobutton(self.askCreateWayFrame, text='Graph', bg='white', font=('TkDefaultFont', 13), variable=optionVar, value=2, command=self.createFromGraph)
        option2.grid(row=2,column=0)

    def createFromODE(self):
        pass

    def createFromGraph(self):
        self.askCreateWayFrame.grid_forget()
        self.graphFrame.grid(row=0,column=0,sticky="n")
        tk.Label(self.graphFrame, text='User-defined GRN', font=('TkDefaultFont', 12)).grid(row=0,column=0,sticky="nw")
        # TBD: the interactively constructing GRN
