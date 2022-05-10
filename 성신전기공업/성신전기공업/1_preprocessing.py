'''
    데이터 전처리에 사용한 함수들
    Notes:
        코드로 처리한 뒤, 특이한 데이터들은 수작업으로 처리했기 때문에
        데이터 전처리에 사용한 함수들을 실행하면 오류가 발생할 수 있으므로
        주석처리를 해제하여서 실행하는 것보다 함수설명(Docstring)과 주석을 읽어주시면 감사하겠습니다.
'''

import os
import re
import tqdm
import requests
import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def join_file():
    '''
    Raw 데이터에 있는 시트를 통합하고 수주파일과 매출파일을 합침

    Note:
        년도별로 시트가 나뉘어져 수주,매출 데이터가 기록되어 있음
    '''

    # 수주데이터 읽기
    df_suju = pd.DataFrame()
    for name in ['2011년','2012년','2013년','2014년','2015년','2016년','2017년','2018년','2019년','2020년']:
        new_df = pd.read_excel('./data/raw/suju.xlsx', header=0, sheet_name=name, dtype={'년월': str})
        df_suju = pd.concat([df_suju,new_df])

    # 매출데이터 읽기
    df_machul = pd.DataFrame()
    for name in ['2011년','2012년','2013년','2014년','2015년','2016년','2017년',
              '2018년','2019년','2020년']:
        new_df = pd.read_excel('./data/raw/machul.xlsx', header=0, sheet_name=name, dtype={'년월': str})
        df_machul = pd.concat([df_machul,new_df])

    # print(df_suju.columns)
    # print(df_machul.columns)

    #colmnn명 재정의
    df_suju.rename(columns = {'년월'        : 'date_ori',
                              ' 납  품  처'  : 'name_ori',
                              '품목'        : 'item_ori',
                              '용   량'     :'volumn_ori',
                              '수량'        : 'count_ori'}, inplace = True)
    df_machul.rename(columns = {'년월'        : 'date_ori',
                              ' 납  품  처'  : 'name_ori',
                              '품목'        : 'item_ori',
                              '용   량'     :'volumn_ori',
                              '수량'        : 'count_ori'}, inplace = True)
    # print(df_suju.columns)
    # print(df_machul.columns)

    #결측치 버리기
    df_suju = df_suju.dropna(axis=0,how='all')
    df_machul = df_machul.dropna(axis=0,how='all')

    # 수주데이터는 kind 열을 s로 변경
    for i in range(len(df_suju)):
        df_suju.loc[i,'kind'] = 's'

    # 매출데이터는 kind 열을 m로 변경
    for i in range(len(df_machul)):
        df_machul.loc[i,'kind'] = 'm'

    #데이터 저장
    df = pd.DataFrame()
    df = pd.concat([df_suju,df_machul], ignore_index=True)
    df = df.sort_values(['date_ori'])
    df = df.reset_index(drop=True)
    df.to_csv('./data/df.csv',index=False)

def split_name():
    '''
    납품처-수요처를 분리하여 각각의 column에 저장

    Note:
        1)납품처, 2)납품처-수요처의 형태로 데이터 존재
    '''

    #데이터 읽기
    df = pd.read_csv('./data/df.csv', header=0, dtype={'date_ori': str})

    # 납품처명이 없는 데이터 제거
    drop_list = []
    for i in range(len(df)):
        name_ori = df.loc[i, 'name_ori']

        if isNaN(name_ori):
            drop_list.append(i)
    df = df.drop(drop_list)
    df = df.reset_index(drop=True)

    # 납품처명 통일을 위해 특정 문자열 제거
    for i in range(len(df)):
        name_ori = df.loc[i,'name_ori']

        name_ori = name_ori.replace('㈜', '')
        name_ori = name_ori.replace(' ', '')
        name_ori = name_ori.replace('(자)', '')
        name_ori = name_ori.replace('(주)', '')
        name_ori = name_ori.replace('(재)', '')
        name_ori = name_ori.replace('(합)', '')
        name_ori = name_ori.replace('(유)', '')

        # 2)납품처 - 수요처 분리1
        if '-' in name_ori:
            split_list = name_ori.split('-')
            name = split_list[0]
            agent = ''

            for split in split_list[1:]:
                agent = agent + split

        # 2)납품처 - 수요처 분리2
        elif '(' in name_ori:
            split_list = name_ori.split('(')
            name = split_list[0]
            agent = ''

            for split in split_list[1:]:
                agent = agent + split
            agent = agent[:-1]
        # 1)납품처
        else:
            name = name_ori
            agent = None

        df.loc[i, 'name'] = name
        df.loc[i, 'agent'] = agent

    #데이터 저장
    df = df.sort_values(['name'])
    df.to_csv('./df.csv', index=False)

