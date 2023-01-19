import c4d
import json
import urllib.request


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

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
    origin = doc[CONTAINER_ORIGIN]
    
    if op:
        xmin,ymin,xmax,ymax = bbox_object(op,origin)
        xmin,ymin = lv95towgs84(xmin,ymin)
        xmax,ymax = lv95towgs84(xmax,ymax)
        
        print(f'{op.GetName()} : {ymin},{xmin},{ymax},{xmax}')

    bd = doc.GetActiveBaseDraw()
    mini,maxi, larg, haut = empriseVueHaut(bd,origin)
    
    xmin,ymin = lv95towgs84(mini.x,mini.z)
    xmax,ymax = lv95towgs84(maxi.x,maxi.z)
    
    print(f'vue : {ymin},{xmin},{ymax},{xmax}')
    
    

# Execute main()
if __name__=='__main__':
    main()