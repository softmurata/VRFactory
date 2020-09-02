import argparse
import os
import glob
import subprocess
import random
import numpy as np
from skimage import io
import cv2


# load rgb image and silhouette image => save npz file format
# how should we cope with camera matrix?

# main function
def set_data(args):
    mesh_numbers = os.listdir(args.raw_dataset_dir)
    
    mesh_image_dirs = [args.raw_dataset_dir + str(m) + '/' + 'images/' for m in mesh_numbers]
    
    new_mesh_numbers = []
    
    for m, mid in zip(mesh_numbers, mesh_image_dirs):
        if len(os.listdir(mid)) == 0:
            delete_dir_name = args.raw_dataset_dir + str(m)
            shell_args = 'rm -rf {}'.format(delete_dir_name)
            subprocess.call(shell_args, shell=True)
        else:
            new_mesh_numbers.append(m)
            
    mesh_numbers = new_mesh_numbers
    
    mesh_numbers = sorted([int(m) for m in mesh_numbers])
    mesh_num = len(mesh_numbers)
    
    mesh_indices = list(range(mesh_num))
    train_num = int(mesh_num * args.split_ratio)
    train_indices = random.sample(mesh_indices, train_num)
    
    train_numbers = sorted([mesh_numbers[idx] for idx in train_indices])
    val_numbers = sorted([mesh_numbers[idx] for idx in mesh_indices if idx not in train_indices])
    
    train_text_path = args.mldata_dir + 'train.txt'
    val_text_path = args.mldata_dir + 'val.txt'

    ts = ''
    for tn in train_numbers:
        ts +='{} '.format(tn)
    vs = ''
    for vn in val_numbers:
        vs +='{} '.format(vn)
    
    
    with open(train_text_path, mode='w') as f:
        f.write(ts)
    
    with open(val_text_path, mode='w') as f:
        f.write(vs)
    
    meshes = []
    for idx, mn in enumerate(mesh_numbers):
        if idx not in train_indices:
            meshes.append([mn, False])
        else:
            meshes.append([mn, True])
    
        
    # training
    train_data_rgbs = []
    train_data_cameras = []
    train_data_voxels = []
    
    # validation
    val_data_rgbs = []
    val_data_cameras = []
    val_data_voxels = []
    
    
    for mesh_number, train_flag in meshes:
        print()
        print('----progress {} data----'.format(mesh_number))
        # set necessary directory's path
        image_dir = args.raw_dataset_dir + str(mesh_number) + '/' + args.image_dir
        silhouette_dir = args.raw_dataset_dir + str(mesh_number) + '/' + args.silhouette_dir
        camera_mat_dir = args.raw_dataset_dir + str(mesh_number) + '/' + args.traje_dir
        voxel_dir = args.raw_dataset_dir + str(mesh_number) + '/' + args.voxel_dir
        
        # extract files
        
        rgb_files = os.listdir(image_dir)
        view_numbers = [int(r.split('.')[0]) for r in rgb_files]
        sorted_index = np.argsort(view_numbers)
        view_numbers = [view_numbers[idx] for idx in sorted_index]
        rgb_files = [image_dir + '{}.png'.format(vn) for vn in view_numbers]
        sil_files = [silhouette_dir + '{}.png'.format(vn) for vn in view_numbers]
        camera_extrinsic_files = [camera_mat_dir + 'extrinsic{}.npy'.format(vn) for vn in view_numbers]
        camera_intrinsic_files = [camera_mat_dir + 'intrinsic{}.npy'.format(vn) for vn in view_numbers]
        
        # concatenate rgb + silhouette image
        rgbs_images, camera_matrices = concatenate_rgb_sil_image(rgb_files, sil_files, camera_extrinsic_files, camera_intrinsic_files, args)
        
        rgbs_shape_size = [1] + list(rgbs_images.shape)
        rgbs_shape_size = tuple(rgbs_shape_size)
        rgbs_images = rgbs_images.reshape(rgbs_shape_size)  # (1, 24, 4, height, width)
        
        cam_shape_size = [1] + list(camera_matrices.shape)
        cam_shape_size = tuple(cam_shape_size)
        camera_matrices = camera_matrices.reshape(cam_shape_size)  # (1, 24, 3, 4) or (1, 24, 4, 4)
        
        # create voxel sets
        voxel_path = voxel_dir + '{}.npz'.format(mesh_number)
        voxel_arr = np.load(voxel_path, mmap_mode='r')['arr_0']
        voxel_shape_size = [1] + list(voxel_arr.shape)
        voxel_shape_size = tuple(voxel_shape_size)
        voxel_arr = voxel_arr.reshape(voxel_shape_size)  # (1, 32, 32, 32)
        
        # add
        if train_flag:
            train_data_rgbs.append(rgbs_images)
            train_data_cameras.append(camera_matrices)
            train_data_voxels.append(voxel_arr)
        else:
            val_data_rgbs.append(rgbs_images)
            val_data_cameras.append(camera_matrices)
            val_data_voxels.append(voxel_arr)
        
    train_data_rgbs = np.concatenate(train_data_rgbs, axis=0)  # (num_data, 24, height, width)
    train_data_cameras = np.concatenate(train_data_cameras, axis=0)  # (num_data, 24, 3, 4) or (num_data, 24, 4, 4)
    train_data_voxels = np.concatenate(train_data_voxels, axis=0)  # (num_data, 32, 32, 32)  32 is voxel_size
    
    val_data_rgbs = np.concatenate(val_data_rgbs, axis=0)  # (num_data, 24, height, width)
    val_data_cameras = np.concatenate(val_data_cameras, axis=0)  # (num_data, 24, 3, 4) or (num_data, 24, 4, 4)
    val_data_voxels = np.concatenate(val_data_voxels, axis=0)  # (num_data, 32, 32, 32)  32 is voxel_size
    
    # save npz file format
    os.makedirs(args.mldata_dir, exist_ok=True)
    train_data_rgbs_path = args.mldata_dir + '{}_train_images.npz'.format(args.class_name)
    train_data_cameras_path = args.mldata_dir + '{}_train_cameras.npz'.format(args.class_name)
    train_data_voxels_path = args.mldata_dir + '{}_train_voxels.npz'.format(args.class_name)
    
    val_data_rgbs_path = args.mldata_dir + '{}_val_images.npz'.format(args.class_name)
    val_data_cameras_path = args.mldata_dir + '{}_val_cameras.npz'.format(args.class_name)
    val_data_voxels_path = args.mldata_dir + '{}_val_voxels.npz'.format(args.class_name)
    
    np.savez(train_data_rgbs_path, train_data_rgbs)
    np.savez(train_data_cameras_path, train_data_cameras)
    np.savez(train_data_voxels_path, train_data_voxels)
    
    np.savez(val_data_rgbs_path, val_data_rgbs)
    np.savez(val_data_cameras_path, val_data_cameras)
    np.savez(val_data_voxels_path, val_data_voxels)

