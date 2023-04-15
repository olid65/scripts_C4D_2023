from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

OD_CALIBRATOR = 1059348 



def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    fn_img = op[OD_CALIBRATOR][0]
    pts_uv = [p for p in op[OD_CALIBRATOR][1]]
    w,h = op[OD_CALIBRATOR][2][0],op[OD_CALIBRATOR][2][1]

    pts_3D = [o.GetMg().off for o in op.GetChildren()]
    print(pts_3D)

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()