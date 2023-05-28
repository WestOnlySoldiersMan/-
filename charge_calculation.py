'''计算充电量'''
import pandas as pd
import os
from datetime import datetime
import sklearn
car_name_list=[]#车的名称列表
car_charge_num=[0]*15#车的充电次数列表
car_drive_num=[0]*15#车的行驶次数列表
for i in range(1,16):
    s='CL'
    s+=str(i)
    car_name_list.append(s)
'''停车充电'''
def Parking_Charge(data,data2,file):
    charge_start = data[(data['充电状态'].shift(1) == 3) & (data['充电状态'] == 1)]
    if charge_start.empty:
        return None
    # 计算每次充电的总电流之和
    total_charge_current = []
    end_time=[]
    soc_end_list=[]#soc列表
    voltage_list=[]#电压平均值
    current_list=[]#电流平均值
    charge_count=[]#充电次数
    charge_temperature=[]#可充电子系统温度平均值
    charge_v=[]#可充电储能装置电压
    charge_c=[]#可充电储能装置电流
    single_v=[]#单体电池平均电压
    for index, row in charge_start.iterrows():
        try:
            end_index = data[(data.index > index) & (data['充电状态'] != 1)].index[0]-1
        except:
            end_index=0
        total_current = data.loc[index:end_index-1, '总电流'].sum()/180
        total_charge_current.append(total_current)
        try:
            index2 = data2[(data2['数据时间'] >= data.loc[index, '数据时间'])].index[0]
        except:
            index2=0
        try:
            end_index2 = data2[(data2['数据时间'] <= data.loc[end_index, '数据时间'])].index[-1]
        except:
            end_index2=0
        if end_index!=0 and end_index2!=0:
            end_time.append(data.loc[end_index,'数据时间'])
            soc_end_list.append(data.loc[end_index, 'SOC'])
            voltage_list.append(data[(data.index>=index) & (data.index<=end_index)]['总电压'].mean())
            current_list.append(data[(data.index >= index) & (data.index <= end_index)]['总电流'].mean())
        else:
            end_time.append(data['数据时间'].iloc[-1])
            soc_end_list.append(data['SOC'].iloc[-1])
            voltage_list.append(data[data.index >= index]['总电压'].mean())
            current_list.append(data[data.index >= index]['总电流'].mean())
        if index2!=0:
            if  end_index2!=0:
                charge_temperature.append(data2[(data2.index >= index2) & (data2.index <= end_index2)][
                                              '可充电储能子系统各系统平均温度'].mean())
                charge_v.append(data2[(data2.index >= index2) & (data2.index <= end_index2)]['可充电储能装置电压'].mean())
                charge_c.append(data2[(data2.index >= index2) & (data2.index <= end_index2)]['可充电储能装置电流'].mean())
                single_v.append(data2[(data2.index >= index2) & (data2.index <= end_index2)]['单体电池平均电压'].mean())
            else:
                charge_temperature.append(data2[data2.index >= index2]['可充电储能子系统各系统平均温度'].mean())
                charge_v.append(data2[data2.index >= index2]['可充电储能装置电压'].mean())
                charge_c.append(data2[data2.index >= index2]['可充电储能装置电流'].mean())
                single_v.append(data2[data2.index >= index2]['单体电池平均电压'].mean())
        else:
            charge_temperature.append(0)
            charge_v.append(0)
            charge_c.append(0)
            single_v.append(0)
        car_charge_num[car_name_list.index(file.split('_')[0])]+=1
        charge_count.append(car_charge_num[car_name_list.index(file.split('_')[0])])
    p_charge=charge_start.copy()
    # 对每个元素应用函数获取时间
    def time_diff(row):
        dt_start = row['数据时间']
        dt_end = row['充电结束时间']
        diff = dt_end - dt_start
        return diff.total_seconds() / 60
    p_charge.loc[:,'结束时SOC']=soc_end_list
    def soc_diff(row):
        soc_start=row['SOC']
        soc_end=row['结束时SOC']
        diff=soc_end-soc_start
        return diff
    def required_charge(row):# #转换为40%-90%所需充电量
        soc_change=row['本次充电SOC变化']
        charge_num=row['充电量']
        try:
            required=(90-40)/soc_change*charge_num
        except:
            return 0
        return required
    p_charge.loc[:,'本次充电SOC变化']=p_charge.apply(soc_diff,axis=1)
    p_charge.loc[:,'充电量'] = total_charge_current
    p_charge.loc[:,'充电结束时间']=end_time
    p_charge.loc[:,'车辆名称']=file.split('_')[0]
    p_charge.loc[:,'本次充电时间']=p_charge.apply(time_diff, axis=1)
    p_charge.loc[:,'平均工作电压']=voltage_list
    p_charge.loc[:,'平均工作电流']=current_list
    p_charge.loc[:,'充电次数']=charge_count
    p_charge.loc[:,'转换为40%-90%SOC所需充电量']=p_charge.apply(required_charge,axis=1)
    # p_charge.loc[:,'平均行驶速度']=0
    p_charge.loc[:,'可充电子系统温度平均值']=charge_temperature
    p_charge.loc[:,'可充电储能装置平均电压']=charge_v
    p_charge.loc[:,'可充电储能装置平均电流']=charge_c
    p_charge.loc[:,'单体电池平均电压']=single_v
    p=p_charge[['数据时间','充电结束时间','本次充电时间','车辆名称','充电次数',
                '累计里程','本次充电SOC变化','充电量','平均工作电压',
                '平均工作电流','可充电子系统温度平均值','可充电储能装置平均电压',
                '可充电储能装置平均电流','单体电池平均电压','转换为40%-90%SOC所需充电量']]
    return p

