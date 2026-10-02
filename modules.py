from maya import cmds
from bousterRig.joints import JointChain
from bousterRig.controllers import Controller, IKSplineController
from bousterRig.utils import NodeEditorWindow

class System:
    _start_socket = None
    _end_socket = None

    def __init__(self, jnt, name, **kwargs):
        ctrl = Controller(name, color="BLUE", matchTo=jnt, parentConstraintTo=jnt, **kwargs)

        self._start_socket = cmds.group(ctrl.offset, n=f"mod_{name}")
        self._end_socket = jnt

    @property
    def startSocket(self):
        return self._start_socket
    @property
    def endSocket(self):
        return self._end_socket
    @property
    def mod(self):
        return self._mod

class FKSystem(System):
    def __init__(self, jnt, name):
        self._chain = JointChain(jnt, 'FK', length=3, color="BLUE")
        cmds.select(jnt, hi=True)
        _jnts = cmds.ls(long=True,sl=True, type="joint")[:3]
        
        for idx, jnt in enumerate(_jnts):
            cmds.parentConstraint(self._chain.jntChain[idx], jnt)

        _sC = self._chain.startChain
        _mC = self._chain.middleChain
        _eC = self._chain.endChain

        if '_l' in self._chain.startChain:
            _sC = self._chain.startChain.replace('_l', '_L')
            _mC = self._chain.middleChain.replace('_l', '_L')
            _eC = self._chain.endChain.replace('_l', '_L')
        elif '_r' in self._chain.startChain:
            _sC = self._chain.startChain.replace('_r', '_R')
            _mC = self._chain.middleChain.replace('_r', '_R')
            _eC = self._chain.endChain.replace('_r', '_R')

        
        
        #self._controllers = [Controller(f"{_sC}", color="BLUE"), Controller(f"{_mC}", color="BLUE"), Controller(f"{_eC}", color="BLUE")]
        _scale_start_chain = cmds.getAttr(f"{self._chain.middleChain}.tx") * 0.1 * 0.5
        _scale_middle_chain = cmds.getAttr(f"{self._chain.endChain}.tx") * 0.1 * 0.5
        _scale_end_chain = _scale_middle_chain/2

        _up = Controller(f"{_sC}", color="BLUE", shape="cube",
                        scale=(0.5, _scale_start_chain, 0.5), rotate=(0, 0, -90),
                        matchTo=self._chain.startChain, orientConstraintTo=self._chain.startChain)
        _middle = Controller(f"{_mC}", color="BLUE", shape="cube",
                            scale=(0.5, _scale_middle_chain, 0.5), rotate=(0, 0, -90),
                            matchTo=self._chain.middleChain, orientConstraintTo=self._chain.middleChain,
                             parentTo=_up.curve)
        _down = Controller(f"{_eC}", color="BLUE", shape="cube",
                            scale=(0.5, _scale_end_chain, 0.5), rotate=(0, 0, -90),
                            matchTo=self._chain.endChain, orientConstraintTo=self._chain.endChain,
                           parentTo=_middle.curve)

        self._controllers = [_up, _middle, _down]

        cmds.hide(self._chain.startChain)
        
        self._mod = cmds.group(self._controllers[0].offset, self._chain.startChain, n=f"mod_FK_{name}")
        self._end_socket = self._chain.endChain
        self._start_socket = self._mod


    @property
    def start_controller(self):
        return self._controllers[0]

    @property
    def middle_controller(self):
        return self._controllers[1]

    @property
    def end_controller(self):
        return self._controllers[2]

    @property
    def controllers(self):
        return self._controllers

