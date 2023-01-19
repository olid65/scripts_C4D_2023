import c4d
import json
import urllib.request
import webbrowser 
import pyautogui


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# zoom max = 13
# zoom min = 1

#pour une largeur d'écran de 2560 px
#valeurs de zoom (mesurée manuellement pour chaque niveau
#vraiment pas précis !! :
dic_zoom = {13 : 255.90/2560,
            12 : 639/2560,
            11 : 1270/2560,
            10 : 2550/2560,
            9 : 5110/2560,
            8 : 6390/2560,
            7 : 12780/2560,
            6 : 25570/2560,
            5 : 51120/2560,
            4 : 127850/2560,
            3 : 255600/2560,
            2 : 639000/2560,
            1 : 1278000/2560,
            }

#valeurs des pixels en mètre
#attention rajouter 1 à l'id de la list pour que cela corresponde au niveau de zoom 
#(a été calculé à partir des mesure faites dans dic_zoom)
val_pix = [ 499.21875 ,
            249.609375 ,
            99.84375 ,
            49.94140625 ,
            19.96875 ,
            9.98828125 ,
            4.9921875 ,
            2.49609375 ,
            1.99609375 ,
            0.99609375 ,
            0.49609375 ,
            0.249609375 ,
            0.0999609375 ,]

CONTAINER_ORIGIN =1026473

def empriseVueHaut(bd,origine):
    dimension = bd.GetFrame()
    largeur = dimension["cr"]-dimension["cl"]
    hauteur = dimension["cb"]-dimension["ct"]
    mini =  bd.SW(c4d.Vector(0,hauteur,0)) + origine
    maxi = bd.SW(c4d.Vector(largeur,0,0)) + origine
    return  mini,maxi,largeur,hauteur


def bbox_object(obj,origin):
    pos = obj.GetMg().off
    mp = obj.GetMp()
    rad = obj.GetRad()

    centre = origin+pos+mp

    c4d.CopyStringToClipboard(str(centre.x-rad.x))
    xmin = centre.x-rad.x
    ymin = centre.z-rad.z
    xmax = centre.x+rad.x
    ymax = centre.z+rad.z
    return xmin,ymin,xmax,ymax


def lv95towgs84(x,y):
    url = f'http://geodesy.geo.admin.ch/reframe/lv95towgs84?easting={x}&northing={y}&format=json'

    f = urllib.request.urlopen(url)
    #TODO : vérifier que cela à bien fonctionnéé (code =200)
    txt = f.read().decode('utf-8')
    json_res = json.loads(txt)

    return float(json_res['easting']),float(json_res['northing'])


# Main function
def main():
    #on récupère la taille de l'écran actif
    screen_size = pyautogui.size()
    origin = doc[CONTAINER_ORIGIN]

    """if op:
        xmin,ymin,xmax,ymax = bbox_object(op,origin)
        xmin,ymin = lv95towgs84(xmin,ymin)
        xmax,ymax = lv95towgs84(xmax,ymax)

        print(f'{op.GetName()} : {ymin},{xmin},{ymax},{xmax}')"""

    bd = doc.GetActiveBaseDraw()
    mini,maxi, larg, haut = empriseVueHaut(bd,origin)
    
    #calcul de la valeur du pixel dans la cible
    px = (maxi.x-mini.x)/screen_size.width
    print('px',px)
    zoom = 13
    for i,v in enumerate(val_pix):
        #print('v',v)
        if v<px:
            zoom = i
            break
    centre = (mini+maxi)/2
    x,z = centre.x,centre.z
    url = 'https://map.geo.admin.ch/?lang=fr&topic=ech&bgLayer=ch.swisstopo.pixelkarte-farbe&layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.astra.wanderland-sperrungen_umleitungen&layers_opacity=1,1,1,0.8,0.8&layers_visibility=false,false,false,false,false&layers_timestamp=18641231,,,,'
    url = 'https://map.geo.admin.ch/?lang=fr'
    url+= f'&E={x}&N={z}&zoom={zoom}'
    webbrowser.open(url)
    return


    xmin,ymin = lv95towgs84(mini.x,mini.z)
    xmax,ymax = lv95towgs84(maxi.x,maxi.z)

    print(f'vue : {ymin},{xmin},{ymax},{xmax}')



# Execute main()
if __name__=='__main__':
    main()