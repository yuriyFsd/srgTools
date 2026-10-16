
import sys
import pythoncom
import Pyfemap
import ctypes # for Windows
from Pyfemap import constants as feConstants
import member
import utils

def femapConnect() -> Pyfemap.model:
    try:
        existObj = pythoncom.connect(Pyfemap.model.CLSID)
        global femap
        femap = Pyfemap.model(existObj)
        rc = femap.feAppMessage(feConstants.FCM_NORMAL, "Connected!")
    except Exception as error:
        print(error)
        ctypes.windll.user32.MessageBoxW(0,"Can't connect to Femap API Server", "Error", 1)
        
        sys.exit("Can't connect to Femap API Server ")
    return femap

def getActiveGroup() -> femap.Group:
    fGroup: femap.Group = femap.feGroup
    rc = fGroup.Get(fGroup.Active)
    return fGroup

def _getElementalSecondNode(elem_id: int, known_node_id: int) -> int:
    f_elem = femap.feElem
    rc = f_elem.Get(elem_id)
    elem_nodes = f_elem.vnode  # list/array of node IDs
    for node_id in elem_nodes:
        if node_id != 0 and node_id != known_node_id:
            return node_id
    return 0  # if no second node found

def _getNextElementOfMember(elem_id, group_elems_set, prev_elem_id=0) -> list:
    next_elem: femap.elem = femap.feElem
    curr_elem: femap.elem = femap.feElem
    rc = curr_elem.Get(elem_id)

    elem_nodes = curr_elem.vnode  # array of node IDs
    nodal_elem_set = femap.feSet
    first_node = 0
    nodes_counter = 0
    for ni, node in enumerate(elem_nodes):
        if node != 0:
            nodes_counter += 1
            rc = nodal_elem_set.Clear()
            rc = nodal_elem_set.AddRule(node, FGD_ELEM_BYNODE)
            while nodal_elem_set.Next():
                next_elem_id = nodal_elem_set.CurrentID
                # Skip invalid candidates
                if group_elems_set.IsAdded(next_elem_id) != feConstants.FE_OK: continue
                if next_elem_id == elem_id: continue
                if next_elem_id == prev_elem_id: continue
                rc = next_elem.Get(next_elem_id)

                if next_elem.Type != feConstants.FET_L_BEAM: continue
                if next_elem.propId != curr_elem.propId: continue
                if (next_elem.orient[0] != curr_elem.orient[0] and
                    next_elem.orient[1] != curr_elem.orient[1] and
                    next_elem.orient[2] != curr_elem.orient[2]):
                    continue
                last_node = _getElementalSecondNode(int(next_elem_id), int(node))
                first_node = _getElementalSecondNode(elemId, elem_nodes(ni)) if (ni == 0 or (prev_elem_id > 0 and ni == 1)) else first_node
                if first_node == 0 and nodes_counter == 2:
                    first_node = _getElementalSecondNode(int(elem_id), int(node))

                return [next_elem_id, first_node, last_node]

    # Not in member
    check_if_element_below_to_member = 0
    return [0, 0]

def get_single_elem_2_nodes(elem_id: int) -> list:
    f_elem = femap.feElem
    rc = f_elem.Get(elem_id)
    elem_nodes = f_elem.vnode
    nodes = []
    for elem_node in elem_nodes:
        if elem_node > 0:
            nodes.append(elem_node)
            if len(nodes) == 2:
                return nodes
    return nodes 


def get_member_fem(group_elems_set: femap.Set, is_second_search_direction: bool, prev_direction_2nd_elem: int = 0) -> dict: 
    elems_of_member = [group_elems_set.First]
    prev_elem_id = 0

    if is_second_search_direction: prev_elem_id = prev_direction_2nd_elem

    i = 0
    last_node_id = 0
    first_node_id = 0
    member = {
        "end-nodes": [],
        "elements": []
    }
    while True:
        if i > 0: prev_elem_id = elems_of_member[i - 1]

        new_elem_id_node_id_of_member = _getNextElementOfMember(
            int(elems_of_member[i]),
            group_elems_set,
            prev_elem_id
        )

        if new_elem_id_node_id_of_member[0]:
            i += 1
            elems_of_member.append(new_elem_id_node_id_of_member[0])

            first_node_id = new_elem_id_node_id_of_member[1] if i == 1 else first_node_id
            last_node_id = new_elem_id_node_id_of_member[2]
     
            member["end-nodes"] = [first_node_id, last_node_id]
            member["elements"] = elems_of_member
            rc = 1
        else:
            break

    # Handle single-element member case
    if len(member["elements"]) == 0 and not is_second_search_direction:
        member["end-nodes"] = get_single_elem_2_nodes(elems_of_member[0])
        member["elements"] = elems_of_member
        rc = 1

    return member


