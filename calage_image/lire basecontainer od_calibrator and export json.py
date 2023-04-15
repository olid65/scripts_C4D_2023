from typing import Optional
import c4d
import json

OD_CALIBRATOR = 1059348

"""Sélectionner le neutre contennat les points 3D généré par le plugin
   Calibrateur d'images
   Il doit contenir un BaseContainer
   le fn de l'image sous [0]
   et le sousbasecontainer avec lespoints 2D sous [1]
   et la taille de l'image sous [2]

   Changer manuellement le filename"""


doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected



def main() -> None:
    fn = '/Users/olivierdonze/Documents/Mandats/Meyrin1965/Meyrin1965.json'
    bc =  op[OD_CALIBRATOR]
    fn_img = bc[0]
    size_img = bc[2][0],bc[2][1]
    uvs = [(p[1].x,p[1].y,0) for p in bc[1]]
    vec2tuple = lambda v : (v.x,v.y,v.z)
    pts3D = [vec2tuple(o.GetMg().off) for o in op.GetChildren()]

    dico = {'fn_img':fn_img,
            'size_img':size_img,
            'uvs': uvs,
            'pts3D':pts3D}
    print(dico)

    with open(fn,'w') as f:
        f.write(json.dumps(dico, indent =4))

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()