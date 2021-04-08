import tkinter as tk

class AboutFrame(tk.Frame):
    def __init__(self,master,w,h):
        tk.Frame.__init__(self,master,width=w,height=h)
        self.root=master
        self.createAboutPage()

    def createAboutPage(self):
        tk.Label(self, text='About TMELand', font=("Verdana", 12, "bold"), width=20, height=2).pack(pady=5)
        #
        about='TMELand: A lightweight, python-based application, which can draw both more accurate landscape and detailed state transition paths between attractors based on differential equations of gene regulatory network.\n\n'\
            'Platform: cross-platform (have been tested on Windows 10, Ubuntu 18.04, and macOS Catalina 10.15.7)\n\n' \
              'Language: python 3.7\n\n' \
              'License: GPL v3.0\n\n' \
              'Contact: If there is any bug, error or improvement when you use, please post your issue on the GitHub website (https://github.com/JieZheng-ShanghaiTech/TMELand) or send your suggestions or bug reports to zhengjie@shanghaitech.edu.cn or chunheli@fudan.edu.cn.'

        tk.Message(self,text=about,font=("Verdana", 10),justify=tk.LEFT,highlightbackground='black',
                                     highlightcolor='black', highlightthickness=1).pack(pady=5)
        # tk.Button(self,text='OK',command=self.quit).grid(row=6)

    # def quit(self):
    #     pass