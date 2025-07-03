import sys
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

def getSoligGeom(id):  #1434 - just pipe
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

createBeamPipeProp()

arcCurve = femap.feCurve
rc = arcCurve.Get(32128)
getArcGeom(arcCurve)
rc = arcCurve.Get(32124)
getArcGeom(arcCurve)
32119
rc = arcCurve.Get(32119)
getArcGeom(arcCurve)
#getSoligGeom(1434)
