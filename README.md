# Multisite Photometry Image Processing Application
## Description
This application takes raw image files produced by the Multisite Photometry System and processes those images into 1-dimensional traces representing flourescence signal. This application is capable of processing up to 5 seperate recording regions, as well as a "correction" signal fiber that is submerged in a flourophore solution. Additionally, this application can process an unlimited number of interpolated "channels", each with a different excitation wavelength, this enables use of isosbestic correction or even the use of multiple flourphores (provided they possess distinct flourescence excitation frequencies) in the same fiber/brain region.
## Deployment
This code can be run either using the provided conda enviroment or using the executable release (generated with pyinstaller). You may generate your own binary using the pyinstaller command below.
```
pyinstaller --onefile --hidden-import=scipy.io MSPhotomApp.py
```
