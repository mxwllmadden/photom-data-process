import MSPhotomAnalysis as msp
import MSPhotomGUI as msg
import scipy, os, tkinter as tk, numpy as np, os, tifffile
from dataclasses import dataclass
from PIL import Image
from matplotlib import pyplot

def abs_dir(relative):
    this_file_path = os.path.abspath(__file__)
    this_dir = os.path.split(this_file_path)[0]
    return os.path.join(this_dir,relative)

def test_generateexampledata(): #this generates example data and returns the expected output
    #Create "expected traces"
    t = np.arange(3000,dtype='uint16') #length in images
    backgroundsignal = (np.sin(t/477)+1)*50 #background signal is applied to every trace
    pure_signal = []
    pure_signal.append(t/30) #a simple ascending trace
    pure_signal.append((3000-t)/30) #a simple descending trace
    pure_signal.append(np.sin(t/100)*20)
    pure_signal.append(np.sin(t/50)*20)
    pure_signal.append(np.sin(t/20)*20)
    pure_signal.append(np.sin(t/100)*50)
    plot_signal = [] # The background signal is added to each trace.
    for i in range(len(pure_signal)): plot_signal.append(pure_signal[i] + backgroundsignal)

    if os.path.exists(abs_dir("testdata")) == False:
        os.makedirs(abs_dir("testdata"))
    
    templateimage = np.zeros((424,424))
    for i in range(3000): #create the images
        imarray = templateimage
        imarray[147:277,147:277] = backgroundsignal[i]
        imarray[0:130,0:130] = plot_signal[0][i]
        imarray[0:130,147:277] = plot_signal[1][i]
        imarray[0:130,294:424] = plot_signal[2][i]
        imarray[294:424,0:130] = plot_signal[3][i]
        imarray[294:424,147:277] = plot_signal[4][i]
        imarray[294:424,294:424] = plot_signal[5][i]

        # tifffile.imsave(abs_dir("testdata\\img0_"+str(i)+".tif"),
        #                 imarray,
        #                 metadata={"ImageWidth" : 424,
        #                           "ImageLength": 424,
        #                           "BitsPerSample": 16,
        #                           "Compression": "NONE",
        #                           "PageNumber": (0,0)},
        #                 photometric='minisblack')
        x = Image.fromarray(imarray)
        x.save(abs_dir("testdata\\img0_"+str(i)+".tif"))

        print(str(round(i/3000*100,1))+"%")
    
    def checkavrg(array,rowrange,colrange,originalval):
        r = np.average(array[rowrange[0]:rowrange[1],colrange[0]:colrange[1]])
        if round(originalval,6) == round(r,6): return True
        else: return False

    error = False
    for i in range(3000):
        img = tifffile.imread(abs_dir("testdata\\img0_"+str(i)+".tif"))
        imarray = np.array(img)
        rangelistrow = [(147,277),(0,130),(0,130),(0,130),(294,424),(294,424),(294,424)]
        rangelistcol = [(147,277),(0,130),(147,277),(294,424),(0,130),(147,277),(294,424)]
        traces = [backgroundsignal]
        for j in plot_signal: traces.append(j)
        for j in range(len(rangelistrow)):
            if not checkavrg(imarray,rangelistrow[j],rangelistcol[j],traces[j][i]): error = True
    
    if error == True: print("IMAGE AND TRACES DO NOT MATCH")
    else: print("TEST IMAGES HAVE BEEN GENERATED SUCCESSFULLY")



    
test_generateexampledata()





    
    

    
