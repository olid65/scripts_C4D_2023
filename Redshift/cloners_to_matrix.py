from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

#ATTENTION TRANFORME TOUS LES CLONEURS DU DOC EN MATRICE AVEC TAG REDSHIFT

def get_cloners(obj,typ = c4d.Omgcloner,lst = [], stop = None):
    while obj:
        if obj.CheckType(typ):
            lst.append(obj)
            print(obj.GetName())
        get_cloners(obj.GetDown(),lst = lst, stop = stop)
        if obj == stop: return lst
        obj = obj.GetNext()
        
    return lst

def main() -> None:
    for o in doc.GetActiveObjects(0):
        o.DelBit(c4d.BIT_ACTIVE)
    obj = doc.GetFirstObject()

    lst = get_cloners(obj)
    for o in lst:
        o.SetBit(c4d.BIT_ACTIVE)
        
    c4d.CallCommand(440000237) # Swap Cloner/Matrix
    
    for o in doc.GetActiveObjects(0):
        tag_rs = c4d.BaseTag(1036222)# tag RS object
        inexdata = c4d.InExcludeData()
        o.InsertTag(tag_rs)
        for child in o.GetChildren():
            child[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.OBJECT_UNDEF
            child[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = c4d.OBJECT_UNDEF
            inexdata.InsertObject(child,1)
        tag_rs[c4d.REDSHIFT_OBJECT_PARTICLE_MODE] = 4 # mode custom object = 4 sphere =2    
        tag_rs[c4d.REDSHIFT_OBJECT_PARTICLE_CUSTOM_OBJECTS] = inexdata    
        
    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()