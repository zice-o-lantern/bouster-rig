from maya import cmds
from bousterRig.utils import ColorKeys


class JointChain:
    
    _colorIndex = ColorKeys.BLUE.value
    
    def __init__(self, jnt, name, length, **kwargs):
        
        _jntChain = cmds.duplicate(jnt, fullPath=True, n=name + '_' + jnt)
        _renameChain = _jntChain[1:length]
        _deleteChain = _jntChain[length:]
        
        for element in _deleteChain:
            try:
                cmds.delete(element)
            except:
                continue
        
        for idx, jnt_name in enumerate(reversed(_renameChain)):
            #cmds.rename(jnt_name, '{0}_{1}'.format(name, jnt_name.split('|')[-1]))
            cmds.rename(jnt_name, f'{name}_{jnt_name.split("|")[-1]}')
        
        _jnt = cmds.parent(_jntChain[0], w=True)
        
        cmds.select(_jnt, hi=True)
        self._jntChain = cmds.ls(long=True, sl=True, type='joint')
        
        if 'color' in kwargs:
            self.color = kwargs["color"]   
    
    def __repr__(self):
        return self._jntChain
    
    @property
    def color(self):
        return self._colorIndex
    
    @color.setter
    def color(self, value):
        for jnt in self._jntChain:
            cmds.setAttr(f"{jnt}.overrideEnabled", 1)
            cmds.setAttr(f"{jnt}.overrideColor", ColorKeys[value].value)
        self._colorIndex = ColorKeys[value].value
    
    @property
    def startChain(self):
        return self._jntChain[0].split('|')[-1]
    
    @property
    def endChain(self):
        return self._jntChain[-1].split('|')[-1]
    
    @property
    def middleChain(self):
        _index = round(len(self._jntChain)/2)-1
        return self._jntChain[_index].split('|')[-1]
    
    @property
    def jntChain(self):
        return self._jntChain
        
    