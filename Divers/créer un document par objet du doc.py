from typing import Optional
import c4d
import os

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:


    dirname = 'dossier'
    #path of c4d document
    path_doc = doc.GetDocumentPath()
    if not path_doc:
        print('No path')
        return
    pth =os.path.join(path_doc, dirname)
    if not os.path.exists(pth):
        os.mkdir(pth)

    o = doc.GetFirstObject()
    while o:
        #for each objet we create a new document
        new_doc = c4d.documents.BaseDocument()
        clone = o.GetClone()
        
        #copy all tags
        for tag in clone.GetTags():
            #tag_clone = tag.GetClone()
            #clone.InsertTag(tag_clone)
            #if texture tag we copy the texture
            if tag.GetType() == c4d.Ttexture:
                mat = tag[c4d.TEXTURETAG_MATERIAL]
                if mat:
                    mat_clone = mat.GetClone()
                    new_doc.InsertMaterial(mat_clone)
                    tag[c4d.TEXTURETAG_MATERIAL] = mat_clone
                    
        #we add the object to the new document
        new_doc.InsertObject(clone)


        #we save the document
        name = os.path.join(pth, o.GetName() + '.c4d')
        c4d.documents.SaveDocument(new_doc, name, c4d.SAVEDOCUMENTFLAGS_0, c4d.FORMAT_C4DEXPORT)

        o = o.GetNext()


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()