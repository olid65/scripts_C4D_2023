from typing import Optional
import c4d
import os
import glob
import sys

#DESACTIVE NE FONCTIONNE PLUS !!!
#message : ModuleNotFoundError: No module named 'pandas._libs.interval'
#import pandas as pd

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    # Définir le répertoire de travail
    directory = "/Users/olivierdonze/switchdrive/Mandats/Parc_naturel_regional_vallee_Trient/c4d/calage_travaux_etu/PNR_Trient_calage_AP3/tex"

    # Récupérer tous les fichiers .png et .wld dans le répertoire
    png_files = glob.glob(os.path.join(directory, "*.png"))
    #wld_files = glob.glob(os.path.join(directory, "*.wld"))

    # créer une liste pour stocker les noms de fichiers
    file_list = []

    # Parcourir les fichiers .png et ajouter les noms de fichiers à la liste
    for png_file in png_files:
        png_name = os.path.basename(png_file)
        # Récupérer le nom de fichier sans extension
        png_base_name = os.path.splitext(png_name)[0]
        print(png_file)
        print(png_file[:-4]+'.wld')
        if os.path.isfile(png_file[:-4]+'.wld'):
            file_list.append([png_name])

    # Créer un dataframe pandas à partir de la liste de fichiers
    #df = pd.DataFrame(file_list, columns=["PNG File"])

    # Enregistrer le dataframe dans un fichier .xlsx
    #df.to_excel(os.path.join(directory,"file_list.xlsx"), index=False)

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()