class IKSystem(System):
    def __init__(self, jnt, end_chain_name, **kwargs):
        
        # Parent constraint to joints
        self._chain = JointChain(jnt, 'IK', length=3, color="RED")
        cmds.select(jnt, hi=True)
        _joints = cmds.ls(long=True,sl=True, type="joint")[:3]
        
        for idx, jnt in enumerate(_joints):
            cmds.parentConstraint(self._chain.jntChain[idx], jnt)
        
        _orientToWorld = False
        if "orientToWorld" in kwargs:
            _orientToWorld = kwargs["orientToWorld"]

        _ik_scale = 1
        if "scale_ik" in kwargs:
            _ik_scale = kwargs["scale_ik"]

        self._encChain_controller = Controller(f"IK_{end_chain_name}", shape="cube", height_baseline=True, color="RED",
                matchTo=self._chain.endChain, orientToWorld=_orientToWorld,
                scale=(_ik_scale, _ik_scale, _ik_scale))
        _offset = self._encChain_controller.curve
        
        #IK Handle
        _ikHandle = cmds.ikHandle(sj=self._chain.jntChain[0], ee=self._chain.jntChain[-1], n=f"ikh_{end_chain_name}")
        cmds.hide(_ikHandle[0])
        cmds.rename(_ikHandle[1], f"eff_{end_chain_name}")

        ### Pole Vector
        _scale_poleVector = 0.2
        if "scalePoleVector" in kwargs:
            _scale_poleVector = kwargs["scalePoleVector"]

        self._poleVector = Controller(f"pv_{end_chain_name}", shape="sphere", color="RED",
                scale=(_scale_poleVector, _scale_poleVector, _scale_poleVector), matchTo=self._chain.middleChain)
        # self._poleVector.matchTo(self._chain.middleChain)

        _dir = 1
        if "_R" in end_chain_name:
            _dir = -1

        if "direction" in kwargs and kwargs["direction"] == "forward":
            _dir *= -1

        _pv_distance = 20 * _dir

        if "pvDistance" in kwargs:
            _pv_distance = kwargs["pvDistance"] * _dir

        cmds.move(0, _pv_distance, 0, self._poleVector.offset, r=True, os=True)
        
        cmds.poleVectorConstraint(self._poleVector.curve, f"ikh_{end_chain_name}")

        if "softIK" in kwargs and kwargs["softIK"]:
            print("hi")
            _offset_softIK = cmds.group(em=True, n=f"offset_softIK_{end_chain_name}")
            cmds.matchTransform(_offset_softIK, self._encChain_controller.offset, pos=True, rot=True)
            _offset_softIK = cmds.parent(_offset_softIK, self._encChain_controller.curve)
            _offset = _offset_softIK
            # cmds.parent(_ikHandle[0], _offset)

            # Add ratio attribute to handle
            cmds.addAttr(self._encChain_controller.curve, ln="ratio", at="float", min=0, max=1, dv=0.1, keyable=True)

            print(_offset_softIK)
            # Distance between handle and start chain
            editor_name = NodeEditorWindow()
            editor_name.show_window()

            cmds.nodeEditor(editor_name.window, e=True, ct=[-1, f"IK/FK Switch {end_chain_name}"])
            cmds.createNode('distanceBetween', name=f"hardDistance_{end_chain_name}")
            cmds.connectAttr(f"{self._chain.startChain}.worldMatrix[0]", f"hardDistance_{end_chain_name}.inMatrix1")
            cmds.connectAttr(f"{self._encChain_controller.curve}.worldMatrix[0]", f"hardDistance_{end_chain_name}.inMatrix2")
            cmds.expression(s=f"$chainLength = {self._chain.middleChain}.translateX + {self._chain.endChain}.translateX;\n\n$softRatio = $chainLength * (1 - {self._encChain_controller.curve}.ratio);\n\n$targetDistance = $chainLength - $softRatio;\n\n$hardDis = {f'hardDistance_{end_chain_name}'}.distance;\n\n$expResult = max($targetDistance * (1 - exp(($softRatio - $hardDis)/$targetDistance)), 0);\n\ntranslateY = $expResult;",
                    n=f"softIK_{end_chain_name}", o=_offset_softIK[0], uc="all", ae=True)
            


        # Foot Roll
        if "footRoll" in kwargs and kwargs["footRoll"]:
            footRoll_loc_par = kwargs["footRollLoc"]

            # Parent foot roll to ik controller
            cmds.parent(footRoll_loc_par, _offset)

            cmds.select(footRoll_loc_par, hi=True)
            footRoll_locs = cmds.ls(long=True, sl=True, type='transform')

            _loc_controllers = []
            for loc in footRoll_locs:
                if _loc_controllers == []:
                    _loc_controllers.append(Controller(f"fr_{loc.split('|')[-1]}", shape="sphere", color="RED", scale=(0.2, 0.2, 0.2), matchTo=loc, 
                            parentTo=_offset))
                    
                else:
                    _loc_controllers.append(Controller(f"fr_{loc.split('|')[-1]}", shape="sphere", color="RED", scale=(0.2, 0.2, 0.2), matchTo=loc,
                            parentTo=_loc_controllers[-1].curve))

            cmds.aimConstraint(_loc_controllers[-1].curve, self._chain.endChain, aimVector=(1, 0, 0), upVector=(0, 0, 1), worldUpType="vector", worldUpVector=(0, 0, 1))

            _ball = cmds.listRelatives(_joints[-1], children=True, type='joint')[0]
            cmds.aimConstraint(_loc_controllers[-2].curve, _ball, aimVector=(1, 0, 0), upVector=(0, 0, 1), worldUpType="vector", worldUpVector=(0, 0, 1))
            cmds.delete(footRoll_loc_par)
            
            # print(footRoll_locs)
            cmds.parent(_ikHandle[0], _loc_controllers[-1].curve)


        else:
            cmds.parent(_ikHandle[0], _offset)
            cmds.move(0, 0, 0, _ikHandle[0], r=True, os=True, a=True)
            cmds.parentConstraint(self._encChain_controller.curve, self._poleVector.offset, mo=True)

        cmds.hide(self._chain.startChain)

        # cmds.orientConstraint(_ikHandle[0], self._chain.endChain, mo=True)
        

        self._mod = cmds.group(self._chain.startChain, self._poleVector.offset, self._encChain_controller.offset,
                   n=f"mod_IK_{end_chain_name}")
        self._end_socket = self._chain.endChain
        self._start_socket = self._chain.startChain

    @property
    def ik_controller(self):
        return self._encChain_controller

    @property
    def pv_controller(self):
        return self._poleVector

