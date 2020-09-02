import bpy
import mathutils
import random
from math import radians

upper_axes = ['X', 'Z']
lower_axes = ['Y']
directions = ['L', 'R']


# upper_left_parent_angle, upper_left_child1_angle, upper_left_child2_angle, upper_right_parent_angle, upper_right_child1_angle, upper_right_child2_angle, lower_left_parent_angle, lower_left_child1_angle, lower_right_parent_angle, lower_right_child1_angle
angles = [[random.randint(-20, 20) for _ in range(10)] for _ in range(1)]

prefix = 'J_Bip'

armature_name = 'Armature.001'

# get armature class
armature = bpy.data.objects[armature_name]
armature.select_set(True)
bones = armature.pose.bones

upper_bone_groups = ['Shoulder', 'UpperArm', 'LowerArm']
lower_bone_groups = ['UpperLeg', 'LowerLeg']

upper_groups = []
for direct in directions:
    for upper_bone_name in upper_bone_groups:
        target_bone_name = prefix + '_' + direct + '_' + upper_bone_name
        upper_groups.append(target_bone_name)
        
lower_groups = []
for direct in directions:
    for lower_bone_name in lower_bone_groups:
        target_bone_name = prefix + '_' + direct + '_' + lower_bone_name
        lower_groups.append(target_bone_name)
        
upper_left_groups = upper_groups[:len(upper_bone_groups)]
upper_right_groups = upper_groups[len(upper_bone_groups):]

lower_left_groups = upper_groups[:len(lower_bone_groups)]
lower_right_groups = upper_groups[len(lower_bone_groups):]

# upper left side process
upper_left_parent_bone_class = bones[upper_left_groups[0]]
upper_left_child1_bone_class = bones[upper_left_groups[1]]
upper_left_child2_bone_class = bones[upper_left_groups[2]]

# upper right side process
upper_right_parent_bone_class = bones[upper_right_groups[0]]
upper_right_child1_bone_class = bones[upper_right_groups[1]]
upper_right_child2_bone_class = bones[upper_right_groups[2]]

# lower left side process
lower_left_parent_bone_class = bones[lower_left_groups[0]]
lower_left_child1_bone_class = bones[lower_left_groups[1]]

# lower right side process
lower_right_parent_bone_class = bones[lower_right_groups[0]]
lower_right_child1_bone_class = bones[lower_right_groups[1]]


# Initialize upper left side matrix
upper_left_init_parent_matrix = upper_left_parent_bone_class.matrix
upper_left_init_child1_matrix = upper_left_child1_bone_class.matrix
upper_left_init_child2_matrix = upper_left_child2_bone_class.matrix

# Initialize upper right side matrix
upper_right_init_parent_matrix = upper_right_parent_bone_class.matrix
upper_right_init_child1_matrix = upper_right_child1_bone_class.matrix
upper_right_init_child2_matrix = upper_right_child2_bone_class.matrix

# Initialize lower left side matrix
lower_left_init_parent_matrix = lower_left_parent_bone_class.matrix
lower_left_init_child1_matrix = lower_left_child1_bone_class.matrix

# Initialize lower right side matrix
lower_right_init_parent_matrix = lower_right_parent_bone_class.matrix
lower_right_init_child1_matrix = lower_right_child1_bone_class.matrix



for upper_left_parent_angle, upper_left_child1_angle, upper_left_child2_angle, upper_right_parent_angle, upper_right_child1_angle, upper_right_child2_angle, lower_left_parent_angle, lower_left_child1_angle, lower_right_parent_angle, lower_right_child1_angle in angles:
    print(upper_left_parent_angle, upper_left_child1_angle, upper_left_child2_angle, upper_right_parent_angle, upper_right_child1_angle, upper_right_child2_angle, lower_left_parent_angle, lower_left_child1_angle, lower_right_parent_angle, lower_right_child1_angle)
    
    axis = random.sample(upper_axes, 1)[0]
    
    # upper left side
    # parent bone class rotation
    mat_rot = mathutils.Matrix.Rotation(radians(upper_left_parent_angle), 4, axis)
    rot = upper_left_init_parent_matrix @ mat_rot
    upper_left_parent_bone_class.matrix = rot
            
    # child1 bone class rotation
    mat_rot = mathutils.Matrix.Rotation(radians(upper_left_child1_angle), 4, axis)
    rot = upper_left_init_child1_matrix @ mat_rot
    upper_left_child1_bone_class.matrix = rot
            
    # child2 bone class rotation
    mat_rot = mathutils.Matrix.Rotation(radians(upper_left_child2_angle), 4, axis)
    rot = upper_left_init_child2_matrix @ mat_rot
    upper_left_child2_bone_class.matrix = rot
    
    
    # upper right side
    # parent bone class rotation
    mat_rot = mathutils.Matrix.Rotation(radians(upper_right_parent_angle), 4, axis)
    rot = upper_right_init_parent_matrix @ mat_rot
    upper_right_parent_bone_class.matrix = rot
            
    # child1 bone class rotation
    mat_rot = mathutils.Matrix.Rotation(radians(upper_right_child1_angle), 4, axis)
    rot = upper_right_init_child1_matrix @ mat_rot
    upper_right_child1_bone_class.matrix = rot
            
    # child2 bone class rotation
    mat_rot = mathutils.Matrix.Rotation(radians(upper_right_child2_angle), 4, axis)
    rot = upper_right_init_child2_matrix @ mat_rot
    upper_right_child2_bone_class.matrix = rot
    
    
    axis = lower_axes[0]
    # lower left side
    # parent bone class rotation
    mat_rot = mathutils.Matrix.Rotation(radians(lower_left_parent_angle), 4, axis)
    rot = lower_left_init_parent_matrix @ mat_rot
    lower_left_parent_bone_class.matrix = rot
            
    # child1 bone class rotation
    mat_rot = mathutils.Matrix.Rotation(radians(lower_left_child1_angle), 4, axis)
    rot = lower_left_init_child1_matrix @ mat_rot
    lower_left_child1_bone_class.matrix = rot
    
    
    # lower right side
    # parent bone class rotation
    mat_rot = mathutils.Matrix.Rotation(radians(lower_right_parent_angle), 4, axis)
    rot = lower_right_init_parent_matrix @ mat_rot
    lower_right_parent_bone_class.matrix = rot
            
    # child1 bone class rotation
    mat_rot = mathutils.Matrix.Rotation(radians(lower_right_child1_angle), 4, axis)
    rot = lower_right_init_child1_matrix @ mat_rot
    lower_right_child1_bone_class.matrix = rot
    
            
    # take multiview angle's picture

        




