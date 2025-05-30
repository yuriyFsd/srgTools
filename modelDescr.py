import pythoncom
import Pyfemap
import datetime
from Pyfemap import constants as feConstants
import tkinter as tk
from tkinter import scrolledtext

#import ctypes # for Windows
import win32com.client as win32
win32.gencache.is_readonly=False
import comtypes.client
tlb_path = r"C:\Program Files\Siemens\Femap 2406\femap.tlb"
comtypes.client.GetModule(tlb_path)

# existObj = pythoncom.connect(Pyfemap.model.CLSID)
# femap = Pyfemap.model(existObj)

# rc = femap.feAppMessage(feConstants.FCM_NORMAL, "Status")
# userData = femap.feUserData
# dataTitle = "myData"

def setUserData():
    userText = "fdfdf \n fdffdf \n dsfdfdf df df dfsfsd11111111111111 ff2234 32 sdf sfd fsd fsd f"
    rc = userData.WriteString(userText)
    rc = userData.PutTitle(dataTitle)
    print({rc})


def getUserData(title):
    rc = userData.GetTitle(title)
    print(rc)
    [rc, uData] = userData.ReadString()    
    print(uData)
    femap.feAppMessage(feConstants.FCM_HIGHLIGHT, uData)

def createInputTextBox():
    print("Creating input text box")
    canvas = tk.Canvas(root, height=800, width = 600, bg = "white")
    canvas.pack()
    string_box = tk.Entry(root)
    canvas.create_window(250, 125, window = string_box)
    input_string = string_box.get()
    print(f"Input string: {input_string}")

def addText(event=None, entry=None, textArea=None):
    text = entry.get()
    if text:
        textArea.config(state=tk.NORMAL)
        textArea.insert(tk.END, '\n' + text)
        entry.delete(0, tk.END)
        print("Adding text")
    else: 
        print("No text to add")
    textArea.config(state=tk.DISABLED)

def editTextArea(textArea=None):
    print("Editing text area")    
    textArea.config(state=tk.NORMAL)
    textArea.focus()
    # textArea.bind("<Return>", lambda event: addText(event, entry, textArea))
    print("Text area is now editable")

def saveTextArea(textArea=None):    
    textArea.config(state=tk.DISABLED)
    userText = textArea.get("1.0", tk.END).strip()
    if userText:
        print(userText)
        # rc = userData.WriteString(userText)
        # rc = userData.PutTitle(dataTitle)
        # print(f"User data saved with title '{dataTitle}': {userText}")
    else:
        print("No text to save")


def uiPanel():
    root = tk.Tk()
    root.title("User Description For Femap Model")
    #root.geometry("400x400")
    root.columnconfigure(0, weight=1)
    #root.columnconfigure(1, weight=1)
    #root.rowconfigure(0, weight=1)
    # root.rowconfigure(1, weight=1)

    frame = tk.Frame(root)
    frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(0, weight=1)
        
    textArea = scrolledtext.ScrolledText(frame)
    textArea.insert(tk.END, "Enter your description here...\n sdsdsdsd аываыа ыаыв ааыва ")
    textArea.config(state = "disabled")
    textArea.grid(row=1, column=0, columnspan=2, sticky="new", padx=5, pady=5)

    editBtn = tk.Button(frame, text = "Edit", command = lambda: editTextArea(textArea))
    editBtn.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

    saveBtn = tk.Button(frame, text = "Save", command = lambda: saveTextArea(textArea))
    saveBtn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    entry = tk.Entry(frame)
    entry.grid(row=2, column=0, sticky='sew', padx=5, pady=5)
    entry.bind(("<Return>"), lambda event: addText(event, entry, textArea))
    
    addBtn = tk.Button(frame, text = "Add", command = lambda: addText(None, entry, textArea))
    addBtn.grid(row=2, column=1, padx=5, pady=5, sticky='w')
    

    # label = tk.Label(root, text="Enter your description:")

    # label.configure(font=("Arial", 14), text="mymymyModel User Description")
    # label.pack()

    # label1 = tk.Entry(root)
    # label1.insert(0, float(x1)**0.5)
    # label1["state"] = "readonly

    # InputBox = tk.Button(root, text = "Input Box", padx=10,pady=10,
    #                 fg = "white", bg ="blue", command = createInputTextBox)
    # InputBox.pack()

    root.mainloop()

uiPanel()
#setUserData()
#getUserData(dataTitle)