class IKFKSystem:
    def __init__(self, joint, mod_name, **kwargs):
        cmds.select(joint, hi=True)
        _jntName = joint.split("|")[-1]
        self._chain = cmds.ls(long=True, sl=True, type="joint")[:3]
        self._fk = FKSystem(_jntName, mod_name)
        self._ik = IKSystem(_jntName, mod_name, **kwargs)
        
        self._settings = Controller(f"settings_{mod_name}", shape="cross", color="GREEN",scale=(0.25, 0.25, 0.25),
                                    matchTo=joint, orientToWorld=True)
        # cmds.matchTransform(self._settings.offset, joint, pos=True)
        cmds.rotate('90deg', 0, 0, self._settings.offset)

        _dir = 1
        if "_R" in mod_name:
            _dir = -1

        _settings_distance = 20
        if "xAlignSettings" in kwargs and kwargs["xAlignSettings"]:
            cmds.move(_settings_distance * _dir, 0, 0, self._settings.offset, r=True)
        else:
            cmds.move(0, _settings_distance, 0, self._settings.offset, r=True)
        
        attrs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
        
        cmds.addAttr(self._settings.curve, ln="switchIkFk", at="enum", en="IK:FK:", keyable=True)
        cmds.setAttr(f"{self._settings.curve}.switchIkFk", e=True, keyable=True)
        for attr in attrs:
            cmds.setAttr(f"{self._settings.curve}.{attr}", lock=True, keyable=False, channelBox=False)

        self._mod = cmds.group(self._ik.mod, self._fk.mod, self._settings.offset, n=f"mod_{mod_name}")


    @property
    def settings(self):
        return self._settings

    @property
    def fk(self):
        return self._fk

    @property
    def ik(self):
        return self._ik

    @property
    def chain(self):
        return self._chain

