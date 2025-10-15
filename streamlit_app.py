import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from streamlit_option_menu import option_menu
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

import pandasai
import streamlit as st
st.write("✅ pandasai version:", pandasai.__version__)

from pandasai import SmartDataframe
from pandasai import SmartDatalake
#from pandasai.llm import OpenAI
from pandasai.llms.openai import OpenAI
#from pandasai.llm.connectors.openai import OpenAIConnector
#from pandasai.connectors.openai import OpenAIConnector


#from pandasai.prompts import AbstractPrompt

from streamlit_extras.buy_me_a_coffee import button

button(username="humanist96s", floating=True, width=221)

st.title("아파트 투자 매물 조회 서비스")

st.text("✅ 본 사이트의 정보는 참고용이지 어떠한 책임도 지지 않습니다. ✅")

selected = option_menu(None, ["Home", "시각화", "AI챗봇", "급매", "갭투자"],
                            icons=['house', 'clipboard-data', 'robot', 'map', "file-spreadsheet"],
                            menu_icon="cast", default_index=0, orientation="horizontal",
                            styles={
                                "container": {"padding": "0!important", "background-color": "#fafafa"},
                                "icon": {"color": "orange", "font-size": "25px"},
                                "nav-link": {"font-size": "18px", "text-align": "left", "margin": "0px",
                                                "--hover-color": "#eee"},
                                "nav-link-selected": {"background-color": "green"},
                            }
                        )

def convert_price_to_number(price_str):
    """
    한글로 표시된 금액을 숫자로 변환하는 함수
    예: '34억9천' -> 34900
    """
    if pd.isnull(price_str) or price_str in ['0', '0건']:
        return 0
    num_str = price_str.replace('억', '').replace('천', '')
    num_parts = price_str.split('억')
    billion = 0
    thousand = 0
    if '억' in price_str:
        billion = int(num_parts[0]) * 10000
        if '천' in num_parts[1]:
            thousand = int(num_parts[1].replace('천', '')) * 10
    elif '천' in price_str:
        thousand = int(num_parts[0].replace('천', '')) * 10
    return int(billion + thousand)


def home():
    st.caption(
    """ 
    - 네이버 호가와 국토부 실거래가 기준 정보 제공(업데이트 주기 : 매주 월요일)
    - 아직 베타버전(👷)입니다.
    - 네이버 URL이 올바르지 않은 경우는 네이버부동산에서 아파트명을 수정하여 검색해보세요.
    - 문의나 요구사항이 있으면 언제든지 연락주세요.(humanist96@gmail.com) 🙏.
    """)
    
    st.markdown("""---""")
    
    st.text("👇 시각화(대시보드) 예 👇")

    st.image("시각화.png", caption='시각화_대시보드')

    st.markdown("""---""")
    
    st.text("👇 AI챗봇 사용 예 👇")

    st.image("자연어_조회.png", caption='자연어 조회 사용예')

    st.markdown("""---""")

    st.text("👇 급매 사용 예 👇")

    st.image("구선택.png", caption='급매 사용예')

    st.markdown("""---""")

    st.text("👇 갭투자 사용 예 👇")

    st.image("갭투자.png", caption='갭투자 사용예')

    st.markdown("""---""")

def dashboard():

    st.caption(
    """ 
    - 본 시각화 페이지는 대시보드로써 로딩시간이 걸릴 수 있습니다. 잠시만 기다려주세요. 
    - 아직 베타버전(👷)입니다. (현재는 서울 데이터만 존재)
    - 화면에서 특정 조건과 선택만으로 원하는 정보를 변경 조회 가능하세요..
    - 문의나 요구사항이 있으면 언제든지 연락주세요.(humanist96@gmail.com) 🙏.
    """
    )
    
    st.text("👇 PC 전체화면에서 이용하시면 더욱 가시성이 좋습니다. 👇")
    
    link = '[full screen](http://49.247.172.187:5601/goto/eedf0e854cafa2539d5557d4f38514bb)'
    st.markdown(link, unsafe_allow_html=True)
    
    #components.iframe("http://49.247.170.21:5601/goto/fd4da9040a36e48602238e5a3b38efb3", height=4000)

    st.text("👇 아래에서는 네이버 전체 시세정보를 탐색할 수 있습니다. 👇")

    link2 = '[full screen](http://49.247.172.187:5601/goto/eedf0e854cafa2539d5557d4f38514bb)'
    st.markdown(link2, unsafe_allow_html=True)

    #components.iframe("http://49.247.170.21:5601/goto/f433462f1273ecd6430ca75c8bc3d9b8", height=1000)                  


