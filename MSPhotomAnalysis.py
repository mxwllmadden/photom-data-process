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

# This function is called in a second thread when you hit "Process" for the image processing window.
def photomthreadedfunc(container,dataset): 
            # STEP 1: Generate all the mask arrays for each region from the dataset info.
            # Each mask is a boolean numpy array with the selected region as "True" and all else as "False"
            dataset.regionmasks = []
            for i in range(len(dataset.regionnames)):
                cx = sum(dataset.regioncoords[i][0:3:2])/2
                cy = sum(dataset.regioncoords[i][1:4:2])/2
                rad = dataset.regioncoords[i][2] - dataset.regioncoords[i][0]
                dataset.regionmasks.append(npy_circlemask(424,424,cx,cy,rad))
            #STEP 2: Iterate through every directory that contains images
            dataset.tracesbydirthenreg = []
            for i in dataset.imagedirectorylist:
                #STEP 3: use the masks we generated to pull the mean value for each region in each image
                traces = photomimageprocess(i,container.imgprefix.get(),dataset.regionmasks)
                #STEP 4: remove the mean of the background trace from all other traces
                traces = subtractbackgroundsignal(traces)
                #STEP 5: split each trace by channel
                traces = splittraces(traces)
                #STEP 6: add the resultant traces to the dataset
                dataset.tracesbydirthenreg.append(traces)
                #STEP 7: Also save the traces in the directory of the images.
                filename = i + "\\" + i.split("\\")[-1]
                tracedict = {}
                scipy.io.savemat(filename,tracedict)
            container.processbutton["state"] = "normal"
            # now we need to save a local matlab file containing all the traces.

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

def photomimageprocess(directory,imgprefix,masks):
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
        imdir = directory+"\\"+imgprefix +"0_"+ str(i+1) + ".tif" # Currently, this function doesn't catch images with "1_"
        if os.path.exists(imdir):
            imdat = loadimg(imdir)
            print(imdir)
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

def splittraces(traces):
    pass

def loadimg(path):
    img = Image.open(path)
    img.load()
    imgdata = np.asarray(img,dtype="int32")
    return imgdata