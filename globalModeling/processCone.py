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

def processConeGeom(solidGeomId):
    endsGeom = getSolidConeSurfaces(solidGeomId)
    #femap.feAppMessageBox(0, f'''{round(endsGeom[0]["radius"]*1000)} {round(endsGeom[1]["radius"]*1000)}''' )
    if (round(endsGeom[0]["radius"]*1000) == round(endsGeom[1]["radius"]*1000)):
        #femap.feAppMessageBox(0,"Cylinder detected" )
        propId = createBeamCylProp(endsGeom)
    else:
        propId = createBeamConeProp(endsGeom)
    
    elemId = createElem(endsGeom[0]['center'], endsGeom[1]['center'], propId)
    return {}

def createNodeAtLocation(loc):
    fnode = femap.feNode
    fnode.xyz = loc
    # fnode.y = loc[1]
    # fnode.z = loc[2]
    rc = fnode.Put(fnode.NextEmptyID())
    # print(rc)
    # print(fnode.ID)
    # femap.feViewRegenerate(0)
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

#    95720
#    95721
    #print('nextID ', felem.NextEmptyID())
    rc = felem.Put(felem.NextEmptyID())
    print(rc)
    print(felem.ID)
    femap.feViewRegenerate(0)
    return 1

def pointsDistance(coord1, coord2):
    point1 = np.array(coord1)
    point2 = np.array(coord2)
    return np.linalg.norm(point1 - point2)

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
    # print('ALLPROP: ', numProp, title)

def getPropIdByTitle(title):
    allPropIdsTitles = getAllPropIdsTitles()
    index = allPropIdsTitles["title"].index(title) if title in allPropIdsTitles["title"] else -1
    print('index: ', index, allPropIdsTitles["id"][index])
    if (index >= 0):
        return allPropIdsTitles["id"][index]

def createBeamCylProp(endsGeom):
    mmThkFirstEnd = round(endsGeom[0]['thk'] * 1000)
    mmDiaFirstEnd = round(endsGeom[0]['radius'] * 2 * 1000)
    mmLength = round(pointsDistance(endsGeom[0]['center'], endsGeom[1]['center']) * 1000)
    matl = getActiveMatlIdAndTitle()
    propTitle = f'''TUBE - {mmDiaFirstEnd}x{mmThkFirstEnd} - L{mmLength} ({matl["title"]})'''
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
    #rc = myProp.SetflagI(0, 1) # Tapered beam flag

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

def createBeamConeProp(endsGeom):
    mmThkFirstEnd = round(endsGeom[0]['thk'] * 1000)
    mmThkSecondEnd = round(endsGeom[1]['thk'] * 1000)
    mmDiaFirstEnd = round(endsGeom[0]['radius'] * 2 * 1000)
    mmDiaSecondEnd = round(endsGeom[1]['radius'] * 2 * 1000)
    mmLength = round(pointsDistance(endsGeom[0]['center'], endsGeom[1]['center']) * 1000)
    matl = getActiveMatlIdAndTitle()
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
       
     # "Cone1python" #CONE - 2850x70/220x70 - L2250      TUBE - 2850x70 - L3600
    myProp.title = propTitle
    myProp.type = feConstants.FET_L_BEAM

    #rc = myProp.Put(newId)#newId)  
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
    print(rc)
    myProp.Put(newId)
    return myProp.ID

def getPropNumber(propTitle):
    return 1


def findReqdPropId(title): #PAUSED ON THIS FUNCTION
    fprop = femap.feProp
    rc = fprop.AreDuplicate ( nProp1, nProp2, ignoretitle )
    rc, id = fprop.Find(title)
    return id

def getSolidConeSurfaces(solidGeomId):
    solid = femap.feSolid
    rc = solid.Get(solidGeomId)
    
    rc, numsrfs, surfIds = solid.Surfaces(2)

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
    # print('check end!!! of surface', surfId)
    surf = femap.feSurface
    rc = surf.Get(surfId)
    # rc, pdConcaveRadius, pdConvexRadius, pbIsPlanar = surf.MinRadiiOfCurvature()
    # print (pdConcaveRadius, pdConvexRadius, pbIsPlanar, rc, surfId)
    rc, numCurves, curveIDs = surf.Curves(nCombinedMode = 2)
    # print(curveIDs)
    curve = femap.feCurve
    biggerRad = -1
    smallerRad = 10e+6
    center = -1.0
    for curveId in curveIDs:
        rc = curve.Get(curveId)
        if curve.IsArc() == -1:
            rc, center, normal, startPt, endPt, angle, radius = curve.ArcCircleInfo()
            # print('arcCircle: ', 'curveId = ', curve.ID, center, radius)
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
            # return {
            #     'center': center,
            #     'radius': radius
            # }

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

def selectConeSolid():
    # solidSelector = femap.feSelector
    # solidSelector.MultipleMode = False
    # solidSelector.SelectEntity = feConstants.FT_SOLID 39
    solidSet = femap.feSet
    print(solidSet.ID)
    rc = -1
    while rc == -1:
        rc, id = solidSet.SelectID(feConstants.FT_SOLID, 'Select cone solig geom') #39
        print(rc, id)
        if id > 0:
            processConeGeom(id) #1440

# selectConeSolid()