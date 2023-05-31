import os
import numpy as np
import pandas as pd
from copy import deepcopy
from openpyxl import load_workbook
from sklearn.impute import KNNImputer

# 使用KNN算法实现数据清洗
def KNN(file_name, sheet_index):
    # 提取文件矩阵信息
    df = pd.read_excel(file_name, sheet_name=sheet_index)
    matrix = np.array(df)

    # 查找错误位置(分别在矩阵和xlsx文件中的位置)
    try: rows, cols = np.where((str(matrix) == '0xFE') | (str(matrix) == '0xFF'))
    except: return 0
    addresses = np.transpose(np.array([cols, rows])).tolist()
    places = deepcopy(addresses)
    for address in addresses:
        address[0] = chr(65 + address[0])
        address[1] += 2

    # 使用KNN算法预测缺失信息
    matrix = np.where((matrix == '0xFE') | (matrix == '0xFF'), np.nan, matrix)
    knn = KNNImputer()
    df_filled = knn.fit_transform(matrix)

    # 填充xlsx文件中的缺失信息
    workbook = load_workbook(filename=file_name)
    sheet = workbook.worksheets[sheet_index]
    while len(addresses) != 0:
        sheet[str(addresses[0][0]) + str(addresses[0][1])] = df_filled[places[0][1], places[0][0]]
        addresses = addresses[1:]
        places = places[1:]
    workbook.save(filename=file_name)
    return 1

# 获取训练集文件地址集合
training_path = list()
training_folder_path = '原始数据/训练集'
file_names = os.listdir(training_folder_path)
for file_name in file_names:
    file_path = os.path.join(training_folder_path, file_name)
    training_path.append(file_path)

# 对各个文件的各个表进行清洗
for file_name in training_path:
    for i in range(3):
        if KNN(file_name,i) == 0:
            print(' 文件 ' + file_name[9:] + ' sheet' + str(i) + ' 无需进行数据清洗......')
        else: print(' 正在对文件 ' + file_name[9:] + ' sheet' + str(i) + ' 进行数据清洗......')
