import c4d
import json
import urllib
import os
from zipfile import ZipFile
from pprint import pprint
import subprocess
import sys
import shapefile as shp

#ID pour stocker l'échelle du MNT si on veut pouvoir la changer après
ID_BUILDING_SCALE = 1059451

SCALE_MNT = 1.5
SCALE_BUILDINGS = 1.0

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

#ATTENTION SI LE DOC EST GEOREFERENCE AVEC UNE ALTITUDE AUTRE QUE 0 -> problème
CONTAINER_ORIGIN = 1026473

TXT_NOT_SAVED = "Le document doit être enregistré pour pouvoir copier les buildings, vous pourrez le faire à la prochaine étape\nVoulez-vous continuer ?"

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

def empriseVueHaut(bd, origine):
    dimension = bd.GetFrame()
    largeur = dimension["cr"] - dimension["cl"]
    hauteur = dimension["cb"] - dimension["ct"]

    mini = bd.SW(c4d.Vector(0, hauteur, 0)) + origine
    maxi = bd.SW(c4d.Vector(largeur, 0, 0)) + origine

    return mini, maxi

def lv95towgs84(x,y):
    url = f'http://geodesy.geo.admin.ch/reframe/lv95towgs84?easting={x}&northing={y}&format=json'

    f = urllib.request.urlopen(url)
    #TODO : vérifier que cela à bien fonctionnéé (code =200)
    txt = f.read().decode('utf-8')
    json_res = json.loads(txt)

    return float(json_res['easting']),float(json_res['northing'])


def get_list_from_STAC_swisstopo(url,xmin,ymin,xmax,ymax):
    #conversion coordonnées
    est,sud = lv95towgs84(xmin,ymin)
    ouest, nord = lv95towgs84(xmax,ymax)

    sufixe_url = f"/items?bbox={est},{sud},{ouest},{nord}"


    url += sufixe_url
    f = urllib.request.urlopen(url)
    txt = f.read().decode('utf-8')
    json_res = json.loads(txt)

    res = []

    for item in json_res['features']:
        for k,dic in item['assets'].items():
            href = dic['href']
            #on garde que les gdb
            if href[-8:] == '.gdb.zip':
                #dans la version 3 on a soit un url qui se termine par swissbuildings3d_3_0_2021_2056_5728.gdb.zip
                #qui contient la moitié de la suisse
                #ou swissbuildings3d_3_0_2020_1301-31_2056_5728.gdb.zip sous forme de tuile
                #-> donc on ne garde que la dernière qui après un split('_') a une longueur de 7
                if len(dic['href'].split('/')[-1].split('_'))==7:
                    res.append(dic['href'])
    return res

def getPathToQGISbin(path_to_QGIS = None):
    #Si le path_to_QGIS n'est pas renseigné on prend le chemin par défaut selon la plateforme
    win = sys.platform == 'win32'
    if not path_to_QGIS:
        if sys.platform == 'win32':
            path_to_QGIS = 'C:\\Program Files'
        else:
            path_to_QGIS = '/Applications'
    for folder_name in os.listdir(path_to_QGIS):
        if 'QGIS'  in folder_name:
            if win :
                path = os.path.join(path_to_QGIS,folder_name,'bin')
            else:

                path = os.path.join(path_to_QGIS,folder_name,'Contents/MacOS/bin')

            if os.path.isdir(path):
                # on vérifie qu'il y ait bien gdal_translate
                #TODO vérifier les autres
                if win :
                    if os.path.isfile(os.path.join(path,'gdal_translate.exe')):
                        return path
                else:
                    if os.path.isfile(os.path.join(path,'gdal_translate')):
                        return path
    return None

def ogrBIN_OK(path_to_QGIS_bin, exe = 'ogr2ogr'):
    if sys.platform == 'win32':
        exe+='.exe'
    path = os.path.join(path_to_QGIS_bin,exe)
    if os.path.isfile(path):
        return path
    else:
        return False

############################################################################################################
#IMPORT SHAPEFILES
############################################################################################################

def listdirectory2(path):
    fichier=[]
    for root, dirs, files in os.walk(path):
        for i in files:
            #print(i)
            if i == 'Building_solid.shp':
                fichier.append(os.path.join(root, i))
    return fichier

