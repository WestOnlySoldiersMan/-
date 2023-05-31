import os
import io
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# 获取训练集文件地址集合
training_path = list()
training_folder_path = '原始数据/训练集'
file_names = os.listdir(training_folder_path)
for file_name in file_names:
    file_path = os.path.join(training_folder_path, file_name)
    training_path.append(file_path)

# 构造数据属性概述和可视化分析图
os.chdir('数据分析结果')
for i,file in enumerate(training_path):
    if i != 0: os.chdir('..')
    if not os.path.exists(file_names[i][:-5]):
        os.mkdir(file_names[i][:-5])
    os.chdir(file_names[i][:-5])
    print('正在对文件 ' + file_names[i][:-5] + ' 进行数据分析......')
    for j in range(3):
        if j == 0: f = open('车辆运行数据属性概述.txt','w')
        elif j == 1: f = open('驱动电机数据属性概述.txt','w')
        elif j == 2: f = open('可充电储能装置数据属性概述.txt','w')
        df_dict = pd.read_excel('../../' + training_path[i], sheet_name=j)
        buf = io.StringIO()
        df_dict.info(buf=buf)
        f.write(buf.getvalue() + '\n')
        f.write(df_dict.describe().to_string())
        if j == 0:
            Fig, Axes = plt.subplots(4,3,figsize=(18,12))
            plt.suptitle('车辆运行数据特征属性区间分布图',fontsize=20)
            Axes[0, 0].set_title('数据时间分布图')
            sns.histplot(df_dict['数据时间'],bins=8,edgecolor='black',ax=Axes[0][0])
            Axes[0, 1].set_title('车速数据分布图')
            sns.histplot(df_dict['车速'], bins=20, edgecolor='black', ax=Axes[0][1])
            Axes[0, 2].set_title('车辆状态分布图')
            sns.countplot(x='车辆状态', data=df_dict, edgecolor='black', ax=Axes[0][2])
            Axes[1, 0].set_title('充电状态分布图')
            sns.countplot(x='充电状态', data=df_dict, edgecolor='black', ax=Axes[1][0])
            Axes[1, 1].set_title('累计里程分布图')
            sns.histplot(df_dict['累计里程'], bins=20, edgecolor='black', ax=Axes[1][1])
            Axes[1, 2].set_title('总电压分布图')
            sns.histplot(df_dict['总电压'], bins=20, edgecolor='black', ax=Axes[1][2])
            Axes[2, 0].set_title('总电流分布图')
            sns.histplot(df_dict['总电流'], bins=20, edgecolor='black', ax=Axes[2][0])
            Axes[2, 1].set_title('SOC分布图')
            sns.histplot(df_dict['SOC'], bins=20, edgecolor='black', ax=Axes[2][1])
            Axes[2, 2].set_title('电池单体电压最高值分布图')
            sns.histplot(df_dict['电池单体电压最高值'], bins=20, edgecolor='black', ax=Axes[2][2])
            Axes[3, 0].set_title('电池单体电压最低值分布图')
            sns.histplot(df_dict['电池单体电压最低值'], bins=20, edgecolor='black', ax=Axes[3][0])
            Axes[3, 1].set_title('最高温度值分布图')
            sns.histplot(df_dict['最高温度值'], bins=15, edgecolor='black', ax=Axes[3][1])
            Axes[3, 2].set_title('最低温度值分布图')
            sns.histplot(df_dict['最低温度值'], bins=15, edgecolor='black', ax=Axes[3][2])
            plt.tight_layout(h_pad=0.5)
            plt.savefig('车辆运行数据分布图.png')
        elif j == 1:
            Fig, Axes = plt.subplots(3, 2, figsize=(18, 12))
            plt.suptitle('驱动电机数据特征属性区间分布图', fontsize=20)
            Axes[0, 0].set_title('驱动电机控制器温度分布图')
            sns.histplot(df_dict['驱动电机控制器温度'], bins=50, edgecolor='black', ax=Axes[0][0])
            Axes[0, 1].set_title('驱动电机转速分布图')
            sns.histplot(df_dict['驱动电机转速'], bins=50, edgecolor='black', ax=Axes[0][1])
            Axes[1, 0].set_title('驱动电机转矩分布图')
            sns.histplot(df_dict['驱动电机转矩'], bins=50, edgecolor='black', ax=Axes[1][0])
            Axes[1, 1].set_title('驱动电机温度分布图')
            sns.histplot(df_dict['驱动电机温度'], bins=50, edgecolor='black', ax=Axes[1][1])
            Axes[2, 0].set_title('电机控制器输入电压分布图')
            sns.histplot(df_dict['电机控制器输入电压'], bins=100, edgecolor='black', ax=Axes[2][0])
            Axes[2, 1].set_title('电机控制器直流母线电流分布图')
            sns.histplot(df_dict['电机控制器直流母线电流'], bins=50, edgecolor='black', ax=Axes[2][1])
            plt.tight_layout(h_pad=0.5)
            plt.savefig('驱动电机数据分布图.png')
        elif j == 2:
            column1 = df_dict['可充电储能子系统各温度探针检测到的温度值']
            data_list = [x.split(',') for x in column1]
            for k in range(len(data_list)):
                data_list[k] = [float(x) for x in data_list[k]]
            average1 = [sum(row)/len(row) for row in data_list]
            column2 = df_dict['单体电池电压']
            data_list = [x.split(',') for x in column2]
            for k in range(len(data_list)):
                data_list[k] = [float(x) for x in data_list[k]]
            average2 = [sum(row) / len(row) for row in data_list]
            Fig, Axes = plt.subplots(2, 2, figsize=(18, 12))
            plt.suptitle('可充电储能装置数据特征属性区间分布图', fontsize=20)
            Axes[0, 0].set_title('可充电储能装置电压分布图')
            sns.histplot(df_dict['可充电储能装置电压'], bins=50, edgecolor='black', ax=Axes[0][0])
            Axes[0, 1].set_title('可充电储能装置电流分布图')
            sns.histplot(df_dict['可充电储能装置电流'], bins=50, edgecolor='black', ax=Axes[0][1])
            Axes[1, 0].set_title('可充电储能子系统各温度探针检测到的温度平均值分布图')
            sns.histplot(average1, bins=50, edgecolor='black', ax=Axes[1][0])
            Axes[1, 1].set_title('单体电池电压分布图')
            sns.histplot(average2, bins=50, edgecolor='black', ax=Axes[1][1])
            plt.tight_layout(h_pad=0.5)
            plt.savefig('可充电储能装置数据区间分布图.png')
            plt.close('all')