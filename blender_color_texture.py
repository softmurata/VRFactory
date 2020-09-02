import bpy
import os
# we have some errors like no hair images => set default hair images in directory

def texturing_from_glb(model_title):
    glb_path = 'C:/Users/TeamVRAN/Documents/VRFactory/VRDatasetGLB/{}.glb'.format(model_title)
    texture_dir = 'C:/Users/TeamVRAN/Documents/VRFactory/Textures/{}/'.format(model_title)
    obj_path = 'C:/Users/TeamVRAN/Documents/VRFactory/VRDatasetOBJ/{}.obj'.format(model_title)
    
    default_directory = 'C:/Users/TeamVRAN/Documents/VRFactory/Textures/default/'

    # delete all objects
    # bpy.ops.object.select_all(action='SELECT')
    # bpy.ops.object.delete(use_global=False, confirm=False)

    objects = bpy.data.objects
    for obj in objects.values():
        objects.remove(obj)

    # delete all materials
    materials = bpy.data.materials
    material_num = len(materials)
    print(materials.keys())
    for mat in materials.values():
        materials.remove(mat)

    # import glb file
    bpy.ops.import_scene.gltf(filepath=glb_path)

    materials = bpy.data.materials
    
    print()
    print('---material configuration----')
    print(materials.keys())
    
    delete_flag = True

    if len(materials) <= 5 or materials.keys()[0].split('.')[0] == '0':
        print('not VR format')
        delete_flag = False
        
    else:
        
        name_list = materials.keys()
        components = ['Hair', 'EyeExtra', 'EyeHighlight', 'EyeIris', 'EyeWhite', 'Face', 'FaceBrow', 'FaceEyelash', 'FaceEyeline', 'FaceMouth', 'HairBack', 'Bottoms', 'Tops', 'Accessory', 'AccessoryNeck', 'Body', 'Shoes', 'OnePiece', 'Onepice']
        
        for c in components:
            for mat in materials:
                mat_names = mat.name.split('_')
                if c in mat_names:
                    mat.name = c
        
        # reget
        name_list = materials.keys()
        
        # delete images
        images = bpy.data.images
        
        for im in images.values():
            images.remove(im)
            
        # get image files from texture directory
        image_files = os.listdir(texture_dir)
        
        # rename image file
        for c in components:
            for im in image_files:
                path_names = im.split('_')
                if path_names[-1] in ['nml.png', 'spe.png', 'out.png']:
                    # os.remove(texture_dir + im)  # why?
                    continue
                else:
                    if c in path_names:
                        change_im = texture_dir + c + '.png'
                        im = texture_dir + im
                        if not os.path.exists(change_im):
                            os.rename(im, change_im)
        
        image_files = os.listdir(texture_dir)
        image_files = [texture_dir + im for im in image_files]
        
        for img_path in image_files:
            images.load(img_path)
        
        for name in name_list:
            print()
            print('now {} process'.format(name))
            
            # exception
            if name.split('.')[0] not in components:
                delete_flag = False
                continue
        
            # get material
            material = materials[name]

            # get node and node_tree
            nodes = material.node_tree.nodes
            node_tree = material.node_tree
            
            # create new node
            restore_node_list = ['マテリアル出力', '画像テクスチャ']
            
            for mat_name, mat_value in nodes.items():
                if mat_name not in restore_node_list:
                    nodes.remove(mat_value)
                    
            # create principled bsdf node
            pbsdf_node = nodes.new('ShaderNodeBsdfPrincipled')
            
            # set links
            links = node_tree.links
                
            mat_out = nodes['マテリアル出力']
            # color_factor = nodes['ミックス']
            try:
                tex_img = nodes['画像テクスチャ']
            except:
                tex_img = nodes.new('ShaderNodeTexImage')
                img_path = default_directory + name.split('.')[0] + '.png'
                images.load(img_path)
                
            print(images.keys())
            
            # load image
            try:    
                if len(name.split('.')) >= 2:
                    prefix = name.split('.')[0]
                    tex_img.image = images[prefix + '.png']
                else:
                    tex_img.image = images[name + '.png']
            except:
                print('cannot load image file')
                delete_flag = False
                
            
            # create link 
            link1 = links.new(tex_img.outputs[0], pbsdf_node.inputs[0])
            link2 = links.new(tex_img.outputs[1], pbsdf_node.inputs[18])
            link3 = links.new(pbsdf_node.outputs[0], mat_out.inputs[0])
            # activate link process
            active_object = bpy.context.active_object
            active_object.active_material = material
        
        # save obj file
        scene = bpy.context.scene
        data_name = 'Armature'
            
        for ob in scene.objects:
            
            prefix = ob.name[:8]  # Armature
            if prefix == data_name and ob.name in bpy.data.objects.keys():
                    
                bpy.ops.export_scene.obj(filepath=obj_path)
            
            
    # remove glb file from pc
    if delete_flag:
        os.remove(glb_path)
    
