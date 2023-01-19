from typing import Optional
import c4d
import os
from pprint import pprint
import json
doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

CONTAINER_ORIGIN = 1026473

def main() -> None:
    
    fn = '/Users/olivierdonze/switchdrive/Mandats/Parc_naturel_regional_vallee_Trient/SIG/Maquette_large_Mt_Blanc/OSM_peaks_cadrage2.geojson'
    with open(fn, encoding = 'utf-8') as f:
        srce = c4d.BaseObject(c4d.Onull)
        srce.SetName('source_peaks')
        res = c4d.BaseObject(c4d.Onull)
        res.SetName(os.path.basename(fn)[:-8])
        data = json.loads(f.read())
        origin = doc[CONTAINER_ORIGIN]
        for feat in data['features']:
            x,z = feat['geometry']['coordinates']
            prop = feat['properties']
            name = prop['name']
            
            if not name : continue
            
            if prop['ele']:
                alt = float(prop['ele'])
            else:
                alt = 0.
    
            
            
            pt = c4d.Vector(x,alt,z)
            if not origin : 
                origin = c4d.Vector(pt)
                doc[CONTAINER_ORIGIN] = origin
            pt-=origin
            inst = c4d.BaseObject(c4d.Oinstance)
            inst.SetAbsPos(pt)
            inst.SetName(name)
            inst[c4d.INSTANCEOBJECT_LINK] = srce
            inst.InsertUnderLast(res)
    
        doc.InsertObject(res)
        doc.InsertObject(srce)
        c4d.EventAdd()
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()