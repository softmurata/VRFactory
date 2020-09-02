import argparse
import json
import subprocess


parser = argparse.ArgumentParser()
parser.add_argument('--file_name', type=str, default='0000000000.vrm')
args = parser.parse_args()

f = open('data_regist.json')
database = json.load(f)

print()
print('---file number---')
print(database[args.file_name.split('.')[0]] + '.vrm')
print()


"""
f = open('data_regist.json')
database = json.load(f)

target_numbers = database.values()

for tn in target_numbers:
    args = 'mkdir ./SoftRasDataset/{}'.format(tn)
    subprocess.call(args, shell=True)
    
for type_name in ['OBJ', 'MASK', 'RENDER', 'CAMERA']:
    for tn in target_numbers:
        args = 'mkdir ./PIFuDataset/{}/{}'.format(type_name, tn)
        subprocess.call(args, shell=True)
"""

