import MSPhotomAnalysis as msp
import numpy as np
import PIL.Image as img

dir = 'D:\\Alli Photometry\\05-17-23\\MRKPFCREV 4 Run 1\\mrk_pfc0_2.tif'
imprfx = "mrk_pfc"

x = msp.loadimg(dir)
y = msp.npy_circlemask(424,424,5,5,20)
z = img.fromarray(y)
b = np.where(y,x,0)
c = img.fromarray(b)
print(b.sum())
print(y.sum())
print(b.sum()/y.sum())
