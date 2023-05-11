from typing import Optional
import c4d
from math import pi

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

#rounding angle
ROUND = 3

def selectContour(op):

    nb = c4d.utils.Neighbor()
    nb.Init(op)
    bs = op.GetSelectedEdges(nb,c4d.EDGESELECTIONTYPE_SELECTION)
    bs.DeselectAll()
    for i,poly in enumerate(op.GetAllPolygons()):
        inf = nb.GetPolyInfo(i)
        if nb.GetNeighbor(poly.a, poly.b, i)==-1:
            bs.Select(inf['edge'][0])

        if nb.GetNeighbor(poly.b, poly.c, i)==-1:
            bs.Select(inf['edge'][1])


        #si pas triangle
        if not poly.c == poly.d :
            if nb.GetNeighbor(poly.c, poly.d, i)==-1:
                bs.Select(inf['edge'][2])

        if nb.GetNeighbor(poly.d, poly.a, i)==-1:
            bs.Select(inf['edge'][3])

    op.SetSelectedEdges(nb,bs,c4d.EDGESELECTIONTYPE_SELECTION)

def edge2spline(op):

    res = c4d.utils.SendModelingCommand(command = c4d.MCOMMAND_EDGE_TO_SPLINE,
                                    list = [op],
                                    mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION,
                                    doc = doc)
    return op.GetDown()



def getSplineAngles(sp) -> None:
    #trouver les points avec un angle à 90°
    angles = []
    pts = [c4d.Vector(p.x,0,p.z)for p in op.GetAllPoints()]
    pred = pts[-1]
    nxt = pts[1]
    for i,p in enumerate(pts):
        v1 = pred-p
        v2 = nxt-p
        angle = c4d.utils.GetAngle(v1, v2)
        if round(angle,ROUND)==round(pi/2,ROUND):
            angles.append(i)
        pred = p
        if i==(len(pts)-2):
            nxt = pts[0]
        elif i==(len(pts)-1):
            continue
        else:
            nxt = pts[i+2]
    return angles

def main() -> None:

    #if no object selected
    if op is None:
        c4d.gui.MessageDialog('Please select an object.')
        return

    #if not polygonal object
    if not op.CheckType(c4d.Opolygon):
        c4d.gui.MessageDialog('Please select a polygonal object.')
        return

    #optimization
    c4d.utils.SendModelingCommand(command = c4d.MCOMMAND_OPTIMIZE,
                                    list = [op],
                                    mode = c4d.MODELINGCOMMANDMODE_POINTSELECTION,
                                    doc = doc)

    #select contour
    selectContour(op)

    #edge to spline
    sp = edge2spline(op)

    #optimize spline
    c4d.utils.SendModelingCommand(command = c4d.MCOMMAND_OPTIMIZE,
                                    list = [sp],
                                    mode = c4d.MODELINGCOMMANDMODE_POINTSELECTION,
                                    doc = doc)

    #unfold the object
    op.DelBit(c4d.BIT_OFOLD)

    #get spline angles
    angles = getSplineAngles(sp)
    print(angles)

    c4d.EventAdd()


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()