def ai_home():

    st.caption(
    """ 
    - AI를 이용하여 자연어로 원하는 정보에 대한 답변을 얻을 수 있습니다.
    - 컬럼명이나 필터링 값 들은 ''으로 지정해주세요. AI에게는 친절하게 질문하셔야 합니다. 
    - 좋은 질문 예 1) '서울특별시'의 '최저비율'이 가장 낮은 top 5는?
    - 좋은 질문 예 2) '강남구'의 '매물최저가_숫자' 오름차순으로 상위 10개
    - 좋은 질문 예 3) '마포구', '2020년' 이후 입주한 아파트 중에 '최저비율'이 가장 낮은 top 3를 오름차순으로 정렬
    - 좋은 질문 예 4) '시/군' 기준으로 건수가 가장 많은 순으로 '시/군' 값과 개수를 나열
    - 좋은 질문 예 5) '마포구'에서 가장 '최저비율'이 가장 낮은 top 10중에서 '매출최저가_숫자'의 내림차순으로 정렬
    - 좋은 질문 예 6) '서울특별시'에서 '구'별 "매물최저가_숫자"의 평균이 높은 순서대로 나열해줘
    """
    )
    llm = OpenAI(st.secrets["api_key"])
    #llm = OpenAIConnector(api_token=st.secrets["api_key"])
    df1 = pd.read_csv("급매.csv")

    #열의 값을 숫자로 변환하여 새로운 열에 저장
    df1['최고가_숫자'] = df1['최고가'].apply(convert_price_to_number)
    df1['최저가(22년이후)_숫자'] = df1['최저가(22년이후)'].apply(convert_price_to_number)
    df1['최저가(2개월이내)_숫자'] = df1['최저가(2개월이내)'].apply(convert_price_to_number)
    df1['매물최저가_숫자'] = df1['매물최저가'].apply(convert_price_to_number)
    df1['전세매물최고_숫자'] = df1['전세매물최고'].apply(convert_price_to_number)
    df1['전세매물최저_숫자'] = df1['전세매물최저'].apply(convert_price_to_number)

    df2 = pd.read_csv("갭.csv")

    #열의 값을 숫자로 변환하여 새로운 열에 저장
    df2['실거래가_숫자'] = df2['실거래가'].apply(convert_price_to_number)
    df2['매매최고가_숫자'] = df2['매매최고가'].apply(convert_price_to_number)
    df2['갭투자금액_숫자'] = df2['갭투자금액'].apply(convert_price_to_number)
    df2['전세가_숫자'] = df2['전세가'].apply(convert_price_to_number)

    #sdf = SmartDataframe(df, config={"llm": llm})
    dl = SmartDatalake([df1, df2], config={"llm": llm})
    #dl = SmartDatalake([df1], config={"llm": llm})

    with st.form("form"):
        question = st.text_input("Prompt")
        submit = st.form_submit_button("Submit")

    if submit and question:
        with st.spinner('응답 기다리는 중...'):
            answer_sdf=dl.chat("Show the results of the answers to the following questions in a dataframe:" + question)
            
            try:
                #sdf -> df
                answer=answer_sdf.copy()

                st.data_editor(
                    filter_dataframe(answer),
                    column_config={
                        "URL": st.column_config.LinkColumn("Link")
                    },
                    hide_index=True,
                )
            except:
                st.text("죄송하지만 질문을 이해하지 못했습니다. 좀 더 잘 표현해주세요 ")


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]
    return df

if selected == 'Home':
    home()
elif selected == '시각화':
    dashboard()
elif selected == 'AI챗봇':
    ai_home()
elif selected == '급매':
    df = pd.read_csv("급매.csv")

    #열의 값을 숫자로 변환하여 새로운 열에 저장
    df['최고가_숫자'] = df['최고가'].apply(convert_price_to_number)
    df['최저가(22년이후)_숫자'] = df['최저가(22년이후)'].apply(convert_price_to_number)
    df['최저가(2개월이내)_숫자'] = df['최저가(2개월이내)'].apply(convert_price_to_number)
    df['매물최저가_숫자'] = df['매물최저가'].apply(convert_price_to_number)
    df['전세매물최고_숫자'] = df['전세매물최고'].apply(convert_price_to_number)
    df['전세매물최저_숫자'] = df['전세매물최저'].apply(convert_price_to_number)

    st.data_editor(
        filter_dataframe(df),
        column_config={
            "URL": st.column_config.LinkColumn("Link")
        },
        hide_index=True,
    )

elif selected == '갭투자':
    df = pd.read_csv("갭.csv")
    #st.dataframe(filter_dataframe(df))

    #열의 값을 숫자로 변환하여 새로운 열에 저장
    df['실거래가_숫자'] = df['실거래가'].apply(convert_price_to_number)
    df['매매최고가_숫자'] = df['매매최고가'].apply(convert_price_to_number)
    df['갭투자금액_숫자'] = df['갭투자금액'].apply(convert_price_to_number)
    df['전세가_숫자'] = df['전세가'].apply(convert_price_to_number)

    st.data_editor(
        filter_dataframe(df),
        column_config={
            "URL": st.column_config.LinkColumn("Link")
        },
        hide_index=True,
    )
else:
    st.warning("Wrong")

# HTML 코드 삽입 (왼쪽 상단 정렬)
chatbot_html = """
<style>
  /* 챗봇 위치를 왼쪽 상단으로 이동 */
  #chatling-embed {
      position: fixed !important;
      top: 20px !important;
      left: 20px !important;
      z-index: 1000 !important;
  }
</style>
<script>
  window.chtlConfig = { chatbotId: "3591773561" };
</script>
<script async data-id="3591773561" id="chatling-embed-script" 
type="text/javascript" src="https://chatling.ai/js/embed.js"></script>
"""

# Streamlit에서 HTML 실행
st.components.v1.html(chatbot_html, height=0)  # height=0으로 설정하면 공간 차지 X

