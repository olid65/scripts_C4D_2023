from typing import Optional
import c4d
from shapely  import LinearRing,simplify

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

TOLERANCE = 200
def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    pts = [(p.x,p.z) for p in op.GetAllPoints()]
    poly = LinearRing(pts)
    poly_simpl = simplify(poly, tolerance=TOLERANCE, preserve_topology=True)
    new_pts = [c4d.Vector(x,0,z) for x,z in list(poly_simpl.coords)]
    
    if new_pts[0] == new_pts[-1]:
        new_pts = new_pts[:-1]
    
    new_sp = c4d.SplineObject(len(new_pts), c4d.SPLINETYPE_LINEAR)
    new_sp.SetAllPoints(new_pts)
    
    new_sp.SetMg(c4d.Matrix(op.GetMg()))
    new_sp.Message(c4d.MSG_UPDATE)
    new_sp[c4d.SPLINEOBJECT_CLOSED] =True
    doc.InsertObject(new_sp)
    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()