# main function(test)
model_titles = os.listdir('C:/Users/TeamVRAN/Documents/VRFactory/VRDatasetGLB/')
model_titles = [m.split('.')[0] for m in model_titles]
print(model_titles)

for model_title in model_titles:
    texturing_from_glb(model_title)

"""
import bpy
import os

model_title = '32'
glb_path = 'C:/Users/TeamVRAN/Documents/VRFactory/VRDatasetGLB/{}.glb'.format(model_title)
texture_dir = 'C:/Users/TeamVRAN/Documents/VRFactory/Textures/{}/'.format(model_title)


# delete all objects
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete(use_global=False, confirm=False)

objects = bpy.data.objects
for obj in objects.values():
    objects.remove(obj)

# delete all materials
materials = bpy.data.materials
material_num = len(materials)
print(materials.keys())
if material_num > 0:

    for mat in materials.values():
        materials.remove(mat)

# import glb file
bpy.ops.import_scene.gltf(filepath=glb_path)

materials = bpy.data.materials

if len(materials) <= 5:
    print('not VR format')
    
else:
    
    name_list = materials.keys()
    components = ['Hair', 'EyeExtra', 'EyeHighlight', 'EyeIris', 'EyeWhite', 'Face', 'FaceBrow', 'FaceEyelash', 'FaceEyeline', 'FaceMouth', 'HairBack', 'Bottoms', 'Tops', 'Accessories', 'Body', 'Shoes']
    
    for c in components:
        for mat in materials:
            mat_names = mat.name.split('_')
            if c in mat_names:
                mat.name = c
    
    # reget
    name_list = materials.keys()
    
    # delete images
    images = bpy.data.images
    
    for im in images.values():
        images.remove(im)
        
    # get image files from texture directory
    image_files = os.listdir(texture_dir)
    
    # rename image file
    for c in components:
        for im in image_files:
            path_names = im.split('_')
            if path_names[-1] in ['nml.png', 'spe.png', 'out.png']:
                # os.remove(texture_dir + im)  # why?
                continue
            else:
                if c in path_names:
                    change_im = texture_dir + c + '.png'
                    im = texture_dir + im
                    if not os.path.exists(change_im):
                        os.rename(im, change_im)
    
    image_files = os.listdir(texture_dir)
    image_files = [texture_dir + im for im in image_files]
    
    for img_path in image_files:
        images.load(img_path)
    
    for name in name_list:
        print()
        print('now {} process'.format(name))
    
        # get material
        material = materials[name]

        # get node and node_tree
        nodes = material.node_tree.nodes
        node_tree = material.node_tree
        
        # create new node
        restore_node_list = ['マテリアル出力', 'ミックス', '画像テクスチャ']
        
        for mat_name, mat_value in nodes.items():
            if mat_name not in restore_node_list:
                nodes.remove(mat_value)
                
        # create principled bsdf node
        pbsdf_node = nodes.new('ShaderNodeBsdfPrincipled')
        
        # set links
        links = node_tree.links
        
        if 'ミックス' not in nodes.keys():
            mat_out = nodes['マテリアル出力']
            tex_img = nodes['画像テクスチャ']
            
            tex_img.image = images[name + '.png']
            
            link1 = links.new(tex_img.outputs[0], pbsdf_node.inputs[0])
            link2 = links.new(tex_img.outputs[1], pbsdf_node.inputs[18])
            link3 = links.new(pbsdf_node.outputs[0], mat_out.inputs[0])
            
        else:
            mat_out = nodes['マテリアル出力']
            tex_img = nodes['画像テクスチャ']
            color_factor = nodes['ミックス']
            
            tex_img.image = images[name + '.png']
            
            link1 = links.new(tex_img.outputs[0], color_factor.inputs[1])
            link2 = links.new(color_factor.outputs[0], pbsdf_node.inputs[0])
            link3 = links.new(tex_img.outputs[1], pbsdf_node.inputs[18])
            link4 = links.new(pbsdf_node.outputs[0], mat_out.inputs[0])
            
        # activate link process
        active_object = bpy.context.active_object
        active_object.active_material = material
        
# remove glb file from pc  
os.remove(glb_path)
"""


