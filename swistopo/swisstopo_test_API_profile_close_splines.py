from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    for sp in doc.GetActiveObjects(0):
        pts = [c4d.Vector(p) for p in sp.GetAllPoints()]
        #clone = op.GetClone()
        pt_dbt = c4d.Vector(pts[0])
        pt_dbt.y = 0
        pts.insert(0,pt_dbt)
        
        pt_fin = c4d.Vector(pts[-1])
        pt_fin.y = 0
        pts.append(pt_fin)
        
        sp.ResizeObject(len(pts),0)
        sp.SetAllPoints(pts)
        sp[c4d.SPLINEOBJECT_CLOSED] = True
        sp.Message(c4d.MSG_UPDATE)
    c4d.EventAdd()
    
    
    
    

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()