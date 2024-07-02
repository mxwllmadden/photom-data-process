# -*- coding: utf-8 -*-
"""
Generalizable frames with reusability
"""
from typing import List
import tkinter as tk

class ParameterWindow(tk.Frame):
    def __init__(self, container, paramlabels : List[str], 
                 paramvars : List[tk.StringVar]):
        super().__init__(container)
        # Use the kwargs provided
        self.paramlabels = paramlabels
        self.paramvars = paramvars
        # Create the parameters entry windows etc etc.
        for ind, (label, var) in enumerate(zip(paramlabels, paramvars)):
            tk.Label(self, text = label, anchor="w",width = 20).grid(column=0, row=ind,padx=10,pady=10,sticky="e")
            tk.Entry(self, width=18, textvariable=var).grid(column=1,row=ind,padx=10,pady=10,sticky="w")