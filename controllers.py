from maya import cmds
from bousterRig import utils

class Controller:
    #def __init__(self, name, shape='circle', color='blue', scale=(1, 1, 1)):
    def __init__(self, *args, **kwargs):
        self._curve = Curve(*args, **kwargs)
        _name = args[0]
        #self.offset = 'offset_' + name
        self._offset = 'offset_' + _name
        cmds.group(n=self._offset, em=True)
        cmds.parent(self._curve, self._offset)

        if "matchTo" in kwargs and "orientToWorld" in kwargs:
            cmds.matchTransform(self._offset, kwargs["matchTo"], pos=kwargs["orientToWorld"])
        elif "matchTo" in kwargs:
            cmds.matchTransform(self._offset, kwargs["matchTo"])

        if "parentConstraintTo" in kwargs:
            cmds.parentConstraint(self._curve, kwargs["parentConstraintTo"])

        if "orientConstraintTo" in kwargs:
            cmds.orientConstraint(self._curve, kwargs["orientConstraintTo"], mo=True)

        if "parentTo" in kwargs:
            cmds.parent(self._offset, kwargs["parentTo"])
    
    @property
    def curve(self):
        return self._curve
    
    @property
    def offset(self):
        return self._offset
        
class Curve:
    #def __init__(self, name, shape, color, scale):
    def __init__(self, *args, **kwargs):
        self._name = f"ctrl_{args[0]}"
        _name = f"ctrl_{args[0]}"
        
        #if hasattr(self, 'shape'):
        if "shape" in kwargs:
            _shape = kwargs["shape"]
            exec(f"self.create_{_shape}_curve(_name, **kwargs)")
        else:
            cmds.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=20, d=3, ut=0, tol=0.01, s=8, ch=1, n=self._name)

        #self.colorIndex = utils.COLOR_KEYS[color]
        if 'color' in kwargs:
            cmds.setAttr(_name + '.overrideEnabled', 1)
            cmds.setAttr(_name + '.overrideColor', utils.ColorKeys[kwargs["color"]].value)
        
        if 'scale' in kwargs:
            _scale = kwargs["scale"]
            cmds.scale(_scale[0], _scale[1], _scale[2], _name)
            if 'rotate' in kwargs:
                _rotate = kwargs["rotate"]
                print(_rotate)
                cmds.rotate(f"{_rotate[0]}deg", f"{_rotate[1]}deg", f"{_rotate[2]}deg", _name)
            cmds.makeIdentity(_name, a=True)


    def __repr__(self):
        return self._name
    def __str__(self):
        return self._name
    
    @staticmethod
    def create_cube_curve(*args, **kwargs):
        name=args[0]     
        cube = cmds.curve(d=1, n=name, p=[(-10, 0, -10),(10, 0, -10), (10, 0, 10), (-10, 0, 10), (-10, 0, -10)])
        _shape = cmds.listRelatives()[0]
        cmds.rename(_shape, name + 'Shape1')
        
        cmds.curve(d=1, p=[(-10, 0, -10),(10, 0, -10), (10, 0, 10), (-10, 0, 10), (-10, 0, -10)])
        cmds.move(0, 20, 0)    
        cmds.makeIdentity(a=True)
        _shape = cmds.listRelatives()[0]
        cmds.parent(_shape, name, s=True, r=True)
        cmds.rename(_shape, name + 'Shape2')
        cmds.delete('curve1')
        
        cmds.curve(d=1, p=[(-10, 0, -10),(10, 0, -10), (10, 0, 10), (-10, 0, 10), (-10, 0, -10)])
        #cube3 = cmds.rename(cube3, name + 'Shape3')
        cmds.move(10, 10, 0) 
        cmds.rotate(0, 0, '-90deg')   
        cmds.makeIdentity(a=True)
        _shape = cmds.listRelatives()[0]
        cmds.parent(_shape, name, s=True, r=True)
        cmds.rename(_shape, name + 'Shape2')
        cmds.delete("curve1")
        
        cmds.curve(d=1, p=[(-10, 0, -10),(10, 0, -10), (10, 0, 10), (-10, 0, 10), (-10, 0, -10)])
        cmds.move(-10, 10, 0) 
        cmds.rotate(0, 0, '-90deg')   
        cmds.makeIdentity(a=True)
        _shape = cmds.listRelatives()[0]
        cmds.parent(_shape, name, s=True, r=True)
        cmds.rename(_shape, name + 'Shape3')
        cmds.delete("curve1")

        if "move" in kwargs:
            _move = kwargs["move"]

            cmds.select(f"{name}Shape4.cv[0:4]", f"{name}Shape2.cv[0:4]", f"{name}Shape1.cv[0:4]",
                        f"{name}Shape3.cv[0:4]")
            cmds.move(_move[0], _move[1], _move[2], r=True, os=True, wd=True)

        if 'height_baseline' in kwargs and kwargs['height_baseline']:
            cmds.move(0, -10, 0, name, r=True)
            cmds.move(0, 0, 0, name + '.scalePivot', name + '.rotatePivot', a=True)
            cmds.makeIdentity(name, a=True)
        return cube

    @staticmethod
    def create_trapeze_curve(*args, **kwargs):
        name=args[0]
        Curve.create_cube_curve(*args, **kwargs)
        cmds.select(f"{name}Shape1.cv[0:4]", f"{name}Shape4.cv[1:2]", f"{name}Shape3.cv[1:2]")
        cmds.scale(0.5, 1, 1, p=(0, 0, 0))

    @staticmethod
    def create_sphere_curve(*args, **kwargs):
        name = args[0]
        sphere = cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=20, d=3, ut=0, tol=0.01, s=8, ch=1, n=name)
        
        cmds.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=20, d=3, ut=0, tol=0.01, s=8, ch=1)
        _shape = cmds.listRelatives()[0]
        cmds.parent(_shape, name, s=True, r=True)
        cmds.rename(_shape, name + 'Shape1')
        cmds.delete('nurbsCircle1')

        cmds.circle(c=(0, 0, 0), nr=(0, 0, 1), sw=360, r=20, d=3, ut=0, tol=0.01, s=8, ch=1)
        _shape = cmds.listRelatives()[0]
        cmds.parent(_shape, name, s=True, r=True)
        cmds.rename(_shape, name + 'Shape1')
        cmds.delete('nurbsCircle1')
        return sphere
    
    @staticmethod
    def create_cross_curve(*args, **kwargs):
        name = args[0]
        points = [(-10, 0, -10), (-10, 0, -30), (10, 0, -30), (10, 0, -10), (30, 0, -10), (30, 0, 10), (10, 0, 10), (10, 0, 30), (-10, 0, 30), (-10, 0, 10), (-30, 0, 10), (-30, 0, -10), (-10, 0, -10)]
        cmds.curve(d=1, p=points, n=name)

    @staticmethod
    def create_star_curve(*args, **kwargs):
        name = args[0]
        cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=20, d=3, ut=0, tol=0.01, s=8, ch=1, n=name)
        cmds.select(f"{name}.cv[0]", f"{name}.cv[2]", f"{name}.cv[4]", f"{name}.cv[6]", r=True)
        cmds.scale(0.15, 0.15, .15, r=True, p=(0, 0, 0))

    @staticmethod
    def create_square_curve(*args, **kwargs):
        name = args[0]
        cmds.curve(d=1, p=[(-10, 0, -10), (10, 0, -10), (10, 0, 10), (-10, 0, 10), (-10, 0, -10)],n=name)


class IKSplineController(Controller):
    def __init__(self, *args, **kwargs):
        Controller.__init__(self, *args, **kwargs)
        _order = kwargs['order']
        self._joint = cmds.joint(self._curve, n=f"jnt_splineCurve_{_order}")
        cmds.hide(f"jnt_splineCurve_{_order}")

    @property
    def joint(self):
        return self._joint
