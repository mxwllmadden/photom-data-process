# This script is intended to process image files taken using the Multisite Photometry system in Brian Mathur's Lab at University of Maryland Baltimore
# For details on the configuration of the multisite photometry system hardware, see X

import tkinter as tk
from tkinter import ttk

#Set features of the GUI window
gui = tk.Tk()
gui.title("Multisite Photometry Data Processing")
gui.geometry("500x500")
gui.resizable(0,0)
#Set features of the frame for widgets
tabControl = ttk.Notebook(gui)
tab1 = tk.Frame(tabControl)
tab2 = tk.Frame(tabControl)
tabControl.add(tab1, text='Raw Dataset Processing')
tabControl.add(tab2, text='Background Parameters')
tabControl.pack(expand=1, fill="both")
#Setup styles

#Setup all the widgets present on the gui
tk.Label(tab1, text="Dataset Folder Path", anchor="w",width=20).grid(column=0, row=0, padx=10, pady=(10,0))
tk.Label(tab1, text="Start Date", anchor="w",width=20).grid(column=0, row=3, padx=10, pady=(10,0))
tk.Label(tab1, text="End Date", anchor="w",width=20).grid(column=1, row=3, padx=10, pady=(10,0))
tk.Label(tab1, text="Animal Basename", anchor="w",width=20).grid(column=0, row=6, padx=10, pady=(10,0))
tk.Label(tab1, text="Start #", anchor="w",width=20).grid(column=1, row=6, padx=10, pady=(10,0))
tk.Label(tab1, text="End #", anchor="w",width=20).grid(column=2, row=6, padx=10, pady=(10,0))
tk.Entry(tab1, width=50).grid(column=0, row=1, columnspan=2, padx=(10,0), pady=(0,10), sticky="w")
tk.Entry(tab1, width=18).grid(column=0, row=4, padx=10, pady=(0,10), sticky="w")
tk.Entry(tab1, width=18).grid(column=1, row=4, padx=10, pady=(0,10), sticky="w")
tk.Entry(tab1, width=18).grid(column=0, row=7, padx=10, pady=(0,10), sticky="w")
tk.Entry(tab1, width=18).grid(column=1, row=7, padx=10, pady=(0,10), sticky="w")
tk.Entry(tab1, width=18).grid(column=2, row=7, padx=10, pady=(0,10), sticky="w")
tk.Button(tab1, text="Open...").grid(column=2,row=1,padx=10, pady=(0,10), sticky="w")
t1buttoncanvas = tk.Canvas(tab1)
t1buttoncanvas.grid(column=2,row=8,padx=10,pady=0,sticky="se")
tk.Button(t1buttoncanvas, text="Load Runs").grid(column=0, row=0,padx=0, pady=(0,10), sticky="se")
tk.Button(t1buttoncanvas, text="PROCESS!!!!!").grid(column=0, row=1,padx=0, pady=(0,10), sticky="se")
tk.Button(t1buttoncanvas, text="QUIT").grid(column=0, row=10,padx=2, pady=(0,10), sticky="se")
#Create canvas to contain Treeview
runcanvas = tk.Canvas(tab1)
runcanvas.grid(column=0,row=8,padx=10,pady=10,sticky="nw", columnspan=3)
runtree = ttk.Treeview(runcanvas, height=10, columns=('date','run'),selectmode='browse')
runtree.grid(row=0,column=0)
runtree.column("#0", width=20)
runtree.column("date", width=130)
runtree.column("run", width=130)
runtree.heading("date", text="Date", anchor="w")
runtree.heading("run", text="Run", anchor="w")
rtreescroll = ttk.Scrollbar(runcanvas, orient="vertical", command=runtree.yview)
rtreescroll.grid(row=0,column=1,sticky="ns")
runtree.config(yscrollcommand=rtreescroll.set)
runtree.bind('<Motion>', 'break')

#tab2 widgets
tk.Label(tab2, text="These are the Parameters used for processing the Image Datasets.").grid(column=0,row=0,columnspan=3,padx=10,pady=10,sticky="nsew")
tk.Label(tab2, text="Image Prefix").grid(column=0,row=1,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="ROI 1 name").grid(column=0,row=2,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="ROI 2 name").grid(column=0,row=3,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="ROI 3 name").grid(column=0,row=4,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="ROI 4 name").grid(column=0,row=5,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="ROI 5 name").grid(column=0,row=6,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="# of Images/Trial").grid(column=0,row=7,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="Image Size").grid(column=0,row=8,padx=10,pady=10,sticky="e")
#Set the string variables for the Entry Fields
im_prefix = tk.StringVar()
roi1 = tk.StringVar()

im_prefix_ent = tk.Entry(tab2, width=18, textvariable="\l_pta")
roi1_ent = tk.Entry(tab2, width=18, textvariable="PTA")
roi2_ent = tk.Entry(tab2, width=18, textvariable="NA")
roi3_ent = tk.Entry(tab2, width=18, textvariable="NA")
roi4_ent = tk.Entry(tab2, width=18, textvariable="NA")
roi5_ent = tk.Entry(tab2, width=18, textvariable="NA")
imgptrial = tk.Entry(tab2, width=18, text=200)
imgsiz = tk.Entry(tab2, width=18, text=424)
im_prefix_ent.grid(column=1,row=0,padx=10,pady=10,sticky="w")
roi1_ent.grid(column=1,row=1,padx=10,pady=10,sticky="w")
roi2_ent.grid(column=1,row=3,padx=10,pady=10,sticky="w")
roi3_ent.grid(column=1,row=4,padx=10,pady=10,sticky="w")
roi4_ent.grid(column=1,row=5,padx=10,pady=10,sticky="w")
roi5_ent.grid(column=1,row=6,padx=10,pady=10,sticky="w")
imgptrial.grid(column=1,row=7,padx=10,pady=10,sticky="w")
imgsiz.grid(column=1,row=8,padx=10,pady=10,sticky="w")
im_prefix_ent.grid(column=1,row=9,padx=10,pady=10,sticky="w")

gui.mainloop()