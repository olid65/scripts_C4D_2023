from typing import Optional
import c4d
import urllib.request
import urllib.parse 
import json
from pprint import pprint
from math import pi
from random import random as rdm

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

#si FORME est à True la source des instances se fera sur la base du champ FORME
#sinon sur la base de feuillus/conifères
FORME = True

CONTAINER_ORIGIN = 1026473

def empriseVueHaut(bd, origine):
    dimension = bd.GetFrame()
    largeur = dimension["cr"] - dimension["cl"]
    hauteur = dimension["cb"] - dimension["ct"]

    mini = bd.SW(c4d.Vector(0, hauteur, 0)) + origine
    maxi = bd.SW(c4d.Vector(largeur, 0, 0)) + origine

    return mini, maxi, largeur, hauteur


def empriseObject(obj, origine):
    geom = obj
    if not geom.CheckType(c4d.Opoint):
        geom = geom.GetCache()
        if not geom.CheckType(c4d.Opoint) : return None
    mg = obj.GetMg()
    pts = [p*mg+origine for p in geom.GetAllPoints()]
    lst_x = [p.x for p in pts]
    lst_y = [p.y for p in pts]
    lst_z = [p.z for p in pts]
    
    xmin = min(lst_x)
    xmax = max(lst_x)
    ymin = min(lst_y)
    ymax = max(lst_y)
    zmin = min(lst_z)
    zmax = max(lst_z)
    
    mini = c4d.Vector(xmin,ymin,zmin)
    maxi = c4d.Vector(xmax,ymax,zmax)
    
    return mini, maxi

def plaquer_sur_poly(objs,terrain):

    if not objs : return None
	
    if not terrain.GetType()==c4d.Opolygon:
        c4d.gui.MessageDialog('Le terrain doit être un objet polygonal')
        return False        

    rc = c4d.utils.GeRayCollider()
    rc.Init(terrain)
    bbox = terrain.GetRad()
    mg_t = terrain.GetMg()
    inv_m = ~mg_t
    centre = terrain.GetMp()*mg_t

    y_max = centre.y +  bbox.y + 1000
    lg = bbox.y * 2 + 2000
  
    for o in objs :
        mg =o.GetMg()
        i_m= ~mg
        pos = mg.off*inv_m
        pos.y = y_max
		
        if rc.Intersect(pos, c4d.Vector(0,-1,0),lg):
            x= rc.GetNearestIntersection()
            pos.y-=x['distance']
            mg.off = pos*mg_t
            o.SetMg(mg)

    return True


