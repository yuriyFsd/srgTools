import sys
import numpy as np
import pythoncom
import Pyfemap
import re
#import os
from pathlib import Path
from Pyfemap import constants as feConstants

#import ctypes # for Windows
# import win32com.client as win32
# win32.gencache.is_readonly=False
# import comtypes.client
# tlb_path = r"C:\Program Files\Siemens\Femap 2406\femap.tlb"
# comtypes.client.GetModule(tlb_path)

def femapConnect():
    try:
        existObj = pythoncom.connect(Pyfemap.model.CLSID)
        global femap
        femap = Pyfemap.model(existObj)
        rc = femap.feAppMessage(feConstants.FCM_NORMAL, "Connected!")
    except Exception as error:
        print(error)
        #ctypes.windll.user32.MessageBoxW(0,"Can't connect to Femap API Server", "Error", 1)
        sys.exit("Can't connect to Femap API Server ")
        return femap

def exportAnSetById(anSetId, filePath):
    #activate anSet
    anSet = femap.feAnalysisMgr
    rc = anSet.Get(anSetId)
    rc = femap.feAppMessage(feConstants.FCM_NORMAL, anSet.title)
    anSet.Active = anSetId
    solverBrand = 8 #NX
    fileTitle = re.sub(r'\W+', '-', anSet.title)  #sanitize title for file name    
    fileName = str(filePath) + '/' + fileTitle + ".dat"
    # print(fileName)
    #create empty file
    try:
        open(fileName, 'w').close()
    except Exception as error:
        print(error)
    #"E:/projects/2024/dev/python/femap/testAutomate.dat"
    rc = femap.feFileWriteNastran(solverBrand, fileName) #file should be created in advance

def selectAnSets():
    filename = Path(femap.ModelName)
    filePath = filename.parent #femap.ModelName #"E:/projects/2024/dev/python/femap/"
    #  Dim fset As femap.Set
    fset = femap.feSet
    rc = fset.SelectMultiIDV2(feConstants.FT_AMGR_DIR, 1, "Select Analysis Sets to Export as Nastran NX")
    #  fset.Debug
    #  Debug.Print rc
    fset.Reset
    while fset.Next():
        fsetId = fset.CurrentID
        exportAnSetById(fsetId, filePath)

    #End Sub

femapConnect()
selectAnSets()
