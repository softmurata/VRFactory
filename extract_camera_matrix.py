import bpy
import numpy as np
from mathutils import Matrix
from mathutils import Vector


def get_intrinsic_from_blender(cam_data):
    f_in_mm = cam_data.lens  # focal length(mm)
    print('focal length:', f_in_mm)
    scene = bpy.context.scene
    
    # resolution
    resolution_x_in_px = scene.render.resolution_x
    resolution_y_in_px = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100
    sensor_width_in_mm = cam_data.sensor_width
    sensor_height_in_mm = cam_data.sensor_height
    pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
    
    if cam_data.sensor_fit == 'VERTICAL':
        s_u = resolution_x_in_px * scale / sensor_width_in_mm / pixel_aspect_ratio
        s_v = resolution_y_in_px * scale / sensor_height_in_mm
    else:
        # 'HORIZONTAL' or 'AUTO'
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
        s_u = resolution_x_in_px * scale / sensor_width_in_mm
        s_v = resolution_y_in_px * scale * pixel_aspect_ratio / sensor_height_in_mm
        
    # K(intrinsic parameters)
    alpha_u = f_in_mm * s_u
    alpha_v = f_in_mm * s_v
    u_0 = resolution_x_in_px * scale / 2
    v_0 = resolution_y_in_px * scale / 2
    skew = 0
    
    K = Matrix(((alpha_u, skew, u_0),
                (0, alpha_v, v_0),
                (0, 0, 1)))
    print('K:', K)
    return K


# camera rotation and translation matrix
# 3 coordinate
# 1. The world coordinate 'world'
#    - right handed
# 2. The blender camera coordinate 'bcam'
#    - x is horizontal
#    - y is up
#    - right handed: negative z look at direction
# 3. desired computer vision camera coordinate 'cv'
#    - x is horizontal
#    - y is down
#    - right handed: positive z look at direction

def get_RT_matrix_from_blender(cam):
    # blender camera
    R_bcam2cv = Matrix(((1, 0, 0), (0, -1, 0), (0, 0, -1)))
    location, rotation = cam.matrix_world.decompose()[0:2]
    # print('location:', location, 'rotation:', rotation)
    # rotation matrix
    R_world2bcam = rotation.to_matrix().transposed()
    # print('rotation:', R_world2bcam)
    # translation vector
    T_world2bcam = -1 * R_world2bcam @ location
    # print('translation:', T_world2bcam)
    
    # world to computer vision
    R_world2cv = R_bcam2cv @ R_world2bcam
    T_world2cv = R_bcam2cv @ T_world2bcam
    print('rotation:', R_world2cv)
    print('translation:', T_world2cv)
    
    # 3 * 4 RT matrix
    RT = Matrix((R_world2cv[0][:] + (T_world2cv[0], ),
                 R_world2cv[1][:] + (T_world2cv[1], ),
                 R_world2cv[2][:] + (T_world2cv[2], )))
    
    return RT

idx = 15
n_view = 36
# camera object class
cam = bpy.data.objects['Camera.%03d' % (idx)]
# camera data class
cam_data = cam.data

# get intrinsic matrix
K = get_intrinsic_from_blender(cam_data)
# get extrinsic matrix
RT = get_RT_matrix_from_blender(cam)

P = K @ RT
print('projection:', P)



