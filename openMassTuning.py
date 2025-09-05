from pathlib import Path
import glob
import ctypes # for Windows
import win32com.client as win32
win32.gencache.is_readonly=False

toolNameMainPart = "masstuning"

fileName = glob.glob(f"*{toolNameMainPart}*.xlsm")[0]
if len(fileName) == 0:
    ctypes.windll.user32.MessageBoxW(0, f"Cannot find {toolNameMainPart}*.xlsm file", "Error", 1)
    exit()

try: 
    excel = win32.Dispatch('Excel.Application')
    excel.Visible = True
    toolPath = str(Path.cwd()) + fr'\{fileName}'
    wb = excel.Workbooks.open(toolPath)
except:
    ctypes.windll.user32.MessageBoxW(0,"Cannot open welding tool Excel file", "Error", 1)