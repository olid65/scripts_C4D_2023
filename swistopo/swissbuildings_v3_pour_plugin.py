from typing import Optional
import c4d
import os
from glob import glob
import sys

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

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

def get_swissbuildings3D_v3_gdbs(path):
    """renvoie une liste de fichier dxf contenus dans
       un sous-dossier qui contient le mot swissbuildings3d"""
    lst_gdb = None

    for root, dirs, files in os.walk(path, topdown=False):
        for name in dirs:
            #print(name)
            if name == 'swissbuildings3d_v3' :
                lst_gdb = [fn_dxf for fn_dxf in glob(os.path.join(root, name,'*.gdb'))]
    return lst_gdb


def gdbs2shp(lst_gdbs,path_to_ogr2ogr):
    #conversion GDB->SHP
        
    for fn_gdb in lst_gdbs:
        dir_shp = os.path.join(pth_shapefile,os.path.basename(fn_gdb[:-4]))
        #on convertit uniquement si le dossier n'existe pas
        if not os.path.isdir(dir_shp):
            os.mkdir(dir_shp)
            req = f'"{path_to_ogr2ogr}" "{dir_shp}" "{fn_gdb}"'
            #print(req)
            output = subprocess.check_output(req,shell=True)


def main() -> None:
    
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
    
    path = "/Users/olivierdonze/Documents/TEMP/test_meyrin/swisstopo"
    
    lst_gdbs = get_swissbuildings3D_v3_gdbs(path)
    
    #TODO si on n'a pas de gdb ???'
    
    gdbs2shp(lst_gdbs,path_to_ogr2ogr)
    

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()