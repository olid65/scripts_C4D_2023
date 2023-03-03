from typing import Optional
import c4d
import sys
from math import pi, asinh,tan,radians,pow, cos
from pprint import pprint
import os
from glob import glob
import urllib.request

""" Sélectionner un objet ->position de l'axe """

try :
    from pyproj import Transformer
except:
    sys.path.append('/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
    from pyproj import Transformer


#d'après https://cs108.epfl.ch/archive/22/p/02_osm.html'

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

CONTAINER_ORIGIN =1026473
C = 40075016.686 #taille de la terre à l'équateur


def empriseVueHaut(bd, origine):
    dimension = bd.GetFrame()
    largeur = dimension["cr"] - dimension["cl"]
    hauteur = dimension["cb"] - dimension["ct"]

    mini = bd.SW(c4d.Vector(0, hauteur, 0)) + origine
    maxi = bd.SW(c4d.Vector(largeur, 0, 0)) + origine

    return mini, maxi, largeur, hauteur


def empriseObject(obj, origine):
    mg = obj.GetMg()

    rad = obj.GetRad()
    centre = obj.GetMp()

    # 4 points de la bbox selon orientation de l'objet
    pts = [c4d.Vector(centre.x + rad.x, centre.y + rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y + rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y - rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y - rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y - rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y + rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y + rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y - rad.y, centre.z + rad.z) * mg]

    mini = c4d.Vector(min([p.x for p in pts]), min([p.y for p in pts]), min([p.z for p in pts])) + origine
    maxi = c4d.Vector(max([p.x for p in pts]), max([p.y for p in pts]), max([p.z for p in pts])) + origine

    return mini, maxi

def LV95_to_WGS84(x,y):
    transformer = Transformer.from_crs("EPSG:2056","EPSG:4326")
    return transformer.transform(x, y)


#d'après https://cs108.epfl.ch/archive/22/p/02_osm.html'

def latlon2xy(lat,lon):
    x = (1/(2*pi)) * (radians(lat) + pi)
    y = (1/(2*pi)) * (pi-asinh(tan(radians(lon))))
    return x,y

def pos_tuile_OSM(x,y,zoom = 19):
    fact = pow(2,8+zoom)
    return x*fact, y*fact

def get_tile_index(point,zoom):
    lon,lat = LV95_to_WGS84(point.x,point.z)
    x,y = latlon2xy(lat,lon)
    x,y = pos_tuile_OSM(x,y,zoom = zoom)
    return int(x/256), int(y/256)

def get_OSMtile_from_ptlv95(point,zoom):
    """renvoie l'url de la tuile osm"""
    x,y = get_tile_index(point,zoom)
    # types de cartes disponibles ->
    # https://wiki.openstreetmap.org/wiki/Raster_tile_providers

    #https://manage.thunderforest.com/dashboard (inscription -> api_key)
    api_key = '363ccef1633546f9a38bde9e0d53c879'
    dic = {'OpenCycleMap' : f'https://tile.thunderforest.com/cycle/{zoom}/{x}/{y}.png?apikey={api_key}',
           'Transport'    : f'https://tile.thunderforest.com/transport/{zoom}/{x}/{y}.png?apikey={api_key}',
           'Landscape'    : f'https://tile.thunderforest.com/landscape/{zoom}/{x}/{y}.png?apikey={api_key}',}

    url = f'https://tile.openstreetmap.org/{zoom}/{x}/{y}.png'
    #url = f'https://stamen-tiles.a.ssl.fastly.net/toner/{zoom}/{x}/{y}.png'
    #url = f'https://stamen-tiles.a.ssl.fastly.net/watercolor/{zoom}/{x}/{y}.jpg'
    return url


def main() -> None:
    larg_img_px = 256
    origine = doc[CONTAINER_ORIGIN]
    bd = doc.GetActiveBaseDraw()
    mini, maxi, l, h = empriseVueHaut(bd, origine)
    diff = maxi-mini
    largeur = maxi.x-mini.x
    centre = (maxi+mini)/2
    #calcul du zoom
    lon,lat = LV95_to_WGS84(centre.x,centre.z)
    taille_px_target = largeur/larg_img_px

    zoom = 0

    while zoom<=20:
        taille_px = C *cos(lat) * pow(0.5,zoom+8)
        if taille_px<taille_px_target:
            print(taille_px)
            break
        zoom+=1

    xmin_id,ymax_id = get_tile_index(mini,zoom)
    xmax_id,ymin_id = get_tile_index(maxi,zoom)
    print(xmin_id,xmax_id)
    print(ymin_id,ymax_id)
    dic_url = {}
    for i in range(xmax_id-xmin_id+1):
        for n in range(ymax_id-ymin_id+1):
            x,y = (xmin_id+i,ymin_id+n)
            dic_url[(x,y)] = f'https://tile.openstreetmap.org/{zoom}/{x}/{y}.png'

    print(print(dic_url))
    pprint(dic_url)
    
    
    pth_dwnload = '/Users/olivierdonze/Documents/TEMP/dwnld_OSM_tiles'
    #on vide le dossier
    #for fn in glob(os.path.join(pth_dwnload,'/*')):
        #os.remove(fn)
    
    for (x,y),url in dic_url.items():
        print(url)
        continue
        ext = url.split('.')[-1]
        fn = os.path.join(pth_dwnload,f'{x}_{y}{ext}')
        
        req = urllib.request.Request(
            url=url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response = urllib.request.urlopen(req,timeout=10)
        
        #response = urllib.request.urlopen(url)
        
        with open(fn, 'wb') as file:
            file.write(response.read())
    return




    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    v = doc[CONTAINER_ORIGIN]+op.GetMg().off
    lon,lat = LV95_to_WGS84(v.x,v.z)

    #voir https://wiki.openstreetmap.org/wiki/Zoom_levels
    #C ∙ cos(latitude) / 2 (zoomlevel + 8)
    taille_tuile = C *cos(lat) * pow(0.5,zoom)
    print(taille_tuile)
    taille_px = C *cos(lat) * pow(0.5,zoom+8)
    print(taille_px)

    print(get_OSMtile_from_ptlv95(v,zoom))
    
    #
    




"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()