def get_geom_profile(member_elem_id: int) -> dict:
    f_beam = femap.feElem
    rc = f_beam.Get(member_elem_id)
    f_prop = femap.feProp
    rc = f_prop.Get(f_beam.propId)

    if f_prop.Type == feConstants.FET_L_BEAM:
        shape_flags = f_prop.vflagI
        shape_flag = f_prop.flagI(1)
        tapering_flag = f_prop.flagI(0)
        # elem_geom = {}
        elem_geom["material"] = f_prop.matlId

        if shape_flag == 6 and tapering_flag == 0:
            elem_geom["geomName"] = "circular-tube"
            elem_geom["radius"] = f_prop.pval(40)       # tube radius
            elem_geom["wall-thks"] = f_prop.pval(45)    # tube wall thickness
        elif shape_flag == 6 and tapering_flag == 1:
            elem_geom["geomName"] = "cone"              # FSHP_CIRC_TUBE
            elem_geom["wall-thks"] = f_prop.pval(45)    # tube wall thickness
            elem_geom["radius-a"] = f_prop.pval(40)     # tube end A radius
            elem_geom["radius-b"] = f_prop.pval(55)     # tube end B radius
        elif shape_flag == 9:  # H-profile
            elem_geom["geomName"] = "H-profile"
            elem_geom["height"] = f_prop.pval(40)              # H beam height
            elem_geom["top-flange-width"] = f_prop.pval(41)    # top flange width
            elem_geom["bottom-flange-width"] = f_prop.pval(42) # bottom flange width
            elem_geom["top-flange-thks"] = f_prop.pval(43)     # top flange thickness
            elem_geom["bottom-flange-thks"] = f_prop.pval(44)  # bottom flange thickness
            elem_geom["web-thks"] = f_prop.pval(45)            # web thickness
            return None
        else:
            return None
    else:
        return None
#         'sizes = circTubeSizes(fProp.id)
# 'Beam/Bar Sections: 1 = Rectangular
# 'Bar, 2 = Rectangular Tube, 3 =
# 'Trapezoidal Bar, 4 = Trapezoidal
# 'Tube, 5 = Circular Bar, 6 = Circular
# 'Tube, 7 = Hex Bar, 8 = Hex Tube, 9
# '= I, 10 = Channel, 11 = Angle, 12 =
# 't , 13 = Z, 14 = Hat, 15 = General
    return elem_geom


def getMemberGeometry(memberElems: list, nodes: list, sessionProps: dict) -> int:
    elemGeomProfile: dict = getGeomProfile(memberElems[0])

    pass

def collectMemberElementsByActiveGroup():
    femapConnect()
    activeGroup: femap.Group = getActiveGroup()
    fSet: femap.Set = femap.feSet
    rc = fSet.AddGroup(feConstants.FT_ELEM, activeGroup.ID)
    sessionProps = {}
    # member = {}
    # member("end-nodes") = []
    # member("elements") = []
    while fSet.count > 0:
        isSecondSearchDirection = False
        memberFem: dict = get_member_fem(fSet, isSecondSearchDirection)

        if len(memberFem["elements"]) >= 1:
            isSecondSearchDirection = True
            memberFem_2ndDir: dict = get_member_fem(
                fSet,
                isSecondSearchDirection,
                memberFem["elements"][1]
            )

        if memberFem_2ndDir and len(memberFem_2ndDir["elements"]) > 0:
             memberFem["elements"] = utils.merge_two_arrays(memberFem["elements"], memberFem_2ndDir("elements"), True)
             memberFem["end-nodes"] = [memberFem("end-nodes")(1), memberFem_2ndDir("end-nodes")(1)]

        memberSolidId = getMemberGeometry(memberFem("elements"), memberFem("end-nodes"), sessionProps)
