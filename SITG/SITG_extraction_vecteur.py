from typing import Optional
import c4d
import json

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

class LayerVectorSITG(object):    
    def __init__(self, dico):
        self.id = dico['id']
        self.name = dico['name']
        self.prefixe = self.name.split('_')[0]
        self.url = dico['url']
        self.type = dico['geometryType']
        self.fields = dico['fields']
        self.maxRecordCount = dico['maxRecordCount']
        #self.extend = dico['extend']
        self.description = dico['description']
    


class MonDlg(c4d.gui.GeDialog):
    ID_FILTER_PREFIXE = 2001
    ID_FILTER_TYPE = 2002
    ID_FILTER_CONTENT = 2003
    
    ID_COMBO_LAYERS = 2010
    
    prefixe = None
    typ = None
    content = None
    
    def __init__(self,fn):
        if not fn : return
        self.lst_lyr_all = []
        self.prefixes = []
        self.types = []
        
        with open(fn,encoding = 'utf-8') as f:
            lst = json.load(f)
            for dico in lst:
                lyr = LayerVectorSITG(dico)
                if not lyr.type in self.types:
                    self.types.append(lyr.type)
                if not lyr.prefixe in self.prefixes:
                    self.prefixes.append(lyr.prefixe)
                self.lst_lyr_all.append(lyr)
        self.lst_lyr = list(self.lst_lyr_all)


    def CreateLayout(self):
        self.SetTitle('Extraction SITG vecteur : ')
        ##########################################
        #FILTRES
        self.AddStaticText(1000,name="FILTRES : ", flags=c4d.BFH_MASK,initw=150)
        
        self.GroupBegin(1001,flags=c4d.BFH_SCALEFIT, cols=2, rows=3)
        self.GroupBorderSpace(20, 20, 20, 20)
        self.AddStaticText(1002,name="Préfixe : ", flags=c4d.BFH_MASK,                                            initw=150)
        self.AddComboBox(self.ID_FILTER_PREFIXE, flags=c4d.BFH_LEFT, initw=300, allowfiltering=True)
        self.AddStaticText(1002,name="Type de géométrie : ", flags=c4d.BFH_MASK,                                            initw=150)
        self.AddComboBox(self.ID_FILTER_TYPE, flags=c4d.BFH_LEFT, initw=300)
        self.AddStaticText(1002,name="Contient : ", flags=c4d.BFH_MASK,                                            initw=150)
        self.AddEditText(self.ID_FILTER_CONTENT, flags=c4d.BFH_LEFT, initw=300)
        self.GroupEnd()
        
        self.AddSeparatorH( initw = 300)
        ##########################################
        #CHOIX COUCHE
        
        self.AddStaticText(1020,name="CHOIX DE LA COUCHE : ", flags=c4d.BFH_MASK, initw=150)
        
        self.GroupBegin(1021,flags=c4d.BFH_SCALEFIT, cols=2, rows=1)
        self.GroupBorderSpace(20, 20, 20, 20)
        self.AddStaticText(1022,name="Couche vectorielle : ", flags=c4d.BFH_MASK,
                                             initw=150)
        self.AddComboBox(self.ID_COMBO_LAYERS, flags=c4d.BFH_LEFT, initw=300, inith=0, specialalign=False, allowfiltering=True)                                    
        #self.AddComboBox(1004,flags=c4d.BFH_MASK, initw=250) 
        self.GroupEnd()
        
        ###########################################
        #
        return True
        
    def InitValues(self):
        
        self.AddChild(self.ID_FILTER_PREFIXE,0,'-')
        for i,pref in enumerate(self.prefixes):
             self.AddChild(self.ID_FILTER_PREFIXE,i+1,pref)
        
        self.AddChild(self.ID_FILTER_TYPE,0,'-')
        for i,typ in enumerate(self.types):
            self.AddChild(self.ID_FILTER_TYPE,i+1,typ)
        
        for i,lyr in enumerate(self.lst_lyr):
            #on supprime le 0 car il rajoute un champ
            #if i>0:
            self.AddChild(self.ID_COMBO_LAYERS,i,lyr.name)
        return True
    
    def majLayers(self):
        self.FreeChildren(self.ID_COMBO_LAYERS)
        self.SetLong(self.ID_COMBO_LAYERS,0)
        
        self.lst_lyr.clear()
        
        for lyr in self.lst_lyr_all:
            pref = True
            typ = True
            content = True
            if self.prefixe:
                if lyr.name[:len(self.prefixe)] != self.prefixe:
                    pref = False
            
            if self.typ:
                if self.typ != lyr.type:
                    typ = False
            
            if self.content:
                if self.content not in lyr.name:
                    content = False

            if pref & typ & content:
                self.lst_lyr.append(lyr)
        
        if self.lst_lyr:
            for i,lyr in enumerate(self.lst_lyr):
                self.AddChild(self.ID_COMBO_LAYERS,i,lyr.name)
        
        
    def Command(self,id,msg): 
        
        if id==self.ID_FILTER_PREFIXE : 
            res = self.GetLong(self.ID_FILTER_PREFIXE)
            if res == 0:
                self.prefixe = None
            else:
                self.prefixe = self.prefixes[res-1]
            self.majLayers()
        
        if id==self.ID_FILTER_TYPE : 
            res = self.GetLong(self.ID_FILTER_TYPE)
            if res == 0:
                self.typ = None
            else:
                self.typ = self.types[res-1]
            self.majLayers()
        
        if id==self.ID_FILTER_CONTENT : 
            self.content = self.GetString(self.ID_FILTER_CONTENT).upper()
            self.majLayers()
            
        
        if id==self.ID_COMBO_LAYERS : 
            res = self.GetLong(self.ID_COMBO_LAYERS)
            lyr = self.lst_lyr[res]
            print(lyr.name, lyr.url,lyr.type)

        return True

def main() -> None:
    fn = '/Users/olivierdonze/switchdrive/PYTHON/SITG_divers/SITG_vector_layers.json'
    dlg = MonDlg(fn)
    dlg.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE)
    return

    

    with open(fn,encoding = 'utf-8') as f:
        lst = json.load(f)
        print(lst)
        for dico in lst:
            print(dico['name'])


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()