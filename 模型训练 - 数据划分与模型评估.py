import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense
import datetime
car_name_list=[]#车的名称列表
final_result=[]
for i in range(1,16):
    s='CL'
    s+=str(i)
    car_name_list.append(s)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def datetime_to_int(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()
def score(Y,y):
    s=0
    for i in range(len(Y)):
        s+=1-(abs(Y[i]-y[i][0])/abs(Y[i]))
    return s/len(Y)

# 读取文件
df = pd.read_csv("D:\电池预测\数据\\final_data.csv",parse_dates=[0])

# 数据清洗(筛选缺失数据与异常数据)
result = set()
missing_rows = df.isnull().any(axis=1)
for index,j in enumerate(missing_rows):
    if j: result.add(index)
for index, row in df.iterrows():
    if row['转换为40%-90%SOC所需充电量'] > -50: result.add(index)
    if row['转换为40%-90%SOC所需充电量'] < -80: result.add(index)
    if row['本次充电时间'] > 150: result.add(index)
    if row['电机控制器直流母线平均电流'] < 0: result.add(index)
    if row['电机控制器直流母线平均电流'] > 12: result.add(index)
    for i in row:
        if i == '0' or i == 0: result.add(index); break
result = sorted(list(result))
result.reverse()
df.drop(result,inplace=True)
#训练集、测试集切分
for i in car_name_list:
    d=df.copy()
    d=d[d['车辆名称']==i]
    split_index = int(d.shape[0] * 0.7)
    data=d.copy()
    test_data=d.copy()
    data = data.iloc[:split_index, :]
    test_data = test_data.iloc[split_index:, :]
    def time_change(row):
        df_time=row['数据时间']
        return datetime_to_int(df_time)
    data.loc[:,'拟充电时间']=data.apply(time_change,axis=1)
    test_data.loc[:,'拟充电时间']=test_data.apply(time_change,axis=1)
    data=data[['拟充电时间','累计里程','转换为40%-90%SOC所需充电量']]
    test_data=test_data[['拟充电时间','累计里程','转换为40%-90%SOC所需充电量']]
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

    # 预测值
    test_y = model.predict(test_x.reshape(test_x.shape[0], test_x.shape[1], 1))
    # 真实值
    true_y = test_data['转换为40%-90%SOC所需充电量']

    final_result.append(score(true_y.tolist(),test_y.tolist()))

x=car_name_list
y=final_result
plt.bar(x,y)
plt.title('数据柱状图')
plt.ylabel('模型评分')
plt.xlabel('车辆模型')
print(final_result)
plt.show()
