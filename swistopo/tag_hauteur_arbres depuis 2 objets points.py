from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

"""Sélectionner le cloneur
   les objets suivants sont points collet et point sommets"""
   
HAUT_SRCE = 10

def main() -> None:
    cloner = op
    pts_collets = cloner.GetNext()
    pts_sommets = pts_collets.GetNext()

    hauteurs = []
    for pt_collet, pt_sommet in zip(pts_collets.GetAllPoints(),pts_sommets.GetAllPoints()):
        haut = pt_sommet.y - pt_collet.y
        hauteurs.append(haut)


    tagHauteurs = c4d.BaseTag(440000231)
    cloner.InsertTag(tagHauteurs)
    tagHauteurs.SetName('facteurs_hauteur_arbres')
    # ATTENTION bien mettre des float dans la liste sinon cela ne marche pas !
    scale_factor_haut = lambda x: float(x) / HAUT_SRCE - 1.
    c4d.modules.mograph.GeSetMoDataWeights(tagHauteurs, [scale_factor_haut(h) for h in hauteurs])
    
    c4d.EventAdd()


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()