'''行驶充电'''
def Driving_charge(data,file):
    # 筛选出充电状态为2且总电流小于0的时间段
    drive_charge = data[(data['充电状态'] == 2) & (data['总电流'] < 0)]
    if drive_charge.empty:
        return None
    total_charge_current = []
    end_time = []
    soc_end_list = []  # soc列表
    voltage_list = []  # 电压平均值
    current_list = []  # 电流平均值
    charge_count = []  # 充电次数
    average_speed=[]#平均行驶速度
    for index, row in drive_charge.iterrows():
        end_index = data[(data.index > index) & ((data['充电状态'] != 2) | (data['总电流'] >= 0))].index[0]
        total_current = data.loc[index:end_index-1, '总电流'].sum()/180
        total_charge_current.append(total_current)
        if end_index != 0:
            end_time.append(data.loc[end_index, '数据时间'])
            soc_end_list.append(data.loc[end_index, 'SOC'])
            voltage_list.append(data[(data.index >= index) & (data.index <= end_index)]['总电压'].mean())
            current_list.append(data[(data.index >= index) & (data.index <= end_index)]['总电流'].mean())
            average_speed.append(data[(data.index >= index) & (data.index <= end_index)]['车速'].mean())
        else:
            end_time.append(data['数据时间'].iloc[-1])
            soc_end_list.append(data['SOC'].iloc[-1])
            voltage_list.append(data[data.index >= index]['总电压'].mean())
            current_list.append(data[data.index >= index]['总电流'].mean())
            average_speed.append(data[data.index >= index]['车速'].mean())
        car_charge_num[car_name_list.index(file.split('_')[0])] += 1
        charge_count.append(car_charge_num[car_name_list.index(file.split('_')[0])])
    p_charge = drive_charge.copy()

    # 对每个元素应用函数获取时间
    def time_diff(row):
        dt_start = row['数据时间']
        dt_end = row['充电结束时间']
        diff = dt_end - dt_start
        return diff.total_seconds() / 60

    p_charge.loc[:, '结束时SOC'] = soc_end_list

    def soc_diff(row):
        soc_start = row['SOC']
        soc_end = row['结束时SOC']
        diff = soc_end - soc_start
        return diff

    def required_charge(row):  # #转换为40%-90%所需充电量
        soc_change = row['本次充电SOC变化']
        charge_num = row['充电量']
        try:
            required = (90 - 40) / soc_change * charge_num
        except:
            return 0
        return required
    p_charge.loc[:, '本次充电SOC变化'] = p_charge.apply(soc_diff, axis=1)
    p_charge.loc[:, '充电量'] = total_charge_current
    p_charge.loc[:, '充电结束时间'] = end_time
    p_charge.loc[:, '车辆名称'] = file.split('_')[0]
    p_charge.loc[:, '本次充电时间'] = p_charge.apply(time_diff, axis=1)
    p_charge.loc[:, '平均工作电压'] = voltage_list
    p_charge.loc[:, '平均工作电流'] = current_list
    p_charge.loc[:, '充电次数'] = charge_count
    p_charge.loc[:, '转换为40%-90%SOC所需充电量'] = p_charge.apply(required_charge, axis=1)
    p_charge.loc[:,'平均行驶速度']=average_speed
    p = p_charge[
        ['数据时间', '充电结束时间', '本次充电时间', '车辆名称', '充电次数', '累计里程','平均行驶速度', '本次充电SOC变化', '充电量',
         '平均工作电压', '平均工作电流', '转换为40%-90%SOC所需充电量']]
    return p

