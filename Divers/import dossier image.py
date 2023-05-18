import c4d
import os,glob
 
ABSOLU = 1101
ALPHA = 1102
PLAN = 1103
OK = 1201
CANCEL = 1202
lst_ext = ['.jpg','.tif','.tga','.png','.psd','.b3d','.gif']
class ImportImages():
    def __init__(self,dossier,absolu,alpha,plan):
        self.pos = c4d.Vector(0)
        os.chdir(dossier)
        if plan :
            grpe = c4d.BaseObject(c4d.Onull)
            path,name = os.path.split(dossier)
            grpe.SetName(name)
        for fn in os.listdir(dossier):
            nom,ext = os.path.splitext(fn)
            if absolu : fn = os.path.abspath(fn)
            if ext in lst_ext:
                mat = self.creer_mat(fn,nom,alpha)
                if plan :
                    #affiche = self.creer_plan_image(fn,nom,mat)
                    affiche = self.creer_poly_image(fn,nom,mat)
                    if affiche :
                        affiche.InsertUnder(grpe)
        if plan : doc.InsertObject(grpe)
        
    def creer_mat(self,fn,nom,alpha=True):
        mat = c4d.BaseMaterial(c4d.Mmaterial)
        mat.SetName(nom)
        doc.InsertMaterial(mat)
        shd = c4d.BaseList2D(c4d.Xbitmap)
        shd[c4d.BITMAPSHADER_FILENAME] = fn
        mat[c4d.MATERIAL_COLOR_SHADER] = shd
        mat.InsertShader(shd)
        mat[c4d.MATERIAL_USE_SPECULAR]=False
    
        if alpha :
            mat[c4d.MATERIAL_USE_ALPHA]=True
            shda = c4d.BaseList2D(c4d.Xbitmap)
            shda[c4d.BITMAPSHADER_FILENAME] = fn 
            mat[c4d.MATERIAL_ALPHA_SHADER]=shda
            mat.InsertShader(shda)
            
        mat.Message(c4d.MSG_UPDATE)
        mat.Update(True, True)
        return mat   
        
    def creer_plan_image(self,fn,nom,mat):
        bmp = c4d.bitmaps.BaseBitmap()
        if bmp.InitWith(fn)[0]== c4d.IMAGERESULT_OK:
            larg,haut = bmp.GetSize()
            bmp.FlushAll()
            plan = c4d.BaseObject(c4d.Oplane)
            plan.SetAbsPos(self.pos)
            self.pos.x+=larg
            plan.SetName(nom)
            plan[c4d.PRIM_PLANE_WIDTH]=larg
            plan[c4d.PRIM_PLANE_HEIGHT]=haut
            plan[c4d.PRIM_PLANE_SUBW]=1
            plan[c4d.PRIM_PLANE_SUBH]=1
            plan[c4d.PRIM_AXIS]=5
            tag = c4d.TextureTag()
            tag.SetMaterial(mat)
            tag[c4d.TEXTURETAG_PROJECTION]=6
            plan.InsertTag(tag)
        
            return plan #doc.InsertObject(plan)
        else : return None
        
    def creer_poly_image(self,fn,nom,mat):
        bmp = c4d.bitmaps.BaseBitmap()
        if bmp.InitWith(fn)[0]== c4d.IMAGERESULT_OK:
            larg,haut = bmp.GetSize()
            self.pos.x+=larg/2
            mi_l=larg/2
            bmp.FlushAll()
            plan = c4d.PolygonObject(4,1)
            plan.SetAbsPos(self.pos)
            plan.SetName(nom)
            plan.SetPoint(0,c4d.Vector(mi_l,0,0))
            plan.SetPoint(1,c4d.Vector(mi_l,haut,0))
            plan.SetPoint(2,c4d.Vector(-mi_l,haut,0))
            plan.SetPoint(3,c4d.Vector(-mi_l,0,0))
            plan.SetPolygon(0,c4d.CPolygon(0,1,2,3))
            self.pos.x+=larg/2
            
            tag = c4d.TextureTag()
            tag.SetMaterial(mat)
            tag[c4d.TEXTURETAG_PROJECTION]=6
            plan.InsertTag(tag)
            
            tuvw = c4d.UVWTag(1)
            tuvw.SetSlow(0,c4d.Vector(0,1,0),
                           c4d.Vector(0,0,0),
                           c4d.Vector(1,0,0),
                           c4d.Vector(1,1,0))
            plan.InsertTag(tuvw)
            plan.Message(c4d.MSG_UPDATE)        
            return plan #doc.InsertObject(plan)
        else : return None
class MonDlg(c4d.gui.GeDialog):
    def __init__(self):
        self.dossier = c4d.storage.LoadDialog(flags=c4d.FILESELECT_DIRECTORY,title="Dossier contenant les images")
        self.absolu = True
        self.alpha= True
        self.plan = True
            
    def CreateLayout(self):
        self.SetTitle("Options d'importation")
        self.GroupBegin(1100,flags=c4d.BFH_SCALEFIT, cols=1, rows=3)
        self.GroupBorderSpace(10, 10, 10, 10)                                  
        self.AddCheckbox(ABSOLU,flags=c4d.BFH_MASK, initw=250,inith=15,name="chemin absolu ")                                  
        self.AddCheckbox(ALPHA,flags=c4d.BFH_MASK, initw=250,inith=15,name='canal alpha')                                  
        self.AddCheckbox(PLAN,flags=c4d.BFH_MASK, initw=250,inith=15,name='plan pour chaque texture') 
        self.GroupEnd()
        self.GroupBegin(1200,flags=c4d.BFH_SCALEFIT, cols=2, rows=1)
        self.GroupBorderSpace(10, 10, 10, 10)
        self.AddButton(OK,flags=c4d.BFH_MASK, initw=50,inith=15,name='OK') 
        self.AddButton(CANCEL,flags=c4d.BFH_MASK, initw=50,inith=15,name='Annuler') 
        self.GroupEnd()
        return True
            
    def InitValues(self):
        self.SetBool(ABSOLU,True)
        self.SetBool(ALPHA,True)
        self.SetBool(PLAN,True)
        self.absolu = True
        self.alpha= True
        self.plan = True
        
        return True
        
    def Command(self,id,msg):
        if id == ABSOLU : self.absolu = self.GetBool(ABSOLU)
        if id == ALPHA : self.alpha = self.GetBool(ALPHA)
        if id == PLAN : self.plan = self.GetBool(PLAN)
        
        if id == OK:
            self.Close()
            ImportImages(self.dossier,self.absolu,self.alpha,self.plan)
        if id == CANCEL:
            self.Close()
            
        return True
 
if __name__=='__main__':
    
    dlg = MonDlg()
    dlg.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE)
    
    c4d.EventAdd()  