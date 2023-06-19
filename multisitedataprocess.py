# This script is intended to process image files taken using the Multisite Photometry system in Brian Mathur's Lab at University of Maryland Baltimore
# For details on the configuration of the multisite photometry system hardware, see X

#This code was written while I was (re)learning python and as a result there are a couple things that could have been done much better. 
#Specifically, I refrained from using classes as at the time of writing the code I did not have a firm grasp of their use.

import tkinter as tk
from tkinter import ttk, filedialog
import os
from PIL import Image, ImageTk


def fileselect():
    dirpath.set(filedialog.askdirectory())

def loadruns():
    #This function searches the listed directory for a list of folders matching the parameters described through the entry fields.
    global dir_list
    global dir_coords
    dir_list = []
    if not (ani_start.get().isdigit() and ani_end.get().isdigit()):
        ani_start.set("ERROR")
        ani_end.set("ERROR")
        return
    if os.path.exists(dirpath.get()):
        dirpath_dates = os.listdir(dirpath.get()) #get the names of all the files/folders in the target directory
        dirpath_dates = [f for f in dirpath_dates if not os.path.isfile(dirpath.get()+'/'+f)] #filter so that only directories (not files) appear
        #next we generate a list of possible dates from the start and end dates provided by the user.
        #extract the month day and year using string indexes
        if len(date_end.get()) == 10 and len(date_start.get()) == 10 and \
            date_start.get()[2] == date_start.get()[5] == date_end.get()[2] == date_end.get()[5] == "-": #Checking to make sure (broadly) that the date format is correct
            d_s_extract = [date_start.get()[0:2], date_start.get()[3:5], date_start.get()[6:10]]
            d_e_extract = [date_end.get()[0:2], date_end.get()[3:5], date_end.get()[6:10]]
            #Dates are now extracted from input as strings. We need to ensure they are all numbers then convert to integers.
            #Note: each list is MONTH, DAY, YEAR
            if all(x.isdigit() for x in d_s_extract) and all(x.isdigit() for x in d_e_extract):
                #excellent. now we need to iterate through each of the possible intermediate dates and determine if the corresponding directory is present
                d_s_extract = [int(i) for i in d_s_extract] #convert all elements of each list to integers using int()
                d_e_extract = [int(i) for i in d_e_extract]
                #check each possible date via a nested for loop
                dateslist = []
                s_convdate = (d_s_extract[1]) + (d_s_extract[0]*32) + (d_s_extract[2]*384)
                e_convdate = (d_e_extract[1]) + (d_e_extract[0]*32) + (d_e_extract[2]*384)+1
                for e in range(s_convdate,e_convdate):
                    y, d = divmod(e,384)
                    m, d = divmod(d,32)
                    targetpath = dirpath.get()+"/"+str(m).zfill(2)+"-"+str(d).zfill(2)+"-"+str(y).zfill(2) #contruct the path to check for
                    if os.path.exists(targetpath):
                        #add the path to the targetpath list
                        dateslist.append(targetpath)
            else:
                date_end.set("ERROR: format")
                date_start.set("ERROR: format")
                return
        else:
            date_start.set("ERROR: format")
            date_end.set("ERROR: format")
            return
    else:
        dirpath.set("ERROR: Path does not exist")
        return
    #Now that we have a list of valid paths for each date of recording, each directory must be searched for folders matching the specificied animal prefix.
    #generating animal names
    animallist=[]
    for i in range(int(ani_start.get()), int(ani_end.get())+1):
        animallist.append("/" + ani_prefix.get()+" "+str(i)+" ")
    
    #Clear the treeviewer widget
    for i in runtree.get_children(): runtree.delete(i)
    for i in dateslist:
        for k in animallist:
            for j in range(len(os.listdir(i))): #this is here to set the theoretical maximum number of runs. Its better than what the old photom did because it can handle an arbitrary number of runs, though its kind of messy.
                targetpath = i + k + "Run " + str(j+1)
                if os.path.exists(targetpath): 
                    dir_list.append(targetpath)
                    runtree.insert('', 'end', text = str(j), values=(i[-10:],(k+"Run "+str(j+1))[1:len(k+"Run "+str(j+1))]))
    if len(dir_list)>0: regselectbutton["state"] = "normal"
    else: regselectbutton["state"] = "disabled"

