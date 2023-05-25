from typing import Optional
import c4d
import shapefile
import os

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

CONTAINER_ORIGIN = 1026473

NOM_CHAMP = 'essence'

def main() -> None:
    fn = '/Volumes/My Passport Pro/SITG/Relief_magnin/RELIEF_MAGNIN_3D_shape/ARBRES.shp'
    origin = doc[CONTAINER_ORIGIN]
    
    dico = {}
    with shapefile.Reader(fn) as reader:
        fields_name = [f[0].lower() for f in reader.fields][1:]
        print(fields_name)
        if NOM_CHAMP in fields_name:
            idx = fields_name.index(NOM_CHAMP)
        else: 
            print(f'Pas de champ {NOM_CHAMP}')
            return
        for shp, rec in zip(reader.iterShapes(), reader.iterRecords()):
            x,z = shp.points[0]
            pos = c4d.Vector(x,shp.z[0],z)-origin
            essence = rec[idx]
            dico.setdefault(essence,[]).append(pos)
            
    res = c4d.BaseObject(c4d.Onull)
    res.SetName(os.path.basename(fn)[:-4])
    
    srces = c4d.BaseObject(c4d.Onull)
    srces.SetName(f'sources_{res.GetName()}')
    for k in sorted(dico.keys()):
        onull = c4d.BaseObject(c4d.Onull)
        onull.SetName(k)
        onull.InsertUnderLast(res)
        
        srce = c4d.BaseObject(c4d.Onull)
        srce.SetName(k)
        srce.InsertUnderLast(srces)
        
        for pos in dico[k]:
            inst = c4d.BaseObject(c4d.Oinstance)
            inst[c4d.INSTANCEOBJECT_LINK] = srce
            inst.SetAbsPos(pos)
            inst.SetName(k.lower())
            inst.InsertUnderLast(onull)
            
    doc.InsertObject(res)
    doc.InsertObject(srces)
    c4d.EventAdd()
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()