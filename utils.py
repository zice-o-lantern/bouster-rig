from maya import cmds
from enum import Enum

class ColorKeys(Enum):
    BLUE = 6
    RED = 13
    GREEN = 14
    YELLOW = 17

class NodeEditorWindow:
    
    def __init__(self):
        if cmds.window('nodeEd', exists=True):
            cmds.deleteUI('nodeEd')
    
        self._nodeEd = cmds.window('nodeEd',title="Node Editor", w=300, h=400)
        
        form = cmds.formLayout()
        
        self._p = cmds.scriptedPanel(type="nodeEditorPanel", label="Node Editor")
        cmds.formLayout(form, e=True, af=[(self._p,s,0) for s in ("top", "bottom", "left", "right")])
        
    @property
    def window(self):
        return self._p + "NodeEditorEd"

    def show_window(self):
        cmds.showWindow(self._nodeEd)