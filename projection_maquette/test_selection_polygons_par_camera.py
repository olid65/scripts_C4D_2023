from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

"""Mettre les caméras en haut de la liste des objets et sélectionner l'objet polygonal"""

# From https://code.vonc.fr/selections
# Merci à César Vonc !
def CalculeNormalesPolys(obj) :

    """
        Calcule les normales des polys de l'objet.

        Paramètres :
            obj (PolygonObject) - Objet

        Renvoie :
            (liste de Vector) - Liste des normales
    """

    polys = obj.GetAllPolygons()
    pts = obj.GetAllPoints()
    nbPolys = obj.GetPolygonCount()

    norPolys = [c4d.Vector()] * nbPolys
    nor = c4d.Vector()

    for i, poly in enumerate(polys) :
        nor = (pts[poly.a] - pts[poly.c]).Cross(pts[poly.b] - pts[poly.d])
        nor.Normalize()
        norPolys[i] = nor

    return norPolys

# From https://code.vonc.fr/selections
# Merci à César Vonc !
def CalculeCentrePolys(obj) :

    """
        Calcule le centre des polys de l'objet.

        Paramètres :
            obj (PolygonObject) - Objet

        Renvoie :
            (liste de Vector) - Liste des positions
    """

    polys = obj.GetAllPolygons()
    pts = obj.GetAllPoints()
    nbPolys = obj.GetPolygonCount()

    centrePolys = [c4d.Vector()] * nbPolys
    centre = c4d.Vector()

    for i, poly in enumerate(polys) :
        if poly.c != poly.d :
            centre = (pts[poly.a] + pts[poly.b] + pts[poly.c] + pts[poly.d]) / 4.
        else :
            centre = (pts[poly.a] + pts[poly.b] + pts[poly.c]) / 3.
        centrePolys[i] = centre

    return centrePolys

def main() -> None:
    
    lst_cam = []
    cam = doc.GetFirstObject()
    while cam.CheckType(c4d.Ocamera):
        lst_cam.append(cam)
        cam = cam.GetNext()
    
    if not lst_cam:
        c4d.gui.MessageDialog("Il faut mettre les caméras en haut de la hiérarchie d'objets")
        return
    if len(lst_cam)==1:
        c4d.gui.MessageDialog("Il n'y a qu'une caméra")
        return

    lst_cam_name_pos = [(cam.GetName(),cam.GetMg().off) for cam in lst_cam]
    #print(lst_cam_name_pos)

    polygon_object = op
    
    if not polygon_object.CheckType(c4d.Opolygon):
        c4d.gui.MessageDialog("Il faut sélectionner un objet polygonal")
        return

    centres_polys = CalculeCentrePolys(polygon_object)
    normales_polys = CalculeNormalesPolys(polygon_object)

    mg_poly = polygon_object.GetMg()

    dic_selections = {}

    for i,(centre,normale) in enumerate(zip(centres_polys,normales_polys)):
        centre = centre*mg_poly
        camera = None
        angle_min = 999999
        for cam,pos_cam in lst_cam_name_pos:
            angle_cam = (centre-pos_cam).GetNormalized()
            angle = c4d.utils.GetAngle(angle_cam, normale)
            if angle_min > angle :
                angle_min = angle
                camera = cam

        dic_selections.setdefault(camera,[]).append(i)
    
    for camera, lst in dic_selections.items():
        tag_selection = c4d.BaseTag(c4d.Tpolygonselection)
        tag_selection[c4d.ID_BASELIST_NAME] = camera
        bs = tag_selection.GetBaseSelect()
        bs.DeselectAll()
        for i in lst:
            bs.Select(i)
        op.InsertTag(tag_selection)
    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()