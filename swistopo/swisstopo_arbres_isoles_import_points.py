import c4d
import json
import os.path
import sys
from pprint import pprint
from pathlib import Path

#sys.path.append('/Users/olivierdonze/Library/Preferences/Maxon/Maxon Cinema 4D R25_EBA43BEE/library/scripts/swisstopo/utils')
#import geojson
#from geojson import Feature, Point, FeatureCollection

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

CONTAINER_ORIGIN = 1026473


###########################################################
# LECTURE FICHIERS JSON
############################################################

def pointObjectFromGeojson(fn,doc):
    """ renvoie un objet polygonal avec uniquement les points du fichier geojson
        avec un vertex color tag qui affiche toujours les points selon color"""
    
    origine = doc[CONTAINER_ORIGIN]
    basename = os.path.basename(fn)
    with open(fn) as f:
        data = json.load(f)
        error = data.get('error',None)
        if error:
            print(f"'{os.path.basename(fn)}' n'a pas été téléchargé correctement")
            print(f"code : {error['code']} {error['message']}")
            for detail in error['details']:
                print(f"--> {detail}")
            return None


        pts = []
        features = data.get('features',None)
        if not features:
            print(f"No 'features' in {basename}")
            return None

        for feat in features:
            x,y,z = feat['geometry']['coordinates']
            pz = c4d.Vector(x,z,y)
            if not origine:
                origine = pz
                doc[CONTAINER_ORIGIN] = origine
            pts.append(c4d.Vector(x,z,y)-origine)


        nb_pts = len(pts)
        pos = sum(pts)/nb_pts
        pts = [p-pos for p in pts]

        res = c4d.PolygonObject(nb_pts,0)
        res.SetAllPoints(pts)
        res.SetName(basename)

        #vertex_color_tag = c4d.VertexColorTag(nb_pts)
        #vertex_color_tag[c4d.ID_VERTEXCOLOR_DRAWPOINTS] = True

        #data = vertex_color_tag.GetDataAddressW()
        #for idx in range(nb_pts):
            #c4d.VertexColorTag.SetPoint(data, None, None, idx, color)
        #res.InsertTag(vertex_color_tag)

        res.SetAbsPos(pos)

        return res

##############################################################################
# MOGRAPH ARBRES ISOLES

