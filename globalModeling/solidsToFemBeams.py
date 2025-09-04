import sys
import numpy as np
import pythoncom
import Pyfemap
from Pyfemap import constants as feConstants

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

def processSingleSolid(solidGeomId, matlId = None):
    endsGeom = getSolidConeSurfaces(solidGeomId)
    matl = {}
    if not matlId:
        matl = getActiveMatlIdAndTitle()
    else:
        matl["id"] = matlId
        matl["title"] = getEntityTitleById(matlId, feConstants.FT_MATL)
    #femap.feAppMessageBox(0, f'''{round(endsGeom[0]["radius"]*1000)} {round(endsGeom[1]["radius"]*1000)}''' )
    if (round(endsGeom[0]["radius"]*1000) == round(endsGeom[1]["radius"]*1000)):
        #femap.feAppMessageBox(0,"Cylinder detected" )
        propId = createBeamCylProp(endsGeom, matl)
    else:
        propId = createBeamConeProp(endsGeom, matl)
    elemId = createElem(endsGeom[0]['center'], endsGeom[1]['center'], propId)

def createNodeAtLocation(loc):
    fnode = femap.feNode
    fnode.xyz = loc
    rc = fnode.Put(fnode.NextEmptyID())
    return fnode.ID

def createElem(loc1, loc2, propId):
    node1 = createNodeAtLocation(loc1)
    node2 = createNodeAtLocation(loc2)
    felem = femap.feElem
    felem.type = feConstants.FET_L_BEAM
    felem.topology = 0
    felem.propID = propId
    felem.SetNode(0, node1)
    felem.SetNode(1, node2)

    felem.Setorient(0, 0) #vec2(0)
    felem.Setorient(1, 0) #vec2(1)
    felem.Setorient(2, 1) #vec2(2)

    rc = felem.Put(felem.NextEmptyID())
    femap.feViewRegenerate(0)
    return 1

def pointsDistance(coord1, coord2):
    point1 = np.array(coord1)
    point2 = np.array(coord2)
    return np.linalg.norm(point1 - point2)

def getEntityTitleById(id, entityType):
    if entityType == feConstants.FT_MATL:
        fmat = femap.feMatl
        rc = fmat.Get(id)
        return fmat.title
    elif entityType == feConstants.FET_PROPERTY:
        fprop = femap.feProp
        rc = fprop.Get(id)
        return fprop.title
    return None

def getActiveMatlIdAndTitle():
    fmat = femap.feMatl    
    id = fmat.Active
    if (id == 0):
        femap.feAppMessageBox(0,"Activate Material and run again." )
        return
    rc = fmat.Get(id)
    return {"id": id, "title": fmat.title}

def getAllPropIdsTitles():
    fprop = femap.feProp
    rc, numProp, propIds, exist, proptype, mid, extramid, layer, color, layupID, refCSys, titles = fprop.GetAllArray(0) #first 0 - means retreive all props
    return {"id": propIds, "title": titles}

def getPropIdByTitle(title):
    allPropIdsTitles = getAllPropIdsTitles()
    index = allPropIdsTitles["title"].index(title) if title in allPropIdsTitles["title"] else -1
    if (index >= 0):
        return allPropIdsTitles["id"][index]

def createBeamCylProp(endsGeom, matl):
    mmThkFirstEnd = round(endsGeom[0]['thk'] * 1000)
    mmDiaFirstEnd = round(endsGeom[0]['radius'] * 2 * 1000)
    propTitle = f'''TUBE - {mmDiaFirstEnd}x{mmThkFirstEnd} ({matl["title"]})'''
    existPropId = getPropIdByTitle(propTitle)
    if existPropId:
        femap.feAppMessage(1,"!!!CHECK!!! TO BE USED PROP: " + str(existPropId))
        return existPropId

    fprop = femap.feProp
    rc = fprop.Last()
    newId = fprop.ID + 1
    femap.feAppMessage(1,"!!!CHECK!!! NEW PROP TO BE CREATED: " + propTitle )

    myProp = femap.feProp
    myProp.matlID = matl["id"]
    myProp.title = propTitle
    myProp.type = feConstants.FET_L_BEAM
    rc = myProp.SetflagI(1, feConstants.FSHP_CIRC_TUBE)# = 6 #feConstants.FSHP_CIRC_TUBE

    computeOnlyOneEnd = True
    shapeID = feConstants.FSHP_CIRC_TUBE
    dimensions = [endsGeom[0]['radius'], 0, 0, 0, 0, endsGeom[0]['thk']] #[0.139, 0, 0, 0, 0, 0.012]
    EvalMethod = 1 #0=Auto, 1=Orig-inal, 2=Alternate, 3=Nastran PBEAML
    shear_center_offset = False
    Warping = False
    stress_recovery = False
    rc = myProp.ComputeStdShape2(computeOnlyOneEnd, shapeID, dimensions, feConstants.FSOR_RIGHT, EvalMethod, shear_center_offset, Warping, stress_recovery)
    myProp.Put(newId)
    return myProp.ID

