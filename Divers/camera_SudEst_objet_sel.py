from typing import Optional
import c4d
from math import tan

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    cam = c4d.BaseObject(c4d.Ocamera)
    angle_h_cam = cam[c4d.CAMERAOBJECT_FOV]
    #position
    mg = op.GetMg()
    centre = op.GetMp()*mg
    rad = op.GetRad()
    ppt_SudEst = c4d.Vector(centre.x + rad.x, centre.y, centre.z - rad.x ) 
    
    demi_diagonale = centre-ppt_SudEst
    dist = demi_diagonale.GetLength()
    print(dist)
    dist_perp = tan(angle_h_cam/2)/dist
    perpendiculaire = demi_diagonale.Cross(c4d.Vector(0,1,0)).GetNormalized()
    print(perpendiculaire)
    print(dist_perp)
    pos_cam = centre + perpendiculaire * dist*2
    print(pos_cam)
    cam.SetAbsPos(pos_cam)
    
    
    
    
    doc.InsertObject(cam)
    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()