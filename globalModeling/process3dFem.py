import sys
# import pythoncom
# import Pyfemap
# from Pyfemap import constants as feConstants
import tkinter as tk
from tkinter import simpledialog, messagebox
#from solidsToFemBeams import selectOneSolid, getEntityTitleById, processSingleSolid, updatePropTitles, processTubularSolidsByFemapAlgo, createMeshOnLines, regenerateFemapView, femapConnect
import solidsToFemBeams

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
            # groupId = int(dialog.result[0])
            # global materialId
            # materialId = int(dialog.result[1])
        except (TypeError, ValueError):
            messagebox.showinfo("Input Error", "Invalid input. Please enter valid integers.")
            return None
        callback((groupId, materialId))
    else:
        return None
    root.destroy()
    if groupId is None:
        return None
    if groupId < 1:
        messagebox.showinfo("Input Error", "Group ID must be greater than 0")
        return None
    return groupId



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
    solidsToFemBeams.femapConnect()
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

def runMainDialog():
    global root
    root = tk.Tk()
    root.title("Main Dialog")
    root.geometry("200x200") #dialog panel size
    tk.Label(root, text="Choose an action:").pack(pady=20)

    tk.Button(root, text="By Selecting Group And Mat'l", command=lambda: getGroupIdAndMaterialIdFromUserDialog(handle_selection)).pack(pady=10)
    tk.Button(root, text="By Active Mat'l & Single Solid", command=solidsToFemBeams.selectOneSolid).pack(pady=10)

    root.mainloop()

# START EXECUTION 
runMainDialog()