'''行驶状态数据处理'''
def Drive(data,motor_data,file):
    drive_data=data[((data['车辆状态'].shift(1)!=1) & (data['车辆状态']==1)) | ((data.index==0)&(data['车辆状态']==1))]
    if drive_data.empty:
        return None
    average_speed=[]#平均车速
    motor_control_temperature=[]#驱动电机控制器温度
    motor_speed=[]#驱动电机转速
    motor_temperature=[]#驱动电机温度
    motor_imput_v=[]#电机输入电压
    motor_current=[]#电机控制器直流母线电流
    drive_count=[]#行驶次数
    end_time=[]#停下时间
    for index,row in drive_data.iterrows():
        try:
            end_index=data[(data.index>index) & (data['车辆状态']!=1)].index[0]-1
        except:
            end_index=data.index[-1]
        end_time.append(data.loc[end_index,'数据时间'])
        try:
            motor_index =motor_data[(motor_data['数据时间']>=data.loc[index,'数据时间'])].index[0]
        except:
            motor_index=0
        try:
            motor_end_index = motor_data[(motor_data['数据时间'] <= data.loc[end_index, '数据时间'])].index[-1]
        except:
            motor_end_index=0
        average_speed.append(data[(data.index >= index) & (data.index <= end_index)]['车速'].mean())
        if motor_index!=0:
            motor_control_temperature.append(motor_data[(motor_data.index >= motor_index) & (motor_data.index <= motor_end_index)]['驱动电机控制器温度'].mean())
            motor_speed.append(motor_data[(motor_data.index >= motor_index) & (motor_data.index <= motor_end_index)]['驱动电机转速'].mean())
            motor_temperature.append(motor_data[(motor_data.index >= motor_index) & (motor_data.index <= motor_end_index)]['驱动电机温度'].mean())
            motor_imput_v.append(motor_data[(motor_data.index >= motor_index) & (motor_data.index <= motor_end_index)]['电机控制器输入电压'].mean())
            motor_current.append(motor_data[(motor_data.index >= motor_index) & (motor_data.index <= motor_end_index)]['电机控制器直流母线电流'].mean())
        else:
            motor_control_temperature.append(0)
            motor_speed.append(0)
            motor_temperature.append(0)
            motor_imput_v.append(0)
            motor_current.append(0)
        car_drive_num[car_name_list.index(file.split('_')[0])] += 1
        drive_count.append(car_drive_num[car_name_list.index(file.split('_')[0])])
    d_data=drive_data.copy()

    def time_diff(row):
        dt_start = row['数据时间']
        dt_end = row['停下时间']
        diff = dt_end - dt_start
        return diff.total_seconds() / 60
    d_data.loc[:,'平均车速']=average_speed
    d_data.loc[:,'驱动电机控制器平均温度']=motor_control_temperature
    d_data.loc[:,'驱动电机平均转速']=motor_speed
    d_data.loc[:,'驱动电机平均温度']=motor_temperature
    d_data.loc[:,'电机输入平均电压']=motor_imput_v
    d_data.loc[:,'电机控制器直流母线平均电流']=motor_current
    d_data.loc[:,'车辆行驶次数']=drive_count
    d_data.loc[:,'停下时间']=end_time
    d_data.loc[:,'本次行驶时间']=d_data.apply(time_diff,axis=1)
    d_data.loc[:,'车辆名称']=file.split('_')[0]
    d=d_data[['数据时间','停下时间','车辆名称','车辆行驶次数','平均车速','驱动电机控制器平均温度',
              '驱动电机平均转速','驱动电机平均温度','电机输入平均电压','电机控制器直流母线平均电流']]
    return d
