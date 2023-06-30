from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    bd = doc.GetRenderBaseDraw()
    cam = bd.GetSceneCamera(doc)
    
    bs = op.GetPointS()
    bs.DeselectAll()
    
    
    for i,p in enumerate(op.GetAllPoints()):
        pt = bd.WS(p)
        if bd.TestPoint(pt.x,pt.y): bs.Select(i)
        
    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()