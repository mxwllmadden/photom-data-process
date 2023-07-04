import tkinter as tk, os, numpy as np, dataclasses, threading
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageEnhance
from dataclasses import dataclass

# -----------------------------------------Application Main------------------------------------
class Main():
    #This class sets up the primary GUI window.
    def __init__(self) -> None:
        self.root = tk.Tk() #root is the tk.Tk() window
        # Set window properties
        self.root.title("Multisite Photometry Data Processing/Analysis App")
        self.root.geometry("500x500")
        self.root.resizable(0,0)
        # Create notebook for application tabs, add them in reverse order to appearance
        # This is to allow each application tab object to add its own additional tabs when created
        # and have those tabs appear after the instantiating tab in the list.
        # Each primary analysis window should receive self.tabcontainer and the app object.
        self.tabcontainer = ttk.Notebook(self.root)
        self.tabs = []
        # self.tabs.append(examplepriamryanalysis(self.tabcontainer,self))
        self.tabs.append(MSImageProcessGUI(self.tabcontainer,self))
        # Add all objects to be displayed in tabs to the tabcontainer
        self.tabs.reverse()
        for i in range(len(self.tabs)):
            self.tabcontainer.add(self.tabs[i], text = self.tabs[i].title)
        self.tabcontainer.pack(expand=1, fill="both")

    def addtab(self, classintab, dataset, **kwargs):
        # This method enables Primary Analysis Frames to initiate "helper" frames.
        x = classintab(self.tabcontainer, dataset, **kwargs)
        self.tabs.append(x)
        return x
    
    def run(self):
        self.root.mainloop()

# -----------------------------------------Primary Analysis Frames------------------------------------
class exampleprimaryanalysis(tk.Frame):
    # This class is provided as a template to add additional analysis windows to the application
    # I use a nested dataclass to facilitate passing of information between classes of a specific analysis
    @dataclass
    class ExampleDataClass():
        #primary contains the object 
        primary: ...
        _: dataclasses.KW_ONLY
        example: ... = None

    def __init__(self, container, controller):
        super().__init__(container)
        self.controller = controller
        self.title = "Example"
        # Create dataclass object. This object allows communication between this class and other classes that
        # may be called to assist analysis.
        self.dataset = self.ExampleDataClass(self)
        # Add widgets to the Frame
        tk.Label(self, text="Hello World!", anchor="w",width=20).grid(column=0, row=0, padx=10, pady=(10,0))
        # Add auxillary tabs
        controller.addtab(exampleauxtab, self.dataset) #add any additonal args/kwargs if needed

