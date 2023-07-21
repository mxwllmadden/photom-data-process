import tkinter as tk, os, dataclasses, threading, sys
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from dataclasses import dataclass
from MSPhotomAnalysis import *
from scipy.io import savemat

# The GUI elements have been seperated out into this file to avoid clutter/allow me to focus on the actual
# analysis of the data. Try to keep functions within each of these classes as minimal as possible. All data
# analysis should be front and center within the MSPhotomApp.py file

# -----------------------------------------Application Main------------------------------------
class Main():
    #This class sets up the primary GUI window.
    def __init__(self,root) -> None:
        self.root = root #root is the tk.Tk() window
        # Set window properties
        self.root.title("Multisite Photometry Data Processing/Analysis App")
        self.root.geometry("500x570")
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

# -----------------------------------------Primary Analysis Frames------------------------------------
class exampleprimaryanalysis(tk.Frame):
    # This class is provided as a template to add additional analysis windows to the application
    # I use a nested dataclass to facilitate passing of information between different classes focused on
    # the same analysis.
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
    # Processing of image files into traces

    # This dataclass is meant to store just about every peice of data relevant to the analysis. At the 
    # end of processing, we can save the whole thing.
    @dataclass
    class MSImageDataClass():
        primary: ... #The analysis class.
        _: dataclasses.KW_ONLY
        topdirectory: ... = None #topdirectory of the given dataset, as a tk.StringVar()
        imagedirectorylist: ... = None #list of all of the run directories
        tracesbydirthenreg: ... = None #output of each of the traces after all the reshaping and processing.
        regionnames: ... = None #names of each region
        regioncoords: ... = None #bounding coordinates
        regionmasks: ... = None #generated masks
        imgs_per_trial: ... = None #number of images per trial within a SINGLE channel.
        channels: int = 2

    def __init__(self, container, controller):
        super().__init__(container)
        self.controller = controller
        self.title = 'Image Processing'
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
        # Progress Bars For Processing at the bottom of the widget
        self.longprog = ttk.Progressbar(self, orient="horizontal",length=480,mode="determinate")
        self.longprog["value"] = 0
        self.longprog.grid(column=0,row=10,columnspan=5)
        self.runprog = ttk.Progressbar(self, orient="horizontal",length=480,mode="determinate")
        self.runprog["value"] = 0
        self.runprog.grid(column=0,row=12,columnspan=5)
        self.longprogstat = tk.StringVar()
        self.longprogstat.set("Run Processing Progress...")
        tk.Label(self, width=18, textvariable=self.longprogstat).grid(column=0, row=11, padx=10, pady=(0,10), columnspan=5, sticky="nsew")
        self.shortprogstat = tk.StringVar()
        self.shortprogstat.set("Image Processing Progress...")
        tk.Label(self, width=18, textvariable=self.shortprogstat).grid(column=0, row=13, padx=10, pady=0, columnspan=5, sticky="nsew")
        self.speedout = tk.StringVar()
        self.speedout.set("...")
        tk.Label(self,width=18, textvariable=self.speedout, anchor="w").grid(column=0,row=14,padx = 10,pady=0, sticky="w")
        # set up our helper tab for image parameters
        self.imgprefix = tk.StringVar()
        self.imgprefix.set("mrk_pfc")
        self.imgpertrial = tk.StringVar()
        self.imgpertrial.set("130")
        self.channels = tk.StringVar()
        self.channels.set("2")
        prmvar = [self.imgprefix, self.imgpertrial,self.channels]
        prmlabels = ["Image Prefix", "Images per Trial/Channel","# of Interpolated Channels"]
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
        imgpath = self.dataset.imagedirectorylist[0]+"//"+self.imgprefix.get()+"0_2.tif"
        if os.path.exists(imgpath):
            regions = []
            for i in range(len(self.roi)):
                if self.roi[i].get() != "": regions.append(self.roi[i].get())
            img  = Image.open(imgpath)
            #Better than passing this object I think. Gets executed when imgregionselectionwindow quits.
            def buttonupdate(): self.processbutton["state"] = "normal" 
            imgregionselectionwindow(tk.Toplevel(),self.dataset, img, regions,buttonupdate)
        else:
            popout(tk.Toplevel(),"ERROR","IMAGE NOT FOUND: CHECK IMAGE PREFIX")

    def imageprocess(self):
        # This function is called in a seperate thread when you hit "Process" for the image processing window.
        # Placing it in a second thread allows processing to happen without disrupting the GUI
        # At a future time it may be worthwhile to see if this could be sped up via multiprocessing.
        def photomthreadedfunc(container,dataset, imgpertrial, imgprefix, channelnum): 
            # STEP 1: Generate all the mask arrays for each region from the dataset info.
            # Each mask is a boolean numpy array with the selected region as "True" and all else as "False"
            dataset.regionmasks = []
            dataset.channels = channelnum
            for i in range(len(dataset.regionnames)):
                cx = sum(dataset.regioncoords[i][0:3:2])/2
                cy = sum(dataset.regioncoords[i][1:4:2])/2
                rad = (dataset.regioncoords[i][2] - dataset.regioncoords[i][0])/2
                dataset.regionmasks.append(npy_circlemask(424,424,cy,cx,rad))
            #STEP 2: Iterate through every directory that contains images
            dataset.tracesbydirthenreg = []
            num_runs = len(dataset.imagedirectorylist)
            currun = 0
            self.longprog["value"] = (currun/num_runs)*100
            for i in dataset.imagedirectorylist:
                self.longprogstat.set("Processing "+i.split("/")[-1])
                print("BEGIN: "+i.split("/")[-1])
                #STEP 3: use the masks we generated to pull the mean value for each region in each image
                print("Extracting pixelvalues...")
                traces = photomimageprocess(i,imgprefix,dataset.regionmasks,waitbar = self.runprog, textvar = self.shortprogstat,speedvar = self.speedout)
                #STEP 4: remove the mean of the background trace from all other traces
                print("Subtracting background fiber value...")
                traces = subtractbackgroundsignal(traces)
                #STEP 5: split each trace by channel
                print("Splitting traces by channel...")
                traces = splittraces(traces,dataset.channels)
                #STEP 6: reshape the traces according to the number of images per trial
                print("Splitting trials sequentially...")
                traces = reshapetraces(traces,imgpertrial)
                #STEP 7: add the resultant traces to the dataset
                print("Saving to dataset...")
                dataset.tracesbydirthenreg.append(traces)
                #STEP 8: Also save the traces in the directory of the images.
                print("Saving to file...")
                tracedict = {}
                for j in range(len(traces)):
                    signal, channel = divmod(j, dataset.channels)
                    if signal == 0:
                        key = "corrsig_ch"+str(channel)
                    else:
                        key = "sig"+str(signal)+"_ch"+str(channel)
                    #STEP 8.5: Swap the data axes so that each TRIAL is COLUMN and TIME is ROW
                    #This is done for compatability with legacy regression analysis code.
                    tracedict[key] = np.swapaxes(traces[j],0,1)
                for j in range(2,len(dataset.regionnames)):
                    tracedict[("sig"+str(j-1)+"_str")] = dataset.regionnames[j]
                filename = i + "/" + i.split("/")[-1]+ ".mat"
                savemat(filename,tracedict)
                print("SAVED: "+ filename)
                filename = os.path.dirname(sys.argv[0]) + "\\" + i.split("/")[-1]+ ".mat"
                savemat(filename,tracedict)
                print("SAVED: "+filename)
                currun += 1
                self.longprog["value"] = (currun/num_runs)*100
            container.processbutton["state"] = "normal"
            self.regselbutton["state"] = "normal"
            self.loadbutton["state"] = "normal"
            print("Processing completed!")
            # now we need to save a local matlab file containing all the traces.
        
        # This section initiates the threaded function.
        # It is good practice to specify all inputs to the threaded funtion as ARGUMENTS rather than accessing them from
        # within the function. Otherwise if the user changes a parameter during processing it may cause unexpected behavior.
        procthread = threading.Thread(target=photomthreadedfunc, args=(self, self.dataset, int(self.imgpertrial.get()), self.imgprefix.get(), int(self.channels.get())), daemon=True)
        self.processbutton["state"] = "disabled"
        self.regselbutton["state"] = "disabled"
        self.loadbutton["state"] = "disabled"
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
        self.regions = ["Background Fiber","Correction Fiber"] + regions
        self.img = img
        self.callwhenquit = callwhenquit
        im_disp = ImageTk.PhotoImage(img)
        container.geometry("420x520")
        container.resizable(0,0)
        self.selectioncanvas = tk.Canvas(container,height=424,width=424)
        self.selectioncanvas.place(x=0,y=0)
        self.selectioncanvas.create_image(0,0,image=im_disp,anchor="nw")
        self.selectoval = self.selectioncanvas.create_oval(0,0,100,100,width=4,outline='red')
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

class popout(tk.Frame):
    def __init__(self,container,title,msg):
        super().__init__(container)
        self.container = container
        container.geometry("250x70")
        container.title(title)
        container.resizable(0,0)
        tk.Label(self,text=msg,anchor="center").pack(pady = 4, padx = 4)
        tk.Button(self,text="OK",height=10,width=20,command=self.quit).pack(pady = 4, padx = 4)
        self.pack(expand=1, fill="both")
        container.mainloop()
    def quit(self):
        self.container.destroy()

# -----------------------------------------Initiate Main------------------------------------
if __name__=="__main__":
    root = tk.Tk()
    app = Main(root)
    root.mainloop()