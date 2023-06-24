import tkinter as tk, os, numpy as np, dataclasses
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from dataclasses import dataclass, field

# -----------------------------------------Application Main------------------------------------
class Main():
    def __init__(self) -> None:
        # Create application-wide data object
        self.root = tk.Tk() #root is the tk.Tk() window
        self.controller = self #controller is the current instance of this controller class
        # Set window properties
        self.root.title("Multisite Photometry Data Processing/Analysis App")
        self.root.geometry("500x500")
        self.root.resizable(0,0)
        # Create notebook for application tabs, add them in reverse order to appearance
        # Each primary analysis window should receive self.tabcontainer and the app object.
        self.tabcontainer = ttk.Notebook(self.root)
        self.tabs = []
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
        controller.addtab(exampleauxtab, self.dataset) #add any kwargs if needed

class MSImageProcessGUI(tk.Frame):
    # Processing of image files into raw, unprocessed traces
    @dataclass
    class MSImageDataClass():
        primary: ...
        _: dataclasses.KW_ONLY
        regionnames: ... = None
        regioncoords: ... = None

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
        self.dirpath = tk.StringVar()
        self.date_start = tk.StringVar()
        self.date_end = tk.StringVar()
        self.ani_prefix = tk.StringVar()
        self.ani_start = tk.StringVar()
        self.ani_end = tk.StringVar()
        # Text Entry Fields
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
        tk.Button(buttoncanvas, text="EXIT", command=self.controller.root.destroy).grid(column=0, row=3,padx=2, pady=(0,10), sticky="se")
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

        controller.addtab(ParameterWindow, self.dataset, title = "test")
    
    def fileselect(self):
        pass

    def loadruns(self):
        pass

    def regselect(self):
        pass

    def imageprocess(self):
        pass


# -----------------------------------------Auxillary Tabs/Popups------------------------------------
# Generally in this application, if a frame is expected to persist and be created at startup, it should be a tab
# If it is going to open/close, it should be a popup (toplevel). Toplevel windows are handled within the Primary
# Analysis frames while aux tabs are created using controller.addtab in the init method of the Primary Analysis frame

class exampleauxtab(tk.Frame):
    def __init__(self, container, dataset, **kwargs):
        super().__init__(container)
        # Get the shared dataset and save the primary.
        self.dataset = dataset
        self.primary = dataset.primary
        # Use the kwargs provided
        self.example = kwargs.get("key","default value")
        
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
def isvaliddate(date: str):
    assert isinstance(date, str), 'isvaliddate accepts strings only'
    pass


# -----------------------------------------Initiate the Controller------------------------------------
if __name__=="__main__":
    app = Main()
    app.run()