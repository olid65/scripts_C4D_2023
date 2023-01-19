from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

CONTAINER_ORIGIN = 1026473
"""Attention bouge tous les objets du premier niveau 
   en mettant l'objet sélectionné à 0,0,0
   modifie l'origine du document également"""
   
def main() -> None:
    
    origin = doc[CONTAINER_ORIGIN]
    
    mg = op.GetMg()
    new_origin = origin + mg.off
    doc[CONTAINER_ORIGIN] = new_origin
    trans = -mg.off
    
    o = doc.GetFirstObject()
    doc.StartUndo()
    while o:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE,o)
        mg = o.GetMg()
        mg.off += trans
        
        o.SetMg(mg)
        o = o.GetNext()
    doc.EndUndo()
    c4d.EventAdd()
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()