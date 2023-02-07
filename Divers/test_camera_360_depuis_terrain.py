from typing import Optional
import c4d
from math import pi

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def CreateKey(op,id,value,frame):

    # First check if the track type already exists, otherwise create it...
    track=op.FindCTrack(id)
    if not track:
        track=c4d.CTrack(op,id)
        op.InsertTrackSorted(track)

    curve=track.GetCurve()
    key=curve.AddKey(c4d.BaseTime(frame,doc.GetFps()))

    #ATTENTION SetValue est uniquement fait pour les float, ne marche pas avec des int !!!
    #
    if type(value)==float: #type(value)==int or
        key["key"].SetValue(curve,value)
        #print key["key"].GetValue(curve,value)
    else:
        key["key"].SetGeData(curve,value)

def main() -> None:
    #calcul de la bounding box du terrain
    terrain = op
    bbox = terrain.GetRad()

    #calcul de la hauteur du terrain
    hauteur = bbox.y
    #calcul de la largeur du terrain
    largeur = bbox.x
    #calcul de la profondeur du terrain
    profondeur = bbox.z
    #calcul de la position du terrain
    position = terrain.GetAbsPos()

    #création d'un objet null
    nullobj = c4d.BaseObject(c4d.Onull)
    nullobj.SetName('camera 360° aninmation')
    nullobj.SetAbsPos(c4d.Vector(position.x, position.y + hauteur, position.z))
    doc.InsertObject(nullobj)

    #création d'une camera
    camera = c4d.BaseObject(c4d.Ocamera)
    camera.InsertUnder(nullobj)
    #positionnement de la camera
    camera.SetRelPos(c4d.Vector(largeur,0,0))

    #création d'un objet null au centre du terrain
    nullobj2 = c4d.BaseObject(c4d.Onull)
    nullobj2.SetName('cible camera360')
    nullobj2.SetAbsPos(terrain.GetMp()*terrain.GetMg())
    doc.InsertObject(nullobj2)

    #création d'un tag cible
    tag = c4d.BaseTag(c4d.Ttargetexpression)
    tag[c4d.TARGETEXPRESSIONTAG_LINK] = nullobj2
    camera.InsertTag(tag)

    #animation de la rotation de nullobj sur l'axe X de 0 à 360 en 90 frames
    # DESCID
    id_rot = c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_ROTATION,c4d.DTYPE_VECTOR,0), c4d.DescLevel(c4d.VECTOR_X, c4d.DTYPE_REAL,0)) #DescLevel(ID_BASEOBJECT_ROTATION, DTYPE_VECTOR, 0), DescLevel(VECTOR_X, DTYPE_REAL,0)
    CreateKey(nullobj,id_rot,0,0)
    CreateKey(nullobj,id_rot,pi*2,90)

    c4d.EventAdd()


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()