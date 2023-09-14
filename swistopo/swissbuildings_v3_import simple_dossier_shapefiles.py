from typing import Optional
import c4d
import os
import shapefile as shp
from pathlib import Path

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

CONTAINER_ORIGIN = 1026473

def import_swissbuildings3D_v3_shape(fn,doc):

    r = shp.Reader(str(fn))

    xmin,ymin,xmax,ymax = r.bbox
    centre = c4d.Vector((xmin+xmax)/2,0,(ymax+ymin)/2)

    origin = doc[CONTAINER_ORIGIN]
    if not origin :
        doc[CONTAINER_ORIGIN] = centre
        origin = centre


    # géométries
    shapes = r.shapes()

    pts = []
    polys = []

    id_pt = 0
    id_poly = 0

    nbre = 0
    for shape in shapes:
        xs = [x for x,y in shape.points]
        zs = [y for x,y in shape.points]
        ys = [z for z in shape.z]

        pts_shp = [c4d.Vector(x,z,y)-origin for (x,y),z in zip(shape.points,shape.z)]
        pts+= pts_shp
        nb_pts = len(pts_shp)

        pred = 0
        for i in shape.parts:
            if pred:
                nb_pts_poly = i-pred

            poly = c4d.CPolygon(i+id_pt,i+1+id_pt,i+2+id_pt,i+3+id_pt)
            polys.append(poly)
            pred = i
        id_pt+=len(pts_shp)

    nb_pts = len(pts)
    if nb_pts:
        po =c4d.PolygonObject(nb_pts,len(polys))
        po.SetName(fn.parent.name)
        #TODO : tag phong !
        po.SetAllPoints(pts)
        for i,poly in enumerate(polys):
            po.SetPolygon(i,poly)

        #po.SetAbsPos(axe-origin)
        po.Message(c4d.MSG_UPDATE)
    else:
        print(f'pas depoints : {fn.parent.name}')
        return None
    return po

def main() -> None:
    #pth = Path('/Volumes/My Passport Pro/TEMP/Coteaux_dores/swisstopo/swissbuildings3d_v3/shapefiles')

    #chemin du document actif
    pth = Path(doc.GetDocumentPath())
    if not pth:
        c4d.gui.MessageDialog('Document non enregistré')
        return
    pth = pth / 'swisstopo' / 'swissbuildings3d_v3' / 'shapefiles'
    if not pth.exists():
        print(f'pas de dossier {pth.name}')

    res = c4d.BaseObject(c4d.Onull)
    doc.InsertObject(res)
    res.SetName(pth.parent.name)
    for fn in pth.rglob('*Building_solid.shp'):
        p = import_swissbuildings3D_v3_shape(fn,doc)
        if p:
            p.InsertUnderLast(res)

    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()