from pydicom import *

def getDicomWindowCenterAndLevel(fileName):
    dcmFile = dcmread(fileName)
    return (dcmFile.WindowCenter, dcmFile.WindowWidth)