import sys
import pythoncom
import Pyfemap
from Pyfemap import constants as feConstants
import tkinter as tk
from tkinter import simpledialog

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

def parseSoligGeomSurfaces(solidGeomId):
    solidGeom = femap.feSolid
    rc =  solidGeom.Get(solidGeomId)
    selectingMode = 2 #List contains both the underlying and combined surfaces.
    rc, numsrfs, surfsIds = solidGeom.Surfaces(selectingMode)
    surf = femap.feSurface
    area = 0.0
    for surfId in surfsIds:
        rc = surf.Get(surfId)
        if rc != -1:
            continue
        rc = surf.ApproximateArea(area)
        if area > GEOM_SURFACES['first_biggest']:
            GEOM_SURFACES['second_biggest'] = GEOM_SURFACES['first_biggest']
            GEOM_SURFACES['first_biggest'] = area
            GEOM_SURFACES['end2'] = GEOM_SURFACES['end1']
            GEOM_SURFACES['end1'] = surfId

    return 1


def getShapeTypeOfSolidGeom(solidGeomId):
    solidGeom = femap.feSolid
    rc =  solidGeom.Get(solidGeomId)
    print(solidGeom.type)
    selectingMode = 2 #List contains both the underlying and combined surfaces.
    rc, numsrfs, surfsIds = solidGeom.Surfaces(selectingMode)
    surf = femap.feSurface
    shape_type = ''
    areas = {
        'cone': 0,
        'cylinder': 0,
        'plane': 0,
        'other': 0
    }
    for surfId in surfsIds:
        rc = surf.Get(surfId)
        if rc != -1:
            continue
        rc, area = surf.Area()
        if (surf.IsCone() == -1):
            print('cone', surfId)
            # shape_type = SHAPE_TYPES['cone']
            areas['cone'] += area
        elif (surf.IsCylinder() == -1):
            print('cyl', surfId)
            # shape_type = SHAPE_TYPES['cylinder']
            areas['cylinder'] += area
        elif (surf.IsPlane() == -1):
            print('plane', surfId)
            # shape_type = SHAPE_TYPES['plane']
            areas['plane'] += area
        else:
            print('other', surfId)
            # shape_type = SHAPE_TYPES['other']
            areas['other'] += area
    biggestShapeArea = getBiggestSurfaceAreaField(areas)
    return list(biggestShapeArea.keys())[0]

def getBiggestSurfaceAreaField(areas):
    biggestArea = 0
    biggestField = ''
    for field, area in areas.items():
        if area > biggestArea:
            biggestArea = area
            biggestField = field
    return { biggestField: biggestArea }


print(getShapeTypeOfSolidGeom(1440)) #1440 - cone solid
exit(0)

def createBeamConeProp():
    fprop = femap.feProp
    rc = fprop.Last()
    newId = 2 # fprop.ID + 1
    
    myProp = femap.feProp
    myProp.title = "Cone1"
    myProp.type = feConstants.FET_L_BEAM
    myProp.matlID = 401  # 1 - Steel
    #rc = myProp.Put(newId)#newId)  
    rc = myProp.SetflagI(1, feConstants.FSHP_CIRC_TUBE)# = 6 #feConstants.FSHP_CIRC_TUBE
    rc = myProp.SetflagI(0, 1) # Tapered beam flag
    # rc = myProp.Setpval(40, 0.139)
    # rc = myProp.Setpval(45, 0.012)

    computeOnlyOneEnd = True
    shapeID = feConstants.FSHP_CIRC_TUBE
    dimensions = [0.139, 0, 0, 0, 0, 0.012]
    EvalMethod = 1 #0=Auto, 1=Orig-inal, 2=Alternate, 3=Nastran PBEAML
    shear_center_offset = False
    Warping = False
    stress_recovery = False
    rc = myProp.ComputeStdShape2(computeOnlyOneEnd, shapeID, dimensions, feConstants.FSOR_RIGHT, EvalMethod, shear_center_offset, Warping, stress_recovery)
    dimensions = [0.159, 0, 0, 0, 0, 0.016]
    computeOnlyOneEnd = False
    rc = myProp.ComputeStdShape2(computeOnlyOneEnd, shapeID, dimensions, feConstants.FSOR_RIGHT, EvalMethod, shear_center_offset, Warping, stress_recovery)
    print(rc)
    myProp.Put(newId)
    return 1