def main() -> None:

    origine = doc[CONTAINER_ORIGIN]

    #si pas d'origine message et on quitte
    if not origine:
        c4d.gui.MessageDialog("Le document doit être géoréférencé")
        return
    
    mode = None

    #Si on a un objet sélectionné qui a une géométrie on l'utilise pour la bbox'
    if op and op.CheckType(c4d.Opoint):
        mini,maxi = empriseObject(op, origine)
        
    #si pas d'objet on quitte
    else:
        c4d.gui.MessageDialog("Vous devez sélectionner un objet polygonal (terrain)")
        return
    
    #messsage de confirmation
    rep = c4d.gui.QuestionDialog(f"Voulez-vous extraire les arbres selon l'emprise de {op.GetName()}\n(l'altitude des arbres sera définie par cet objet)\nVoulez-vous continuer ?")
    if not rep: return


    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    server = 'SITG_OPENDATA_04'
    id_lyr = '4571'
    url_base = f'https://ge.ch/sitgags1/rest/services/VECTOR/{server}/MapServer/{id_lyr}/query?'
    #url = 'https://ge.ch/sitgags1/rest/services/VECTOR/SITG_GEOSERVICEDATA/MapServer/7048/query?where=&text=&objectIds=&time=&geometry=2465789.4328%2C1086777.4394%2C2531325.5829%2C1155694.86&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&resultOffset=&resultRecordCount=&queryByDistance=&returnExtentsOnly=false&datumTransformation=&parameterValues=&rangeValues=&f=geojson'
    
    #'outfileds' : 'OBJECTID', 'NOM_COMPLET', 'REMARQUABLE', 'SITUATION', 'TYPE_PLANTATION', 'NOMBRE_TRONCS', 'DIAMETRE_1M', 'CIRCONFERENCE_1M', 'HAUTEUR_TRONC', 'HAUTEUR_TOTALE', 'DIAMETRE_COURONNE', 'FORME', 'STADE_DEVELOPPEMENT', 'VITALITE', 'CONDUITE', 'TYPE_SOL', 'TYPE_SURFACE', 'ESPERANCE_VIE', 'DATE_PLANTATION', 'DATE_PLANTATION_ESTIMEE', 'DATE_OBSERVATION', 'ID_ACTEUR', 'CLASSE', 'RAYON_COURONNE', 'SOUCHE', 'STATUT', 'ID_ARBRE', 'NO_INVENTAIRE',
    
    params = { 
        "inSR" :'2056',
        "outSR" :'2056',
        "geometry": f"{mini.x},{mini.z},{maxi.x},{maxi.z}", 
        "geometryType":"esriGeometryEnvelope",
        "returnGeometry": "true", 
        "returnZ":"true",
        "outfields": "*",
        "f": "geojson" 
    }    
     
    query_string = urllib.parse.urlencode( params ) 
    url = url_base+query_string
    print(url)
    req = urllib.request.Request(url=url)
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode("utf-8"))
    
    #fn = 'E:/OD/TEMP/ica.geojson'
    #fn = '/Users/olivierdonze/Documents/TEMP/ica.geojson'
    #with open(fn,'w') as f:
        #f.write(json.dumps(data,indent=4))
    res = c4d.BaseObject(c4d.Onull)
    res.SetName('arbres_ICA')

    srces = c4d.BaseObject(c4d.Onull)
    srces.SetName('srces_arbres_ICA')

    dico_srces = {}
    dico_null = {}
    if FORME:
        #on répertorie toutes les formes
        formes = list(set([feat['properties']['FORME'] for feat in data['features']]))
        #on crée un objet null pour chaque forme
        for forme in formes:
            null = c4d.BaseObject(c4d.Onull)
            null.SetName(forme)
            null.InsertUnderLast(res)
            dico_null[forme] = null
            null_srce = c4d.BaseObject(c4d.Onull)
            null_srce.SetName(forme)
            null_srce.InsertUnderLast(srces)
            dico_srces[forme] = null_srce
    else:
        feuillus = c4d.BaseObject(c4d.Onull)
        feuillus.SetName('feuillus')
        feuillus.InsertUnderLast(res)
        dico_null['feuillus'] = feuillus
        coniferes = c4d.BaseObject(c4d.Onull)
        coniferes.SetName('coniferes')
        coniferes.InsertUnderLast(res)
        dico_null['coniferes'] = coniferes
        

        feuillus_srce = c4d.BaseObject(c4d.Onull)
        feuillus_srce.SetName('feuillus_srce')
        feuillus_srce.InsertUnderLast(srces)
        coniferes_srce = c4d.BaseObject(c4d.Onull)
        coniferes_srce.SetName('coniferes_srce')
        coniferes_srce.InsertUnderLast(srces)
        dico_srces['feuillus'] = feuillus_srce
        dico_srces['coniferes'] = coniferes_srce

    #TODO : il y a une limite d'extractiomn de 1000 objets (pas certain)
    #que faire si plus de 1000 objets ?
    print(len(data['features']))
    arbres = []
    for feat in data['features']:
        #print(feat['geometry']['type'])
        x,y = feat['geometry']['coordinates']
        #print(x,y)
        pos = c4d.Vector(x,0,y) - origine
        instance = c4d.BaseObject(c4d.Oinstance)
        instance.SetAbsPos(pos)
        
        instance.SetName(feat['properties']['NOM_COMPLET'])
        scale = c4d.Vector(1,1,1)
        haut = feat['properties']['HAUTEUR_TOTALE']
        if haut :
            scale.y = haut/10
        scale_horiz = feat['properties']['DIAMETRE_COURONNE']
        if scale_horiz :
            scale.x = scale.z = scale_horiz/10
        
        instance.SetAbsScale(scale)

        #rotation aléatoire
        rot = c4d.Vector(rdm()*2*pi,0,0)
        instance.SetAbsRot(rot)
        if FORME:
            forme = feat['properties']['FORME']
            instance[c4d.INSTANCEOBJECT_LINK] = dico_srces[forme]
            instance.InsertUnderLast(dico_null[forme])
        else:
            classe = feat['properties']['CLASSE']
            instance[c4d.INSTANCEOBJECT_LINK] = dico_srces[classe]
            instance.InsertUnderLast(dico_null[classe])
        arbres.append(instance)

    #projection des arbres sur le terrain
    plaquer_sur_poly(arbres,op)

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