# #!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import *
import os
import sys

class AskRegister():

    message = None
    title = None
    host = ""

    def __init__(self, message, title, host):

        self.message = message
        self.title = title
        self.host = host
        self.master = tk.Tk()
        self.master.title(self.title)

        if self.host != "":
            pass
        else:
             tk.Label(self.master, text="Etki Alanı Sunucusu : ").grid(row=0)
             self.e1 = tk.Entry(self.master)
             self.e1.grid(row=0, column=1)

        tk.Label(self.master, text="Yetkili Kullanıcı : ").grid(row=1)
        tk.Label(self.master, text="Parola : ").grid(row=2)

        self.e2 = tk.Entry(self.master)
        self.e3 = tk.Entry(show="*")

        self.var1 = IntVar()
        Checkbutton(self.master, text="Active Directory", variable=self.var1, command=self.check1).grid(row=3, column=0, stick=tk.W,
                                                                                         pady=4)
        self.var2 = IntVar()
        self.var2.set(1)
        Checkbutton(self.master, text="OpenLDAP", variable=self.var2, command=self.check2).grid(row=3, column=1, stick=tk.W, pady=4)


        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)

        tk.Button(self.master, text='Çıkış', command=self.master.quit).grid(row=4, column=0, sticky=tk.W, pady=4)
        tk.Button(self.master, text='Tamam', command=self.show).grid(row=4, column=1, sticky=tk.W, pady=4)
        tk.mainloop()

    def show(self):

        if self.var2.get() == 1:
            if self.host != "":
                print(self.e2.get()+" "+self.e3.get()+" "+"LDAP")
            else:
                print(self.e1.get()+" "+self.e2.get()+" "+self.e3.get()+" "+"LDAP")

        if self.var1.get() == 1:
            if self.host != "":
                print(self.e2.get()+" "+self.e3.get()+" "+"AD")
            else:
                print(self.e1.get()+" "+self.e2.get()+" "+self.e3.get()+" "+"AD")

        self.master.quit()

    def check1(self):
        self.var2.set(0)

    def check2(self):
        self.var1.set(0)

if __name__ == '__main__':

    if len(sys.argv) > 1:
        try:
            m_message = sys.argv[1]
            t_title = sys.argv[2]
            h_host = sys.argv[3]
            display = sys.argv[4]
            os.environ["DISPLAY"] = display
            app = AskRegister(m_message, t_title, h_host)
        except Exception as e:
            print(str(e))
    else:
        print("Argument fault. Check your parameters or content of parameters. Parameters:" + str(sys.argv))