from typing import Optional
import c4d
import urllib

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected


def extract_infos_from_url(url):
    if len(url.split('?'))==2:
        req = url.split('?')[1]
        dico = {}
        for part in req.split('&'):
            key,val = part.split('=')
            if key == 'layers' :
                val = val.split(',')
            elif key == 'layers_opacity':
                val = [float(v) for v in val.split(',')]
            elif key == 'layers_visibility' :
                val = [bool(v) for v in val.split(',')]
            elif key == 'layers_timestamp':
                # pour les voyages temporels
                #la date est sous la forme 18641231 -> on récupère que l'année
                val = [int(v[:4]) for v in val.split(',') if v]
            elif key in ['E','N','zoom']: 
                val = float(val)
                
            dico[key] = val
        return dico
    
    return None

def main() -> None:
    
    if c4d.GetClipboardType() == c4d.CLIPBOARDTYPE_STRING:
        url = c4d.GetStringFromClipboard()
        
        #type url courte ou normale :
        #https://s.geo.admin.ch/9a65bfa1ef
        #https://map.geo.admin.ch/?lang=fr&topic=ech&bgLayer=ch.swisstopo.pixelkarte-farbe&layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.astra.wanderland-sperrungen_umleitungen&layers_opacity=1,1,1,0.8,0.8&layers_visibility=false,false,false,false,false&layers_timestamp=18641231,,,,&E=2562220.51&N=1119537.42&zoom=6

        #url courte -> on récupère l'url normale
        pref_courte = 'https://s.geo.admin.ch/'
        len_pref_courte = len(pref_courte)
        
        if len(url)> len_pref_courte and url[:len_pref_courte] == pref_courte:
            with urllib.request.urlopen(url) as f:
                url = f.geturl()

        # traitement de l'url
        pref_url_longue = 'https://map.geo.admin.ch/'
        len_pref_url_longue = len(pref_url_longue)

        if len(url)> len_pref_url_longue and url[:len_pref_url_longue] == pref_url_longue:
            dic = extract_infos_from_url(url)
            est,nord = dic.get('N',None),dic.get('E',None)
            if est and nord:
                centre = c4d.Vector(est,0,nord)
                print(centre)
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()