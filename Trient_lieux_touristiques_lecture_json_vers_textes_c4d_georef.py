from typing import Optional
import c4d
import json



doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected


CONTAINER_ORIGIN = 1026473

def main() -> None:

    origin = doc[CONTAINER_ORIGIN]
    fn = '/Users/olivierdonze/switchdrive/Mandats/Parc_naturel_regional_vallee_Trient/docs/automnales_scenario_lv95.json'
    res = c4d.BaseObject(c4d.Onull)
    srce = c4d.BaseObject(c4d.Onull)
    srce.SetName("source_inst_lieux")
    with open(fn, encoding = 'utf-8') as f:
        for commune,label,x,z,theme in json.loads(f.read()):
            print(commune,label,x,z,theme)
            text = c4d.BaseObject(c4d.Omgtext)
            text.SetName(label)
            text.SetAbsPos(c4d.Vector(x,0,z)-origin)
            text[c4d.PRIM_TEXT_TEXT] = label
            text[c4d.PRIM_TEXT_ALIGN] = c4d.PRIM_TEXT_ALIGN_MIDDLE
            #text.InsertUnderLast(res)

            inst = c4d.BaseObject(c4d.Oinstance)
            inst.SetAbsPos(c4d.Vector(x,0,z)-origin)
            inst.SetName(label)
            inst.InsertUnderLast(res)
            inst[c4d.INSTANCEOBJECT_LINK] = srce

    doc.InsertObject(res)

    doc.InsertObject(srce)
    c4d.EventAdd()
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()