class IKFKSwitch(System):
    def __init__(self, joint, mod_name, **kwargs):
        self._arm_settings = IKFKSystem(joint, mod_name, **kwargs)

        editor_name = NodeEditorWindow()

        editor_name.show_window()

        # Create a new window in the node editor for the IK/FK switch
        cmds.nodeEditor(editor_name.window, e=True, ct=[-1, f"IK/FK Switch {mod_name}"])
        cmds.createNode('floatMath', name=f"switchMath{mod_name}")

        # Add every needed node
        cmds.nodeEditor(editor_name.window, e=True, an=self._arm_settings.settings.curve)
        cmds.nodeEditor(editor_name.window, e=True, an=self._arm_settings.ik.pv_controller.offset)
        cmds.nodeEditor(editor_name.window, e=True, an=self._arm_settings.ik.ik_controller.offset)
        cmds.nodeEditor(editor_name.window, e=True, an=self._arm_settings.fk.start_controller.offset)

        cmds.select(f"switchMath{mod_name}", self._arm_settings.settings.curve)

        cmds.connectAttr(str(self._arm_settings.settings.curve) + ".switchIkFk", f"switchMath{mod_name}.floatB")
        cmds.setAttr(f"switchMath{mod_name}.operation", 1)
        cmds.setAttr(f"switchMath{mod_name}.floatA", 1)

        cmds.connectAttr(str(self._arm_settings.settings.curve) + ".switchIkFk",
                         self._arm_settings.fk.start_controller.offset + ".visibility")
        cmds.connectAttr(f"switchMath{mod_name}.outFloat",
                         self._arm_settings.ik.ik_controller.offset + ".visibility")
        cmds.connectAttr(f"switchMath{mod_name}.outFloat",
                         self._arm_settings.ik.pv_controller.offset + ".visibility")

        for jnt in self._arm_settings.chain:
            jnt_name = jnt.split("|")[-1]

            # Get constraints
            jnt_full_name = jnt + f"|{jnt_name}_parentConstraint1"
            cmds.nodeEditor(editor_name.window, e=True, an=jnt_full_name)
            cmds.connectAttr(str(self._arm_settings.settings.curve) + ".switchIkFk", jnt_full_name + f".FK_{jnt_name}W0")
            cmds.connectAttr(f"switchMath{mod_name}.outFloat", jnt_full_name + f".IK_{jnt_name}W1")

        # self._start_socket = cmds.group(f"mod_FK_{mod_name}", f"mod_IK_{mod_name}", f"offset_settings_{mod_name}",
        #                                 n=f"mod_{mod_name}")
        self._end_socket = self._arm_settings.chain[-1]

    @property
    def ik_socket(self):
        return self._arm_settings.ik.startSocket
    @property
    def pv_socket(self):
        return self._arm_settings.ik.pv_controller
    
    @property
    def fk_socket(self):
        return self._arm_settings.fk.startSocket
    @property
    def ik_controller_socket(self):
        return self._arm_settings.ik.ik_controller.offset

