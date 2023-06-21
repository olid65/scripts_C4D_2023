from typing import Optional
import c4d
from pathlib import Path
import zipfile

def decompress_files_in_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.zip'):
            file_path = os.path.join(directory, filename)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(directory)
            print(f"Le fichier '{filename}' a été décompressé avec succès.")


doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    pth = '/Users/olivierdonze/Downloads/20_Outils de représentation graphique-Travail personnel pour lévaluation Indesign-2028616'
    
    path = Path(pth)
    
    for z in sorted(path.rglob('*.zip')):
        pdir = Path(str(z)[:-4])
        if not pdir.is_dir():
            with zipfile.ZipFile(z, 'r') as zip_ref:
                zip_ref.extractall(pdir.parent)
    

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()