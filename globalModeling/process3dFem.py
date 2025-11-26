import sys
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import solidsToFemBeams
import mergeProperties

#TODO: refactor code: use classes, separate code by layers
#TODO make paneled tool
#TODO: confirmation dialog for groups

SHAPE_TYPES = {
    'cylinder': 1,
    'cone': 2,
    'plane': 3,
    'other': 0,
    1: 'cylinder',
    2: 'cone',
    3: 'plane',
    0: 'other'
}

GEOM_SURFACES = {
    'first_biggest': 0,
    'second_biggest': 0,
    'first_smallest': 0,
    'second_smallest': 0,
    'end1': 2,
    'end2': 3,
}

def getGroupIdAndMaterialIdFromUserDialog(callback):
    # root = tk.Tk()
    #root.withdraw()  # Hide the main window
    class InputDialog(simpledialog.Dialog):
        def body(self, master):
            tk.Label(master, text="Group ID:").grid(row=0, sticky="e")
            tk.Label(master, text="Material ID:").grid(row=1, sticky="e")
            self.group_entry = tk.Entry(master)
            self.material_entry = tk.Entry(master)
            self.group_entry.grid(row=0, column=1)
            self.material_entry.grid(row=1, column=1)
            return self.group_entry

        def apply(self):
            self.result = (
                self.group_entry.get(),
                self.material_entry.get()
            )
    dialog = InputDialog(root, title="Enter Group and Material IDs")
    if dialog.result:
        try:
            groupId = int(dialog.result[0])
            materialId = int(dialog.result[1])
        except (TypeError, ValueError):
            messagebox.showinfo("Input Error", "Invalid input. Please enter valid integers.")
            return None
        confirm = messagebox.askyesno(
            "Confirm Input",
            f"Please confirm to process \n\nGroup ID: {groupId}\nMaterial ID: {materialId}"
        )
        if confirm:
            callback((groupId, materialId))
    else:
        return None

def processConicalSolids(solidIds, materialId):
    for solidId in solidIds:
        solidsToFemBeams.processSingleSolid(solidId, materialId)

def getGeomShapesByGroupSet(solidsSet):
    geomShapesIds = {
        'cylinder': [],
        'cone': [],
        'other': []
    }
    while solidsSet.Next():
        currentSolidId = solidsSet.CurrentID
        if solidsToFemBeams.getShapeTypeOfSolidGeom(currentSolidId) == 'cylinder':
            geomShapesIds['cylinder'].append(currentSolidId)
        elif solidsToFemBeams.getShapeTypeOfSolidGeom(currentSolidId) == 'cone':
            geomShapesIds['cone'].append(currentSolidId)
        else:
            geomShapesIds['other'].append(currentSolidId)
    return geomShapesIds

def processSolidsGroup(groupId, materialId):
    solidsSet = solidsToFemBeams.getSetOfSolidsByGroup(groupId)
    geomSortedByShape = getGeomShapesByGroupSet(solidsSet)
    tracker = solidsToFemBeams.femapStartTrackGeometry()
    propTracker = solidsToFemBeams.femapStartTrackProperty()
    solidsToFemBeams.processTubularSolidsByFemapAlgo(geomSortedByShape['cylinder'], materialId)
    propSet = solidsToFemBeams.getFemapCreatedPropSet(propTracker)
    solidsToFemBeams.updatePropTitles(propSet)
    processConicalSolids(geomSortedByShape['cone'], materialId)
    centerLinesSet = solidsToFemBeams.getFemapCreatedGeometrySet(tracker)
    solidsToFemBeams.createMeshOnLines(centerLinesSet)
    solidsToFemBeams.regenerateFemapView()
    messagebox.showinfo("Success", "Done")

def handle_selection(result):
    groupId, materialId = result
    processSolidsGroup(groupId, materialId)

def confirmDialog(message):
    return messagebox.askyesno("Confirm", message)

def mergeBeamProperties(ignoreNames):
    messagebox.showinfo("info", f"Ignore Names: {bool(ignoreNames)}")
    if confirmDialog("This will merge beam properties of active group based on cross-section and material. Proceed?"):
        mergedPropNum = mergeProperties.mergeBeamProperties(bool(ignoreNames))
        if mergedPropNum > 0:
            messagebox.showinfo("Success", f"{mergedPropNum} beam properties merged successfully.")
        else:
            messagebox.showinfo("0 property paires found at the active group, nothing to merge")

def runMainDialog():
    #solidsToFemBeams.femapConnect()
    global root
    root = tk.Tk()
    #root.attributes('-toolwindow', True) #to remove minimize and maximize buttons
    root.title("Solids to Beams")
    root.geometry("260x240") #dialog panel size

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')
    tab1 = tk.Frame(notebook)
    tab2 = tk.Frame(notebook)
    
    tk.Label(tab1, text="Create Beam Mesh \n(cones or tubes) By Solids").pack(pady=5)
    tk.Label(tab1, text="Choose an option:").pack(pady=5)

    tk.Label(tab1, text="( ! Group option uses \n Femap Algo for tubes only)").pack()
    tk.Button(tab1, text="By Selecting Group And Mat'l", command=lambda: getGroupIdAndMaterialIdFromUserDialog(handle_selection)).pack(pady=10)
    tk.Button(tab1, text="By Active Mat'l & Single Solid", command=solidsToFemBeams.selectOneSolid).pack(pady=10)

    check_var = tk.IntVar()
    tk.Button(tab2, text="Merge Active Group Beam Properties", command=lambda: mergeBeamProperties(check_var.get())).pack(pady=20)
    tk.Checkbutton(tab2, text="Ignore Prop Names", variable=check_var).pack()
    check_var.set(1)  # Default to checked

    notebook.add(tab1, text="Solids to Beams")
    notebook.add(tab2, text="Beam Work")
    root.mainloop()

# START EXECUTION 
runMainDialog()
