import json
import os

data_path = 'data_regist.json'
data_directory = '../../Downloads/VRModel/'

files = os.listdir(data_directory)
file_num = len(files)
file_numbers = ['%06d' % idx for idx in range(file_num)]
file_names = [fn.split('.')[0] for fn in files]


f = open(data_path, 'r')
dic = json.load(f)
for file_name, file_n in zip(file_names, file_numbers):
    dic[file_name] = file_n

print(dic)

f.close()

f = open(data_path, 'w')
json.dump(dic, f)

