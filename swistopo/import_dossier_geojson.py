from typing import Optional
import c4d
import os
from glob import glob
import json



CONTAINER_ORIGIN = 1026473

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected
def lst2vec(lst):
    """transformation tuple ou liste coord x,y(z) en vecteur Cinema4D"""
    if len(lst) ==2:
        x,z = lst
        return c4d.Vector(x,0,z)
    elif len(lst) ==3:
        x,z,y = lst
        return c4d.Vector(x,y,z)

def get_centre(pts):
    lst_x = [v.x for v in pts]
    lst_y = [v.y for v in pts]
    lst_z = [v.z for v in pts]
    return c4d.Vector((min(lst_x)+max(lst_x))/2, (min(lst_y)+max(lst_y))/2,(min(lst_z)+max(lst_z))/2)

def point(coord):
    pass

def multipoint(coord):
    res = None
    if len(coord) ==1 :
        x,z = coord[0]
        res = c4d.BaseObject(c4d.Oinstance)
        res.SetAbsPos(c4d.Vector(x,0,z))
    if len(coord) >1 :
        res = c4d.BaseObject(c4d.Onull)
        pt_ref = c4d.Vector(coord[0][0],0,coord[0][1])
        res.SetAbsPos(pt_ref)
        for x,z in coord:
            inst = c4d.BaseObject(c4d.Oinstance)
            inst.SetAbsPos(c4d.Vector(x,0,y)-pt_ref)
            inst.InsertUnderLast(res)
    return res

def polygon(coord):
    pts = []
    seg = []
    for lst in coord:
        #on supprime le dernier point car c'est le même que le premier
        pts_temp = [lst2vec(l) for l in lst][:-1]
        #stockage du nombre de points par segment
        seg.append(len(pts_temp))
        pts+=pts_temp

    #on calcule le centre des points
    # et on translate tous les points
    centre = get_centre(pts)
    pts = list(map(lambda v: v-centre, pts))
    pcnt = len(pts)
    scnt = len(seg)
    res = c4d.SplineObject(pcnt,c4d.SPLINETYPE_LINEAR)
    res[c4d.SPLINEOBJECT_CLOSED] = True
    res.SetAllPoints(pts)
    res.SetAbsPos(centre)
    if scnt > 1:
        res.ResizeObject( pcnt, scnt=scnt)
        for i,cnt in enumerate(seg):
            res.SetSegment(i, cnt, closed=True)
    res.Message(c4d.MSG_UPDATE)

    return res

def multipolygon(coord):
    pts = []
    seg = []
    for poly in coord:
        for lst in poly:
            #on supprime le dernier point car c'est le même que le premier
            pts_temp = [lst2vec(l) for l in lst][:-1]
            #stockage du nombre de points par segment
            seg.append(len(pts_temp))
            pts+=pts_temp

    #on calcule le centre des points
    # et on translate tous les points
    centre = get_centre(pts)
    pts = list(map(lambda v: v-centre, pts))
    pcnt = len(pts)
    scnt = len(seg)
    res = c4d.SplineObject(pcnt,c4d.SPLINETYPE_LINEAR)
    res[c4d.SPLINEOBJECT_CLOSED] = True
    res.SetAllPoints(pts)
    res.SetAbsPos(centre)
    if scnt > 1:
        res.ResizeObject( pcnt, scnt=scnt)
        for i,cnt in enumerate(seg):
            res.SetSegment(i, cnt, closed=True)
    res.Message(c4d.MSG_UPDATE)

    return res

def linestring(coord):
    pts = [lst2vec(p) for p in coord]


    #on calcule le centre des points
    # et on translate tous les points
    centre = get_centre(pts)
    pts = list(map(lambda v: v-centre, pts))
    pcnt = len(pts)
    #scnt = len(seg)
    res = c4d.SplineObject(pcnt,c4d.SPLINETYPE_LINEAR)
    res[c4d.SPLINEOBJECT_CLOSED] = False
    res.SetAllPoints(pts)
    res.SetAbsPos(centre)
    res.Message(c4d.MSG_UPDATE)

    return res

def multilinestring(coord):
    if len(coord) == 1:
        return linestring(coord[0])

    elif len(coord) > 1:
        pts = []
        segs = []
        for part in coord:
            segs.append(len(part))
            pts.extend([lst2vec(p) for p in part])
        #print(pts)
        centre = get_centre(pts)
        pts = list(map(lambda v: v-centre, pts))
        pcnt = len(pts)
        #scnt = len(seg)
        res = c4d.SplineObject(pcnt,c4d.SPLINETYPE_LINEAR)
        res[c4d.SPLINEOBJECT_CLOSED] = False
        res.SetAllPoints(pts)

        res.ResizeObject(pcnt, len(segs))
        for i,cnt in enumerate(segs):
            res.SetSegment(i,cnt, closed = False)
        res.SetAbsPos(centre)
        res.Message(c4d.MSG_UPDATE)
        return res

    #TODO gérer les plus grand que 1 -> vraies multiline
    return None

dico_func = {
                'Point': point,
                'MultiPoint': multipoint,
                'Polygon': polygon,
                'MultiPolygon': multipolygon,
                'LineString': linestring,
                'MultiLineString':multilinestring,
}

def main() -> None:
    origin = doc[CONTAINER_ORIGIN]
    pth = doc.GetDocumentPath()
    pth = os.path.join(pth,'SIG')
    #pth = '/Users/olivierdonze/Documents/Mandats/Vallee du Trient/C4D/Decoupages_pour_maquettes_physiques_expo/SIG'
    res = c4d.BaseObject(c4d.Onull)
    res.SetName(os.path.basename(pth))
    for fn in sorted(glob(os.path.join(pth,'*.geojson'))):
        dic_objs = {}
        no = c4d.BaseObject(c4d.Onull)
        no.SetName(os.path.basename(fn)[:-8])
        no.InsertUnderLast(res)
        with open(fn, encoding = 'utf-8') as f:
            data = json.loads(f.read())
            for i,feature in enumerate(data['features']):
                geom = feature.get('geometry',None)
                if not geom: continue
                #appelle de la fonction selon le type
                obj = dico_func[geom.get('type',None)](geom['coordinates'])
                if obj :
                    pos = obj.GetAbsPos()
                    if not origin:
                        doc[CONTAINER_ORIGIN] = c4d.Vector(pos)
                        origin = doc[CONTAINER_ORIGIN]
                    pos-= origin


                    #attributs
                    attr = feature['properties']
                    if attr.get('name',None):
                        obj.SetName(attr['name'])

                    elif attr.get('ELEV_MAX',None):
                        obj.SetName(attr['ELEV_MAX'])

                    elif attr.get('label',None):
                        obj.SetName(attr['label'])

                    elif attr.get('id',None):
                        obj.SetName(attr['id'])

                    elif attr.get('ID',None):
                        obj.SetName(attr['ID'])

                    else:
                        obj.SetName('i'+str(i).zfill(3))
                    obj.SetAbsPos(pos)

                    dic_objs.setdefault(geom['type'],[]).append(obj)

        if len(dic_objs.keys()) == 1:
            for k,lst in dic_objs.items():
                for sp in lst :
                    sp.InsertUnderLast(no)
        else:
            for k,lst in dic_objs.items():
                ss_no = c4d.BaseObject(c4d.Onull)
                ss_no.SetName(k)
                for sp in lst :
                    sp.InsertUnderLast(ss_no)
                ss_no.InsertUnderLast(no)

    doc.InsertObject(res)
    c4d.EventAdd()


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()