def import_swissbuildings3D_v3_shape(fn,doc):
    res = c4d.BaseObject(c4d.Onull)
    #pour le nom on donne le nom du dossier parent
    res.SetName(os.path.basename(os.path.dirname(fn)))
    r = shp.Reader(fn)

    xmin,ymin,xmax,ymax = r.bbox
    centre = c4d.Vector((xmin+xmax)/2,0,(ymax+ymin)/2)

    origin = doc[CONTAINER_ORIGIN]
    if not origin :
        doc[CONTAINER_ORIGIN] = centre
        origin = centre


    # géométries
    shapes = r.shapes()

    nbre = 0
    for shape in shapes:
        xs = [x for x,y in shape.points]
        zs = [y for x,y in shape.points]
        ys = [z for z in shape.z]

        #pour l'axe on prend la moyenne de x et z et le min de y auquel on ajoute 3m
        #car les bati swisstopo rajoute 3m sous le point le plus bas du MNT
        #comme ça on peut modifier l'échelle des hauteurs
        axe = c4d.Vector((min(xs)+max(xs))/2,min(ys)+3,(min(zs)+max(zs))/2)

        pts = [c4d.Vector(x,z,y)-axe for (x,y),z in zip(shape.points,shape.z)]

        nb_pts = len(pts)
        polys = []

        pred = 0
        for i in shape.parts:
            if pred:
                nb_pts_poly = i-pred

            poly = c4d.CPolygon(i,i+1,i+2,i+3)
            polys.append(poly)
            pred = i


        po =c4d.PolygonObject(nb_pts,len(polys))
        #TODO : tag phong !
        po.SetAllPoints(pts)
        for i,poly in enumerate(polys):
            po.SetPolygon(i,poly)

        po.SetAbsPos(axe-origin)
        po.Message(c4d.MSG_UPDATE)
        po.InsertUnderLast(res)
    return res

############################################################################################################
#BBOX
############################################################################################################

class Bbox(object):
    def __init__(self,mini,maxi):

        self.min = mini
        self.max = maxi
        self.centre = (self.min+self.max)/2
        self.largeur = self.max.x - self.min.x
        self.hauteur = self.max.z - self.min.z
    def __str__(self):
        return ('X : '+str(self.min.x)+'-'+str(self.max.x)+'->'+str(self.max.x-self.min.x)+'\n'+
                'Y : '+str(self.min.z)+'-'+str(self.max.z)+'->'+str(self.max.z-self.min.z))
    def xInside(self,x):
        """retourne vrai si la variable x est entre xmin et xmax"""
        return x>= self.min.x and x<= self.max.x

    def zInside(self,y):
        """retourne vrai si la variable x est entre xmin et xmax"""
        return y>= self.min.z and y<= self.max.z

    def isInsideX(self,bbox2):
        """renvoie 1 si la bbox est complètement à l'intérier
           renoive 2 si elle est à cheval
           et 0 si à l'extérieur"""
        minInside = self.xInside(bbox2.xmin)
        maxInside = self.xInside(bbox2.xmax)
        if minInside and maxInside : return 1
        if minInside or maxInside : return 2
        #si bbox1 est plus grand
        if bbox2.xmin < self.min.x and bbox2.xmax > self.max.x : return 2
        return 0

    def isInsideZ(self,bbox2):
        """renvoie 1 si la bbox est complètement à l'intérier
           renoive 2 si elle est à cheval
           et 0 si à l'extérieur"""
        minInside = self.zInside(bbox2.ymin)
        maxInside = self.zInside(bbox2.ymax)
        if minInside and maxInside : return 1
        if minInside or maxInside : return 2
        #si bbox1 est plus grand
        if bbox2.ymin < self.min.z and bbox2.ymax > self.max.z : return 2
        return 0

    def ptIsInside(self,pt):
        """renvoie vrai si point c4d est à l'intérieur"""
        return  self.xInside(pt.x) and self.zInside(pt.z)

    def get_pts(self):
        """renvoie les 4 points de la bbox"""
        p1 = self.min
        p2 = c4d.Vector(self.min.x,0,self.max.z)
        p3 = self.max
        p4 = c4d.Vector(self.max.x,0,self.min.z)
        return [p1,p2,p3,p4]

    def touch(self,bbox2):
        """si un des 4 points de la bbox est à l'intérieur renvoie true"""
        for pt in self.get_pts():
            if bbox2.ptIsInside(pt):
                return True
        return False

    @staticmethod
    def fromObj(obj,origine = c4d.Vector()):
        """renvoie la bbox 2d de l'objet"""
        mg = obj.GetMg()

        rad = obj.GetRad()
        centre = obj.GetMp()

        #4 points de la bbox selon orientation de l'objet
        pts = [ c4d.Vector(centre.x+rad.x,centre.y+rad.y,centre.z+rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y+rad.y,centre.z+rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y-rad.y,centre.z+rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y-rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x+rad.x,centre.y-rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x+rad.x,centre.y+rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y+rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x+rad.x,centre.y-rad.y,centre.z+rad.z) * mg]

        mini = c4d.Vector(min([p.x for p in pts]),min([p.y for p in pts]),min([p.z for p in pts])) + origine
        maxi = c4d.Vector(max([p.x for p in pts]),max([p.y for p in pts]),max([p.z for p in pts])) + origine

        return Bbox(mini,maxi)

    def getCube(self,haut = 2000):
        res = c4d.BaseObject(c4d.Ocube)
        taille = c4d.Vector(self.largeur,haut,self.hauteur)
        res[c4d.PRIM_CUBE_LEN] = taille
        pos = self.centre
        pos.y = haut/2
        res.SetAbsPos(self.centre)
        return res

