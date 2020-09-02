import bpy
import os
import numpy as np
from mathutils import Matrix
from mathutils import Vector

# 1. create multiview angle images + camera matrix(Odaiba GPU)
# import_vrm.py => blender_turn_table.py
# 2. create obj file(my local PC)
# blender_color_texture.py

def load_test_object():
    # add cube
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))

    for mat in bpy.data.materials.values():
        bpy.data.materials.remove(mat)
        
    mat_name = "MyMaterial"
    # Test if material exists
    # If it does not exist, create it:
    mat = bpy.data.materials.new(mat_name)

    # Enable 'Use nodes':
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    node_tree = mat.node_tree

    for node in nodes.values():
        nodes.remove(node)

    pbsdf_node = nodes.new('ShaderNodeBsdfPrincipled')
    tex_img = nodes.new('ShaderNodeTexImage')
    output = nodes.new('ShaderNodeOutputMaterial')

    images = bpy.data.images
    img_path = 'C:/Users/TeamVRAN/Documents/VRFactory/Textures/000000/Body.png'
    img_name = 'Body.png'
    images.load(img_path)

    tex_img.image = images[img_name]

    links = node_tree.links

    link1 = links.new(tex_img.outputs[0], pbsdf_node.inputs[0])
    link2 = links.new(tex_img.outputs[1], pbsdf_node.inputs[18])
    link3 = links.new(pbsdf_node.outputs[0], output.inputs[0])

    bpy.context.object.active_material = mat
    
    return
    

# Adjust pose of mesh
def adjust_mesh_pose(angles):
    # angle
    anglex, angley, anglez = angles
    
    # x axis rotation
    anglex = anglex * np.pi / 180.0
    Rx = np.array([[1, 0,              0],
                   [0, np.cos(anglex), -np.sin(anglex)],
                   [0, np.sin(anglex), np.cos(anglex)]])
    
    # y axis rotation
    angley = angley * np.pi / 180.0
    Ry = np.array([[np.cos(angley),  0, np.sin(angley)],
                  [0,               1, 0],
                  [-np.sin(angley), 0, np.cos(angley)]])
    
    # z axis rotation
    anglez = anglez * np.pi / 180.0
    Rz = np.array([[np.cos(anglez), -np.sin(anglez), 0],
                   [np.sin(anglez), np.cos(anglez),  0],
                   [0,              0,               1]])
    
    R = Rz.dot(Rx).dot(Ry)
    
    return R

# setup multiple camera
def add_cam(location, rotation):
    bpy.ops.object.camera_add(location=location, rotation=rotation)
    return bpy.context.active_object



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


# main function

# delete all objects
for obj in bpy.data.objects.values():
    bpy.data.objects.remove(obj)

model_dir = 'C:/Users/TeamVRAN/Documents/VRFactory/VRDatasetGLB/'  # need to fix on odiba linux
model_pathes = os.listdir(model_dir)

# configuration
num_views = 36
origin = (0, 0, 0)
radius = 5
camera_rotation = 10

# create angles list
angles_list = []
for n in range(num_views):
    a = (0, 0, 360 / num_views * n)
    angles_list.append(a)

init_loc = [0, -radius, 0]

locations = []
for angles in angles_list:
    R = adjust_mesh_pose(angles)
    loc = np.dot(R[:3, :3], np.array(init_loc))
    locations.append(tuple(loc.tolist()))
    
print(locations)



for model_path in model_pathes:
    glb_path = model_dir + model_path
    model_title = model_path.split('.')[0]
    # load glb model
    bpt.ops.import_scene.gltf(filepath=glb_path)
    
    for location, angles in zip(locations, angles_list):
        camera_angles = [90 + camera_rotation + angles[0], angles[1], angles[2]]
        rotation = np.array(camera_angles) * np.pi / 180.0
        rotation = tuple(list(rotation))
        add_cam(location, rotation)
    
    my_areas = bpy.context.workspace.screens[0].areas
    my_shading = 'MATERIAL'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'
    
    for area in my_areas:
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = my_shading


    # take pictures by multiple camera
    scene = bpy.context.scene
    
    target_dir = 'C:/Users/TeamVRAN/Documents/VRFactory/SoftRasDataset/{}/'.format(model_title)
    os.makedirs(target_dir, exist_ok=True)

    for ob in scene.objects:
        if ob.type == 'CAMERA':
            print('Set camera %s' % ob.name)
            filename = int(ob.name.split('.')[-1])
            
            # get camera object class
            cam = bpy.data.objects[ob.name]
            # get camera data class
            cam_data = cam.data
                        
            # get intrinsic matrix
            K = get_intrinsic_from_blender(cam_data)
            # get extrinsic matrix
            RT = get_RT_matrix_from_blender(cam)

            P = K @ RT
            print('projection:', P)
            
            camera_dir = target_dir + 'cameramat/'
            os.makedirs(camera_dir, exist_ok=True)
            
            # save camera matrix
            np.save(camera_dir + 'intrinsic{}.npy'.format(filename), K)
            np.save(camera_dir + 'extrinsic{}.npy'.format(filename), RT)
            
            
            image_dir = target_dir + 'images/'
            os.makedirs(image_dir, exist_ok=True)
            
            bpy.context.scene.camera = ob
            file = os.path.join(image_dir, filename)
            # file adjustment
            bpy.context.scene.render.film_transparent = True
            bpy.context.scene.render.image_settings.file_format = 'PNG'
            bpy.context.scene.render.image_settings.color_mode ='RGBA'
            bpy.context.scene.render.filepath = file
            # save render image
            bpy.ops.render.render( write_still=True )
    
    

"""
# test case
# load_test_object()
# load glb file
glb_path = 'C:/Users/TeamVRAN/Documents/VRFactory/VRDatasetGLB/000012.glb'
bpy.ops.import_scene.gltf(filepath=glb_path)


num_views = 36

origin = (0, 0, 0)
radius = 5
camera_rotation = 10
locations = []

# create angles list
angles_list = []
for n in range(num_views):
    a = (0, 0, 360 / num_views * n)
    angles_list.append(a)

init_loc = [0, -radius, 0]

for angles in angles_list:
    R = adjust_mesh_pose(angles)
    loc = np.dot(R[:3, :3], np.array(init_loc))
    locations.append(tuple(loc.tolist()))
    
print(locations)

for location, angles in zip(locations, angles_list):
    
    camera_angles = [90 + camera_rotation + angles[0], angles[1], angles[2]]
    rotation = np.array(camera_angles) * np.pi / 180.0
    rotation = tuple(list(rotation))
    add_cam(location, rotation)
    


my_areas = bpy.context.workspace.screens[0].areas
my_shading = 'MATERIAL'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'


for area in my_areas:
    for space in area.spaces:
        if space.type == 'VIEW_3D':
            space.shading.type = my_shading


# take pictures by multiple camera
scene = bpy.context.scene

for ob in scene.objects:
    if ob.type == 'CAMERA':
        bpy.context.scene.camera = ob
        print('Set camera %s' % ob.name )
        file = os.path.join("C:/Users/TeamVRAN/Documents/VRFactory", ob.name )
        bpy.context.scene.render.film_transparent = True
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_mode ='RGBA'
        bpy.context.scene.render.filepath = file
        bpy.ops.render.render( write_still=True )

"""