class MSImageProcessGUI(tk.Frame):
    # Processing of image files into raw, unprocessed traces
    @dataclass
    class MSImageDataClass():
        primary: ... #The analysis class.
        _: dataclasses.KW_ONLY
        topdirectory: ... = None #topdirectory of the given dataset, as a tk.StringVar()
        imagedirectorylist: ... = None #list of all of the run directories
        tracesbydirthenreg: ... = None #output of each of the traces
        regionnames: ... = None #names of each region
        regioncoords: ... = None #bounding coordinates
        regionmasks: ... = None #generated masks

    def __init__(self, container, controller):
        super().__init__(container)
        self.controller = controller
        self.title = 'Image Dataset Processing'
        self.dataset = self.MSImageDataClass(self)

        # Setting up the widgets on the window
        tk.Label(self, text="Dataset Folder Path", anchor="w",width=20).grid(column=0, row=0, padx=10, pady=(10,0))
        tk.Label(self, text="Start Date", anchor="w",width=20).grid(column=0, row=3, padx=10, pady=(10,0))
        tk.Label(self, text="End Date", anchor="w",width=20).grid(column=1, row=3, padx=10, pady=(10,0))
        tk.Label(self, text="Animal Basename", anchor="w",width=20).grid(column=0, row=6, padx=10, pady=(10,0))
        tk.Label(self, text="Start #", anchor="w",width=20).grid(column=1, row=6, padx=10, pady=(10,0))
        tk.Label(self, text="End #", anchor="w",width=20).grid(column=2, row=6, padx=10, pady=(10,0))
        self.dataset.topdirectory = tk.StringVar()
        self.date_start = tk.StringVar()
        self.date_end = tk.StringVar()
        self.ani_prefix = tk.StringVar()
        self.ani_start = tk.StringVar()
        self.ani_end = tk.StringVar()
        # Text Entry Fields
        tk.Entry(self, width=50, textvariable=self.dataset.topdirectory).grid(column=0, row=1, columnspan=2, padx=(10,0), pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.date_start).grid(column=0, row=4, padx=10, pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.date_end).grid(column=1, row=4, padx=10, pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.ani_prefix).grid(column=0, row=7, padx=10, pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.ani_start).grid(column=1, row=7, padx=10, pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.ani_end).grid(column=2, row=7, padx=10, pady=(0,10), sticky="w")
        # Default values for text entry fields
        self.dataset.topdirectory.set("Use button to right")
        self.date_start.set("05-17-23")
        self.date_end.set("05-17-23")
        self.ani_prefix.set("MRKPFCREV")
        self.ani_start.set("1")
        self.ani_end.set("15")
        #Canvas to organize some buttons
        buttoncanvas = tk.Canvas(self)
        buttoncanvas.grid(column=2,row=9,padx=10,pady=0,sticky="se")
        # Buttons
        tk.Button(self, text="Open...", command=self.fileselect).grid(column=2,row=1,padx=10, pady=(0,10), sticky="w")
        self.loadbutton = tk.Button(buttoncanvas, text="Load Runs", command=self.loadruns)
        self.regselbutton = tk.Button(buttoncanvas, text="Select Regions", command= self.regselect)
        self.processbutton = tk.Button(buttoncanvas, text="PROCESS!!!!!", command = self.imageprocess)
        tk.Button(buttoncanvas, text="EXIT", command=self.controller.root.destroy).grid(column=0, row=3,padx=2, pady=(0,10), sticky="se")
        # Positioning for important buttons
        self.loadbutton.grid(column=0, row=0,padx=0, pady=(0,10), sticky="se")
        self.regselbutton.grid(column=0, row=1,padx=0, pady=(0,10), sticky="se")
        self.processbutton.grid(column=0, row=2,padx=0, pady=(0,10), sticky="se")
        self.regselbutton["state"] = "disabled"
        self.processbutton["state"] = "disabled"
        #self.processbutton["state"] = "disabled"
        # Creating the Treeview widget for displaying the files
        runcanvas = tk.Canvas(self)
        runcanvas.grid(column=0,row=8,padx=10,pady=10,sticky="nw", columnspan=3, rowspan=2)
        self.filetree = ttk.Treeview(runcanvas, height=10, columns=('date','run'),selectmode='browse')
        self.filetree.grid(row=0,column=0)
        self.filetree.column("#0", width=20)
        self.filetree.column("date", width=130)
        self.filetree.column("run", width=130)
        self.filetree.heading("date", text="Date", anchor="w")
        self.filetree.heading("run", text="Run", anchor="w")
        rtreescroll = ttk.Scrollbar(runcanvas, orient="vertical", command=self.filetree.yview)
        rtreescroll.grid(row=0,column=1,sticky="ns")
        self.filetree.config(yscrollcommand=rtreescroll.set)
        self.filetree.bind('<Motion>', 'break')
        # set up our helper tab for image parameters
        self.imgprefix = tk.StringVar()
        self.imgprefix.set("mrk_pfc")
        self.imgpertrial = tk.StringVar()
        prmvar = [self.imgprefix, self.imgpertrial]
        prmlabels = ["Image Prefix", "Images per Trial"]
        self.roi = []
        for i in range(5):
            self.roi.append(tk.StringVar())
            prmvar.append(self.roi[i])
            prmlabels.append("ROI "+str(i+1)+" Name")
        controller.addtab(ParameterWindow, self.dataset, title = "Image Parameters", parameterlabels = prmlabels, parametervars = prmvar)
        self.roi[0].set("PTA")
    
    def fileselect(self):
        self.dataset.topdirectory.set(filedialog.askdirectory())

    def loadruns(self):
        tdir = self.dataset.topdirectory.get()
        datedirlist = []
        rundirlist = []
        if datetonum(self.date_start.get()) and datetonum(self.date_end.get()):
            for i in range(datetonum(self.date_start.get()),datetonum(self.date_end.get())+1):
                
                targetpath = tdir+"/"+numtodate(i)
                if os.path.exists(targetpath):
                    datedirlist.append(targetpath)
        else:
            self.date_start.set("ERROR")
            self.date_end.set("ERROR")
            return
        animallist=[]
        
        for i in range(int(self.ani_start.get()), int(self.ani_end.get())+1):
            animallist.append("/" + self.ani_prefix.get()+" "+str(i)+" ")
        #Clear the treeviewer widget
        for i in self.filetree.get_children(): self.filetree.delete(i)

        for i in datedirlist:
            for k in animallist:
                for j in range(len(os.listdir(i))): #this is here to set the theoretical maximum number of runs. Its better than what the old photom did because it can handle an arbitrary number of runs, though its kind of messy.
                    targetpath = i + k + "Run " + str(j+1)
                    if os.path.exists(targetpath): 
                        rundirlist.append(targetpath)
                        self.filetree.insert('', 'end', text = str(j), values=(i[-8:],(k+"Run "+str(j+1))[1:len(k+"Run "+str(j+1))]))
        self.dataset.imagedirectorylist = rundirlist
        if len(datedirlist)>0: self.regselbutton["state"] = "normal"
        else: self.regselbutton["state"] = "disabled"

    def regselect(self):
        regions = []
        for i in range(len(self.roi)):
            if self.roi[i].get() != "": regions.append(self.roi[i].get())
        img  = Image.open(self.dataset.imagedirectorylist[0]+"/"+self.imgprefix.get()+"0_2.tif")
        #Better than passing the entire class I think. Gets executed when imgregionselectionwindow quits.
        def buttonupdate(): self.processbutton["state"] = "normal" 
        imgregionselectionwindow(tk.Toplevel(),self.dataset, img, regions,buttonupdate)

    def imageprocess(self):
        def threadedfunc(container,dataset):
            #first we need to create a mask for each region.
            dataset.regionmasks = []
            for i in range(len(dataset.regionnames)):
                cx = sum(dataset.regioncoords[i][0:3:2])/2
                cy = sum(dataset.regioncoords[i][1:4:2])/2
                rad = dataset.regioncoords[i][2] - self.dataset.regioncoords[i][0]
                dataset.regionmasks.append(npy_circlemask(424,424,cx,cy,rad))
            #now that we have the masks for each region we can process each of the directories in turn
            dataset.tracesbydirthenreg = []
            for i in dataset.imagedirectorylist:
                traces = photomimageprocess(i,self.imgprefix.get(),self.dataset.regionmasks)
                dataset.tracesbydirthenreg.append(traces)
                #need to add saving the output locally here
            container.processbutton["state"] = "normal"
        procthread = threading.Thread(target=threadedfunc, args=(self, self.dataset),daemon=True)
        self.processbutton["state"] = "disabled"
        procthread.start()



