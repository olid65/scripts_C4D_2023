from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

ALT_BASE = 372 #niveau du lac
#SCALE_VERT = 1.5
ROUND = 3 # niveau d'arrondi pour la sélection des points du bas'


def main() -> None:
    maquette = doc.SearchObject('Maquette swisstopo')
    
    if maquette:
        scale_maquette_dbt = maquette.GetAbsScale()
        maquette.SetAbsScale(c4d.Vector(1,1,1))
    mnt = doc.SearchObject('swissalti3d_2m')
    floor = doc.SearchObject('Floor')

    doc.StartUndo()
    bs = mnt.GetPointS()
    bs.DeselectAll()
    # modification des points de la base
    if mnt:
        mg = mnt.GetMg()
        pts = [p for p in mnt.GetAllPoints()]
        ymin = round(min([p.y for p in pts]),ROUND)
        #ymin = round(1348.6271 ,ROUND) 
        print(ymin)
        
        for i,p in enumerate(pts):
            if round(p.y,ROUND) == ymin:
                bs#.Select(i)
                #print(i)
                p.y = ALT_BASE
                pts[i] = p
        
        #pts = [p for p in mnt.GetAllPoints()]
        
        doc.AddUndo(c4d.UNDOTYPE_CHANGE,mnt)
        mnt.SetAllPoints(pts)
    
    if floor:
        pos = floor.GetAbsPos()
        pos.y = ALT_BASE
        doc.AddUndo(c4d.UNDOTYPE_CHANGE,floor)
        floor.SetAbsPos(pos)
    if maquette:
        maquette.SetAbsScale(scale_maquette_dbt)
    
    doc.EndUndo()
    c4d.EventAdd()
    
    
    

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()