def reg_select():
    #this function's purpose is to allow for the selection of each region.
    #steps: create new window; load image; allow for selection of the appropriate region within the image, do so for each and save within a global variable.
    global reg_coords
    reg_coords = []
    def confirmreg():
        #confirm the location of the circle selector
        print("bong")
        nonlocal activeregion
        x, y, dx, dy = selectioncanvas.coords(selectoval)
        reg_coords.append(x)
        reg_coords.append(y)
        reg_coords.append(dx)
        reg_coords.append(dy)
        name = selectioncanvas.create_oval(x, y, dx, dy, outline='blue', width=3)
        reg_shapelist.append(name)
        if activeregion >= len(regionlist)-1:
            reggui.destroy()
        else:
            activeregion = activeregion + 1
            currentregion.set("Currently selecting "+regionlist[activeregion])


    def drag(event):
        #cirselector.place(x=event.x_reggui, y=event.y_reggui,anchor="center")
        selectioncanvas.moveto(selectoval,event.x-50,event.y-50)

    reggui = tk.Toplevel(gui)
    reggui.geometry(imgsizx.get()+"x"+str(int(imgsizy.get())+100))
    reggui.wm_attributes('-transparentcolor','green')
    reggui.resizable(0,0)
    im  = Image.open(dir_list[1]+im_prefix.get()+"0_2.tif")
    im_disp = ImageTk.PhotoImage(im)
    selectioncanvas = tk.Canvas(reggui,height=420,width=420)
    selectioncanvas.place(x=0,y=0)
    selectioncanvas.create_image(0,0,image=im_disp,anchor="nw")
    selectoval = selectioncanvas.create_oval(0,0,100,100,activewidth = 5, activeoutline='red',activefill='pink',width=4,outline='pink')

    tk.Label(reggui, text="Drag and drop the red circle to cover the selected region").place(x = 10, y = int(imgsizy.get())+10)
    currentregion = tk.StringVar()
    tk.Label(reggui,textvariable=currentregion).place(x=10, y = int(imgsizy.get())+50)

    tk.Button(reggui,text="CONFIRM REGION",command=confirmreg).place(x = int(imgsizx.get())-150, y = int(imgsizy.get())+50)
    
    regionlist = ["CORRECTION FIBER", "BACKGROUND SIGNAL"]
    reg_shapelist = []
    for i in range(5):
        if roi[i].get() != "NA":
            regionlist.append(roi[i].get())
    currentregion.set("Currently selecting "+regionlist[0])
    activeregion = 0
    selectioncanvas.bind("<B1-Motion>", drag)
    reggui.mainloop()


#Create any needed variables that are going to be important.
dir_list = [] #List of directories that need to be scanned through for images to analyze.
reg_coords = [] #The list of coordinates on the photometry image that mark each fiber.

#Set features of the GUI window
gui = tk.Tk()
gui.title("Multisite Photometry Data Processing App")
gui.geometry("500x500")
gui.resizable(0,0)
#Set features of the gui and setup tabs
tabControl = ttk.Notebook(gui)
tab1 = tk.Frame(tabControl)
tab2 = tk.Frame(tabControl)
tabControl.add(tab1, text='Raw Dataset Processing')
tabControl.add(tab2, text='Background Parameters')
tabControl.pack(expand=1, fill="both")
#Setup all the widgets present on the gui
tk.Label(tab1, text="Dataset Folder Path", anchor="w",width=20).grid(column=0, row=0, padx=10, pady=(10,0))
tk.Label(tab1, text="Start Date", anchor="w",width=20).grid(column=0, row=3, padx=10, pady=(10,0))
tk.Label(tab1, text="End Date", anchor="w",width=20).grid(column=1, row=3, padx=10, pady=(10,0))
tk.Label(tab1, text="Animal Basename", anchor="w",width=20).grid(column=0, row=6, padx=10, pady=(10,0))
tk.Label(tab1, text="Start #", anchor="w",width=20).grid(column=1, row=6, padx=10, pady=(10,0))
tk.Label(tab1, text="End #", anchor="w",width=20).grid(column=2, row=6, padx=10, pady=(10,0))
#creating textvariables for the Entry fields
dirpath = tk.StringVar()
date_start = tk.StringVar()
date_end = tk.StringVar()
ani_prefix = tk.StringVar()
ani_start = tk.StringVar()
ani_end = tk.StringVar()
tk.Entry(tab1, width=50, textvariable=dirpath).grid(column=0, row=1, columnspan=2, padx=(10,0), pady=(0,10), sticky="w")
tk.Entry(tab1, width=18, textvariable=date_start).grid(column=0, row=4, padx=10, pady=(0,10), sticky="w")
tk.Entry(tab1, width=18, textvariable=date_end).grid(column=1, row=4, padx=10, pady=(0,10), sticky="w")
tk.Entry(tab1, width=18, textvariable=ani_prefix).grid(column=0, row=7, padx=10, pady=(0,10), sticky="w")
tk.Entry(tab1, width=18, textvariable=ani_start).grid(column=1, row=7, padx=10, pady=(0,10), sticky="w")
tk.Entry(tab1, width=18, textvariable=ani_end).grid(column=2, row=7, padx=10, pady=(0,10), sticky="w")

