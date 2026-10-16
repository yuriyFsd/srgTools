import pythoncom
import Pyfemap
import sys
from Pyfemap import constants as feConstants

#import ctypes # for Windows
import win32com.client as win32
win32.gencache.is_readonly=False
import comtypes.client
tlb_path = r"C:\Program Files\Siemens\Femap 2406\femap.tlb"
comtypes.client.GetModule(tlb_path)

def femapConnect():
    try:
        existObj = pythoncom.connect(Pyfemap.model.CLSID)
        femap = Pyfemap.model(existObj)
        rc = femap.feAppMessage(feConstants.FCM_NORMAL, "Connected!")
    except Exception as error:
        print(error)
        #ctypes.windll.user32.MessageBoxW(0,"Can't connect to Femap API Server", "Error", 1)
        sys.exit("Can't connect to Femap API Server ")
    return femap

femap = femapConnect()

def automidsurf():
    rc = femap.feAppMessage(feConstants.FCM_NORMAL, "3e3e3e11111111111133e!")
    mySet = femap.feSet
    arr = [4,6,8]
    rc = mySet.AddArray(3, arr)
    print(rc)
    mySet.Debug()
   # mySet.Next()
   # print(mySet.CurrentID)
    #rc = femap.feSurfaceMidAuto4(mySet.ID, )
    return 1

x = automidsurf()
