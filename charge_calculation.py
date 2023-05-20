'''计算充电量'''
import pandas as pd
import os
import sklearn
'''停车充电'''
def Parking_Charge(data):
    try:
        charge_start = data[(data['充电状态'].shift(1) == 3) & (data['充电状态'] == 1)]
    except:
        error = [[0, 0, 0, 0, 0, 0]]
        sampe = pd.DataFrame(error, columns=['数据时间', '车辆状态', '充电状态', '总电流', 'SOC', '充电结束时间'])
        return sampe
    # 计算每次充电的总电流之和
    total_charge_current = []
    end_time=[]
    for index, row in charge_start.iterrows():
        try:
            end_index = data[(data.index > index) & (data['充电状态'] != 1)].index[0]
        except:
            end_index=0
        total_current = data.loc[index:end_index-1, '总电流'].sum()/180
        total_charge_current.append(total_current)
        if end_index!=0:
            end_time.append(data.loc[end_index,'数据时间'])
        else:
            end_time.append(data['数据时间'].iloc[-1])
        # 将每次充电的总电流之和添加到充电开始时间节点的数据中
    p_charge=charge_start.copy()
    p_charge.loc[:,'充电量'] = total_charge_current
    p_charge.loc[:,'充电结束时间']=end_time
    return p_charge

'''行驶充电'''
def Driving_charge(data):
    # 筛选出充电状态为2且总电流小于0的时间段
    try:
        drive_charge = data[(data['充电状态'] == 2) & (data['总电流'] < 0)]
    except:
        error=[[0,0,0,0,0,0]]
        sampe=pd.DataFrame(error,columns=['数据时间','车辆状态','充电状态','总电流','SOC','充电结束时间'])
        return sampe
    # 计算每次行驶充电过程中的总电流之和
    total_charge_current = []
    for index, row in drive_charge.iterrows():
        end_index = data[(data.index > index) & ((data['充电状态'] != 2) | (data['总电流'] >= 0))].index[0]
        total_current = data.loc[index:end_index-1, '总电流'].sum()/180
        total_charge_current.append(total_current)

    # 将每次行驶充电的总电流之和添加到数据中
    d_charge=drive_charge.copy()
    d_charge.loc[:,'充电量'] = total_charge_current
    return d_charge

if __name__ == '__main__':
    path='D:/15台车运行数据'#数据地址
    files=os.listdir(path)
    p_charge_list=[]#停车充电
    d_charge_list=[]#行驶充电
    for file in files:
        data_path=os.path.join(path,file)#例子，取第一个文件
        data_all=[]
        for i in range(3):#读取文件数据
            data_all.append(pd.read_excel(data_path,sheet_name=i))
        car=data_all[0]#车辆行驶数据
        moto=data_all[1]
        charge=data_all[2]
        #特征：充电状态由3变为1时，说明车辆已开始充电。车辆在使用过程中，电流为正值时为放电现象，电流为负值时为充电现象
        I=car[['数据时间','车辆状态','充电状态','总电流','SOC']]
        data=I.query("SOC<90 & SOC>40")
        p_charge_list.append(Parking_Charge(data))
        for i,df in enumerate(p_charge_list):
            filename=f'D:\电池预测\{file}p_charge{i+1}.csv'
            df.to_csv(filename,encoding='utf-8',index=False)
            print(f'{filename}saved.')
        d_charge_list.append(Driving_charge(d_charge_list))
        for i,df in enumerate(d_charge_list):
            filename=f'D:\电池预测\{file}d_charge{i+1}.csv'
            df.to_csv(filename,encoding='utf-8',index=False)
            print(f'{filename}saved.')

