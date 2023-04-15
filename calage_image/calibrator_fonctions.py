from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

ID_TAG_OD_CALIBRATOR  = 1032459

def getFirstCalibratorTag(doc, obj = c4d.NOTOK):
    if obj ==  c4d.NOTOK:
        obj = doc.GetFirstObject()
    while obj:
        tag = obj.GetTag(ID_TAG_OD_CALIBRATOR)
        if tag : return tag
        tag = getFirstCalibratorTag(doc, obj.GetDown())
        if tag : return tag
        obj = obj.GetNext()
    return None



def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    
    tag = doc.GetActiveTag()
    
    if not tag or not tag.CheckType(ID_TAG_OD_CALIBRATOR):
        tag = getFirstCalibratorTag(doc, obj = c4d.NOTOK)
    
    
    

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()