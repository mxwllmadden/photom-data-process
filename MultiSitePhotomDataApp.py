import tkinter as tk, os, numpy as np
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

class Controller:
    def __init__(self,root) -> None:
        self.root = root
        root.title("Multisite Photometry Data Processing App")
        root.geometry("500x500")
        root.resizable(0,0)

        # Instantiate each Tab
        self.notebook = ttk.Notebook(root)
        self.tab1 = MSImageGUI(self.notebook,self)
        self.tab2 = MSIbackparam(self.notebook,self)
        self.notebook.add(self.tab1, text = self.tab1.title)
        self.notebook.add(self.tab2, text = self.tab2.title)
        self.notebook.pack(expand=1, fill="both")
    def startregselect(self, imagedirectory, regions):
        self.popout1 = PopoutRegionselect(self, imagedirectory, regions)
        self.popout1.mainloop
    
    def destroyregselect(self, regions, fibercoords):
        self.popout1.destroy()
        del self.popout1
        self.photomregions = regions
        self.fibercoords = fibercoords

class PopoutRegionselect(tk.Toplevel):
    def __init__(self,parent,imagepath,variables) -> None:
        super().__init__(parent)
        self.geometry(imgsizx.get()+"x"+str(int(imgsizy.get())+100))
        self.wm_attributes('-transparentcolor','green')
        self.resizable(0,0)

class MSImageGUI(tk.Frame):
    def __init__(self,notebook,parent) -> None:
        super().__init__(notebook)
        self.parent = parent
        self.title = 'Raw Dataset Processing'
        # Create important variables
        self.imagedirlist = [] #The list of directories identified for analysis
        # Labels
        tk.Label(self, text="Dataset Folder Path", anchor="w",width=20).grid(column=0, row=0, padx=10, pady=(10,0))
        tk.Label(self, text="Start Date", anchor="w",width=20).grid(column=0, row=3, padx=10, pady=(10,0))
        tk.Label(self, text="End Date", anchor="w",width=20).grid(column=1, row=3, padx=10, pady=(10,0))
        tk.Label(self, text="Animal Basename", anchor="w",width=20).grid(column=0, row=6, padx=10, pady=(10,0))
        tk.Label(self, text="Start #", anchor="w",width=20).grid(column=1, row=6, padx=10, pady=(10,0))
        tk.Label(self, text="End #", anchor="w",width=20).grid(column=2, row=6, padx=10, pady=(10,0))
        # Text entry fields
        self.dirpath = tk.StringVar()
        self.date_start = tk.StringVar()
        self.date_end = tk.StringVar()
        self.ani_prefix = tk.StringVar()
        self.ani_start = tk.StringVar()
        self.ani_end = tk.StringVar()
        tk.Entry(self, width=50, textvariable=self.dirpath).grid(column=0, row=1, columnspan=2, padx=(10,0), pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.date_start).grid(column=0, row=4, padx=10, pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.date_end).grid(column=1, row=4, padx=10, pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.ani_prefix).grid(column=0, row=7, padx=10, pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.ani_start).grid(column=1, row=7, padx=10, pady=(0,10), sticky="w")
        tk.Entry(self, width=18, textvariable=self.ani_end).grid(column=2, row=7, padx=10, pady=(0,10), sticky="w")
        # Default values for text entry fields
        self.dirpath.set("Use button to right")
        self.date_start.set("05-17-2023")
        self.date_end.set("05-17-2023")
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
        tk.Button(buttoncanvas, text="EXIT", command=parent.root.destroy).grid(column=0, row=3,padx=2, pady=(0,10), sticky="se")
        # Positioning for important buttons
        self.loadbutton.grid(column=0, row=0,padx=0, pady=(0,10), sticky="se")
        self.regselbutton.grid(column=0, row=1,padx=0, pady=(0,10), sticky="se")
        self.processbutton.grid(column=0, row=2,padx=0, pady=(0,10), sticky="se")
        self.regselbutton["state"] = "disabled"
        self.processbutton["state"] = "disabled"
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

    def fileselect(self):
        self.dirpath.set(filedialog.askdirectory())

    def loadruns(self):
            #This function searches the listed directory for a list of folders matching the parameters described through the entry fields.
            self.imagedirlist = []
            if not (self.ani_start.get().isdigit() and self.ani_end.get().isdigit()):
                self.ani_start.set("ERROR")
                self.ani_end.set("ERROR")
                return
            if os.path.exists(self.dirpath.get()):
                dirpath_dates = os.listdir(self.dirpath.get()) #get the names of all the files/folders in the target directory
                dirpath_dates = [f for f in dirpath_dates if not os.path.isfile(self.dirpath.get()+'/'+f)] #filter so that only directories (not files) appear
                #next we generate a list of possible dates from the start and end dates provided by the user.
                #extract the month day and year using string indexes
                if len(self.date_end.get()) == 10 and len(self.date_start.get()) == 10 and \
                    self.date_start.get()[2] == self.date_start.get()[5] == self.date_end.get()[2] == self.date_end.get()[5] == "-": #Checking to make sure (broadly) that the date format is correct
                    d_s_extract = [self.date_start.get()[0:2], self.date_start.get()[3:5], self.date_start.get()[6:10]]
                    d_e_extract = [self.date_end.get()[0:2], self.date_end.get()[3:5], self.date_end.get()[6:10]]
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
                            targetpath = self.dirpath.get()+"/"+str(m).zfill(2)+"-"+str(d).zfill(2)+"-"+str(y).zfill(2) #contruct the path to check for
                            if os.path.exists(targetpath):
                                #add the path to the targetpath list
                                dateslist.append(targetpath)
                    else:
                        self.date_end.set("ERROR: format")
                        self.date_start.set("ERROR: format")
                        return
                else:
                    self.date_start.set("ERROR: format")
                    self.date_end.set("ERROR: format")
                    return
            else:
                self.dirpath.set("ERROR: Path does not exist")
                return
            #Now that we have a list of valid paths for each date of recording, each directory must be searched for folders matching the specificied animal prefix.
            #generating animal names
            animallist=[]
            for i in range(int(self.ani_start.get()), int(self.ani_end.get())+1):
                animallist.append("/" + self.ani_prefix.get()+" "+str(i)+" ")
            
            #Clear the treeviewer widget
            for i in self.filetree.get_children(): self.filetree.delete(i)
            for i in dateslist:
                for k in animallist:
                    for j in range(len(os.listdir(i))): #this is here to set the theoretical maximum number of runs. Its better than what the old photom did because it can handle an arbitrary number of runs, though its kind of messy.
                        targetpath = i + k + "Run " + str(j+1)
                        if os.path.exists(targetpath): 
                            self.imagedirlist.append(targetpath)
                            self.filetree.insert('', 'end', text = str(j), values=(i[-10:],(k+"Run "+str(j+1))[1:len(k+"Run "+str(j+1))]))
            if len(self.imagedirlist)>0: self.regselbutton["state"] = "normal"
            else: self.regselbutton["state"] = "disabled"

    def regselect(self):
        self.parent.startpopout(self)

    def imageprocess(self):
        pass

class MSIbackparam(tk.Frame):
    def __init__(self,notebook,parent) -> None:
        super().__init__(notebook)
        self.parent = parent
        self.title = 'Background Parameters'


if __name__=="__main__":
    root = tk.Tk()
    Controller(root)
    root.mainloop()
