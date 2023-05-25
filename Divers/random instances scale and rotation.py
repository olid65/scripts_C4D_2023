from typing import Optional
import c4d
from random import random as rdm
from math import pi

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

SCALE_MIN = 0.8
SCALE_MAX = 1.2

def random_instance(obj,stop = None):
    while obj:
        if obj.CheckType(c4d.Oinstance):
            rot = c4d.Vector(pi*2*rdm(),0,0)
            obj.SetAbsRot(rot)
            #ECHELLE
            delta = SCALE_MAX - SCALE_MIN
            s_h = rdm()* delta + SCALE_MIN
            s_diam = rdm()* delta + SCALE_MIN
            scale = c4d.Vector(s_diam,s_h,s_diam)
            obj.SetAbsScale(scale)
        random_instance(obj.GetDown(),stop = stop)
        if obj == stop : return
        obj = obj.GetNext()

def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    random_instance(op,stop = op)
    c4d.EventAdd()
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()