import tkinter as tk
from tkinter import ttk
from MSPhotomGUI import * 

# -----------------------------------------Application Main------------------------------------
class Main():
    #This class sets up the primary GUI window.
    def __init__(self) -> None:
        self.root = tk.Tk() #root is the tk.Tk() window
        # Set window properties
        self.root.title("Multisite Photometry Data Processing/Analysis App")
        self.root.geometry("500x550")
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

# -----------------------------------------Initiate Main------------------------------------
if __name__=="__main__":
    app = Main()
    app.run()

