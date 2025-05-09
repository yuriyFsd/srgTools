
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

getFemap()

panelTitle = 'srgPanel'
tools = [
    {'title': "Welding Tool", 'file': "openWeldingTool.exe"}, 
    {'title': "Items/Slings Rotation", 'file': "openSlingRotationTool.exe"},
    {'title': "AnSets Creation", 'file': "openAnSetTool.exe"},
    {'title': "Beams As Members", 'file': "openProcessBeamsTool.exe"}
]
cmdDir = str(Path.cwd()) #r"C:\Program Files\Siemens\Femap 2406\srgTools"

reCreateToolBar(panelTitle)

for tool in tools:
    res = addUserCommand(tool['title'], cmdDir + "\\" + tool['file'], "", cmdDir)
    cmdId = addToolBarButton(panelTitle,tool['title'])

ctypes.windll.user32.MessageBoxW(0,"SRG Tools Panel has been added to your Femap", "Process Finished", 1)