createBeamConeProp()
femap.feViewRegenerate(0)
exit(0)

def getGroupIdAndMaterialIdFromUser():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
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
            global materialId
            materialId = int(dialog.result[1])
        except (TypeError, ValueError):
            femap.feAppMessageBox(feConstants.FCM_NORMAL, "Invalid input. Please enter valid integers.")
            return None
    else:
        return None
    root.destroy()
    if groupId is None:
        return None
    if groupId < 1:
        femap.feAppMessageBox(feConstants.FCM_NORMAL, "Group ID must be greater than 0")
        return None
    return groupId

def getSetOfSolidsByGroup(groupId):
    mySet = femap.feSet
    rc = mySet.AddGroup(feConstants.FT_SOLID, groupId)
    if rc != -1 or mySet.Count == 0:
        print('rc: ', rc)
        femap.feAppMessageBox(feConstants.FCM_NORMAL, f"Set of solids for group {groupId} is empty or not found")
        return None

    mySet.Debug()
    return mySet

def femapStartTrackGeometry():

    tracker = femap.feTrackData
    rc = tracker.StartGeometry()
    if rc == -1:
        femap.feAppMessage(feConstants.FCM_HIGHLIGHT, "Tracking started successfully")
        return tracker
    else:
        femap.feAppMessageBox(feConstants.FCM_ERROR, "Failed to start tracking")
        return None

def getFemapCreatedGeometrySet(tracker):
    geomSet = femap.feSet
    rc = tracker.Created(feConstants.FT_CURVE, geomSet.ID, True)
    if rc == -1:
        geomSet.Debug()
        return geomSet
    else:
        femap.feAppMessageBox(feConstants.FCM_ERROR, "Failed to get created geometry set")
        return None

def processTubularSolids(solidIds, materialId):
    solidsSet = femap.feSet
    solidsSet.addarray(feConstants.FT_SOLID, solidIds)
    solidsSet.Debug()
    rc = femap.feSolidExtractCenterlines(solidsSet.ID, materialId, True)
    if rc != -1:
        femap.feAppMessageBox(feConstants.FCM_ERROR, f"Cannot extract centerlines for solids")
        return None

def getTubularEndsSurfaceIds(solidId):
    return []

def processConicalSolids(solidIds, materialId):
    for solidId in solidIds:    
        endsSurfaceIds = getTubularEndsSurfaceIds(solidId)

    return 1

def createMeshOnLines(centerLinesSet):
    meshSize = 0
    minLine = 0
    minClosed = 0
    minOther = 0
    spacing = 0
    biasMethod = 0
    bias = 0
    biasLoc = 0
    customSize = 0
    rc = femap.feMeshSizeCurve(centerLinesSet.ID, 1, meshSize, minLine, minClosed, minOther, spacing, biasMethod, bias, biasLoc, customSize)
    if rc != -1:
        femap.feAppMessageBox(feConstants.FCM_ERROR, f"Cannot set mesh size for centerlines")
        return None

    meshElem = True # nodes and elements
    propID = 0
    merge_nodes = True
    offsetToRefPt = 0.0
    orient = [0, 0, 1]  # Default orientation vector
    rc = femap.feMeshCurve2(centerLinesSet.ID, meshElem, propID, merge_nodes, offsetToRefPt, orient )
    if rc != -1:
        femap.feAppMessageBox(feConstants.FCM_ERROR, f"Cannot mesh centerlines")
        return None

def getGeomShapesByGroupSet(solidsSet):
    geomShapesIds = {
        'cylinder': [],
        'cone': [],
        'other': []
    }
    while solidsSet.Next():
        currentSolidId = solidsSet.currentID
        if getShapeTypeOfSolidGeom(currentSolidId) == 'cylinder':
            geomShapesIds['cylinder'].append(currentSolidId)
        elif getShapeTypeOfSolidGeom(currentSolidId) == 'cone':
            geomShapesIds['cone'].append(currentSolidId)
        else:
            geomShapesIds['other'].append(currentSolidId)
    return geomShapesIds


solidsSet = getSetOfSolidsByGroup(getGroupIdAndMaterialIdFromUser())
geomSortedByShape = getGeomShapesByGroupSet(solidsSet)

tracker = femapStartTrackGeometry()
processTubularSolids(geomSortedByShape['cylinder'], materialId)
centerLinesSet = getFemapCreatedGeometrySet(tracker)
createMeshOnLines(centerLinesSet)
femap.feViewRegenerate(0)
exit(0)

