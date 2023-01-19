from typing import Optional
import c4d

"""Sélectionner le ou les plans pour générer les splines à quatre points
   l'axe est orienté selon le sens des deux premiers points"""

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected


def get_spline_from_plane(obj):
    pts = [c4d.Vector(p*obj.GetMg()) for p in obj.GetAllPoints()]

    if len(pts)<3 :
        print('pas assez de points')
        return
    p1,p2,*r = pts

    p1.y = 0
    p2.y = 0

    off = c4d.Vector(p1)
    v1 = (p2-p1).GetNormalized()

    if v1 == c4d.Vector(0):
        print('pas conforme')
        return
    if v1.y :
        print('pas horizontal')
        return

    v2 = c4d.Vector(0,1,0)
    v3 = v1.Cross(v2)

    mg = c4d.Matrix(off,v1,v2,v3)

    #onull = c4d.BaseObject(c4d.Onull)
    #onull.SetMg(mg)
    #doc.InsertObject(onull)

    #

    pts = [p*~mg for p in pts]

    xmin = min([p.x for p in pts])
    xmax = max([p.x for p in pts])
    zmin = min([p.z for p in pts])
    zmax = max([p.z for p in pts])

    sp = c4d.SplineObject(4,c4d.SPLINETYPE_LINEAR)
    sp.SetAllPoints([c4d.Vector(xmin,0,zmin),c4d.Vector(xmax,0,zmin),c4d.Vector(xmax,0,zmax),c4d.Vector(xmin,0,zmax)])
    sp[c4d.SPLINEOBJECT_CLOSED] = True
    sp.SetMg(mg)
    sp.SetName(obj.GetName())
    return sp


def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    
    doc.StartUndo()
    pred = None
    for obj in doc.GetActiveObjects(0):
        if not obj.CheckType(c4d.Opoint):
            obj = op.GetCache()
            if not obj :
                print(f'{obj.GetName()} -> pas objet point')
                break
        sp = get_spline_from_plane(obj)
        doc.InsertObject(sp,pred = pred)
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, sp)
        pred = sp
    c4d.EventAdd()
    doc.EndUndo()
    return
    
    pts = [c4d.Vector(p*obj.GetMg()) for p in obj.GetAllPoints()]

    if len(pts)<3 :
        print('pas assez de points')
        return
    p1,p2,*r = pts

    p1.y = 0
    p2.y = 0

    off = c4d.Vector(p1)
    v1 = (p2-p1).GetNormalized()

    if v1 == c4d.Vector(0):
        print('pas conforme')
        return
    if v1.y :
        print('pas horizontal')
        return

    v2 = c4d.Vector(0,1,0)
    v3 = v1.Cross(v2)

    mg = c4d.Matrix(off,v1,v2,v3)
    print(mg)

    #onull = c4d.BaseObject(c4d.Onull)
    #onull.SetMg(mg)
    #doc.InsertObject(onull)

    #

    pts = [p*~mg for p in pts]

    xmin = min([p.x for p in pts])
    xmax = max([p.x for p in pts])
    zmin = min([p.z for p in pts])
    zmax = max([p.z for p in pts])

    sp = c4d.SplineObject(4,c4d.SPLINETYPE_LINEAR)
    sp.SetAllPoints([c4d.Vector(xmin,0,zmin),c4d.Vector(xmax,0,zmin),c4d.Vector(xmax,0,zmax),c4d.Vector(xmin,0,zmax)])
    sp[c4d.SPLINEOBJECT_CLOSED] = True
    sp.SetMg(mg)
    doc.InsertObject(sp)

    c4d.EventAdd()






    return


    pts = [c4d.Vector(p) for p in op.GetAllPoints()]
    sp = c4d.SplineObject(len(pts), c4d.SPLINETYPE_LINEAR)
    sp.SetAllPoints(pts)
    sp.SetMg(op.GetMg())
    sp.Message(c4d.MSG_UPDATE)
    doc.InsertObject(sp)
    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()