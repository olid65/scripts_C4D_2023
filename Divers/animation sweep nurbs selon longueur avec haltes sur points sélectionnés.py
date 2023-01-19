from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def CreateKey(op,id,value,frame,tangent = 0):

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
    if tangent:
        key["key"].SetTimeLeft(curve,c4d.BaseTime(-tangent,doc.GetFps()))
        key["key"].SetTimeRight(curve,c4d.BaseTime(tangent,doc.GetFps()))

def CreateKeyGrowth(op,frame,growth = 0.0, tangent = 0):
    # DESCID
    id_sweep_growth = c4d.DescID(c4d.DescLevel(c4d.SWEEPOBJECT_GROWTH,c4d.DTYPE_REAL,0))

    #création des clefs
    CreateKey(op,id_sweep_growth,growth,frame,tangent)

def DeleteAllGrowthKeys(op):
    #efface toutes les clefs d'une piste
    id_sweep_growth = c4d.DescID(c4d.DescLevel(c4d.SWEEPOBJECT_GROWTH,c4d.DTYPE_REAL,0))
    track=op.FindCTrack(id_sweep_growth)
    if track :
        curve=track.GetCurve()
        if curve:
            curve.FlushKeys()

def main() -> None:

    attente = 30 #nbre de frames pour la'ttente aux points de spline sélectionnée'
    vitesse = 100 #distance/frame
    tangent = 10

    frame_dprt = 0
    sweep = op
    sp = sweep.GetDown().GetNext()

    sph = c4d.utils.SplineHelp()
    #le flags SPLINEHELPFLAGS_RETAINLINEOBJECT est obligatoire pour la récup de LineObject (sph.SplineToLineIndex(i))
    sph.InitSplineWith(sp,flags = c4d.SPLINEHELPFLAGS_RETAINLINEOBJECT)
    lg = sph.GetSplineLength()
    line_obj = sph.GetLineObject()

    pts_select = []
    bs = sp.GetPointS()
    for i in range(sp.GetPointCount()):
        if bs.IsSelected(i):
            #id du point de la LineObject
            id_pt = sph.SplineToLineIndex(i)
            pts_select.append(id_pt)
    dist = 0
    pred = None

    #on effece les clés existantes
    DeleteAllGrowthKeys(sweep)
    #on crée la première clé
    CreateKeyGrowth(sweep,frame_dprt,growth = 0.0,tangent = tangent)
    no_halte = 0
    for i in range(line_obj.GetPointCount()):
        pt = line_obj.GetPoint(i)
        if pred:
            d = (pt-pred).GetLength()
            dist += d

        if i in pts_select:
            offset = dist/lg
            if 0.0<offset<1.0:

                frame = int(round(dist/vitesse))+no_halte*attente

                CreateKeyGrowth(sweep,frame,growth = offset,tangent = tangent)
                CreateKeyGrowth(sweep,frame+attente,growth = offset,tangent = tangent)
                no_halte+=1

        pred = pt

    #on crée la dernière clé
    frame = int(round(lg/vitesse))+no_halte*attente
    CreateKeyGrowth(sweep,frame,growth = 1.0,tangent = tangent)

    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()