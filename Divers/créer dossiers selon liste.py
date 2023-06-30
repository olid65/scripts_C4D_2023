from typing import Optional
import c4d
from pathlib import Path

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    lst =   ["Au fil de l’eau", "Végétal par étage", "Habiter", "Mobilité", "Savoir de montagne", "Paysage ordinaires et remarquables"]
    path = Path("/Users/olivierdonze/switchdrive/Mandats/Parc_naturel_regional_vallee_Trient/docs/projet_selecionnes_par_thematique")

    #créer les dossiers
    for i in lst:
        #on ajoute le nom du dossier à la fin du path
        path_dir = path / i
        #on crée le dossier
        path_dir.mkdir()




"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()