# -----------------------------------------Auxillary Tabs/Popups------------------------------------
# Generally in this application, if a frame is expected to persist and be created at startup, it should be a tab
# If it is going to open/close, it should be a popup (toplevel). Toplevel windows are handled within the Primary
# Analysis frame that instantiates it while aux tabs are created using controller.addtab inside __init__ method 
# of the corresponding Primary Analysis frame

class exampleauxtab(tk.Frame):
    def __init__(self, container, dataset, **kwargs):
        super().__init__(container)
        # Get the shared dataset and save the primary.
        self.dataset = dataset
        self.primary = dataset.primary
        # Use the kwargs provided
        self.example = kwargs.get("key","default value")

class imgregionselectionwindow(tk.Frame):
    def __init__(self, container, dataset, img, regions, callwhenquit):
        super().__init__(container)
        #dataset setup
        self.dataset = dataset
        self.primary = dataset.primary
        self.container = container
        self.regions = ["Correction Fiber","Background Fiber"] + regions
        self.img = img
        self.callwhenquit = callwhenquit
        im_disp = ImageTk.PhotoImage(img)
        container.geometry("420x520")
        container.wm_attributes('-transparentcolor','green')
        container.resizable(0,0)
        self.selectioncanvas = tk.Canvas(container,height=420,width=420)
        self.selectioncanvas.place(x=0,y=0)
        self.selectioncanvas.create_image(0,0,image=im_disp,anchor="nw")
        self.selectoval = self.selectioncanvas.create_oval(0,0,100,100,activewidth = 5, activeoutline='red',activefill='pink',width=4,outline='pink')
        tk.Label(container, text="Drag and drop the red circle to cover the selected region").place(x = 10, y = 430)
        self.currentregion = tk.StringVar()
        self.currentregion.set("Currently selecting "+self.regions[0])
        tk.Label(container,textvariable=self.currentregion).place(x=10, y = 470)
        tk.Button(container,text="CONFIRM REGION",command=self.confirmreg).place(x = 270, y = 470)
        self.selectioncanvas.bind("<B1-Motion>", self.drag)
        self.activeregion = 0
        self.regshapelist = [] # List that will contain all the circle selectors marking the image
        container.mainloop()


    def confirmreg(self):
        #confirm the location of the circle selector
        x, y, dx, dy = self.selectioncanvas.coords(self.selectoval)
        name = self.selectioncanvas.create_oval(x, y, dx, dy, outline='blue', width=3)
        self.regshapelist.append(name)
        self.activeregion += 1
        if self.activeregion >= len(self.regions):
            self.dataset.regionnames = self.regions
            self.dataset.regioncoords = []
            for i in self.regshapelist:
                self.dataset.regioncoords.append(self.selectioncanvas.coords(i))
                self.callwhenquit()
            self.container.destroy()
        else:
            self.currentregion.set("Currently selecting "+self.regions[self.activeregion])


    def drag(self,event):
        #cirselector.place(x=event.x_reggui, y=event.y_reggui,anchor="center")
        self.selectioncanvas.moveto(self.selectoval,event.x-50,event.y-50)
        
