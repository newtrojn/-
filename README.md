## 데이터 청년 캠퍼스(경기대) - 성신전기공업

--------------------------------------------
### Overview
성신전기공업에서 준 과제는 아래와 같음

    과제 1. 수요처별 상세 구분
    과제 2. 수요처별 구매 시기 분석 및 수주 변화 추이 분석
    과제 3. 수요처별 선호 용량 및 사양 분석
    과제 4. 수주에서 매출까지 소요 기간 분석
--------------------------------------------

### Usage
파일 실행 전 아래 명령어를 콘솔에 입력해주세요

    conda install --file packagelist.txt


 **과제 1. 수요처별 상세 구분(Data Preprocessing)**
  
    File             : 1_preprocessing.py(전처리 함수 모음)
    Language         : Python
    Enviroments      : Pycharm, Spyder, Excel, Google Drive

**과제2. 수요처별 구매 시기 분석 및 수주 변화 추이 분석**

    File             : 2_sarima1.ipynb
                       2_sarima2.rmd
                       2_sarima3.rmd
    Language         : Python, R
    Enviroments      : Spyder, RStudio, Excel         

**과제3. 수요처별 선호 용량 및 사양 분석**

    File             : 3_KNN.ipynb(KNN 분석)
                       3_RNN1.ipynb(RNN1 분석)
                       3_RNN2.ipynb(RNN2 분석)
                       3_LSTM1.ipynb(LSTM 분석)
                       3_LSTM2.ipynb(Bidirectional LSTM 분석)
    Language         : Python
    Enviroments      : Jypyter NoteBook, Excel, Tableau


**과제4. 수주에서 매출까지 소요 기간 분석**

    File             : 4_기간.py(수주~매출 기간 분석)
                       4_조달청.py(조달청 공공데이터 통합 및 추출)
    Language         : Python
    Enviroments      : Pycharm, Tableau

--------------------------------------------
### Raw Data


**suju.xlsx**

성신전기공업의 2011~2020년 수주 데이터

    Attribute : 년월, 납품처, 품목, 용량, 수량

**machul.xlsx**
  
성신전기공업의 2011~2020년 매출 데이터

    Attribute : 년월, 납품처, 품목, 용량, 수량
    
**03.xlsx~18.xlsx**
  
조달청에서 가져온  2003~2021년 공공기관 UPS 입찰 데이터
  
    Attribute
      등록유형, 조달구분, 공고시스템명, 계약구분, 계약번호, 계약변경차수,
      최종계약여부, 수요기관명, 수요기관코드, 수요기관구분, 수요기관지역명,
      계약건명, 계약법구분, 조항호코드, 조항호명, 계약방법, 대표물품분류번호,
      대표품명, 대표세부물품분류번호, 대표세부품명, 다수공급자계약여부, 우수제품여부,
      최초계약일자, 최초계약금액, 계약일자, 계약수량, 계약금액, 증감계약수량,
      증감계약금액, 대금지급구분, 최대납품기한, 공동계약여부, 업체명, 업체기업구분명,
      조달요청번호, 입찰공고번호, 추정가격, 예정가격, 입찰계약방법, 낙찰자결정방법,
      초년도계약번호, 장기계약차수, 장기계속계약여부, 계약지청명, 낙찰업체투찰금액,
      낙찰업체투찰률

--------------------------------------------
### Used Data
**df.csv**
    
성신전기공업의 수주,매출 데이터(suju.xlsx, machul.xlsx)를 통합한 뒤 전처리를 끝낸 최종 데이터
        
    Attribute
      date_ori, name_ori, item_ori, volumn_ori, count_ori, kind, name,
      sub_name, agent, category, volumn, count, year, month, item1, item2,
      category1, category2, category3

**category.csv**
        
카카오맵 API를 이용한 산업분류에서 재분류를 위해 직접 작성한 카테고리

    Attribute : category, new

**new_df.csv**

조달청 공공기관 입찰 데이터(03~18.xlsx)를 통합한 뒤 전처리를 끝낸 최종 데이터
  
    Attribute 
      등록유형, 조달구분, 공고시스템명, 계약구분, 계약번호, 계약변경차수,
      최종계약여부, 수요기관명, 수요기관코드, 수요기관구분, 수요기관지역명,
      계약건명, 계약법구분, 조항호코드, 조항호명, 계약방법, 대표물품분류번호,
      대표품명, 대표세부물품분류번호, 대표세부품명, 다수공급자계약여부, 우수제품여부,
      최초계약일자, 최초계약금액, 계약일자, 계약수량, 계약금액, 증감계약수량,
      증감계약금액, 대금지급구분, 최대납품기한, 공동계약여부, 업체명, 업체기업구분명,
      조달요청번호, 입찰공고번호, 추정가격, 예정가격, 입찰계약방법, 낙찰자결정방법,
      초년도계약번호, 장기계약차수, 장기계속계약여부, 계약지청명, 낙찰업체투찰금액,
      낙찰업체투찰률

**4_기간.csv**

수주~매출간의 기간, 용량 차이를 추출한 데이터

    Attribute : name, period, volumn_s, volumn_m

**data5.csv**

월별 공공기관 수주 건수

    Attribute : count

**dataF.csv**

월별 전체 매출액

    Attribute : money
