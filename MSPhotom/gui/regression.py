# -*- coding: utf-8 -*-
"""
Regression related GUI elements
"""
import tkinter as tk
from tkinter import ttk

class RegressionTab(tk.Frame):
    def __init__(self, container):
        super().__init__(container)

        # Organizational Canvas
        buttoncanvas = tk.Canvas(self)
        buttoncanvas.grid(column=2, row=9, padx=10, pady=0, sticky="se")
        graphcanvas = tk.Canvas(self)
        graphcanvas.grid(column=0, row=8, padx=10, pady=10, sticky="nw", columnspan=3, rowspan=2)

        # Buttons
        self.loadbutton = tk.Button(buttoncanvas, text="Load Runs")
        self.regselbutton = tk.Button(buttoncanvas, text="Select Regions")
        self.processbutton = tk.Button(buttoncanvas, text="PROCESS!!!!!")
        self.reset_button = tk.Button(buttoncanvas, text="RESET")

        self.loadbutton.grid(column=0, row=0, padx=0, pady=(0, 10), sticky="se")
        self.regselbutton.grid(column=0, row=1, padx=0, pady=(0, 10), sticky="se")
        self.processbutton.grid(column=0, row=2, padx=0, pady=(0, 10), sticky="se")
        self.reset_button.grid(column=0, row=3, padx=2, pady=(0, 10), sticky="se")

        self.regselbutton["state"] = "disabled"
        self.processbutton["state"] = "disabled"

        # String Variables and Defaults
        self.topdirectory = tk.StringVar()
        self.bin_size = tk.StringVar()
        self.date_end = tk.StringVar()
        self.ani_prefix = tk.StringVar()
        self.ani_start = tk.StringVar()
        self.ani_end = tk.StringVar()

        self.topdirectory.set("Use button to right")
        self.bin_size.set("1")
        self.date_end.set("05-17-43")
        self.ani_prefix.set("MRKPFCREV")
        self.ani_start.set("1")
        self.ani_end.set("40")

        # Entry Fields
        tk.Entry(self, width=50, textvariable=self.topdirectory).grid(column=0, row=1, columnspan=2, padx=(10, 0),
                                                                      pady=(0, 10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.bin_size).grid(column=0, row=4, padx=10, pady=(0, 10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.ani_prefix).grid(column=0, row=7, padx=10, pady=(0, 10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.ani_start).grid(column=1, row=7, padx=10, pady=(0, 10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.ani_end).grid(column=2, row=7, padx=10, pady=(0, 10), sticky="w")

        # Static Labels
        tk.Label(self, text="Dataset Folder Path", anchor="w", width=20).grid(column=0, row=0, padx=10, pady=(10, 0))
        tk.Label(self, text="Bin Size", anchor="w", width=20).grid(column=0, row=3, padx=10, pady=(10, 0))
        tk.Label(self, text="Animal Basename", anchor="w", width=20).grid(column=0, row=6, padx=10, pady=(10, 0))
        tk.Label(self, text="Start #", anchor="w", width=20).grid(column=1, row=6, padx=10, pady=(10, 0))
        tk.Label(self, text="End #", anchor="w", width=20).grid(column=2, row=6, padx=10, pady=(10, 0))

        # Progress Bars

        self.runprog = ttk.Progressbar(self, orient="horizontal", length=480, mode="determinate")
        self.runprog["value"] = 0
        self.runprog.grid(column=0, row=12, columnspan=5)
        self.shortprogstat = tk.StringVar()
        self.shortprogstat.set("Regressing Images...")
        tk.Label(self, width=18, textvariable=self.shortprogstat).grid(column=0, row=13, padx=10, pady=0, columnspan=5, sticky="nsew")

