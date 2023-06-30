from typing import Optional
import c4d
from pyproj import Transformer


doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

#constante container origin
CONTAINER_ORIGIN = 1026473

def main() -> None:
    #url = "https://www.google.com/maps/place/Obergoms/@46.4798944,8.2851014,1146a,35y,32.91h,77.74t/data=!3m1!1e3!4m6!3m5!1s0x478580089c14aab9:0xe4cfe63dc9be31ec!8m2!3d46.5341052!4d8.3495309!16s%2Fm%2F05p030f?entry=ttu"

    dbt_url = 'https://www.google.com/maps'

    #on vérifie que le doc est géoréférencé
    origin = doc[CONTAINER_ORIGIN]
    if not origin:
        c4d.gui.MessageDialog("Le document n'est pas géoréférencé")
        return
    #récupération de l'url dans le presse-papier
    url = None
    if c4d.GetClipboardType() == c4d.CLIPBOARDTYPE_STRING:
        url = c4d.GetStringFromClipboard()
        print(url)
        if not len(url)>len(dbt_url) and not url[:len(dbt_url)] == dbt_url:
            url= None
    if not url:
        #message d'erreur
        c4d.gui.MessageDialog("Pas d'url dans le presse-papier ou url non valide")
        return

    # Extract the latitude and longitude
    lat,lon,alt,tilt,heading,fov =  url.split("/")[-2].split("@")[1].split(",")
    alt = float(alt[:-1])
    tilt = float(tilt[:-1])
    heading = float(heading[:-1])
    fov = float(fov[:-1])
    print(alt,tilt,heading,fov)

    #conversion wgs84 to lv95
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:2056")

    x,y = transformer.transform(lat, lon)
    pos_camera = c4d.Vector(x,alt,y) - origin

    #création de la caméra
    cam = c4d.BaseObject(c4d.Ocamera)
    cam.SetAbsPos(pos_camera)

    doc.StartUndo()
    doc.InsertObject(cam)
    #doc.SetActiveObject(cam)
    doc.AddUndo(c4d.UNDOTYPE_NEW, cam)
    doc.EndUndo()
    c4d.EventAdd()


    return

    # Extract the other parameters
    params = parse_qs(parsed_url.query)

    elevation = params["!3m1"][0]
    tilt = params["35y"][0]
    heading = params["32.91h"][0]
    fov = params["77.74t"][0]

    print("Latitude:", latitude)
    print("Longitude:", longitude)
    print("Elevation:", elevation)
    print("Tilt:", tilt)
    print("Heading:", heading)
    print("Field of View:", fov)

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()