def concatenate_rgb_sil_image(rgb_files, sil_files, camera_extrinsic_files, camera_intrinsic_files, args):
    rgbs_images = []
    camera_matrices = []
    
    height, width = args.ml_height, args.ml_width
    
    for rgb_path, sil_path, ext_path, intr_path in zip(rgb_files, sil_files, camera_extrinsic_files, camera_intrinsic_files):
        # load image
        rgb = cv2.cvtColor(cv2.imread(rgb_path), cv2.COLOR_BGR2RGB)  # (height, width, 3)
        sil = cv2.imread(sil_path, 0)  # (height, width)
        
        extrinsic = np.load(ext_path)[:3, :]
        intrinsic = np.load(intr_path)
        cam_mat = np.dot(intrinsic, extrinsic)
        cam_shape_size = [1] + list(cam_mat.shape)
        cam_shape_size = tuple(cam_shape_size)
        cam_mat = cam_mat.reshape(cam_shape_size)
        
        # need resize?
        rgb = cv2.resize(rgb, (height, width))
        sil = cv2.resize(sil, (height, width))
        
        # reshape
        rgb = rgb.transpose(2, 0, 1)  # (3, height, width)
        sil = sil.reshape(1, height, width)  # (1, height, width)
        
        rgbs = np.concatenate([rgb, sil], axis=0)
        
        # print('rgb sil shape:', rgbs.shape)
        
        shape_size = [1] + list(rgbs.shape)
        shape_size = tuple(shape_size)
        rgbs = rgbs.reshape(shape_size)  # (4, height, width) => (1, 4, height, width)
        
        rgbs_images.append(rgbs)
        camera_matrices.append(cam_mat)
        
    # concatenation
    rgbs_images = np.concatenate(rgbs_images, axis=0)  # (24, 4, height, width)
    camera_matrices = np.concatenate(camera_matrices, axis=0) # (24, 4, 4) or (24, 3, 4)
    
    return rgbs_images, camera_matrices
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_dataset_dir', type=str, default='./SoftRasDataset/')
    parser.add_argument('--image_dir', type=str, default='images/', help='rgb image directory')
    parser.add_argument('--silhouette_dir', type=str, default='silhouette/', help='silhouette image directory')
    parser.add_argument('--traje_dir', type=str, default='cameramat/', help='camera extrinsic and intrinsic parameter directory')
    parser.add_argument('--voxel_dir', type=str, default='Voxel/')
    parser.add_argument('--ml_height', type=int, default=512)
    parser.add_argument('--ml_width', type=int, default=512)
    parser.add_argument('--mldata_dir', type=str, default='mldataset/')
    parser.add_argument('--split_ratio', type=float, default=0.8)
    parser.add_argument('--class_name', type=str, default='0')
    args = parser.parse_args()
    
    set_data(args)



if __name__ == '__main__':
    main()