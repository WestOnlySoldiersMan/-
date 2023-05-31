import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False
pd.set_option('display.max_columns', None)

# 散点图显示函数
def show_plt(df):
    y = df['转换为40%-90%SOC所需充电量']
    fig, axes = plt.subplots(nrows=4, ncols=4, figsize=(20, 12))
    x = df['数据时间']
    axes[0, 0].scatter(x, y, color='#1f77b4')
    axes[0, 0].set_title('数据时间')
    x = df['累计里程']
    axes[0, 1].scatter(x, y, color='#1f77b4')
    axes[0, 1].set_title('累计里程')
    x = df['充电次数']
    axes[0, 2].scatter(x, y, color='#1f77b4')
    axes[0, 2].set_title('充电次数')
    x = df['平均工作电压']
    axes[0, 3].scatter(x, y, color='#1f77b4')
    axes[0, 3].set_title('平均工作电压')
    x = df['平均工作电流']
    axes[1, 0].scatter(x, y, color='#1f77b4')
    axes[1, 0].set_title('平均工作电流')
    x = df['可充电子系统温度平均值']
    axes[1, 1].scatter(x, y, color='#1f77b4')
    axes[1, 1].set_title('可充电子系统温度平均值')
    x = df['可充电储能装置平均电压']
    axes[1, 2].scatter(x, y, color='#1f77b4')
    axes[1, 2].set_title('可充电储能装置平均电压')
    x = df['可充电储能装置平均电流']
    axes[1, 3].scatter(x, y, color='#1f77b4')
    axes[1, 3].set_title('可充电储能装置平均电流')
    x = df['单体电池平均电压']
    axes[2, 0].scatter(x, y, color='#1f77b4')
    axes[2, 0].set_title('单体电池平均电压')
    x = df['驱动电机控制器平均温度']
    axes[2, 1].scatter(x, y, color='#1f77b4')
    axes[2, 1].set_title('驱动电机控制器平均温度')
    x = df['驱动电机平均转速']
    axes[2, 2].scatter(x, y, color='#1f77b4')
    axes[2, 2].set_title('驱动电机平均转速')
    x = df['驱动电机平均温度']
    axes[2, 3].scatter(x, y, color='#1f77b4')
    axes[2, 3].set_title('驱动电机平均温度')
    x = df['电机输入平均电压']
    axes[3, 0].scatter(x, y, color='#1f77b4')
    axes[3, 0].set_title('电机输入平均电压')
    x = df['电机控制器直流母线平均电流']
    axes[3, 1].scatter(x, y, color='#1f77b4')
    axes[3, 1].set_title('电机控制器直流母线平均电流')
    x = df['本次充电时间']
    axes[3, 2].scatter(x, y, color='#1f77b4')
    axes[3, 2].set_title('本次充电时间')
    x = df['车辆行驶次数']
    axes[3, 3].scatter(x, y, color='#1f77b4')
    axes[3, 3].set_title('车辆行驶次数')
    plt.tight_layout(h_pad=0.5)
    plt.show()

# 读取文件
df = pd.read_csv('final_data.csv',parse_dates=[0,1])

# 显示原文件数据基本属性
df.info()
print(df.describe())

# 数据清洗(筛选缺失数据)
result = set()
missing_rows = df.isnull().any(axis=1)
for index,j in enumerate(missing_rows):
    if j: result.add(index)
for index, row in df.iterrows():
    for i in row:
        if i == '0' or i == 0: result.add(index); break
result = sorted(list(result))
result.reverse()
df.drop(result,inplace=True)

# 显示文件非空数据基本属性
df.info()
print(df.describe())

# 散点图形式显示非空数据各特征与因变量的线性关系
show_plt(df)

# 数据清洗(清洗异常数据)
result = set()
for index, row in df.iterrows():
    if row['转换为40%-90%SOC所需充电量'] > -50: result.add(index)
    if row['转换为40%-90%SOC所需充电量'] < -80: result.add(index)
    if row['本次充电时间'] > 150: result.add(index)
    if row['电机控制器直流母线平均电流'] < 0: result.add(index)
    if row['电机控制器直流母线平均电流'] > 12: result.add(index)
result = sorted(list(result))
result.reverse()
df.drop(result,inplace=True)

# 显示文件非空合法数据基本属性
df.info()
print(df.describe())

# 散点图形式显示非空合法数据各特征与因变量的线性关系
show_plt(df)