def kakaomap(query):
    '''
    납품처의 산업계분류 위해 KakaoMap API 사용

    Args:
        query(str):납품처이름

    Returns:
        tuple: 주소, 업계카테고리, 카카오맵 기준 이름
    '''
    address = None
    category = None
    place = None

    # REST API를 이용
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json?query=' + query
    header = {'Authorization': 'KakaoAK ' + 'key'}
    r = requests.get(url, headers=header)
    result = r.json()

    if len(result['documents']) != 0:
        address = result['documents'][0]['address_name']
        category = result['documents'][0]['category_name']
        place = result['documents'][0]['place_name']

    return (address, category, place)


def Search_navermap(df1, col, opt):
    '''
    네이버지도 API를 이용하여 산업분류

    Args:
        df1(DataFrame): 데이터프레임
        col(list): column명
        opt(str): 옵션

    Returns:
        DataFrame : 데이터프레임 결과
    '''
    v = df1.loc[:, col].values.tolist()
    search_result = []
    for keyword in tqdm.tqdm(v):
        url = f'https://map.naver.com/v5/search/{keyword}'

        if opt == 'headless':
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument("disable-gpu")
            browser = webdriver.Chrome('chromedriver', chrome_options=options)
        else:
            browser = webdriver.Chrome("chromedriver")

        browser.get(url)
        # browser.implicitly_wait(3)
        try:
            browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="searchIframe"]'))
            result_name = browser.find_element_by_class_name('_3Apve').text
            category = browser.find_element_by_class_name("_3B6hV").text
        except:
            result_name = None
            category = None

        search_result.append([keyword, result_name, category])
        browser.quit()
    df1.to_csv('./naver_map_search.csv')
    return df1

def category_split():
    '''
    KakakoMAP API 기준으로 나눈 업계 카테고리를 '>' 기준으로 나눔
    '''

    #데이터 읽기
    df = pd.read_csv('./data/df.csv', header=0, dtype={'date_ori': str})

    # 카테고리 분리
    for i in range(len(df)):
        category = df.loc[i,'category']
        category = category.replace(' ', '')

        # '>' 기준으로 나누기
        split_list = category.split('>')
        print(category, split_list)
        for j in range(len(split_list)):
            column = 'category' + str(j+1)
            df.loc[i, column] = split_list[j]

    df = df.sort_values(['name','date_ori'])

def split_row():
    '''
    여러 개의 데이터가 적혀있는 행 분리

    Examples:
         5K,7.5K,15K,20K,30K -> 5개 행으로 분리
    '''

    #데이터 읽기
    df = pd.read_csv('./data/df.csv', header=0, dtype={'date_ori': str})
    new_df = pd.DataFrame()

    #데이터를 여러 행으로 분리(Example 참조)
    drop_list = []
    for i in range(len(df)):
        volumn_ori = df.loc[i, 'volumn_ori']
        count_ori = df.loc[i, 'count_ori']

        if isNaN(volumn_ori):
            continue

        # 분리기준을 '/'으로 통일
        volumn_ori = volumn_ori.replace(',','/')
        volumn_ori = volumn_ori.replace('외', '')
        volumn_ori = volumn_ori.replace(' ', '')
        volumn_ori = volumn_ori.upper()

        # '/'이 있으면 행 분리
        if '/' in volumn_ori:
            target = df.iloc[i, :]
            split_list = volumn_ori.split('/')
            count = float(count_ori)

            for split in split_list:
                target['volumn'] = split
                if ~isNaN(count_ori) and count != 1:
                    a = round(count / len(split_list), 1)
                    target.loc['count'] = a
                    # print(volumn_ori, count_ori, a)
                else:
                    target.loc['count'] = count
                    # print(volumn_ori, count_ori, count)
                new_df = new_df.append(target, ignore_index=True)
            drop_list.append(i)
        # '/'이 없는 경우
        else:
            df.loc[i, 'volumn'] = volumn_ori
            df.loc[i, 'count'] = count_ori

    df = df.drop(drop_list)
    df = pd.concat([df, new_df], ignore_index=True)
    df = df.reset_index(drop=True)