def createBeamConeProp(endsGeom, matl):
    mmThkFirstEnd = round(endsGeom[0]['thk'] * 1000)
    mmThkSecondEnd = round(endsGeom[1]['thk'] * 1000)
    mmDiaFirstEnd = round(endsGeom[0]['radius'] * 2 * 1000)
    mmDiaSecondEnd = round(endsGeom[1]['radius'] * 2 * 1000)
    mmLength = round(pointsDistance(endsGeom[0]['center'], endsGeom[1]['center']) * 1000)
    propTitle = f'''CONE - {mmDiaFirstEnd}x{mmThkFirstEnd}/{mmDiaSecondEnd}x{mmThkSecondEnd} - L{mmLength} ({matl["title"]})'''
    existPropId = getPropIdByTitle(propTitle)
    if existPropId:
        femap.feAppMessage(1,"!!!CHECK!!! TO BE USED PROP: " + str(existPropId))
        return existPropId
    
    fprop = femap.feProp
    rc = fprop.Last()
    newId = fprop.ID + 1
    femap.feAppMessage(1,"!!!CHECK!!! NEW PROP TO BE CREATED: " + propTitle )

    myProp = femap.feProp
    myProp.matlID = matl["id"] #401  # 1 - Steel
       
    #CONE - 2850x70/220x70 - L2250      TUBE - 2850x70
    myProp.title = propTitle
    myProp.type = feConstants.FET_L_BEAM

    rc = myProp.SetflagI(1, feConstants.FSHP_CIRC_TUBE)# = 6 #feConstants.FSHP_CIRC_TUBE
    rc = myProp.SetflagI(0, 1) # Tapered beam flag
    # rc = myProp.Setpval(40, 0.139)
    # rc = myProp.Setpval(45, 0.012)

    computeOnlyOneEnd = True
    shapeID = feConstants.FSHP_CIRC_TUBE
    dimensions = [endsGeom[0]['radius'], 0, 0, 0, 0, endsGeom[0]['thk']] #[0.139, 0, 0, 0, 0, 0.012]
    EvalMethod = 1 #0=Auto, 1=Orig-inal, 2=Alternate, 3=Nastran PBEAML
    shear_center_offset = False
    Warping = False
    stress_recovery = False
    rc = myProp.ComputeStdShape2(computeOnlyOneEnd, shapeID, dimensions, feConstants.FSOR_RIGHT, EvalMethod, shear_center_offset, Warping, stress_recovery)
    dimensions = [endsGeom[1]['radius'], 0, 0, 0, 0, endsGeom[1]['thk']] #[0.159, 0, 0, 0, 0, 0.016]
    computeOnlyOneEnd = False
    rc = myProp.ComputeStdShape2(computeOnlyOneEnd, shapeID, dimensions, feConstants.FSOR_RIGHT, EvalMethod, shear_center_offset, Warping, stress_recovery)
    myProp.Put(newId)
    return myProp.ID

# def findReqdPropId(title): #PAUSED ON THIS FUNCTION
#     fprop = femap.feProp
#     rc = fprop.AreDuplicate ( nProp1, nProp2, ignoretitle )
#     rc, id = fprop.Find(title)
#     return id

def getSolidConeSurfaces(solidGeomId):
    solid = femap.feSolid
    rc = solid.Get(solidGeomId)
    rc, numsrfs, surfIds = solid.Surfaces(2) # 2=List contains both theunderlying and combined surfaces

    StandartNumSurfaces = 6
    if numsrfs != StandartNumSurfaces:
        femap.feAppMessageBox(feConstants.FCM_HIGHLIGHT, f"Solid {solidGeomId} has {numsrfs} surfaces, expected {StandartNumSurfaces}")
        return []
    
    endSurfaces = getEndSurfaces(surfIds)
    endsGeom = []
    if len(endSurfaces) != 2:
        femap.feAppMessageBox(feConstants.FCM_HIGHLIGHT, f"Solid {solidGeomId} has {len(endSurfaces)} end surfaces, expected 2")
        return []
    for endSurfId in endSurfaces:
        endsGeom.append(getEndGeometryBySurface(endSurfId))
    print(endsGeom)
    return endsGeom

