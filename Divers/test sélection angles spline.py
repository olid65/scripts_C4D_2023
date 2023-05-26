from typing import Optional
import c4d
from math import pi

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    bs = op.GetPointS()
    bs.DeselectAll()
    mg = op.GetMg()
    pts = [p*mg for p in op.GetAllPoints()]
    pts2d = [c4d.Vector(p.x,0,p.z) for p in pts]
    
    nb_pts = len(pts2d)
    
    pred = pts2d[-1]
    
    for i,p in enumerate(pts2d):
        if i == nb_pts-1 : i=0
        nxt =pts2d[i+1]
        v1 = pred-p
        v2 = nxt-p
        
        #Si la distance est trop courte on a un problème
        #ATTENTION s'il y a des points trop proches dans les angles
        #Cela va poser un problème !!!!!!!!!!!
        #TODO -> régler ce cas
        if v2.GetLength()<0.1:
            continue
        
        angle = round(c4d.utils.GetAngle(v1,v2),2)
        if angle < 3.14:
            print(i, angle)
            bs.Select(i)
        
        
        pred = p
        
    c4d.EventAdd()
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()