import pandas as pd

#조달청 데이터 읽기
df_list = []
for file_name in ['03','06','09','12','15','18']:
    df = pd.read_excel('./data/raw/'+ file_name +'.xlsx', header=0)
    df_list.append(df)

#데이터 합치기
df = pd.DataFrame()
for one_df in df_list:
    df = pd.concat([df,one_df],axis=0)

#조건에 따라 데이터 추출 및 저장
df = df.sort_values(['최초계약일자'])
df = df[df['업체명'].str.contains('성신')]
df = df[df['최종계약여부'] == 'Y']
df = df[~df['계약건명'].str.contains('부품')]
df.to_csv('./data/new_df.csv',index=False)
# df.to_excel('new_df.xlsx',index=False)
