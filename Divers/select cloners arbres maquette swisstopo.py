from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

NAME_FOR_SEARCH = ['Forêts','Arbres isolés']

def searchCloneurs(obj, lst = [], stop = None):
    while obj:
        if obj.CheckType(c4d.Omgcloner):
            lst.append(obj)
        searchCloneurs(obj.GetDown(), lst = lst, stop = stop)
        if obj == stop : return lst
        obj = obj.GetNext()
    return lst

def main() -> None:

    lst_parent = []
    lst_cloners = []

    for name in NAME_FOR_SEARCH:
        obj = doc.SearchObject(name)
        if obj:
            searchCloneurs(obj, lst = lst_cloners, stop = obj)

    for i,o in enumerate(lst_cloners):
        if i:
            doc.SetActiveObject(o,c4d.SELECTION_ADD)
        else:
            doc.SetActiveObject(o,c4d.SELECTION_NEW)

    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()