tk.Button(tab1, text="Open...", command=fileselect).grid(column=2,row=1,padx=10, pady=(0,10), sticky="w")
t1buttoncanvas = tk.Canvas(tab1)
t1buttoncanvas.grid(column=2,row=9,padx=10,pady=0,sticky="se")
loadbutton = tk.Button(t1buttoncanvas, text="Load Runs", command=loadruns)
loadbutton.grid(column=0, row=0,padx=0, pady=(0,10), sticky="se")
regselectbutton = tk.Button(t1buttoncanvas, text="Select Regions", command=reg_select)
regselectbutton.grid(column=0, row=1,padx=0, pady=(0,10), sticky="se")
regselectbutton["state"] = "disabled"
processbutton = tk.Button(t1buttoncanvas, text="PROCESS!!!!!")
processbutton.grid(column=0, row=2,padx=0, pady=(0,10), sticky="se")
processbutton["state"] = "disabled"
tk.Button(t1buttoncanvas, text="EXIT", command=gui.destroy).grid(column=0, row=3,padx=2, pady=(0,10), sticky="se")
#Create canvas to contain Treeview, this is for ease of formatting
runcanvas = tk.Canvas(tab1)
runcanvas.grid(column=0,row=8,padx=10,pady=10,sticky="nw", columnspan=3, rowspan=2)
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
##All widgets on tab2
tk.Label(tab2, text="These are the Parameters used for processing the Image Datasets.").grid(column=0,row=0,columnspan=3,padx=10,pady=10,sticky="nsew")
tk.Label(tab2, text="Image Prefix").grid(column=0,row=1,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="ROI 1 name").grid(column=0,row=2,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="ROI 2 name").grid(column=0,row=3,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="ROI 3 name").grid(column=0,row=4,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="ROI 4 name").grid(column=0,row=5,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="ROI 5 name").grid(column=0,row=6,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="# of Images/Trial").grid(column=0,row=7,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="Image Size").grid(column=0,row=8,padx=10,pady=10,sticky="e")
tk.Label(tab2, text="X").grid(column=2,row=8,padx=0,pady=0,sticky="w")
#Set the string variables for the Entry Fields
im_prefix = tk.StringVar()
roi = [0,0,0,0,0]
roi[0] = tk.StringVar()
roi[1] = tk.StringVar()
roi[2] = tk.StringVar()
roi[3] = tk.StringVar()
roi[4] = tk.StringVar()
imgptrial = tk.StringVar()
imgsizx = tk.StringVar()
imgsizy = tk.StringVar()
tk.Entry(tab2, width=18, textvariable=im_prefix).grid(column=1,row=1,padx=10,pady=10,sticky="w")
tk.Entry(tab2, width=18, textvariable=roi[0]).grid(column=1,row=2,padx=10,pady=10,sticky="w")
tk.Entry(tab2, width=18, textvariable=roi[1]).grid(column=1,row=3,padx=10,pady=10,sticky="w")
tk.Entry(tab2, width=18, textvariable=roi[2]).grid(column=1,row=4,padx=10,pady=10,sticky="w")
tk.Entry(tab2, width=18, textvariable=roi[3]).grid(column=1,row=5,padx=10,pady=10,sticky="w")
tk.Entry(tab2, width=18, textvariable=roi[4]).grid(column=1,row=6,padx=10,pady=10,sticky="w")
tk.Entry(tab2, width=18, text=200, textvariable=imgptrial).grid(column=1,row=7,padx=10,pady=10,sticky="w")
tk.Entry(tab2, width=18, text=424, textvariable=imgsizx).grid(column=1,row=8,padx=(10,0),pady=10,sticky="w")
tk.Entry(tab2, width=18, text=424, textvariable=imgsizy).grid(column=3,row=8,padx=(0,10),pady=10,sticky="w")

#default in each entry field for tab 1
dirpath.set("Use button to right")
date_start.set("05-17-2023")
date_end.set("05-17-2023")
ani_prefix.set("MRKPFCREV")
ani_start.set("1")
ani_end.set("15")
#default text for each field on tab2
im_prefix.set("/mrk_pfc")
for i in range(5):
    roi[i].set("NA")
roi[0].set("PTA")
imgptrial.set("200")
imgsizx.set("420")
imgsizy.set("420")

gui.mainloop()