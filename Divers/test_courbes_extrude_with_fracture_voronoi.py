from typing import Optional
import c4d
from math import ceil, floor

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

EQUIDIST = 0.5
#épaisseur de la tranche avant modification par effecteur
#elle doit avoir une certaine valeur mais être très fine
#après elle est multiplié par l'échelle y de l'effecteur simple
#pour éviter les bords en pente
EPAISSEUR_TRANCHE = 0.01

#nombre de courbe pour alerte
WARNING = 100
TXT_WARNING = f"Attention il y a plus de {WARNING} courbes \nVoulez vous continuer ?"


#TODO VERIFIER LES CALCULS POUR EPAISSEUR


def main() -> None:
    
    if not op:
        print("pas d'objet")
        return

    if not op.CheckType(c4d.Opolygon):
        print("pas d'objet polylgona")
        #TODO -> dans ce cas récupérer le cache
        return

    #SPLINE DECOUPE
    rad = op.GetRad()
    mp = op.GetMp()*op.GetMg()

    #TODO si l'axe est tourné ?

    alt_max = mp.y + rad.y
    alt_min = mp.y - rad.y


    alt_min=floor(alt_min/EQUIDIST)*EQUIDIST
    #print(alt_min)
    alt_max =ceil(alt_max/EQUIDIST)*EQUIDIST
    #print(alt_max)

    nb_courbes = (alt_max-alt_min)/EQUIDIST
    if nb_courbes>WARNING:
        rep =  c4d.gui.QuestionDialog( f"Attention il y a environ {int(nb_courbes)} courbes \nVoulez vous continuer ?")
        if not rep : return

    sp = c4d.SplineObject(2, c4d.SPLINETYPE_LINEAR)
    sp.SetPoint(0,c4d.Vector(0,alt_min,0))
    sp.SetPoint(1,c4d.Vector(0,alt_max,0))
    #sp.SetAbsPos()
    sp.Message(c4d.MSG_UPDATE)
    
    doc.StartUndo()
    doc.InsertObject(sp)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,sp)

    pt_amaount_sp = (alt_max-alt_min)/EQUIDIST+1 #à vérifier

    #VORONOI FRACTURE
    fract = c4d.VoronoiFracture()
    fract.AddSceneObject(sp)
    fract.Message(c4d.MSG_UPDATE)
    doc.InsertObject(fract)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,fract)
    #donner une épaisseur !
    fract[c4d.ID_FRACTURE_GAP] = (alt_max-alt_min)/(pt_amaount_sp-1)/2 - EPAISSEUR_TRANCHE
    bc = fract.GetSourceSettingsContainerForIndex(0)

    bc[c4d.ID_FRACTURETAG_POINTAMOUNT]= pt_amaount_sp
    
    clone = op.GetClone()
    clone.InsertUnder(fract)


    #EFFECTEUR SIMPLE POUR EPAISSEUR DES TRANCHES
    eff = c4d.BaseObject(c4d.Omgplain)
    eff[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = False
    eff[c4d.ID_MG_BASEEFFECTOR_SCALE_ACTIVE] = True
    eff[c4d.ID_MG_BASEEFFECTOR_SCALE,c4d.VECTOR_Y] = (EQUIDIST-EPAISSEUR_TRANCHE)/EPAISSEUR_TRANCHE/2
    doc.InsertObject(eff)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,eff)

    #ajout dans Fracture Voronoi
    ie_data = fract[c4d.ID_MG_VF_MOTIONGENERATOR_EFFECTORLIST]
    ie_data.InsertObject( eff, 1)
    fract[c4d.ID_MG_VF_MOTIONGENERATOR_EFFECTORLIST] = ie_data
    
    #objet d'origine invisible
    doc.AddUndo(c4d.UNDOTYPE_CHANGE,op)
    op[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.OBJECT_OFF
    op[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = c4d.OBJECT_OFF
    
    
    #doc.AddUndo(c4d.UNDOTYPE_CHANGE,op)
    doc.SetActiveObject(fract,c4d.SELECTION_NEW)
    
    doc.EndUndo()

    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()