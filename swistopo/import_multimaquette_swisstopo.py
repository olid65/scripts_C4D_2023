from typing import Optional
import c4d
import os
from extractor import isRectangleNordSud, getPathToQGISbin, DlgBbox, empriseObject, get_list_from_STAC_swisstopo
from extractor import URL_STAC_SWISSTOPO_BASE, DIC_LAYERS, CONTAINER_ORIGIN, FOLDER_NAME_SWISSTOPO
import shutil

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

MNT_MIN = 0.5
PAS_MNT = 0.1 #incrément pour taille de la maille pour approximer le nb max de points
MAX_PTS_MNT = 2000000 #Nombre max de points dans le MNT en milions

MNT = True
BATI3D = True
ARBRES = False
FORETS = False
ORTHO = False

def main() -> None:
    #chemin pour dossier tex
    path_tex = os.path.join(doc.GetDocumentPath(),'tex')

    origine = doc[CONTAINER_ORIGIN]

    #création d'un dossier avec le même nom que le fichier c4d
    dir_main = os.path.join(doc.GetDocumentPath(),doc.GetDocumentName()[:-4])
    os.makedirs(dir_main, exist_ok=True)

    #création d'un dossier par plan
    for o in doc.GetActiveObjects(0):
        #nom sans extension
        name = o.GetName()[:-4]
        #création du dossier
        path = os.path.join(dir_main,name)
        if not os.path.exists(path):
            os.makedirs(path)
        #création d'un nouveau fichier.c4d dans le dossier
        fn_c4d = os.path.join(path,name+'.c4d')
        if not os.path.isfile(fn_c4d):
            doc2 = c4d.documents.BaseDocument()
            #document en mètres
            doc2[c4d.DOCUMENT_DOCUNIT] = c4d.UnitScaleData(doc[c4d.DOCUMENT_DOCUNIT])
            clone = o.GetClone()
            #tag Ttexture
            mat_clone = None
            tag = o.GetTag(c4d.Ttexture)
            if tag:
                mat = tag[c4d.TEXTURETAG_MATERIAL]
                if mat:
                    mat_clone = mat.GetClone()
                    doc2.InsertMaterial(mat_clone)
            if mat_clone:
                tag_clone = clone.GetTag(c4d.Ttexture)
                if tag_clone:
                    tag_clone[c4d.TEXTURETAG_MATERIAL] = mat_clone     

            #copie de l'image utilisée par le tag Ttexture dans le dossier tex de la nouvelle scène
            if mat_clone and mat:
                shd = mat[c4d.MATERIAL_COLOR_SHADER]
                if shd:
                    fn_img = shd[c4d.BITMAPSHADER_FILENAME]
                    fn_img_full = os.path.join(path_tex,fn_img)
                    if fn_img:
                        #copie de l'image dans le dossier tex du doc2
                        fn_img2 = os.path.join(path,'tex',os.path.basename(fn_img))
                        if not os.path.isfile(fn_img2):
                            os.makedirs(os.path.dirname(fn_img2), exist_ok=True)
                            shutil.copyfile(fn_img_full, fn_img2)
            #TODO : centrer l'objet dans le nouveau fichier et modifier la position de l'origine    
            doc2[CONTAINER_ORIGIN]= origine
            #copie de l'objet dans le nouveau fichier
            doc2.InsertObject(clone)
            c4d.documents.SaveDocument(doc2, fn_c4d, c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST, c4d.FORMAT_C4DEXPORT)
            #print(f"Création de {fn_c4d}")
        
    
    return
    splines = [sp for sp in doc.GetActiveObjects(0) if sp.CheckType(c4d.Ospline) or sp.GetPointCount()!=4]
    if not splines:
        c4d.gui.MessageDialog("Il n'y a pas de splines sélectionnées (ou les splines n'ont pas 4 points)")
        return

    origine = doc[CONTAINER_ORIGIN]
    if not origine:
        c4d.gui.MessageDialog(DlgBbox.TXT_NO_ORIGIN)
        return

    #Vérification que le fichier est enregistré
    path_doc = doc.GetDocumentPath()

    while not path_doc:
        rep = c4d.gui.QuestionDialog(self.TXT_NOT_SAVED)
        if not rep : return True
        c4d.documents.SaveDocument(doc, "", c4d.SAVEDOCUMENTFLAGS_DIALOGSALLOWED, c4d.FORMAT_C4DEXPORT)
        c4d.CallCommand(12098) # Enregistrer le projet
        path_doc = doc.GetDocumentPath()

    #Vérification qu'on n'est pas sur le NAS de l'école
    if 'hes-nas-prairie.hes.adhes.hesge.ch' in path_doc:
        c4d.gui.MessageDialog(self.TXT_NAS_HEPIA)
        return True

    #Vérification qu'il n'y ait pas de caractères spéciaux dans le chemin !
    #GDAL ne supporte pas
    try :
        path_doc.encode(encoding='ASCII')
    except:
        c4d.gui.MessageDialog(self.TXT_PATH_CAR_SPECIAL)
        return True


    qgispath = getPathToQGISbin()

    if not qgispath:
        rep = c4d.gui.QuestionDialog(DlgBbox.TXT_NO_PATH_TO_QGIS_QUESTION)
        if not rep : return

    urls =[]

    for sp in splines:
        #print(isRectangleNordSud(sp))

        bbox = empriseObject(sp, origine)
        if not bbox:
            print(f"Pas de bbox pour {sp.GetName()}")
            continue
        mini,maxi = bbox
        xmin,ymin,xmax,ymax = mini.x,mini.z,maxi.x,maxi.z
        larg = xmax-xmin
        haut = ymax-ymin


        #calcul de la taille de la maille
        taille_maille = MNT_MIN
        nb_pts_mnt = (larg/taille_maille) * (haut/taille_maille)
        while nb_pts_mnt>(MAX_PTS_MNT):
            taille_maille+=PAS_MNT
            nb_pts_mnt =  (larg/taille_maille) * (haut/taille_maille)

        #MNT
        if MNT:

            tri = '_2_'

            if taille_maille <2:
                tri = '_0.5_'

            url = URL_STAC_SWISSTOPO_BASE+DIC_LAYERS['mnt']
            lst = [v for v in get_list_from_STAC_swisstopo(url,xmin,ymin,xmax,ymax) if tri in v]

            for url in lst:
                if url not in urls:
                    urls.append(url)

            print(len(urls))


    print(urls[0])

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()