def process_volumn():
    '''
    UPS 용량, 배터리 용량 등 정리

    Examples:
        50K(BLPOW,SCR) -> 50
        ITX12V 120AH -< 120
    '''

    #데이터 읽기
    df = pd.read_csv('./data/df.csv', header=0, dtype={'date_ori': str})

    for i in range(len(df)):
        volumn = df.loc[i, 'volumn']
        count = df.loc[i, 'count']
        item = df.loc[i, 'item']

        if isNaN(volumn):
            continue

        # UPS용량 정리
        if 'UPS' == item:
            volumn = clean_UPSvolumn(volumn)
            df.loc[i,'volumn'] = volumn
            df.loc[i,'count'] = count

        # 배터리용량 정리
        elif 'battery' == item:
            if 'AH' == volumn[-2:]:
                split_list1 = volumn.split('AH')
            elif 'A' == volumn[-1:]:
                split_list1 = volumn.split('A')
            else:
                volumn = re.sub(r'[^0-9]', '', volumn)
                if volumn == '':
                    df.loc[i,'volumn'] = None
                else:
                    df.loc[i,'volumn'] = volumn
                continue


            count_str = split_list1[1]
            if count_str != '':
                num = int(re.sub(r'[^0-9]', '', count_str))
                if isNaN(count):
                    df.loc[i,'count'] = num
                else:
                    df.loc[i,'count'] = int(count) * num
            else:
                pass

            split_list2 = split_list1[0].split('V')
            if len(split_list2) > 1:
                volumn = int(re.sub(r'[^0-9]', '', split_list2[1]))
            else:
                volumn = int(re.sub(r'[^0-9]', '', split_list2[0]))
            df.loc[i,'volumn'] = volumn

        #나머지
        else:
            df.loc[i, 'volumn'] = None

            a = df.loc[i, 'item']
            b = df.loc[i, 'volumn_ori']
            c = df.loc[i, 'volumn']
            d = df.loc[i, 'count_ori']
            e = df.loc[i, 'count']
            print(a, b, c, d, e)

def classify_category1():
    '''
    1차 카테고리 분류
    '''

    #데이터 읽기
    df = pd.read_csv('./data/df.csv', header=0, dtype={'date_ori': str})

    for i in range(len(df)):
        label = None

        category1 = df.loc[i, 'category1']
        category2 = df.loc[i, 'category2']
        category3 = df.loc[i, 'category3']
        category4 = df.loc[i, 'category4']
        category5 = df.loc[i, 'category5']

        # 산업분류 재정의(1차)
        if category1 == '서비스,산업':
            if category2 in ['에너지','무역업,중개업']:
                label = 'B2B'
            elif category2 == '건설,건축':
                if category3 == '건설자재':
                    label = '부품제조'
                elif category3 in ['시공업체','소방기구,소방설비']:
                    label = '완제품제조'
                elif category3 in ['건축설계,컨설팅','인테리어']:
                    label = 'B2BC2C'
                elif category3 in ['조립식,주문주택','종합건설사']:
                    label = 'B2B'
            elif category2 in  ['관리,운영','전문대행','광고','환경']:
                label = 'B2BC2C'
            elif category2 in ['인터넷,IT','정보통신','기업','인터넷','인터넷,iT']:
                label = 'IT'
            elif category2 == '제조업':
                if category3 in ['OA,사무기기','농약,비료','가구','사료','인쇄']:
                    label = 'C2C'
                elif category3 in ['자동차부품','철강','교통,수송','섬유','산업용품','화학']:
                    label = '부품제조'
                elif category3 in ['의료용품','전기,전자','산업용로봇','기차,철도','통신장비','기타주변기기제조업','전기자동제어반']:
                    label = '완제품제조'
        elif category1 in ['가정,생활','문화,예술','스포츠,레저','여행']:
            label = 'C2C'
        elif category1 == '교육,학문':
            label = '교육'
        elif category1 == '교통,수송':
            if category2 == '자동차':
                label = 'C2C'
            elif category2 == '운송':
                label = 'B2B'
        elif category1 in ['금융,보험','언론,미디어']:
            label ='B2BC2C'
        elif category1 == '부동산':
            if category2 == '주거시설':
                label = 'C2C'
            elif category2 == '부동산서비스':
                label = 'B2B'
        elif category1 == '의료,건강':
            label = '의료안전'
        elif category1 == '사회,공공기관':
            if category2 == '공사,공단':
                if category3 in ['에너지관리공단','한국가스공사','한국가스안전공사',
                                 '한국석유관리원','한국수자원공사','한국전력공사','한국지역난방공사']:
                    label = '에너지'
                else:
                    label = '공공'
            else:
                label = '공공'

        df.loc[i,'label'] = label

