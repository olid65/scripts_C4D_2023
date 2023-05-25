from typing import Optional
import c4d
import json
import os

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    fname = 'swissbuilding_objektart_tableau_traduction_OD.json'
    fn_json = os.path.join(os.path.dirname(__file__),fname)
    #fn_json = '/Volumes/My Passport Pro/swisstopo/swissbuilding_objektart_tableau_traduction_OD.json'
    
    with open(fn_json, encoding = 'utf-8') as f :
        dico = json.load(f)
        
    for obj in op.GetChildren():
        name = dico.get(obj.GetName(), obj.GetName())
        for o in obj.GetChildren():
            name2 = o.GetName()
            name2 = name2.replace(obj.GetName(),name)
            o.SetName(name2)
        obj.SetName(name)
    c4d.EventAdd()


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()