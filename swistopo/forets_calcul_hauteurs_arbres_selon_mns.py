from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

DELTA_ALT = 100
HAUT_SRCE = 10

def getMinMaxY(obj):
    """renvoie le minY et le maxY en valeur du monde d'un objet"""
    mg = obj.GetMg()
    alt = [(pt * mg).y for pt in obj.GetAllPoints()]
    return min(alt) - DELTA_ALT, max(alt) + DELTA_ALT

def pointsOnSurface(pts,mnt):
    """pts en coord globales"""
    grc = c4d.utils.GeRayCollider()
    grc.Init(mnt)
    mg_mnt = mnt.GetMg()
    invmg_mnt = ~mg_mnt

    minY,maxY = getMinMaxY(mnt)
    res = []
    ray_dir = ((c4d.Vector(0,0,0)*invmg_mnt) - (c4d.Vector(0,1,0)*invmg_mnt)).GetNormalized()
    length = maxY-minY
    for i,p in enumerate(pts):
        dprt = c4d.Vector(p.x,maxY,p.z)*invmg_mnt
        intersect = grc.Intersect(dprt,ray_dir,length)
        if intersect :
            pos = grc.GetNearestIntersection()['hitpos']
            res.append(c4d.Vector(pos*mg_mnt))
        else:
            res.append(c4d.Vector(p))

    return res

def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    
    name_mns = 'swisssurface3d-raster_50cm'
    mns = doc.SearchObject(name_mns)
    if not mns:
        c4d.gui.MessageDialog(f'{name_mns} pas trouvé, opération impossible')
        return
    
    
    modata = c4d.modules.mograph.GeGetMoData(op)
    if not modata:
        c4d.gui.MessageDialog(f'Vous devez sélectionner un cloneur mograph')
        return
    
    pts_base = [c4d.Vector(m.off) for m in modata.GetArray(c4d.MODATA_MATRIX)]
    
    pts_haut = pointsOnSurface(pts_base,mns)
    
    hauteurs = [ph.y-pb.y for ph,pb in zip(pts_haut,pts_base) ]
    
    tagHauteurs = c4d.BaseTag(440000231)
    op.InsertTag(tagHauteurs)
    tagHauteurs.SetName('hauteurs')
    # ATTENTION bien mettre des float dans la liste sinon cela ne marche pas !
    scale_factor_haut = lambda x: float(x) / HAUT_SRCE - 1.
    c4d.modules.mograph.GeSetMoDataWeights(tagHauteurs, [scale_factor_haut(h) for h in hauteurs])
    
    c4d.EventAdd()
    return
    res = c4d.PolygonObject(len(pts),0)
    res.SetAllPoints(pts)
    res.SetMg(c4d.Matrix(op.GetMg()))
    res.Message(c4d.MSG_UPDATE)
    
    doc.InsertObject(res)
    c4d.EventAdd()
    

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()