def split_date():
    '''
    년월을 년/월로 분리

    Examples:
        2010.01 -> year:2010, month:1
        2010.1 -> year:2010, month:10
    '''

    #데이터 읽기
    df = pd.read_csv('./data/df.csv', header=0, dtype={'date_ori': str})

    for i in range(len(df)):
        date = df.loc[i,'date_ori']

        split_list = date.split('.')
        year = split_list[0]
        month = split_list[1]

        # Example 같은 비정상 데이터 존재
        if month == '1':
            month = month + '0'

        df.loc[i, 'year'] = year
        df.loc[i, 'month'] = month
        # print(date, year, month)

def classify_item():
    '''
    품목명 재정의 및 통일
    '''

    #데이터 읽기
    df = pd.read_csv('./data/df.csv', header=0, dtype={'date_ori': str})

    for i in range(len(df)):
        item_ori = df.loc[i, 'item_ori']
        if isNaN(item_ori):
            item1 = '기타'
            item2 = '기타'
            df.loc[i, 'item1'] = item1
            df.loc[i, 'item2'] = item2
            continue

        item = df.loc[i, 'item']
        if isNaN(item):
            continue

        item_ori = item_ori.upper()
        item_ori = item_ori.replace(' ', '')
        item1 = None
        item2 = None

        # 품목 재정의
        if item == 'etc':
            item1 = '부품'
            item2 = '부품'
        elif item_ori in ['UPS','UPS외','UPS임대','UPSQ','임대','UPS증설추가']:
            item1 = '장비'
            item2 = 'UPS'
        elif item_ori in ['INV', '인버터', '충전기', '주파수변환기', '정류기', 'AVR', 'BC','충전기외','정류기외','SNMP',
                          '모드버스통신','통신','SNMP교체','SNMP외','SMPS','통신모듈','통신연결','DCCH','NI.SI']:
            item1 = '장비'
            item2 = 'UPS외'
        elif item_ori in ['축전지', '충전기', '축전지추가', '축전지교체','밧데리','축전지교에','축전교체','축전지교체외',
                        '축전지교체','축전지고체외','밧데리교체','축전지','축전지외', '축전지점검', '폐자재', '폐전지',
                          '밧데리', '밧데리및함', '축전지함', '밧데리함외', '밧데리함','폐축전지','축전지설치','축전지고체','축저닞교체',
                          '축전지철거','ITX12V40AH','축전지교쳬','BMS']:
            item1 = '배터리'
            item2 = '배터리'
        elif item_ori in ['UPS점검','및시운전', '점검', '정밀점검', '접점', '점거외', '유지모술', '오버홀외', '이사','오버홀', '유지보수',
                          '주말대기','유지보슈','정밀정검','개보수','유집보수','우지보수','오버홀작업','점검대기','재작업','기술지원']:
            item1 = '점검/수리'
            item2 = '점검/유지보수'
        elif item_ori in ['UPS수리', 'UPS수리외', 'A/S', '부품수리', '수리외', '수리', 'FAN교체','부품교체','FAN','수리리','부품교체',
                          '술','수리부품','유지보술']:
            item1 = '점검/수리'
            item2 = '수리'
        elif item_ori in ['추가작업','전기공사','이전설치','이전','설치공사','이전설치외','대기','이설작업','이전설치공사','재작업'
                          '이전','분전반공사','분전반개조','시운전','설치시운전','클린작업','수배전반','공사','설치','철거',]:
            item1 = '점검/수리'
            item2 = '설치'
        elif item_ori == '교육':
            item1 = '점검/수리'
            item2 = '교육'
        elif item_ori in ['부픔','부룸','부품','부픔,''부룸','전류변환장치','뒷문짝','차단기','찬넬', '문짝', '예비품' , '전원장치','콘덴서' ,'필터',
                          '콘텍터' ,'MBP', '판넬', '배선', '뒷판', '베이스외' ,'판넬' ,'경보판넬' ,'건식변압기', '경보박스' ,'베이스' ,
                          '부품외', '가대', '추가자재', '변압기반', '분전반', '부속', '내진가대' ,'변압기', '외함' ,'MBP', '분번반',
                          '정류기모듈', '차단기판넬', '경보박스외' ,'축전지가대','UPS외함','T/R','T/R교체','EATON','부룸','콘덴서교체',
                          '차단기외','콘덴셔교체','MBP판넬','차폐변압기외']:
            item1 = '부품'
            item2 = '부품'
        elif item_ori in ['수리및축전지','철거,이전설치외','수리및축전지교체','점검및수리','UPS,정류기','가대및SNMP','축전지교체및수리',
                          '점검/축전지교체','철거및수리','점검및축전지','점검및시운전','축전지및수리','UPS수리및축전지교체','축전교체및수리',
                          '수리및부품','점검및축전지','수리,축전지','UPS,SNMP','철거및재설치','이전및전기공사','수리및점검']:
            if item == 'battery':
                item1 = '배터리'
                item2 = '배터리'
            elif item == 'other':
                item1 = '부품'
                item2 = '부품'
            elif item == 'UPS':
                item1 = 'UPS'
                item2 = 'UPS'
            else:
                item1 = '직접수정'
                item2 = '직접수정'
        else:
            item1 = '기타'
            item2 = '기타'

        df.loc[i,'item1'] = item1
        df.loc[i,'item2'] = item2

