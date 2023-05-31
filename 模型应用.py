import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense
import datetime
car_name_list=[]#车的名称列表
final_result=[]
for i in range(20,25):
    s='CL'
    s+=str(i)
    car_name_list.append(s)
def datetime_to_int(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()
def str_to_datetime(string, format):
    return datetime.datetime.strptime(string, format)

X = pd.read_csv("D:\电池预测\打榜数据\\final_data.csv",parse_dates=[0,1])
Y = pd.read_csv("D:\电池预测\打榜数据\\result.csv",parse_dates=[1])

# 数据清洗(筛选缺失数据与异常数据)
result1 = set()
missing_rows = X.isnull().any(axis=1)
for index,j in enumerate(missing_rows):
    if j: result1.add(index)
for index, row in X.iterrows():
    if row['转换为40%-90%SOC所需充电量'] > -50: result1.add(index)
    if row['转换为40%-90%SOC所需充电量'] < -80: result1.add(index)
    if row['本次充电时间'] > 150: result1.add(index)
    if row['电机控制器直流母线平均电流'] < 0: result1.add(index)
    if row['电机控制器直流母线平均电流'] > 12: result1.add(index)
    for i in row:
        if i == '0' or i == 0: result1.add(index); break
result1 = sorted(list(result1))
result1.reverse()
X.drop(result1,inplace=True)

for i in car_name_list:
    data=X.copy()
    test_data=Y.copy()
    data=data[data['车辆名称']==i]
    data.drop(['驱动电机控制器平均温度','驱动电机平均转速','驱动电机平均温度','车辆行驶次数','电机输入平均电压','电机控制器直流母线平均电流','充电结束时间','本次充电时间','车辆名称','充电次数','本次充电SOC变化','充电量','平均工作电压',
                    '平均工作电流','可充电子系统温度平均值','可充电储能装置平均电压',
                    '可充电储能装置平均电流','单体电池平均电压'],axis=1,inplace=True)

    test_data = test_data[test_data['车辆号']==i]
    test_data.drop(['车辆号'],axis=1,inplace=True)
    def time_change(row):
        df_time=row['数据时间']
        date_string=df_time
        date_format='%Y-%m-%d %H:%M:%S'
        df_time=str_to_datetime(date_string,date_format)
        return datetime_to_int(df_time)
    def time_change2(row):
        df_time=row['拟充电时间']
        date_string=df_time
        date_format='%Y-%m-%d %H:%M'
        df_time=str_to_datetime(date_string,date_format)
        return datetime_to_int(df_time)

    data.loc[:,'拟充电时间']=data.apply(time_change,axis=1)
    data.drop(['数据时间'],axis=1,inplace=True)
    test_data.loc[:,'充电时间']=test_data.apply(time_change2,axis=1)
    test_data.drop(['拟充电时间'],axis=1,inplace=True)
    data=data[['拟充电时间','累计里程','转换为40%-90%SOC所需充电量']]
    test_data=test_data[['充电时间','拟充电时刻里程','估计的充电量']]
    train_data=data.copy()

    # 提取训练集和测试集
    train_x, train_y = train_data.iloc[:, :-1].values, train_data.iloc[:, -1].values
    test_x = test_data.iloc[:, :-1].values

    # 数据归一化
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    train_x = scaler.fit_transform(train_x)
    test_x = scaler.transform(test_x)

    # 构建LSTM模型
    # units是LSTM层的输出维度,定义神经元的个数,能将输入序列转为units个特征向量
    # activation是LSTM层的激活函数
    # input_shape是LSTM层的输入形状

    model = Sequential()
    model.add(LSTM(units=100, activation='relu', input_shape=(train_x.shape[1], 1)))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')

    # 训练模型
    model.fit(train_x.reshape(train_x.shape[0], train_x.shape[1], 1), train_y, epochs=200, batch_size=50)

    # 预测测试集
    test_y = model.predict(test_x.reshape(test_x.shape[0], test_x.shape[1], 1))

    final_result.extend(test_y.tolist())
print(final_result)