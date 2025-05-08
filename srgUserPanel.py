
import pythoncom
import Pyfemap
from Pyfemap import constants as feConstants
import sys
from pathlib import Path
import ctypes # for Windows
import win32com.client as win32
win32.gencache.is_readonly=False
import comtypes.client
tlb_path = r"C:\Program Files\Siemens\Femap 2406\femap.tlb"
comtypes.client.GetModule(tlb_path)

from tkinter import messagebox
# Import the generated module
import comtypes.gen

def installConfirmation():
    return messagebox.askokcancel("SRG ToolBar Installation", "To install SRG ToolBar on Femap?\n\n")

def getFemap():
    global femap
    try:
        existObj = pythoncom.connect(Pyfemap.model.CLSID)
        femap = Pyfemap.model(existObj)
    except Exception as error:
       print(error)
       ctypes.windll.user32.MessageBoxW(0,"Can't connect to Femap API Server", "Error", 1)
       sys.exit("Can't connect to Femap API Server ")

    femap.feAppMessage(0, "Python Connected To Femap")

def reCreateToolBar(title):
    femap.feDeleteToolbar(title)
    return femap.feAddToolbar(title, feConstants.FCCL_TOP) == -1
    

def addUserCommand(cmdTitle, path, cmdArgs, startDir):
    [rc, num, titles, patches, args, startDirs] = femap.feGetUserCommands()
    if cmdTitle not in titles:
        return femap.feAddUserCommand(cmdTitle, path, cmdArgs, startDir) == -1

def addToolBarButton(barName, cmdTitle):
    cmdIndex = 0
    cmdBitmap = ""
    [ rc, id] = femap.feAddToolbarUserCommand(barName, cmdIndex, cmdTitle, cmdBitmap)
    return id

#----------main flow:-------------------
if installConfirmation() == False: exit()
#getFemap()
panelTitle = 'srgPanel'
cmdTitle = "Welding Tool"
tools = [
    {'title': "Welding Tool", 'file': "openWeldingTool.exe"}, 
    {'title': "Slings Rotation", 'file': "openSlingsRotationTool.exe"}
]

cmdDir = Path.cwd() #r"C:\Program Files\Siemens\Femap 2406\srgTools"

reCreateToolBar(panelTitle)
for tool in tools:
    res = addUserCommand(tool['title'], cmdDir + "\\" + tool['file'], "", cmdDir)
    cmdId = addToolBarButton(panelTitle,tool['title'])
rc = 1

exit()

def getExcel():
    excel = win32.Dispatch('Excel.Application')
    excel.Visible = True
    wb = excel.Workbooks.open(r"E:\projects\2024\dev_welding_tool\test.xlsm")
    worsheet = wb.Worksheets(1)
    worsheet.Cells(1, 1).Value = "Hello World111"

getExcel()
exit()
try:
    existObj = pythoncom.connect(Pyfemap.model.CLSID)
    femap = Pyfemap.model(existObj)
    femap.feAppMessage(0, "Python API Started")    

    #Throw an error if no Femap instance opened
except:
    sys.exit('Femap not open')


def createUIpanel(panelTitle):
    rc = femap.feAddToolbar(panelTitle, 0)
    # if(femap.feAddToolbar(panelTitle, 0) != -1): return False
    
    # [rc, menuId] = femap.feAddToolbarSubmenu(panelTitle, -1, "First Tool")

    #1 Create by python exe (or bas) file that open required excel
    #2 Create user command and run that exe from #1
    #3 Add user command to own panel
    femap.feAddUserCommand("MyCommandTest", "Ctrl+A", )
    [rc, cmdId] = femap.feAddToolbarUserCommand(panelTitle, 0, "TestCommand", "")

    rc = rc
if not createUIpanel("testPanel"):
    rc =  femap.feAppMessageBox(0, "Error")
    print(rc)