############################################################################################################
#FERMETURE DES TROUS
############################################################################################################
def selectContour(op):
    res = False

    nb = c4d.utils.Neighbor()
    nb.Init(op)
    bs = op.GetSelectedEdges(nb,c4d.EDGESELECTIONTYPE_SELECTION)
    bs.DeselectAll()
    for i,poly in enumerate(op.GetAllPolygons()):
        inf = nb.GetPolyInfo(i)
        if nb.GetNeighbor(poly.a, poly.b, i)==-1:
            bs.Select(inf['edge'][0])

        if nb.GetNeighbor(poly.b, poly.c, i)==-1:
            bs.Select(inf['edge'][1])


        #si pas triangle
        if not poly.c == poly.d :
            if nb.GetNeighbor(poly.c, poly.d, i)==-1:
                bs.Select(inf['edge'][2])
                res = True
        if nb.GetNeighbor(poly.d, poly.a, i)==-1:
            bs.Select(inf['edge'][3])
            res = True

    op.SetSelectedEdges(nb,bs,c4d.EDGESELECTIONTYPE_SELECTION)
    return res

def closePolys(op,doc):
    doc.SetMode(c4d.Medges)
    nbr = c4d.utils.Neighbor()
    nbr.Init(op)
    vcnt = op.GetPolygonCount()
    settings = c4d.BaseContainer()
    settings[c4d.MDATA_CLOSEHOLE_INDEX] = op
    doc.AddUndo(c4d.UNDO_CHANGE,op)

    for i in range(0,vcnt):
        vadr = op.GetPolygon(i)
        pinf = nbr.GetPolyInfo(i)
        if nbr.GetNeighbor(vadr.a, vadr.b, i) == c4d.NOTOK:
            settings[c4d.MDATA_CLOSEHOLE_EDGE] = pinf["edge"][0]
            c4d.utils.SendModelingCommand(command = c4d.ID_MODELING_CLOSEHOLE_TOOL, list = [op], mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION, bc = settings, doc = doc)
            nbr.Init(op)
        if nbr.GetNeighbor(vadr.b, vadr.c, i) == c4d.NOTOK:
            settings[c4d.MDATA_CLOSEHOLE_EDGE] = pinf["edge"][1]
            c4d.utils.SendModelingCommand(command = c4d.ID_MODELING_CLOSEHOLE_TOOL, list = [op], mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION, bc = settings, doc = doc)
            nbr.Init(op)
        if vadr.c != vadr.d and nbr.GetNeighbor(vadr.c, vadr.d, i) == c4d.NOTOK:
            settings[c4d.MDATA_CLOSEHOLE_EDGE] = pinf["edge"][2]
            c4d.utils.SendModelingCommand(command = c4d.ID_MODELING_CLOSEHOLE_TOOL, list = [op], mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION, bc = settings, doc = doc)
            nbr.Init(op)
        if nbr.GetNeighbor(vadr.d, vadr.a, i) == c4d.NOTOK:
            settings[c4d.MDATA_CLOSEHOLE_EDGE] = pinf["edge"][3]
            c4d.utils.SendModelingCommand(command = c4d.ID_MODELING_CLOSEHOLE_TOOL, list = [op], mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION, bc = settings, doc = doc)
            nbr.Init(op)

