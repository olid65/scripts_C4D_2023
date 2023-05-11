from typing import Optional
import c4d
from glob import glob
import os
from pprint import pprint
from random import shuffle
import math

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

MY_BITMAP_BUTTON = 10000
STATIC_TEXT = 20000
NB_COLS = 3

class MyDialog(c4d.gui.GeDialog):

    def __init__(self,lst_fn):
        self.lst_fn = lst_fn[:21]
        self.cnt = len(self.lst_fn)
        self.lst_rdm = self.lst_fn[:]
        shuffle(self.lst_rdm)
        self.fn = self.lst_rdm.pop()
        self.change = False
        self.name = None

    def CreateLayout(self):

        self.SetTitle("My Python Dialog")

        self.GroupBegin(0, c4d.BFH_SCALEFIT|c4d.BFH_SCALEFIT, NB_COLS, int(math.ceil(self.cnt/NB_COLS)), "Bitmap Example",0)

        for i,fn_img in enumerate(self.lst_fn):
            self.GroupBegin(100+i, c4d.BFH_SCALEFIT|c4d.BFH_SCALEFIT, 1, 2, "Bitmap Example",0)
            bc = c4d.BaseContainer()
            bc.SetBool(c4d.BITMAPBUTTON_BUTTON,True)                            #Create a new container to store the button image
            bc.SetString(c4d.BITMAPBUTTON_TOOLTIP, "<b>Bold Text</b><br>New line")
            #fn = c4d.storage.GeGetC4DPath(c4d.C4D_PATH_DESKTOP) #Gets the desktop path
            #path = '/Volumes/SITG_OD/Obliques_2013/E_thumbnails/260020024_1.jpg' #os.path.join(fn,'myimage.jpg')               #The path to the image
            bc.SetFilename(MY_BITMAP_BUTTON+i, fn_img)              #Add this location info to the conatiner
            
            self.myBitButton=self.AddCustomGui(MY_BITMAP_BUTTON+i, c4d.CUSTOMGUI_BITMAPBUTTON, "Bitmap Button", c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 30, 30, bc)
            self.myBitButton.SetImage(fn_img, False)             #Add the image to the button
            self.name,ext = os.path.splitext(os.path.basename(fn_img))
            self.AddStaticText(STATIC_TEXT+1, c4d.BFH_CENTER | c4d.BFV_SCALEFIT,name = os.path.basename(fn_img)[:-4])
            self.GroupEnd()
        self.GroupEnd()
        return True



    #Do something when the button is pressed
    def Command(self, id, msg=None):
        if id>=MY_BITMAP_BUTTON:
            print("Button pressed: ", id, os.path.basename(self.lst_fn[id-MY_BITMAP_BUTTON]))

        return True

def main() -> None:
    
    pth = '/Users/olivierdonze/switchdrive/Cinema4d_python/Forester_gui_OD/thumbnails'
    lst = []
    lst_img = []
    #get all directories from path
    for dirname in glob(os.path.join(pth,'*')):
        if not os.path.isdir(dirname): continue
        lst.append({os.path.basename(dirname):[fn for fn in glob(os.path.join(dirname,'*.jpg'))]})
        lst_img.extend([fn for fn in glob(os.path.join(dirname,'*.jpg'))])
    #pprint(lst) 
    
    dlg = MyDialog(lst_img)
    dlg.Open(c4d.DLG_TYPE_MODAL, defaultw=200, defaulth=200)
                                    
        
    
    
    

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()