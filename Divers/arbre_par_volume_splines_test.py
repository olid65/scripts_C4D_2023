from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected


"""sélectionner la spline tronc, les branches doivent être enfant du même objet"""
def main() -> None:
    tronc = op
    
    #liste des branches
    branches = [sp for sp in tronc.GetUp().GetChildren() if sp.CheckType(c4d.Ospline) and sp != tronc]
    print(len(branches))
    
    
    
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()