class ParameterWindow(tk.Frame):
    def __init__(self, container, dataset, **kwargs):
        super().__init__(container)
        # Get the shared dataset and save the primary.
        self.dataset = dataset
        self.primary = dataset.primary
        # Use the kwargs provided
        self.paramlabels = kwargs.get("parameterlabels",["Example:"])
        self.paramvars = kwargs.get("parametervars",["Example"])
        self.title = kwargs.get("title","Custom Parameters")
        # Create the parameters entry windows etc etc.
        self.update()
    def update(self):
        # destroy all widgets currently on the frame.
        for widget in self.winfo_children():
            widget.destroy()
        # create all widgets on frame
        for i in range(min(len(self.paramlabels),len(self.paramvars))):
            if isinstance(self.paramlabels[i],list):
                for j in range(len(self.paramlabels[i])):
                    tk.Label(self, text = self.paramlabels[i][j], anchor="w",width = 20).grid(column=j*2, row=i,padx=10,pady=10,sticky="e")
            else:
                tk.Label(self, text = self.paramlabels[i], anchor="w",width=20).grid(column=0, row=i, padx=10, pady=10,sticky="e")
            if isinstance(self.paramvars[i],list):
                for j in range(len(self.paramvars[i])):
                    tk.Entry(self, width=18, textvariable=self.paramvars[i][j]).grid(column=j*2+1,row=i,padx=10,pady=10,sticky="w")
            else:
                tk.Entry(self, width=18, textvariable=self.paramvars[i]).grid(column=1,row=i,padx=10,pady=10,sticky="w")

# -----------------------------------------Analysis Functions/Classes------------------------------------
# If its not hyper specific to a class, put it here. Makes it easier to reuse.
def datetonum(date: str):
    assert isinstance(date, str), 'datetonum accepts strings only'
    if len(date) != 8:
        return False
    if date[2] != "-" or date[5] != "-":
        return False
    mdyextract = [date[0:2], date[3:5], date[6:8]]
    if all(x.isdigit() for x in mdyextract):
        mdyextract = [int(i) for i in mdyextract]
        return ((mdyextract[1]) + (mdyextract[0]*32) + (mdyextract[2]*384))
    else:
        return False
    
def numtodate(numcode: int):
    assert isinstance(numcode, int), 'numtodate accepts integers only'
    y, d = divmod(numcode,384)
    m, d = divmod(d,32)
    return (str(m).zfill(2)+"-"+str(d).zfill(2)+"-"+str(y).zfill(2))

# Creates a numpy mask array with a circle region. Is used for masking image files to pull only the selected fiber region.
def npy_circlemask(sizex,sizey,circlex,circley,radius):
    mask = np.empty((sizex,sizey))
    for x in range(sizex):
        for y in range(sizey):
            if ((x-circlex)**2 + (y-circley)**2)**(0.5) <= radius:
                mask[x,y] = True
            else:
                mask[x,y] = False
    return mask

def photomimageprocess(directory,imgprefix,masks):
    # within a given directory, analyze all images within that directory.
    imgls = [f for f in os.listdir(directory) if f.endswith('.tif')]
    imgls = [f for f in imgls if imgprefix in f]
    maximgnum = len(imgls) # This is to set the theoretical maximum number of images that will be processed
    # Iterating up to maximgnum has a downside, if the file names "skip" (1,2,4,5) then the last image will not be analyzed.
    # In the above example, 1,2,4 would be analyzed and 5 will be left out. I would like to alter this behavior in the future
    # to be better at catching files that may not match this.
    #create numpy arrays for each mask
    traces = []
    for j in masks:
        traces.append(np.zeros((maximgnum)))
    for i in range(maximgnum):
        imdir = directory+"\\"+imgprefix +"0_"+ str(i+1) + ".tif" # Currently, this function doesn't catch images with "1_"
        if os.path.exists(imdir):
            imdat = loadimg(imdir)
            print(imdir)
            for j in range(len(masks)):
                np.put(traces[j],i,np.ma.masked_array(imdat, masks[j]).mean())
    return traces

def loadimg(path):
    img = Image.open(path)
    img.load()
    imgdata = np.asarray(img,dtype="uint32")
    return imgdata



# -----------------------------------------Initiate the Controller------------------------------------
if __name__=="__main__":
    app = Main()
    app.run()

