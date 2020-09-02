import subprocess
import os
import json
import numpy as np
import glob

# script for conversion of obj data

def import_download_to_document():
    download_dir = '../../Downloads/VRModel/'
    document_dir = './VRDataset/'
    os.makedirs(document_dir, exist_ok=True)
    
    args = "cp -r {} {}".format(download_dir, document_dir)
    subprocess.call(args, shell=True)

def convert_ordered_vrm_file():
    dataset_dir = './VRDataset/'
    vrm_files = glob.glob(dataset_dir + '*.vrm')

    for num, vrm_file in enumerate(vrm_files):
        convert_path = dataset_dir + str(num) + '.vrm'
        args = "mv -f {} {}".format(vrm_file, convert_path)
        subprocess.call(args, shell=True)
    
    
def convert_vrm_into_glb():
    dataset_dir = './VRDataset/'
    glb_dataset_dir = './VRDatasetGLB/'
    
    os.makedirs(glb_dataset_dir, exist_ok=True)
    
    vrm_files = glob.glob(dataset_dir + '*.vrm')
    numbers = [int(v.split('/')[-1].split('.')[0]) for v in vrm_files]
    vrm_files_for_glb = [glb_dataset_dir + str(n) + '.vrm' for n in numbers]
    glb_files = [glb_dataset_dir + str(n) + '.glb' for n in numbers]
    
    for fnum, vrm_file, vrm_file_for_glb, glb_file in zip(numbers, vrm_files, vrm_files_for_glb, glb_files):
        args = "cp -f {} {}".format(vrm_file, vrm_file_for_glb)
        subprocess.call(args, shell=True)
        args = "mv {} {}".format(vrm_file_for_glb, glb_file)
        subprocess.call(args, shell=True)
        
        
def convert_vrm_into_glb_with_regist_format():
    dataset_dir = '../../Downloads/VRModel/'
    glb_dataset_dir = './VRDatasetGLB/'
    os.makedirs(glb_dataset_dir, exist_ok=True)
    
    data_regist_path = 'data_regist.json'
    f = open(data_regist_path)
    regist_data = json.load(f)
    
    for vrm_num, glb_num in regist_data.items():
        args = "cp -f {}{}.vrm {}{}.vrm".format(dataset_dir, vrm_num, glb_dataset_dir, glb_num)
        subprocess.call(args, shell=True)
        args = 'mv {}{}.vrm {}{}.glb'.format(glb_dataset_dir, glb_num, glb_dataset_dir, glb_num)
        subprocess.call(args, shell=True)
    
    
        
        
def move_to_document_to_download():
    download_dir = '../../Downloads/GLBModel/'
    document_dir = './VRDatasetGLB/'
    os.makedirs(download_dir, exist_ok=True)
    
    args = "cp -r {} {}".format(document_dir, download_dir)
    subprocess.call(args, shell=True)
    
        

if __name__ == '__main__':
    # according to particular cases, switching
    # import_download_to_document()
    # convert_ordered_vrm_file()
    # convert_vrm_into_glb()
    # move_to_document_to_download()
    convert_vrm_into_glb_with_regist_format()






