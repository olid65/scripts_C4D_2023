from typing import Optional
import c4d
import os

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    pth = doc.GetDocumentPath()
    if not pth :
        print('Document non enregistré')
        return
    
    
    #création d'un dossier de rendu au m^ême emplacement que le fichier
    dir_render = os.path.join(pth,'rendus')
    os.makedirs(dir_render, exist_ok=True)
    
    
    rd = doc.GetActiveRenderData()
    rd[c4d.RDATA_FORMAT]= 1104 #JPEG
    rd[c4d.RDATA_PATH] = os.path.join(dir_render,'$prj_$YY$MM$DD_$hh$mm$ss')
    rd.Message(c4d.MSG_UPDATE)
    
    c4d.EventAdd()
    

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()