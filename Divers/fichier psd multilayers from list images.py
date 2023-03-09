from typing import Optional
import c4d
from glob import glob
import os

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    pth = '/Users/olivierdonze/Documents/TEMP/test_swisstopo_wms/tex/swisstopo_images'
    lst_img = [f for f in glob(f'{pth}/*.png')]
    
    if len(lst_img) <1:
        print('No images in folder or only one')
        return
    
    # Create multipass
    pred = None
    for fn in lst_img:
        #print(mpass)
        if not pred:
            bmp = c4d.bitmaps.BaseBitmap()
            bmp.InitWith(fn)
            mpass =c4d.bitmaps.MultipassBitmap.AllocWrapper(bmp)
            pred = mpass

        layer = pred.AddLayer(None, c4d.COLORMODE_ARGB)
        layer.SetParameter(c4d.MPBTYPE_NAME, os.path.basename(fn)[:-4])
        layer.SetParameter(c4d.MPBTYPE_SAVE, True)
    
    for fn,mpass in zip(lst_img,pred.GetLayers()):
        img = c4d.bitmaps.BaseBitmap()
        img.InitWith(fn)
        img.CopyTo( mpass)
        mpass.SetDirty()
    fn_psd = f'{pth}/test.psd'
    pred.Save(fn_psd,c4d.FILTER_PSD,data=None,savebits = c4d.SAVEBIT_MULTILAYER)
    print(pred.GetLayerCount())