def classify_category2():
    '''
    2차 카테고리 분류
    '''

    #데이터 읽기
    df = pd.read_csv('./data/df.csv', header=0, dtype={'date_ori': str})
    classify = pd.read_csv('./data/category.csv', header=0) # 새로운 산업분류 기준 데이터

    for i in range(len(df)):
        category = df.loc[i, 'category']

        index_list = classify[classify['category'] == category].index.to_list()

        if len(index_list) > 0:
            index = index_list[0]
        else:
            continue

        # 재분류(2차)
        new_category = classify.loc[index, 'new']
        new_category = new_category.replace(' ','')
        new_category = new_category.replace(' ','')
        split_list = new_category.split('>')

        df.loc[i, 'category1'] = split_list[0]
        df.loc[i, 'category2'] = split_list[1]
        df.loc[i, 'category3'] = split_list[2]

def clean_UPSvolumn(volumn):
    '''
    UPS용량을 숫자만 남게 정리

    Args:
        volumn(str): 통일되지 않은 UPS용량

    Returns:
        str : UPS용량

    Examples:
        10KVA -> 10

    '''
    # 단위 제거
    if 'KVA' in volumn:
        volumn = volumn.replace('KVA', '')
    elif 'KV' in volumn:
        volumn = volumn.replace('KV', '')
    elif 'K' in volumn:
        volumn = volumn.replace('K', '')
    elif 'KVA' in volumn:
        volumn = volumn.replace('KVA', '')
    elif 'VA' in volumn:
        volumn = volumn.replace('VA', '')

    if volumn is None:
        return None

    # 단위가 아닌 문자열 제거
    else:
        volumn = volumn.replace('외', '')
        volumn = volumn.replace('EATON', '')
        volumn = volumn.replace('ETON', '')
        volumn = volumn.replace('BL1000', '')
        volumn = volumn.replace('SS-020', '')
        volumn = volumn.replace('BL3000', '')
        volumn = volumn.replace('SCR', '')
        volumn = volumn.replace('PW9390', '')
        volumn = volumn.replace('BL2000', '')
        volumn = volumn.replace('POWERWARE', '')
        volumn = volumn.replace('SSECO', '')
        volumn = volumn.replace('RM', '')
        volumn = volumn.replace('NET', '')
        volumn = volumn.replace('2U', '')
        volumn = volumn.replace('GREEN', '')
        volumn = volumn.replace('BLP', '')
        volumn = volumn.replace('BLP SCR', '')
        volumn = volumn.replace('BL', '')
        volumn = volumn.replace('(', '')
        volumn = volumn.replace(')', '')
        volumn = volumn.strip()
        return volumn

def cleaning(str):
    '''
    공백제거, 대문자로 변경

    Args:
        str: 문자열

    Returns:
        str: 문자열
    '''
    str = str.strip()
    str = str.upper()
    str = str.replace(' ', '')

    return str

def isNaN(num):
    '''
    결측치 확인

    Args:
        num: 숫자

    Returns:
        bool: True(None), False(Not None)

    '''
    return num != num
