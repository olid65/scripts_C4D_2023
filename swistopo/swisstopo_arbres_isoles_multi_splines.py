from typing import Optional
import c4d
import json
import urllib
from pathlib import Path

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected


CONTAINER_ORIGIN = 1026473

def get_url(url_base,params):
    #Il faut un /query? à la fin de l'url de base
    end = '/query?'
    if url_base[-len(end):]!= end:
        #s'il y a déjà le slash à la fin'
        if url_base[-1] == '/':
            url_base+= end[1:]
        else:
            url_base+=end
    #encodage de l'url pour éviter les espaces et cararctères spéciaux
    query_string = urllib.parse.urlencode( params )
    return url_base + query_string

def spline2json(sp,origine):
    """pour géométrie JSON à mettre sous geometry de la requête
       et indiquer sous geometryType=esriGeometryPolygon"""
    res = {}
    res["spatialReference"] = {"wkid" : 2056}
    mg = sp.GetMg()
    sp = sp.GetRealSpline()
    if not sp: return None
    pts = [p*mg+origine for p in sp.GetAllPoints()]

    nb_seg = sp.GetSegmentCount()
    if not nb_seg:
        res["rings"] = [[[p.x,p.z] for p in pts]]

    else:
        res["rings"] = []
        id_pt = 0
        for i in range(nb_seg):
            cnt = sp.GetSegment(i)['cnt']
            res["rings"].append([[p.x,p.z] for p in pts[id_pt:id_pt+cnt]])
            id_pt+=cnt
    return json.dumps(res)

def url_geojson_trees(bbox_or_spline,origine):
    """ si une spline est dans bbox_or_spline renvoie les élément à l'intérieur du polygone,
        si c'est' un tuple de 4 float (bbox) renvoie les élément à l'intérieur de la bbox"""
    url_base = 'https://hepiadata.hesge.ch/arcgis/rest/services/suisse/TLM_C4D_couverture_sol/FeatureServer/0'
    xmin=ymin=xmax=ymax = None
    try:  sp = bbox_or_spline.GetRealSpline()
    except : sp = None
    if not sp:
        try:
            xmin,ymin,xmax,ymax = bbox_or_spline
            float(xmin),float(ymin),float(xmax),float(ymax)
        except: pass

    if not sp and not xmin:
        raise TypeError("bbox_or_spline must be a tuple of 4 floats or a SplineObject")

    #par défaut on met les paramètres selon la bbox (enveloppe)
    params = {
                "geometry" : f"{xmin},{ymin},{xmax},{ymax}",
                "geometryType": "esriGeometryEnvelope",
                "outSR":'2056',
                "returnGeometry":"true",
                "returnZ": "true",
                "spatialRel":"esriSpatialRelIntersects",
                "f":"geojson"
              }
    #si on a une spline on change ces deux paramètres
    if sp:
        params["geometry"] = spline2json(sp,origine)
        params["geometryType"] = "esriGeometryPolygon"

    url = get_url(url_base,params)
    return url

def write_jsonfile(data,fn_dst):
    try:
        with open(fn_dst,'w') as f:
            f.write(json.dumps(data))
    except:
        return False
    return True

def get_json_from_url(url):
    req = urllib.request.Request(url=url)
    try :
        resp = urllib.request.urlopen(req)

    except urllib.error.HTTPError as e:
        print(f'HTTPError: {e.code}')
        return None

    except urllib.error.URLError as e:
        # Not an HTTP-specific error (e.g. connection refused)
        # ...
        print(f'URLError: {e.reason}')
        return None

    else:
        # 200
        data = json.loads(resp.read().decode("utf-8"))
        return data

    return None

def geojson_trees(bbox_or_spline,origine,fn_dst):
    """ si une spline est dans bbox_or_spline renvoie les élément à l'intérieur du polygone,
        si c'est' un tuple de 4 float (bbox) renvoie les élément à l'intérieur de la bbox"""
    url = url_geojson_trees(bbox_or_spline,origine)
    data = get_json_from_url(url)

    error = data.get("error",None)
    if error:
        print (Warning(f"geojson_trees : code : {error['code']}, {error['message']},{error['details']}"))
        return False

    if data:
        return write_jsonfile(data,fn_dst)

    return False

def main() -> None:
    pth = Path('/Volumes/My Passport Pro/TEMP/Chermignon_Crans/swisstopo')
    origine = doc[CONTAINER_ORIGIN]
    id_fn = 1
    for sp in op.GetChildren():
        fn_dst = pth / f'arbres_isoles_{str(id_fn).zfill(2)}.geojson'
        geojson_trees(sp,origine,fn_dst)
        print(fn_dst)
        id_fn +=1
        
        
    
    


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()