import c4d
from c4d import gui
#Welcome to the world of Python


def cubeSelonVueHaut():

    bd = doc.GetActiveBaseDraw()
    camera = bd.GetSceneCamera(doc)
    if not camera[c4d.CAMERA_PROJECTION]== c4d.Ptop:
        c4d.gui.MessageDialog("""Ne fonctionne qu'avec une caméra en projection "haut" """)
        return

    dimension = bd.GetFrame()
    largeur = dimension["cr"]-dimension["cl"]
    hauteur = dimension["cb"]-dimension["ct"]

    mini =  bd.SW(c4d.Vector(0,hauteur,0))
    maxi = bd.SW(c4d.Vector(largeur,0,0))
    centre = (mini+maxi)/2.
    #return  mini,maxi,largeur,hauteur
    plan = c4d.BaseObject(c4d.Oplane)
    doc.InsertObject(plan)
    plan.SetAbsPos(centre)
    plan[c4d.PRIM_AXIS] = c4d.PRIM_AXIS_YP
    plan[c4d.PRIM_PLANE_WIDTH] = maxi.x-mini.x
    plan[c4d.PRIM_PLANE_HEIGHT] = maxi.z-mini.z
    
    #cube[c4d.PRIM_CUBE_LEN] = c4d.Vector(maxi.x-mini.x,0,maxi.z-mini.z)
    doc.SetActiveObject(plan)

def main():
    cubeSelonVueHaut()
    c4d.EventAdd()

if __name__=='__main__':
    main()