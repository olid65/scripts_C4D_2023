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

    sizes = []
    for fn in lst_img:
        bmp = c4d.bitmaps.BaseBitmap()
        bmp.InitWith(fn)
        sizes.append(bmp.GetSize())


    if len(set(sizes)) != 1:
        print(set(sizes))
        c4d.gui.MessageDialog(f'Il faut que toutes les images aient la même taille en pixels')
        return

    x,y = sizes[0]
    mpass = c4d.bitmaps.MultipassBitmap(x,y,c4d.COLORMODE_ARGB)
    temp = mpass.GetLayers()[0]

    for i in range(x):
        for n in range(y):
            temp.SetPixel(i,n,255,255,255)

    for i,fn in enumerate(lst_img):
        layer = mpass.AddLayer(None, c4d.COLORMODE_ARGB)
        layer.SetParameter(c4d.MPBTYPE_NAME, os.path.basename(fn)[:-4])
        layer.SetParameter(c4d.MPBTYPE_SAVE, True)
        #alpha = mpass.AddAlpha(layer,c4d.COLORMODE_ALPHA)
        img = c4d.bitmaps.BaseBitmap()
        img.InitWith(fn)
        print('channel count img :',img.GetChannelCount())
        print('channel count layer :',layer.GetChannelCount())
        img.Save(f'/Users/olivierdonze/Documents/TEMP/a_jeter/{i}.png',c4d.FILTER_PNG, None, c4d.SAVEBIT_ALPHA)
        #c4d.bitmaps.ShowBitmap(img)
        inc = img.GetBt() // 8
        print(inc)
        bytesArray = bytearray(x * y * inc)
        memoryView = memoryview(bytesArray)
        for row in range(y):
            memoryViewSlice = memoryView[row*(x*inc):]
            img.GetPixelCnt(0, row,x, memoryViewSlice, inc, c4d.COLORMODE_ARGB, c4d.PIXELCNT_APPLYALPHA)

        for row in range(y):
            memoryViewSlice = memoryView[row * (x * inc):]
            layer.SetPixelCnt(0, row, x, memoryViewSlice, inc, c4d.COLORMODE_ARGB, c4d.PIXELCNT_APPLYALPHA)


    fn_psd = f'{pth}/test.psd'
    mpass.Save(fn_psd,c4d.FILTER_PSD,data=None,savebits = c4d.SAVEBIT_MULTILAYER) #|c4d.SAVEBIT_ALPHA
    print(mpass.GetLayerCount())
    print(mpass.GetAlphaLayerCount())

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
        img = c4d.bitmaps.BaseBitmap()
        img.InitWith(fn)
        #img.CopyTo(layer)

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


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()