def Final_meger(p_charge,drive):
    average_speed = []  # 平均车速
    motor_control_temperature = []  # 驱动电机控制器温度
    motor_speed = []  # 驱动电机转速
    motor_temperature = []  # 驱动电机温度
    motor_imput_v = []  # 电机输入电压
    motor_current = []  # 电机控制器直流母线电流
    drive_count = []  # 行驶次数
    for index,row in p_charge.iterrows():
        time=p_charge.loc[index,'数据时间']
        end_index=drive[(drive['数据时间']<=time)].index[-1]
        motor_control_temperature.append(drive[(drive.index<end_index)]['驱动电机控制器平均温度'].mean())
        motor_speed.append(drive[(drive.index<end_index)]['驱动电机平均转速'].mean())
        motor_temperature.append(drive[(drive.index<end_index)]['驱动电机平均温度'].mean())
        motor_imput_v.append(drive[(drive.index<end_index)]['电机输入平均电压'].mean())
        motor_current.append(drive[(drive.index<end_index)]['电机控制器直流母线平均电流'].mean())
        average_speed.append(drive[(drive.index<end_index)]['平均车速'].mean())
        drive_count.append(drive.loc[end_index,'车辆行驶次数'])
    d_data=p_charge.copy()
    d_data.loc[:, '驱动电机控制器平均温度'] = motor_control_temperature
    d_data.loc[:, '驱动电机平均转速'] = motor_speed
    d_data.loc[:, '驱动电机平均温度'] = motor_temperature
    d_data.loc[:, '电机输入平均电压'] = motor_imput_v
    d_data.loc[:, '电机控制器直流母线平均电流'] = motor_current
    d_data.loc[:,'车辆行驶次数']=drive_count
    return d_data
def get_list_average(data):
    def list_mean1(row):
        l=row['可充电储能子系统各温度探针检测到的温度值']
        l=l.split(',')
        float_l=[float(i) for i in l]
        return sum(float_l)/len(float_l)
    def list_mean2(row):
        l=row['单体电池电压']
        l=l.split(',')
        float_l = [float(i) for i in l]
        return sum(float_l)/len(float_l)
    x=data.copy()
    x.loc[:,'可充电储能子系统各系统平均温度']=x.apply(list_mean1,axis=1)
    x.loc[:,'单体电池平均电压']=x.apply(list_mean2,axis=1)
    return x
if __name__ == '__main__':
    path='D:/15台车运行数据'#数据地址
    files=os.listdir(path)
    p_charge_list=[]#停车充电
    d_charge_list=[]#行驶充电
    x=0
    y=0
    for file in files:
        if x==0:
            flag1=True
        else:
            flag1=False
        if y==0:
            flag2=True
        else:
            flag2=False
        data_path=os.path.join(path,file)#例子，取第一个文件
        data_all=[]
        for i in range(3):#读取文件数据
            data_all.append(pd.read_excel(data_path,sheet_name=i))
        car=data_all[0]#车辆行驶数据
        moto=data_all[1]#驱动电机数据
        charge=data_all[2]#可充电储能装置数据
        #特征：充电状态由3变为1时，说明车辆已开始充电。车辆在使用过程中，电流为正值时为放电现象，电流为负值时为充电现象
        I1=car[['数据时间','累计里程','总电压','车辆状态','充电状态','总电流','SOC','车速']]
        I2=moto
        I3=get_list_average(charge)
        p_charge_list=Parking_Charge(I1,I3,file)
        drive = Drive(I1,I2,file)
        drive.dropna()
        try:
            final_data=Final_meger(p_charge_list,drive)
            final_data.dropna()
            filename = f'D:\电池预测\数据\\final_data.csv'
            final_data.to_csv(filename, encoding='utf_8_sig', mode='a', header=flag1, index=False)
            print(f'{file}----f-saved.')
        except:
            print(f'{file}----f无记录')
        try:
            filename = f'D:\电池预测\数据\drive.csv'
            drive.to_csv(filename, encoding='utf_8_sig', mode='a', header=flag1, index=False)
            print(f'{file}----drive-saved.')
        except:
            print(f'{file}----没有行驶记录')

        try:
            filename=f'D:\电池预测\数据\p_charge.csv'
            p_charge_list.to_csv(filename,encoding='utf_8_sig',mode='a',header=flag1,index=False)
            print(f'{file}----p-saved.')
        except:
            print(f'{file}----没有停车充电')
        x=1

        # d_charge_list=Driving_charge(data,file)
        # try:
        #     filename=f'D:\电池预测\数据\d_charge.csv'
        #     d_charge_list.to_csv(filename,encoding='utf_8_sig',mode='a',header=flag2,index=False)
        #     print(f'{file}----d-saved.')
        # except:
        #     print(f'{file}----没有行驶充电')
        # y=1
