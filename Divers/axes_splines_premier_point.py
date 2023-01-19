from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def axeFirstPoint(sp):
    ml = sp.GetMl()
    pos_init = ml.off
    pos = c4d.Vector(sp.GetPoint(0))
    
    trans = pos-pos_init
    pts = [p-trans for p in sp.GetAllPoints()]
    ml.off = pos
    sp.SetMl(ml)
    sp.SetAllPoints(pts)
    sp.Message(c4d.MSG_UPDATE)
    
# Main function
def main():
    for sp in op.GetChildren():
        axeFirstPoint(sp)
    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()