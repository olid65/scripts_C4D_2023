from typing import Optional
import c4d
import urllib.request
import urllib.error
import json

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected


URL_STAC_SWISSTOPO_BASE = 'https://data.geo.admin.ch/api/stac/v0.9/collections/'


DIC_LAYERS = {'ortho':'ch.swisstopo.swissimage-dop10',
              'mnt':'ch.swisstopo.swissalti3d',
              'mns':'ch.swisstopo.swisssurface3d-raster',
              'bati3D':'ch.swisstopo.swissbuildings3d_2',
              'bati3D_v3':'ch.swisstopo.swissbuildings3d_3_0',
              }
def lv95towgs84(x,y):
    url = f'http://geodesy.geo.admin.ch/reframe/lv95towgs84?easting={x}&northing={y}&format=json'

    f = urllib.request.urlopen(url)
    #TODO : vérifier que cela à bien fonctionnéé (code =200)
    txt = f.read().decode('utf-8')
    json_res = json.loads(txt)

    return float(json_res['easting']),float(json_res['northing'])


def main() -> None:
    
    url = URL_STAC_SWISSTOPO_BASE + DIC_LAYERS['mns']
    
    xmin,ymin,xmax,ymax = 2565394.585999999,1100495.015999999,2565894.585999999,1100695.015999999
    
    #conversion coordonnées
    est,sud = lv95towgs84(xmin,ymin)
    ouest, nord = lv95towgs84(xmax,ymax)
    
    sufixe_url = f"/items?bbox={est},{sud},{ouest},{nord}"
    url += sufixe_url
    
    data = None
    try :
        f = urllib.request.urlopen(url)
        status_code = f.getcode()
    
        if status_code == 200:
            # Traitement des données de la réponse ici
            data = f.read()
            #print("Succès :", data)
        else:
            print(f"Erreur HTTP {status_code}: La requête a échoué.")
            
    except urllib.error.HTTPError as e:
        # Gérer les erreurs HTTP (par exemple, 404, 500, etc.)
        print(f"Erreur HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        # Gérer les erreurs d'URL (par exemple, URL invalide)
        print(f"Erreur d'URL : {e.reason}")
    except Exception as e:
        # Gérer les autres erreurs potentielles
        print(f"Une erreur s'est produite : {e}")
        
    if not data : 
        print('No data')
        return None
    
    res = []
    json_res = json.loads(data)
    links = json_res.get('links', None)
    if links :
        for link in links:
            if link['rel'] == 'next':
                #url = link['href']  
                print(link['href']) 
    
    for item in json_res['features']:
            for k,dic in item['assets'].items():
                href = dic['href']
                res.append()
    
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()