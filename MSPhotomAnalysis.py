"""
Photometry image analysis functions. Deal with actual processing of images into
signal traces
"""


import os, numpy as np,tifffile as tf, time
from matplotlib import pyplot
from PIL import Image

def datetonum(date: str):
    """
    Convert a date string in the format 'MM-DD-YY' to a numerical representation.

    Parameters
    ----------
    date : str
        Date string in the format 'MM-DD-YY'.

    Returns
    -------
    int
        Date in numerical format.

    """
    
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

def npy_circlemask(sizex : int, sizey : int,circlex : int,circley : int,radius : int):
    """
    Creates a numpy mask array with a circle region. Is used for masking image 
    files to pull only the selected fiber region.

    Parameters
    ----------
    sizex : in
        DESCRIPTION.
    sizey : TYPE
        DESCRIPTION.
    circlex : TYPE
        DESCRIPTION.
    circley : TYPE
        DESCRIPTION.
    radius : TYPE
        DESCRIPTION.

    Returns
    -------
    mask : np.array of numpy.bool_
        Array of bool values to be used a mask over a specific circular region.

    """
    mask = np.empty((sizex,sizey), dtype="bool_")
    for x in range(sizex):
        for y in range(sizey):
            if ((x-circlex)**2 + (y-circley)**2)**(0.5) <= radius:
                mask[x,y] = 1
            else:
                mask[x,y] = 0
    return mask

def photomimageprocess(directory,imgprefix,masks,**kwargs):
    """
    Process images within a directory using provided masks to extract signal traces.

    Parameters
    ----------
    directory : str
        Path to the directory containing the images.
    imgprefix : str
        prefix common to image filenames.
    masks : list of numpy.ndarray
        List containing masks for signal extraction.
    **kwargs: Additional keyword arguments.
      - waitbar (tkinter.ttk.Progressbar, optional): Tkinter Progressbar widget to display progress.
      - textvar (tkinter.StringVar, optional): Tkinter StringVar to display text output.
      - speedvar (tkinter.StringVar, optional): Tkinter StringVar to display processing speed.


    Returns
    -------
    traces : list of numpy.ndarray
        List containing signal traces extracted from the images.

    """
    waitbar = kwargs.get("waitbar", None)
    txtout = kwargs.get("textvar", None)
    speedvar = kwargs.get("speedvar",None)
    starttime = time.time()
    # within a given directory, analyze all images within that directory.
    imgls = [f for f in os.listdir(directory) if f.endswith('.tif')]
    imgls = [f for f in imgls if imgprefix in f]
    maximgnum = len(imgls) # This is to set the theoretical maximum number of images that will be processed
    # Iterating up to maximgnum has a downside, if the file names "skip" (1,2,4,5) then the last image will not be analyzed.
    # In the above example, 1,2,4 would be analyzed and 5 will be left out. I would like to alter this behavior in the future
    # to be better at catching files.
    traces = [] 
    for j in masks: #create 1 numpy array for each mask (and therefore signal)
        traces.append(np.zeros((maximgnum)))
    for i in range(maximgnum): #iterate through all the imagefiles
        imdir = directory+"/"+imgprefix +"0_"+ str(i+1) + ".tif" # Currently, this function doesn't catch images with "1_"
        if os.path.exists(imdir):
            imdat = loadimg(imdir)
            if waitbar != None: waitbar["value"] = (i/maximgnum)*100
            if txtout != None: txtout.set(imdir)
            if speedvar != None: speedvar.set(str(round(i/(time.time()-starttime),1))+" images/second")
            for j in range(len(masks)): #iterate through each mask and apply each mask and get average value.
                avrgsig = (np.where(masks[j], imdat, 0).sum())/masks[j].sum()
                np.put(traces[j],i,avrgsig)
    return traces

def subtractbackgroundsignal(traces): 
    """
    Subtract background signal from each trace.

    This function subtracts the background signal, represented by the first array in the list, 
    from each subsequent array in the input list of traces.

    Parameters
    ----------
    traces : list of numpy.ndarray
        DESCRIPTION.

    Returns
    -------
    subtrace : list of numpy.ndarray
        List containing the traces data with background signal subtracted.

    """
    subtrace = []
    for i in range(1,len(traces)):
        subtrace.append(np.subtract(traces[i],traces[0]))
    return subtrace

def splittraces(traces,channels):
    """
    Split traces data into individual channels.

    Parameters
    ----------
    traces : (list of numpy.ndarray)
        List containing traces data..
    channels : int
        Number of channels in the traces data.

    Returns
    -------
    splittraces : TYPE
        DESCRIPTION.

    """
    splittraces = []
    for i in range(len(traces)):
        for j in range(channels): splittraces.append(traces[i][j::channels])
    return splittraces

def reshapetraces(traces,imgptrial):
    """
    Reshape traces data into a specified number of trials per image.
    
    Parameters
    ----------
    traces : (list of numpy.ndarray)
        List containing traces data..
    imgptrial : int
        Number of trials per image.

    Returns
    -------
    reshapedtraces : (list of numpy.ndarray)
        List containing reshaped traces data with specified trials per image.

    """
    reshapedtraces = []
    for i in range(len(traces)):
        size = np.prod(traces[i].shape)
        trials, remainder = divmod(size,imgptrial)
        x = traces[i][0:(trials*imgptrial)]
        reshapedtraces.append(np.reshape(x,(trials,imgptrial)))
    return reshapedtraces


def loadimg(path):
    """
    Load an image from the specified path.

    Parameters
    ----------
    path : str
        pathlike object specifying location of image file.

    Returns
    -------
    imarray : np.array
        Array representing pixels of image.

    """
    # img = tf.imread(path)
    with Image.open(path) as img:
        imarray = np.array(img)
    return imarray