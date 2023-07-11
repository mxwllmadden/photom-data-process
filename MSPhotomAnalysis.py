import os, numpy as np, scipy
from PIL import Image


# -----------------------------------------Analysis Functions/Classes------------------------------------
# Actual functions for data analysis. These are front and center as they are the MOST IMPORTANT part of the
# application. Make sure to write comments saying when/how/if the GUI calls a function.

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
    mask = np.empty((sizex,sizey), dtype="bool_")
    for x in range(sizex):
        for y in range(sizey):
            if ((x-circlex)**2 + (y-circley)**2)**(0.5) <= radius:
                mask[x,y] = 1
            else:
                mask[x,y] = 0
    return mask

def photomimageprocess(directory,imgprefix,masks,**kwargs):
    waitbar = kwargs.get("waitbar", None)
    txtout = kwargs.get("textvar", None)
    # within a given directory, analyze all images within that directory.
    imgls = [f for f in os.listdir(directory) if f.endswith('.tif')]
    imgls = [f for f in imgls if imgprefix in f]
    maximgnum = len(imgls) # This is to set the theoretical maximum number of images that will be processed
    # Iterating up to maximgnum has a downside, if the file names "skip" (1,2,4,5) then the last image will not be analyzed.
    # In the above example, 1,2,4 would be analyzed and 5 will be left out. I would like to alter this behavior in the future
    # to be better at catching files.
    traces = [] 
    for j in masks: #create numpy arrays for each mask
        traces.append(np.zeros((maximgnum)))
    for i in range(maximgnum): #iterate through all the imagefiles
        imdir = directory+"/"+imgprefix +"0_"+ str(i+1) + ".tif" # Currently, this function doesn't catch images with "1_"
        if os.path.exists(imdir):
            imdat = loadimg(imdir)
            if waitbar != None: waitbar["value"] = (i/maximgnum)*100
            if txtout != None: txtout.set(imdir)
            for j in range(len(masks)): #iterate through each mask and apply each mask and get average value.
                avrgsig = (np.where(masks[j], imdat, 0).sum())/masks[j].sum()
                np.put(traces[j],i,avrgsig)
    return traces

def subtractbackgroundsignal(traces): #accepts a list of 1 dimensional numpy arrays
    #by convention, the first array in the list is the "Background" signal.
    subtrace = []
    for i in range(1,len(traces)):
        subtrace.append(np.subtract(traces[i],traces[0]))
    return subtrace

def splittraces(traces,channels):
    splittraces = []
    for i in range(len(traces)):
        for j in range(channels): splittraces.append(traces[i][j::channels])
    return splittraces

def reshapetraces(traces,imgptrial):
    reshapedtraces = []
    for i in range(len(traces)):
        size = np.prod(traces[i].shape)
        trials, remainder = divmod(size,imgptrial)
        x = traces[i][0:(trials*imgptrial)]
        reshapedtraces.append(np.reshape(x,(trials,imgptrial)))
    return reshapedtraces


def loadimg(path):
    img = Image.open(path)
    img.load()
    imgdata = np.asarray(img,dtype="int32")
    return imgdata