from typing import Optional
import c4d
from extractor import isRectangleNordSud, getPathToQGISbin, DlgBbox, empriseObject, get_list_from_STAC_swisstopo
from extractor import URL_STAC_SWISSTOPO_BASE, DIC_LAYERS, CONTAINER_ORIGIN, FOLDER_NAME_SWISSTOPO

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