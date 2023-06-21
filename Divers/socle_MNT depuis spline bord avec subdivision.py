import c4d
from statistics import mean


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True



# Main function
def main():
    
    #valeur en moins depuis le point minimum pour l'épaisseur du socle
    SOCLE = 3
    
    if not op : return
    
    if not op.CheckType(c4d.Ospline):
        return
    pts = op.GetAllPoints()
    mg = op.GetMg()
    nb_pts_sp = len(pts)
    
    
    
    
    #calcul de la taille de la maille
    #on part du principe que l'on a un maillage régulier
    dist = c4d.Vector.GetDistance(pts[1],pts[0])
    print(dist)
    
    #si le socle ==0 
    #on donne la valeur d'une maille
    #pour pas que certains points se chevauchent (altitude minimum)
    if not SOCLE:
        SOCLE = dist

    alts = [(p*mg).y for p in pts]
    
    #calcul de l'altitude moyenne
    #et du nombre d'itération pour approcher la taille de la maille
    moy = mean(alts)
    print(moy)
    
    #calcul min et max altitude
    ymin = min(alts) -SOCLE
    ymax = max(alts)
    dif = ymax - ymin
    print(ymax,ymin, dif)
    
    nb_iter = int(round((moy-ymin)/dist))
    print(nb_iter)
    


    
    #pour chaque point calcul de la différence d'alt pour socle à plat
    iter_alts = [(alt-ymin)/nb_iter for alt in alts]
    
    nb_pts = nb_pts_sp * nb_iter
    nb_polys = (nb_pts_sp) * nb_iter
            
    res = c4d.PolygonObject(nb_pts,nb_polys)
    
    pts_socle = []
    id_poly = 0
    id_pt = 0
    for i in range(nb_iter):
        for (n,p),dif_alt in zip(enumerate(pts),iter_alts):
            
            pts_socle.append(c4d.Vector(p))
            p.y -= dif_alt
            
            if i>0:
                if n ==0:
                    d = id_pt
                    a = d-nb_pts_sp
                    b = d-1
                    c = d +nb_pts_sp-1
                    
                else:
                    d = id_pt
                    a = d-nb_pts_sp
                    b = a-1
                    c = d-1
                    
                try : res.SetPolygon(id_poly,c4d.CPolygon(a,b,c,d))
                except : 
                    print('----')
                    print(i,n)
                    print(a,b,c,d)
                    print(id_poly)
                    #return
                id_poly+=1
            id_pt+=1
    
    
    res.SetAllPoints(pts_socle)

    res.Message(c4d.MSG_UPDATE)
    doc.InsertObject(res)
    
    c4d.EventAdd()
            
    
    

# Execute main()
if __name__=='__main__':
    main()