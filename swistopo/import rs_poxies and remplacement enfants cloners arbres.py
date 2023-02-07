from typing import Optional
import c4d
import os
from glob import glob

"""SELECTIONNER LES OBJETS PARENTS POUVANT CONTENIR LES CLONERS"""

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def getAllcloners(obj,start,lst = []):
    while obj:
        if obj.CheckType(c4d.Omgcloner):
            lst.append(obj)
        getAllcloners(obj.GetDown(),start,lst)
        if obj == start: break
        obj = obj.GetNext()
    return lst

def main() -> None:
    
    lst_cloners =[]
    for o in doc.GetActiveObjects(0):
        getAllcloners(o,start = o,lst = lst_cloners)
    if not lst_cloners :
        print('pas de cloners')
        return

    first_object = doc.GetFirstObject()
    
    path = '/Users/olivierdonze/switchdrive/C4D/BIBLIOTHEQUE/Redshift_proxies'
    
    for fn in sorted(glob(os.path.join(path,'*.rs'))):
        c4d.documents.MergeDocument(doc, fn, c4d.SCENEFILTER_OBJECTS, None)
    
    #liste des proxies
    lst_proxies = []
    obj = doc.GetFirstObject()
    while obj:
        if obj == first_object : break
        obj.SetBit(c4d.BIT_ACTIVE)
        lst_proxies.append(obj)
        obj = obj.GetNext()  
    
    if not lst_proxies :
        print('pas de proxies')
        return
    
    doc.StartUndo()
    for cloner in lst_cloners:
        #on efface les enfants
        for child in cloner.GetChildren():
            doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ,child)
            child.Remove()
        #et on met un clone de cahque proxy
        for proxy in lst_proxies:
            clone = proxy.GetClone(c4d.COPYFLAGS_NONE)
            clone.InsertUnderLast(cloner)
            doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,clone)
    
    #on efface les poxies de base
    for proxy in lst_proxies:
        proxy.Remove()
            
    doc.EndUndo()
    
    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()