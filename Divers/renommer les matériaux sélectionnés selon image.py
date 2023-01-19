from typing import Optional
import c4d
import os

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    for mat in doc.GetActiveMaterials():
        shd = mat.GetFirstShader()
        print(shd)
        while shd:
            if shd.CheckType(c4d.Xbitmap):
                if shd[c4d.BITMAPSHADER_FILENAME]:
                    mat.SetName(os.path.basename(shd[c4d.BITMAPSHADER_FILENAME])[:-4])
                    break
            shd = shd.GetNext()
    c4d.EventAdd()    


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()