# Main function
def main():
    doc = c4d.documents.GetActiveDocument()
    path_doc = doc.GetDocumentPath()

    while not path_doc:
        rep = c4d.gui.QuestionDialog(TXT_NOT_SAVED)
        if not rep : return True
        c4d.documents.SaveDocument(doc, "", c4d.SAVEDOCUMENTFLAGS_DIALOGSALLOWED, c4d.FORMAT_C4DEXPORT)
        c4d.CallCommand(12098) # Enregistrer le projet
        path_doc = doc.GetDocumentPath()

    pth = os.path.join(path_doc,'swissbuildings3D_v3')
    if not os.path.isdir(pth):
        os.mkdir(pth)

    #dossier principal pour les shapefile
    pth_shapefile = os.path.join(pth,'shapefiles')
    if not os.path.isdir(pth_shapefile):
        os.mkdir(pth_shapefile)

    #chemin pour ogr2ogr

    path_to_QGISbin = getPathToQGISbin()
    if not path_to_QGISbin:
        c4d.gui.MessageDialog("QGIS n'est pas installé ou le chemin n'est pas le bon")
        return True


    #on vérifie que ogr2ogr est bien là
    path_to_ogr2ogr = ogrBIN_OK(path_to_QGISbin)
    if not path_to_QGISbin:
        c4d.gui.MessageDialog("Il semble qu'il manque ogr2ogr dans le dossier de QGIS")
        return True


    origine = doc[CONTAINER_ORIGIN]

    #si pas d'origine message et on quitte
    if not origine:
        c4d.gui.MessageDialog("Le document doit être géoréférencé")
        return

    mode = None

    #Si on a un objet sélectionné qui a une géométrie on l'utilise pour la bbox'
    if op and op.CheckType(c4d.Opoint):
        mini,maxi = empriseObject(op, origine)
        mode = "l'objet sélectionné"

    #sinon on prend la vue de haut
    else :
        bd = doc.GetActiveBaseDraw()
        camera = bd.GetSceneCamera(doc)

        if not camera[c4d.CAMERA_PROJECTION] == c4d.Ptop:
            c4d.gui.MessageDialog("Activez une vue de haut ou sélectionnez un objet pour l'emprise")
            return True
        mode = 'la vue de haut'
        mini, maxi = empriseVueHaut(bd, origine)

    #message pour confirmer le mode
    rep = c4d.gui.QuestionDialog(f"L'extraction va se faire selon l'emprise de {mode}.\nVoulez-vous continuer ?")
    if not rep : return

    xmin,ymin,xmax,ymax = mini.x,mini.z,maxi.x,maxi.z
    #url = 'swissbuildings3d_3_0_2016_1304-42_2056_5728.gdb.zip'
    url_base = 'https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissbuildings3d_3_0'
    lst = get_list_from_STAC_swisstopo(url_base,xmin,ymin,xmax,ymax)
    #pprint(lst)

    #TELECHARGEMENT
    for url in lst:
        name = url.split('/')[-1]
        fn_dst = os.path.join(pth,name)

        #on télécharge uniquement si le dossier gdb n'existe pas
        #pour le nom du gdb c'est un peu complexe
        #le fichier zippé s'appelle : swissbuildings3d_3_0_2020_1301-11_2056_5728.gdb.zip
        #et le dossier .gdb dézippé : swissBUILDINGS3D_3-0_1301-11.gdb
        #c'est un peu bricolé mais ça marche !
        pref = 'swissBUILDINGS3D_3-0_'
        suf = '.gdb'
        name_gdb = pref + name[len(pref)+5:-18] +suf
        fn_gdb = os.path.join(pth,name_gdb)

        if not os.path.isdir(fn_gdb):
            x = urllib.request.urlopen(url)
            with open(fn_dst,'wb') as saveFile:
                saveFile.write(x.read())

            #DEZIPPAGE
            with ZipFile(fn_dst, 'r') as zipObj:
                # Extract all the contents of zip file in current directory
                zipObj.extractall(pth)

            #suppression du zip
            os.remove(fn_dst)

    #conversion GDB->SHP
    for f in os.scandir(pth):
        if f.is_dir() and f.path[-4:]=='.gdb':
            fn_gdb = f.path
            dir_shp = os.path.join(pth_shapefile,os.path.basename(fn_gdb[:-4]))
            #on convertit uniquement si le dossier n'existe pas
            if not os.path.isdir(dir_shp):
                os.mkdir(dir_shp)
                req = f'"{path_to_ogr2ogr}" "{dir_shp}" "{fn_gdb}"'
                #print(req)
                output = subprocess.check_output(req,shell=True)

    #message pour avertir que c'est fini
    #c4d.gui.MessageDialog("Extraction terminée")

    doc.StartUndo()
    #IMPORT DES SHP
    onull_bat = c4d.BaseObject(c4d.Onull)
    onull_bat.SetName('swissbuildings3D_v3')
    path = os.path.join(path_doc,'swissbuildings3D_v3','shapefiles')
    for fn in listdirectory2(path):
        res = import_swissbuildings3D_v3_shape(fn,doc)
        res.InsertUnderLast(onull_bat)
    doc.InsertObject(onull_bat)
    doc.AddUndo(c4d.UNDOTYPE_NEW,onull_bat)

    #Effacer les bâtiment qui sont en dehors de l'emprise
    bbox_mnt = Bbox(mini-origine,maxi-origine)
    #print(bbox_mnt)
    del_lst = []
    for onull in onull_bat.GetChildren():
        for o in onull.GetChildren():
            bbox = Bbox.fromObj(o)
            if not bbox.touch(bbox_mnt):
                del_lst.append(o)
    #on efface
    for o in del_lst:
        o.Remove()

    #OPTIMISATION, fermeture des trous, et mise en rouge si pas ok

    for onull in onull_bat.GetChildren():

        #OPTIMIZE POINTS
        settings = c4d.BaseContainer()  # Settings
        settings[c4d.MDATA_OPTIMIZE_TOLERANCE] = 0.1
        settings[c4d.MDATA_OPTIMIZE_POINTS] = True
        settings[c4d.MDATA_OPTIMIZE_POLYGONS] = True
        settings[c4d.MDATA_OPTIMIZE_UNUSEDPOINTS] = True



        res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_OPTIMIZE,
                                        list=[o for o in onull.GetChildren()],
                                        mode=c4d.MODELINGCOMMANDMODE_POLYGONSELECTION,
                                        bc=settings,
                                        doc=doc)

        for o in onull.GetChildren():
            #on ferme d'abord les polygones'
            closePolys(o,doc)
            #si on a encore des edges contour on met l'objet en rouge
            if selectContour(o):
                o[c4d.ID_BASEOBJECT_USECOLOR] = c4d.ID_BASEOBJECT_USECOLOR_ALWAYS
                o[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(1,0,0)
                #icone
                o[c4d.ID_BASELIST_ICON_COLORIZE_MODE] =c4d.ID_BASELIST_ICON_COLORIZE_MODE_CUSTOM
                o[c4d.ID_BASELIST_ICON_COLOR]= c4d.Vector(1,0,0)
                #on le met en haut de la hierarchie
                o.InsertUnder(onull)
            else:
                o[c4d.ID_BASEOBJECT_USECOLOR] = c4d.ID_BASEOBJECT_USECOLOR_OFF
                o[c4d.ID_BASELIST_ICON_COLORIZE_MODE] =c4d.ID_BASELIST_ICON_COLORIZE_MODE_NONE

    ############################
    #MISE A L'ECHELLE
    ############################
    for onull in onull_bat.GetChildren():
        for o in onull.GetChildren():
            pos = o.GetAbsPos()
            #si l'objet avait déjà une échelle on remet sa pos.y à l'échelle 1
            if o[ID_BUILDING_SCALE]:
                pos.y/= o[ID_BUILDING_SCALE]

            pos.y *= SCALE_MNT
            o.SetAbsPos(pos)
            o[ID_BUILDING_SCALE] = SCALE_MNT


            scale = o.GetAbsScale()
            scale.y = SCALE_BUILDINGS
            o.SetAbsScale(scale)

    ############################
    #Sytème pour découper les bâtiments
    ############################
    #objet connector
    connector = c4d.BaseObject(c4d.Oconnector)
    connector[c4d.CONNECTOBJECT_PHONG_MODE]= c4d.CONNECTOBJECT_PHONG_MODE_MANUAL
    connector.SetName('swissbuildings3D_v3')

    #objet booleen
    booleen = c4d.BaseObject(c4d.Oboole)
    booleen[c4d.BOOLEOBJECT_TYPE] = c4d.BOOLEOBJECT_TYPE_INTERSECT
    booleen[c4d.BOOLEOBJECT_HIGHQUALITY] = True
    #on le désactive
    booleen[c4d.ID_BASEOBJECT_GENERATOR_FLAG] = False
    booleen.InsertUnder(connector)


    #on crée un cube pour découper les bâtiments
    cube = bbox_mnt.getCube()
    cube[c4d.ID_BASEOBJECT_XRAY] = True
    cube.InsertUnder(booleen)

    #on insère les bâtiemnts
    onull_bat.InsertUnder(booleen)

    doc.InsertObject(connector)
    doc.AddUndo(c4d.UNDOTYPE_NEW,connector)

    doc.EndUndo()
    c4d.EventAdd()


# Execute main(lst)
if __name__=='__main__':
    main()