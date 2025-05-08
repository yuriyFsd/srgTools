#import os
from pathlib import Path
import ctypes # for Windows
import win32com.client as win32
win32.gencache.is_readonly=False

try: 
    excel = win32.Dispatch('Excel.Application')
    excel.Visible = True
    toolPath = str(Path.cwd()) + r'\test.xlsm' #"E:\projects\2024\dev_welding_tool\test.xlsm"    
    wb = excel.Workbooks.open(toolPath)
except:
    ctypes.windll.user32.MessageBoxW(0,"Cannot open welding tool Excel file", "Error", 1)
