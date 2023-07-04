import MSPhotomApp as msp

dir = 'D:\\Alli Photometry\\05-17-23\\MRKPFCREV 4 Run 1\\mrk_pfc0_1.tif'
imprfx = "mrk_pfc"

x = msp.loadimg(dir)
print(x)