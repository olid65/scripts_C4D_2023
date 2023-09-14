from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

CONTAINER_ORIGIN = 1026473
FACTEUR_DIV = 4


def main() -> None:
    # récupération de l'origine du document
    #origine = doc[CONTAINER_ORIGIN]
    # récupération de la bbox de l'objet
    mg = op.GetMg()
    rad = op.GetRad()
    centre = op.GetMp()
    # 4 points de la bbox selon orientation de l'objet
    pts =  [c4d.Vector(centre.x - rad.x, 0, centre.z + rad.z) * mg ,
            c4d.Vector(centre.x + rad.x, 0, centre.z + rad.z) * mg ,
            c4d.Vector(centre.x + rad.x, 0, centre.z - rad.z) * mg ,
            c4d.Vector(centre.x - rad.x, 0, centre.z - rad.z) * mg ]
    largeur = (pts[2].x-pts[0].x) / FACTEUR_DIV
    hauteur = (pts[2].z - pts[0].z) / FACTEUR_DIV
    pos = c4d.Vector(pts[0].x, 0, pts[0].z)

    res = c4d.BaseObject(c4d.Onull)
    res.SetName("splines")
    doc.InsertObject(res)

    id_obj = 1
    #création des splines découpées
    for i in range(FACTEUR_DIV):
        for n in range(FACTEUR_DIV):
            spline = c4d.SplineObject(4, c4d.SPLINETYPE_LINEAR)
            pts_sp =   [c4d.Vector(0, 0, 0),
                        c4d.Vector(largeur, 0, 0),
                        c4d.Vector(largeur, 0, hauteur),
                        c4d.Vector(0, 0, hauteur)]
            spline.SetAllPoints(pts_sp)
            spline[c4d.SPLINEOBJECT_CLOSED] = True
            spline.SetAbsPos(pos)
            spline.InsertUnderLast(res)
            spline.SetName("spline_" + str(id_obj).zfill(2))
            id_obj += 1

            pos.x += largeur
        pos.z += hauteur
        pos.x = pts[0].x

    c4d.EventAdd()





"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()