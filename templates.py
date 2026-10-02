from maya import cmds
from bousterRig import modules

def biped_template():
    shoulder_l = modules.System("clavicle_l", name="clavicle_L", shape="cube", scale=(.5, .1, .1), move=(20, -150, 0))
    shoulder_r = modules.System("clavicle_r", name="clavicle_R", shape="cube", scale=(.5, .1, .1), move=(-20, 150, 0))

    arm_l = modules.IKFKSwitch("upperarm_l", "arm_L")

    index_l = modules.IKFKSwitch("index_01_l", "index_L", direction="forward", scale_ik=0.1,
                        scalePoleVector=0.1, pv_distance=5)
    middle_l = modules.IKFKSwitch("middle_01_l", "middle_L")
    ring_l = modules.IKFKSwitch("ring_01_l", "ring_L")
    pinky_l = modules.IKFKSwitch("pinky_01_l", "pinky_L")
    thumb_l = modules.IKFKSwitch("thumb_01_l", "thumb_L")

    arm_r = modules.IKFKSwitch("upperarm_r", "arm_R")
    leg_l = modules.IKFKSwitch("thigh_l", "leg_L", orientToWorld=True, direction="forward", xAlignSettings=True)
    leg_r = modules.IKFKSwitch("thigh_r", "leg_R", orientToWorld=True, direction="forward", xAlignSettings=True)
    spine = modules.IKSplineSystem()
    neck = modules.NeckSystem()

    cmds.parentConstraint(spine.endSocket, neck.startSocket, mo=True)

    # Shoulders
    cmds.parentConstraint(spine.endSocket, shoulder_l.startSocket, mo=True)
    cmds.parentConstraint(spine.endSocket, shoulder_r.startSocket, mo=True)

    # Left arm
    cmds.parentConstraint(shoulder_l.endSocket, arm_l.ik_socket, mo=True)
    cmds.parentConstraint(shoulder_l.endSocket, arm_l.fk_socket, mo=True)

    # Right arm
    cmds.parentConstraint(shoulder_r.endSocket, arm_r.ik_socket, mo=True)
    cmds.parentConstraint(shoulder_r.endSocket, arm_r.fk_socket, mo=True)

def quadruped_template():
    # Root
    root = modules.Controller("root", shape="cross", color="GREEN",scale=(4, 4, 4))
    cmds.group(root.offset, n="mod_root")

    #Shoulder
    shoulder_l = modules.System("clavicle_l", name="clavicle_L", shape="cube", scale=(.5, .1, .1), move=(20, -150, 0))
    shoulder_r = modules.System("clavicle_r", name="clavicle_R", shape="cube", scale=(.5, .1, .1), move=(-20, 150, 0))

    # Limbs
    limb_f_l = modules.IKFKSwitch("upperlimb_f_l", "limb_f_L", orientToWorld=True, direction="forward", 
            softIK=True, footRoll=True, footRollLoc="piv_heel_f_l", xAlignSettings=True)
    limb_f_r = modules.IKFKSwitch("upperlimb_f_r", "limb_f_R", orientToWorld=True, direction="forward", 
            softIK=True, footRoll=True, footRollLoc="piv_heel_f_r")

    # Arm constraints

    cmds.parentConstraint(shoulder_l.endSocket, limb_f_l.ik_socket, mo=True)
    cmds.parentConstraint(shoulder_l.endSocket, limb_f_l.pv_socket.offset, mo=True)

    cmds.parentConstraint(shoulder_r.endSocket, limb_f_r.ik_socket, mo=True)
    cmds.parentConstraint(shoulder_r.endSocket, limb_f_r.pv_socket.offset, mo=True)

    limb_b_l = modules.IKFKSwitch("upperlimb_b_l", "limb_b_L", orientToWorld=True, 
            softIK=True, footRoll=True, footRollLoc="piv_heel_b_l", xAlignSettings=True)
    
    limb_b_r = modules.IKFKSwitch("upperlimb_b_r", "limb_b_R", orientToWorld=True, 
            softIK=True, footRoll=True, footRollLoc="piv_heel_b_r")


    # Spine
    spine = modules.IKSplineSystem()

    # Neck
    neck = modules.NeckSystem()

    cmds.parentConstraint(spine.endSocket, shoulder_l.startSocket, mo=True)
    cmds.parentConstraint(spine.endSocket, shoulder_r.startSocket, mo=True)

    cmds.parentConstraint(spine.body_socket, limb_b_l.ik_socket, mo=True)
    cmds.parentConstraint(spine.body_socket, limb_b_l.pv_socket.offset, mo=True)

    cmds.parentConstraint(spine.body_socket, limb_b_r.ik_socket, mo=True)
    cmds.parentConstraint(spine.body_socket, limb_b_r.pv_socket.offset, mo=True)

    cmds.parentConstraint(spine.body_socket, neck.startSocket, mo=True)
    # Root Constraints
    cmds.parentConstraint(root.curve, spine.startSocket, mo=True)
    cmds.parentConstraint(root.curve, limb_b_l.ik_controller_socket, mo=True)
    cmds.parentConstraint(root.curve, limb_b_r.ik_controller_socket, mo=True)
    cmds.parentConstraint(root.curve, limb_f_r.ik_controller_socket, mo=True)
    cmds.parentConstraint(root.curve, limb_f_l.ik_controller_socket, mo=True)

    cmds.group()