def getSoligGeom(id):  #1434 - just pipe, 1440 - cone
    # myElem = femap.feElem
    # print(dir(myElem))
    # return
    # rc = myElem.get(1)
    # print(rc)

    mySolid = femap.feSolid
    rc =  mySolid.Get(id)
    #print(rc)
    # surfaces = mySolid.vVolSurface
    # print(surfaces)
    print(mySolid.type)
    rc, numsrfs, surfsIds = mySolid.Surfaces(2)
    print(rc)
    print(numsrfs, surfsIds)
    for surfId in surfsIds:
        getSurfData(surfId)
    #get list of surfaces
    #identify ends ?
    return 1

def getSurfData(id):
    mySurf = femap.feSurface
    rc = mySurf.Get(id)
    if mySurf.IsCylinder() == -1:
        print(id, 'cyl')
    
    if mySurf.IsPlane() == - 1: 
        print(id, 'plane')
        nCombinedMode = 2
        rc, numCurves, curveIds = mySurf.Curves(nCombinedMode)
        processCurves(curveIds)
        print(rc, numCurves, curveIds)

    if mySurf.IsCone() == - 1: print(id, 'cone')

    # print(id, mySurf.IsCylinder())
    # print(id, mySurf.i())
    return 1

def processCurves(curveIds):
    curve = femap.feCurve
    for curveId in curveIds:
        rc = curve.Get(curveId)
        print(rc, curveId, 'curvetype = ', curve.type)

def getArcGeom(arcCurve):
    print('isArc', arcCurve.IsArc())
    (rc, center, normal, startPt, endPt, angle, radius) = arcCurve.ArcCircleInfo()
    print(rc, center, normal, startPt, endPt, angle, radius)

def getDist(loc1, loc2):
    return 1

# def checkProp():
#     fprop = femap.feProp
#     rc = fprop.Get(20421)
#     for index in range(100):
#         print(index, fprop.pval(index))

# checkProp()
# exit(0)

def createBeamPipeProp():
    # print(dir(femap.feProp))
    # return
    fprop = femap.feProp
    rc = fprop.Last()
    newId = fprop.ID + 1

    myProp = femap.feProp
    myProp.title = "Pipe1"
    myProp.type = feConstants.FET_L_BEAM
    myProp.matlID = 401  # 1 - Steel
    rc = myProp.Put(newId)  
    rc = myProp.SetflagI(1, feConstants.FSHP_CIRC_TUBE)# = 6 #feConstants.FSHP_CIRC_TUBE
    rc = myProp.Setpval(40, 0.139)
    rc = myProp.Setpval(45, 0.012)
    #rc = myProp.SetArea(0.01)  # 10 cm^2
    print(rc)
    dimensions = [0.139, 0, 0, 0, 0, 0.012]
    rc = myProp.ComputeStdShape(feConstants.FSHP_CIRC_TUBE, dimensions, feConstants.FSOR_RIGHT, feConstants.FSEV_ORIG, 1, 1, 0)
    print('shape = ' , rc)
    rc = myProp.Put(newId)
    femap.feViewRegenerate(0)
    print(rc)
    return newId

#createBeamPipeProp()

def createElem(loc1, loc2):
    felem = femap.feElem
    # print(dir(felem))
    # exit()
    felem.type = feConstants.FET_L_BEAM
    felem.topology = 0
    felem.propID = 111130
    felem.SetNode(0, 95720)
    felem.SetNode(1, 95721)

    felem.Setorient(0, 0) #vec2(0)
    felem.Setorient(1, 0) #vec2(1)
    felem.Setorient(2, 1) #vec2(2)

#    95720
#    95721
    #print('nextID ', felem.NextEmptyID())
    rc = felem.Put(felem.NextEmptyID())
    print(rc)
    print(felem.ID)
    femap.feViewRegenerate(0)
    return 1

def getPerpindicularVectorByLocations(loc1, loc2):

    return 1

createElem(1, 2)
exit()

arcCurve = femap.feCurve
rc = arcCurve.Get(32128)
getArcGeom(arcCurve)
rc = arcCurve.Get(32124)
getArcGeom(arcCurve)
32119
rc = arcCurve.Get(32119)
getArcGeom(arcCurve)
#getSoligGeom(1434)
