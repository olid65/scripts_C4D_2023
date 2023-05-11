from typing import Optional
import c4d
import urllib.request
from urllib.parse import urlencode
import json
from pprint import pprint
from time import time

CONTAINER_ORIGIN =1026473

def get_adress_SITG(string)->list:
    """renvoie une liste de tuples de 4 éléments (rue, commune, easting, northing)
       ou None si pas fonctioné"""
    t1 = time()

    url_base = 'https://geocodage.sitg-lab.ch/api/search?'

    params = {'q':string,
              'suggest':'true'}
    params = urllib.parse.urlencode(params)

    url = url_base + params
    res = []
    with urllib.request.urlopen(url) as resp:
        if resp.getcode()==200:
            data = json.loads(resp.read())
            hits = data.get('hits',None)
            if hits:
                for hit in hits:
                    res.append((hit['ADRESSE'],hit['COMMUNE'],hit['easting'],hit['northing']))

    return res

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    txt = c4d.gui.InputDialog("SITG géocodage", "Saisir le texte qui définit le lieu")
    if not txt:
        return
    print(txt)
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    rep = get_adress_SITG(txt)
    if not rep :
        c4d.gui.MessageDialog("Aucun résultat")
        return
    
    pprint(rep)
    #TODO si plusieurs réponse -> liste pour choisir
    #pour l'instant on prend la première
    adresse,commune,x,z = rep[0]
    rvalue = c4d.gui.QuestionDialog(f"Voulez-vous géoréférencer le doc à {adresse} - {commune}")
    if rvalue:
        doc[CONTAINER_ORIGIN] = c4d.Vector(x,0,z)
            

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()