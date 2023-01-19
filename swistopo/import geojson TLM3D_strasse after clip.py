from typing import Optional
import c4d
import json
import os

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected


#exemple extraction initiale via og2ogr
#ogr2ogr -clipdst 2567613.1657820013 1108343.8926543007 2570413.1657820013 1111143.8926543007 "/Users/olivierdonze/switchdrive/Mandats/Parc_naturel_regional_vallee_Trient/c4d/maquettes_villages/Vernayaz/vernayaz_routes_TLM.geojson" "/Volumes/My Passport Pro/swisstopo/SWISSTLM3D_2022_LV95_LN02.gdb" "TLM_STRASSE"

CONTAINER_ORIGIN = 1026473


def main() -> None:
    fn = '/Users/olivierdonze/switchdrive/Mandats/Parc_naturel_regional_vallee_Trient/c4d/maquettes_villages/Vernayaz/vernayaz_routes_TLM.geojson'
    origin = doc[CONTAINER_ORIGIN]

    res = c4d.BaseObject(c4d.Onull)
    res.SetName(os.path.basename(fn))
    doc.InsertObject(res)
    with open(fn,encoding='utf-8') as f :
        data = json.loads(f.read())

        for feat in data['features']:
            objektart = feat['properties']['OBJEKTART']
            
            if feat['geometry']['type'] =='LineString':
                nb_seg = 1
                pts = [c4d.Vector(x,y,z) - origin for x,z,y in feat['geometry']['coordinates']]
            
            if feat['geometry']['type'] =='MultiLineString':
                coord = feat['geometry']['coordinates']
                nb_seg = len(coord)
                pts = []
                segs = []
                for i,points in enumerate(coord):
                    pts.extend([c4d.Vector(x,y,z) - origin for x,z,y in points])
                    segs.append(len(points))
                    
            nb_pts = len(pts)
            sp = c4d.SplineObject(nb_pts,c4d.SPLINETYPE_LINEAR)
            sp.SetName(objektart)
            sp.SetAllPoints(pts)
            if nb_seg>1:
                sp.ResizeObject(nb_pts, nb_seg)
                for i,n in enumerate(segs):
                    sp.SetSegment(i,n,closed = False)
            
            sp.Message(c4d.MSG_UPDATE)
            sp.InsertUnderLast(res)


    c4d.EventAdd()




"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()