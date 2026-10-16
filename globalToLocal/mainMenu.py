import tkinter as tk
from tkinter import messagebox, ttk
import beamProcessor

def runMainDialog():
    #solidsToFemBeams.femapConnect()
    global root
    root = tk.Tk()
    #root.attributes('-toolwindow', True) #to remove minimize and maximize buttons
    root.title("Beams To Plates Converter")
    root.geometry("260x240") #dialog panel size

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')
    tab1 = tk.Frame(notebook)
    tab2 = tk.Frame(notebook)
    
   # tk.Label(tab1, text="Create Beam Mesh \n(c`ones or tubes) By Solids").pack(pady=5)
   # tk.Label(tab1, text="Choose an option:").pack(pady=5)

   # tk.Label(tab1, text="( ! Group option uses \n Femap Algo for tubes only)").pack()
   # tk.Button(tab1, text="By Selecting Group And Mat'l", command=lambda: getGroupIdAndMaterialIdFromUserDialog(handle_selection)).pack(pady=10)
   # tk.Button(tab1, text="By Active Mat'l & Single Solid", command=solidsToFemBeams.selectOneSolid).pack(pady=10)
    tk.Button(tab1, text = "Auto Create Members Solids", command=beamProcessor.processBeamsToMembers).pack(pady=40)

   # check_var = tk.IntVar()
   # tk.Button(tab2, text="Merge Active Group Beam Properties", command=lambda: mergeBeamProperties(check_var.get())).pack(pady=20)
   # tk.Checkbutton(tab2, text="Ignore Prop Names", variable=check_var).pack()
   # check_var.set(1)  # Default to checked

    notebook.add(tab1, text="Beam Processing")
    notebook.add(tab2, text="*****")
    root.mainloop()

# START EXECUTION 
runMainDialog()