def trees_mograph_cloner(doc, point_object, hauteurs, diametres, objs_srces, centre=None, name=None):
    # tag = doc.GetActiveTag()
    # return

    res = c4d.BaseObject(c4d.Onull)
    if not name: name = NULL_NAME
    res.SetName(name)

    if centre:
        creerGeoTag(res, doc, centre)

    cloner = c4d.BaseObject(ID_CLONER)
    cloner.SetName(NOM_CLONER)
    cloner[c4d.ID_MG_MOTIONGENERATOR_MODE] = 0  # mode objet
    cloner[c4d.MG_OBJECT_LINK] = point_object
    cloner[c4d.MG_POLY_MODE_] = 0  # mode point
    cloner[c4d.MG_OBJECT_ALIGN] = False
    cloner[c4d.MGCLONER_VOLUMEINSTANCES_MODE] = 2  # multiinstances
    cloner[c4d.MGCLONER_MODE] = 2  # repartition aleatoire des clones

    # insertion des objets source
    if objs_srces:
        for o in objs_srces.GetChildren():
            clone = o.GetClone()
            clone.InsertUnderLast(cloner)

    tagHauteurs = c4d.BaseTag(440000231)
    cloner.InsertTag(tagHauteurs)
    tagHauteurs.SetName(NOM_TAG_HAUTEURS)
    # ATTENTION bien mettre des float dans la liste sinon cela ne marche pas !
    scale_factor_haut = lambda x: float(x) / HAUT_SRCE - 1.
    c4d.modules.mograph.GeSetMoDataWeights(tagHauteurs, [scale_factor_haut(h) for h in hauteurs])
    # tagHauteurs.SetDirty(c4d.DIRTYFLAGS_DATA) #plus besoin depuis la r21 !

    tagDiametres = c4d.BaseTag(440000231)
    cloner.InsertTag(tagDiametres)
    tagDiametres.SetName(NOM_TAG_DIAMETRES)
    scale_factor_diam = lambda x: float(x * 2) / DIAM_SRCE - 1.
    c4d.modules.mograph.GeSetMoDataWeights(tagDiametres, [scale_factor_diam(d) for d in diametres])
    # tagDiametres.SetDirty(c4d.DIRTYFLAGS_DATA) #plus besoin depuis la r21 !

    # Effecteur simple hauteurs
    effector_heights = create_effector(NOM_EFFECTOR_HAUTEURS, select=tagHauteurs.GetName())
    effector_heights[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = False
    effector_heights[c4d.ID_MG_BASEEFFECTOR_SCALE_ACTIVE] = True
    effector_heights[c4d.ID_MG_BASEEFFECTOR_SCALE, c4d.VECTOR_Y] = FACTEUR_HAUT

    # Effecteur simple diametres
    effector_diam = create_effector(NOM_EFFECTOR_DIAMETRES, select=tagDiametres.GetName())
    effector_diam[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = False
    effector_diam[c4d.ID_MG_BASEEFFECTOR_SCALE_ACTIVE] = True
    effector_diam[c4d.ID_MG_BASEEFFECTOR_SCALE] = c4d.Vector(FACTEUR_DIAMETRE, 0, FACTEUR_DIAMETRE)

    # Effecteur random
    effector_random = create_effector(NOM_EFFECTOR_RANDOM, typ=ID_RANDOM_EFFECTOR)
    effector_random[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = False
    effector_random[c4d.ID_MG_BASEEFFECTOR_ROTATE_ACTIVE] = True
    effector_random[c4d.ID_MG_BASEEFFECTOR_ROTATION, c4d.VECTOR_X] = pi * 2

    ie_data = cloner[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST]
    ie_data.InsertObject(effector_heights, 1)

    ie_data.InsertObject(effector_diam, 1)
    ie_data.InsertObject(effector_random, 1)
    cloner[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST] = ie_data

    cloner.Message(c4d.MSG_UPDATE)
    cloner.InsertUnder(res)
    effector_heights.InsertUnder(res)
    effector_diam.InsertUnder(res)
    effector_random.InsertUnder(res)
    point_object.InsertUnder(res)

    effector_heights.Message(c4d.MSG_MENUPREPARE, doc)
    effector_diam.Message(c4d.MSG_MENUPREPARE, doc)
    effector_random.Message(c4d.MSG_MENUPREPARE, doc)

    return res

def mograph_system_trees(trees_sommets, mnt, arbres_sources, doc):
    arbres_pts_base = pointsOnSurface(trees_sommets,mnt)
    arbres_pts_base.SetName('arbres_isoles_swisstopo_collets')
    
    #TODO : que faire quand la hauteur == 0
    hauteurs = [pt_sommet.y-pt_base.y for pt_sommet,pt_base in zip(trees_sommets.GetAllPoints(),arbres_pts_base.GetAllPoints())]

    #fonction lambda pour limiter la hauteur à 30m
    f = lambda x: x if x < 30 else 30
    hauteurs = list(map(f,hauteurs))

    rapport = RAPORT_HAUTEUR_DIAMETRE_MIN + random()*RAPORT_HAUTEUR_DIAMETRE_MIN
    diametres = [haut*rapport for haut in hauteurs]


    res = trees_mograph_cloner(doc, arbres_pts_base, hauteurs, diametres, arbres_sources, centre=None, name=None)
    return res





# Main function
def main():
    

    #chemin du document actif
    pth = Path(doc.GetDocumentPath())
    if not pth:
        c4d.gui.MessageDialog('Document must be saved')
        return
    pth = pth / 'swisstopo' / 'arbres_isoles'
    if not pth.exists():
        c4d.gui.MessageDialog('swisstopo/arbres_isoles folder must exist')
        return
    
    for fn in pth.glob('*.geojson'):
        print(fn)
        #ARBRES ISOLES
        isol_trees = pointObjectFromGeojson(fn,doc)
        if isol_trees:
            doc.InsertObject(isol_trees)

    c4d.EventAdd()
    return


    fn_trees = '/Volumes/My Passport Pro/TEMP/Chermignon_Crans/swisstopo/arbres_isoles_merged.geojson'
    #fn = '/Users/olivierdonze/Documents/TEMP/test_geojson_trees_swisstopo/exemple_404.geojson'

    origine = doc[CONTAINER_ORIGIN]
    if not origine:
        print("Pas d'origine")
        return

    #ARBRES ISOLES
    isol_trees = pointObjectFromGeojson(fn_trees,origine)

    if isol_trees:
        doc.InsertObject(isol_trees)


    c4d.EventAdd()







# Execute main()
if __name__=='__main__':
    main()