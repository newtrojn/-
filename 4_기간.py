import pandas as pd
import matplotlib.pyplot as plt

df_ori= pd.read_csv('data/df.csv', header=0, dtype={'date_ori': str})
df_ori = df_ori[df_ori['item2'] == 'UPS']
df_ori_s = df_ori[df_ori['kind'] == 's']
df_ori_m = df_ori[df_ori['kind'] == 'm']
df_ori_s = df_ori_s.reset_index()
df_ori_m = df_ori_m.reset_index()

result_list = []
for i in range(len(df_ori_s)):
    tmp_result = None
    name_s = df_ori_s.loc[i,'name_ori']
    year_s = df_ori_s.loc[i,'year']
    month_s = df_ori_s.loc[i,'month']
    volumn_s = df_ori_s.loc[i,'volumn']
    period_s = year_s * 12 + month_s

    tmp = df_ori_m[df_ori_m['name_ori'] == name_s]
    tmp = tmp.reset_index()
    if len(tmp) > 0:
        tmp = tmp.sort_values(['year','month','volumn'])
        for i in range(len(tmp)):
            year_m = tmp.loc[i, 'year']
            month_m = tmp.loc[i, 'month']
            volumn_m = df_ori_m.loc[i, 'volumn']
            period_m = year_m*12 + month_m

            period = None
            if period_m > period_s:
                if volumn_s == volumn_m:
                    tmp_result = {'name': name_s,
                                  'period': period_m - period_s,
                                  'volumn_s': volumn_s,
                                  'volumn_m': volumn_m}
                    break
                elif period == None:
                    peroid = period_m - period_s
                    tmp_result = {'name': name_s,
                                  'period': period_m - period_s,
                                  'volumn_s': volumn_s,
                                  'volumn_m': volumn_m}
                elif period < (period_m - period_s):
                    break
        if tmp_result is not None:
            result_list.append(tmp_result)
    else:
        pass

df_result = pd.DataFrame(result_list)
df_result.columns = ['name','period','volumn_s','volumn_m']
df_result.to_csv('./data/4_기간.csv',index=False)