def getEndGeometryBySurface(surfId):
    surf = femap.feSurface
    rc = surf.Get(surfId)
    # rc, pdConcaveRadius, pdConvexRadius, pbIsPlanar = surf.MinRadiiOfCurvature()
    rc, numCurves, curveIDs = surf.Curves(nCombinedMode = 2)
    curve = femap.feCurve
    biggerRad = -1
    smallerRad = 10e+6
    center = -1.0
    for curveId in curveIDs:
        rc = curve.Get(curveId)
        if curve.IsArc() == -1:
            rc, center, normal, startPt, endPt, angle, radius = curve.ArcCircleInfo()
            if radius > biggerRad:
                biggerRad = radius
            if radius < smallerRad:
                smallerRad = radius
    # biggerRad = oneRad if oneRad >= secondRad else secondRad
    thk = biggerRad - smallerRad
    return {
        'center': center,
        'radius': biggerRad,
        'thk': thk
    }

def getEndSurfaces(surfIds):
    endSurfaces = []
    for surfId in surfIds:
        surf = femap.feSurface
        rc = surf.Get(surfId)
        if surf.IsPlane() == -1:
            endSurfaces.append(surfId)
    return endSurfaces

def getOneConeEndGeom():
    return {}

def selectOneSolid():
    # solidSelector = femap.feSelector
    # solidSelector.MultipleMode = False
    # solidSelector.SelectEntity = feConstants.FT_SOLID 39
    solidSet = femap.feSet
    rc = -1
    while rc == -1:
        rc, id = solidSet.SelectID(feConstants.FT_SOLID, 'Select Conical or Tubular Solig')
        if id > 0:
            processSingleSolid(id)

def updatePropTitles(propSet):
    femap.feViewRegenerate(0)
    fProp = femap.feProp
    propSet.Debug()
    while propSet.Next():
        rc = fProp.Get(propSet.CurrentID)
        if "Tube" in fProp.title:
            matlTitle = getEntityTitleById(fProp.matlID, feConstants.FT_MATL)
            dia = round(fProp.pval(40) * 1000 * 2)
            thks = round(fProp.pval(45) * 1000)
            fProp.title = f'''TUBE - {dia}x{thks} ({matlTitle})'''
            rc = fProp.Put(fProp.ID)
    femap.feViewRegenerate(0)

def processTubularSolidsByFemapAlgo(solidIds, materialId):
    print("tubes = ", solidIds)
    solidsSet = femap.feSet
    solidsSet.AddArray(len(solidIds), solidIds)
    rc = femap.feSolidExtractCenterlines(solidsSet.ID, materialId, True)
    if rc != -1:
        solidsSet.Debug()
        femap.feAppMessageBox(feConstants.FCM_ERROR, f"Cannot extract centerlines for solids")
        return None

def getBiggestSurfaceAreaField(areas):
    biggestArea = 0
    biggestField = ''
    for field, area in areas.items():
        if area > biggestArea:
            biggestArea = area
            biggestField = field
    return { biggestField: biggestArea }

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
            # shape_type = SHAPE_TYPES['cone']
            areas['cone'] += area
        elif (surf.IsCylinder() == -1):
            # shape_type = SHAPE_TYPES['cylinder']
            areas['cylinder'] += area
        elif (surf.IsPlane() == -1):
            # shape_type = SHAPE_TYPES['plane']
            areas['plane'] += area
        else:
            # shape_type = SHAPE_TYPES['other']
            areas['other'] += area
    biggestShapeArea = getBiggestSurfaceAreaField(areas)
    return list(biggestShapeArea.keys())[0]

def femapStartTrackProperty():
    tracker = femap.feTrackData
    rc = tracker.Start(feConstants.FT_PROP)
    if rc == -1:
        femap.feAppMessage(feConstants.FCM_HIGHLIGHT, "Tracking of Properties started successfully")
        return tracker
    else:
        femap.feAppMessageBox(feConstants.FCM_ERROR, "Failed to start property tracking")
        return None

def femapStartTrackGeometry():
    tracker = femap.feTrackData
    rc = tracker.StartGeometry()
    if rc == -1:
        femap.feAppMessage(feConstants.FCM_HIGHLIGHT, "Tracking geometry started successfully")
        return tracker
    else:
        femap.feAppMessageBox(feConstants.FCM_ERROR, "Failed to start geometry tracking")
        return None

def getFemapCreatedPropSet(tracker):
    fSet = femap.feSet
    rc = tracker.Created(feConstants.FT_PROP, fSet.ID, True)
    if rc == -1:
        fSet.Debug()
        return fSet
    else:
        femap.feAppMessageBox(feConstants.FCM_ERROR, "Failed to get created property set")
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

def getSetOfSolidsByGroup(groupId):
    mySet = femap.feSet
    rc = mySet.AddGroup(feConstants.FT_SOLID, groupId)
    if rc != -1 or mySet.Count == 0:
        femap.feAppMessageBox(feConstants.FCM_NORMAL, f"Set of solids for group {groupId} is empty or not found")
        return None
    return mySet

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

def regenerateFemapView():
    femap.feViewRegenerate(0)

def getPerpindicularVectorByLocations(loc1, loc2): #TODO
    return 1
