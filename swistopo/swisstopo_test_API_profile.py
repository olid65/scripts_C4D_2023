from typing import Optional
import c4d
import urllib
import json

"""Sélectionner la spline géoreferencée chemin de coupe"""

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

CONTAINER_ORIGIN = 1026473

def main() -> None:
    origin = doc[CONTAINER_ORIGIN]
    for op in doc.GetActiveObjects(0):
        if not op.CheckType(c4d.Ospline): continue

        # DEFINITION DE L'URL
        mg = op.GetMg()
        lst = []
        for p in op.GetAllPoints():
            lst.append(p*mg+origin)
    
    
        lst_pt = f"{[[p.x,p.z] for p in lst]}"
    
        url_base = 'https://api3.geo.admin.ch/rest/services/profile.json?'
    
        #lst_pt = f"[[2550050,1206550],[2556950,1204150],[2561050,1207950]]"
    
        geom = f"""{{"type":"LineString","coordinates":{lst_pt}}}"""
    
        # le nombre de points par défaut est à 200
        params = {
            'geom' :f"{geom}",
            "srs":"2056",
            'nb_points':'200'
                }
    
        query_string = urllib.parse.urlencode( params )
        url = url_base+query_string
        #print(url)
    
        # Extraction du profil
    
        pts = []
    
        try:
            with urllib.request.urlopen(url, timeout = 1) as resp:
                data = json.loads(resp.read())
                for i,p in enumerate(data):
                    y = p['alts']['COMB']# il y a DTM2 et DTM25 -> COMB doit être la combinaison ???
                    x = p['easting']
                    z = p['northing']
        
                    pts.append(c4d.Vector(x,y,z)-origin)
        except : #socket.timeout:
    
            print("connection's timeout expired")
            return
    
        sp = c4d.SplineObject(len(pts), c4d.SPLINETYPE_LINEAR)
        sp.SetAllPoints(pts)
        sp.SetName(op.GetName()+'_swisstopo_profile')
        sp.Message(c4d.MSG_UPDATE)
        doc.InsertObject(sp)
    c4d.EventAdd()


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()