class IKSplineSystem(System):
    def __init__(self):
        _ikSpline = cmds.ikHandle(sj="spine_01", ee="spine_05", sol="ikSplineSolver", n="ikh_Spline_spine")
        _mod_name = "Spine"
        cmds.parent(_ikSpline[2], w=True)

        _curve = f"c_IKSpline_{_mod_name}"
        cmds.rename(_ikSpline[2], _curve)

        # Enable Twist controls on ik spline
        cmds.setAttr(f"{_ikSpline[0]}.dTwistControlEnable", 0)
        cmds.setAttr(f"{_ikSpline[0]}.dWorldUpType", 4)
        cmds.setAttr(f"{_ikSpline[0]}.dWorldUpAxis", 3)
        cmds.setAttr(f"{_ikSpline[0]}.dWorldUpVectorX", 0.0)
        cmds.setAttr(f"{_ikSpline[0]}.dWorldUpVectorY", 0.0)
        cmds.setAttr(f"{_ikSpline[0]}.dWorldUpVectorZ", 1.0)
        cmds.setAttr(f"{_ikSpline[0]}.dWorldUpVectorEndX", 0.0)
        cmds.setAttr(f"{_ikSpline[0]}.dWorldUpVectorEndY", 0.0)
        cmds.setAttr(f"{_ikSpline[0]}.dWorldUpVectorEndZ", 1.0)

        self._ctrl_body = Controller("body", shape="square", color="YELLOW", scale=(3, 3, 3), rotate=(0, 0, 85),
                               matchTo="pelvis")

        ctrl_pelvis = Controller("pelvis", color="YELLOW", shape="trapeze", scale=(1.1, 1.1, 1.1), rotate=(0, 90, -90),
                                 move=(0, -15, 0), height_baseline=True, matchTo="pelvis", parentConstraintTo="pelvis",
                                 parentTo=self._ctrl_body.curve)

        ctrl_fk_spine_01 = Controller("FK_spine_01", color="YELLOW", shape="cube",
                                      scale=(.2, 2, 2), height_baseline=True,
                                      matchTo="spine_01", parentTo=self._ctrl_body.curve)

        ctrl_fk_spine_02 = Controller("FK_spine_02", color="YELLOW", shape="cube",
                                      scale=(.2, 2, 2), height_baseline=True,
                                      matchTo="spine_02", parentTo=ctrl_fk_spine_01.curve)

        ctrl_fk_spine_03 = Controller("FK_spine_03", color="YELLOW", shape="cube",
                                      scale=(.2, 2, 2), height_baseline=True,
                                      matchTo="spine_03", parentTo=ctrl_fk_spine_02.curve)
        # cmds.matchTransform(ctrl_fk_spine_03.offset, "spine_03")

        ctrl_fk_spine_04 = Controller("FK_spine_04", color="YELLOW", shape="cube",
                                      scale=(.2, 2, 2), height_baseline=True,
                                      matchTo="spine_04", parentTo=ctrl_fk_spine_03.curve)

        ctrl_fk_spine_05 = Controller("FK_spine_05", color="YELLOW", shape="cube",
                                      scale=(.2, 2, 2), height_baseline=True,
                                      matchTo="spine_05", parentTo=ctrl_fk_spine_04.curve)

        ctrl_hips = IKSplineController("hips", color="RED", shape="star", scale=(2, 2, 2), order="down",
                                       matchTo="spine_01", parentTo=ctrl_fk_spine_01.curve)

        ctrl_chest_tan = IKSplineController("chestTan", color="RED", shape="star", scale=(2, 2, 2), order="mid",
                                            matchTo="spine_03", parentTo=ctrl_fk_spine_03.curve)

        ctrl_chest = IKSplineController("chest", color="RED", shape="star", scale=(2, 2, 2), order="up",
                                        matchTo="spine_05", parentTo=ctrl_fk_spine_05.curve,
                                        orientConstraintTo="spine_05")

        cmds.skinCluster(_curve, ctrl_hips.joint, ctrl_chest_tan.joint, ctrl_chest.joint, tsb=True)

        cmds.group(self._ctrl_body.offset, _curve, "ikh_Spline_spine", n="mod_spine")
        cmds.hide("ikh_Spline_spine", _curve)

        self._start_socket = self._ctrl_body.offset

        self._end_socket = "spine_05"

    @property
    def body_socket(self):
        return self._ctrl_body.curve
        

class NeckSystem(System):
    def __init__(self):
        _ctrl_neck_01 = Controller("neck_01", color="YELLOW", shape="cube", scale=(.2, 1, 1), height_baseline=True,
                                        matchTo="neck_01", parentConstraintTo="neck_01")

        ctrl_neck_02 = Controller("neck_02", color="YELLOW", shape="cube", scale=(.2, 1, 1), height_baseline=True,
                                  matchTo="neck_02", parentConstraintTo="neck_02", parentTo=_ctrl_neck_01.curve)

        ctrl_head = Controller("head", color="YELLOW", shape="cube", scale=(1.2, 1.2, .7), height_baseline=True,
                               matchTo="head", parentConstraintTo="head", parentTo=ctrl_neck_02.curve)

        self._start_socket = cmds.group(_ctrl_neck_01.offset, n="mod_head")

        self._end_socket = "head"