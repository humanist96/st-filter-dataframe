import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.title("아파트 투자 매물 조회 서비스")

st.text("⭐ 공유하지 마시고 사용 부탁합니다. ⭐")

st.caption(
    """ 
    - 네이버 호가와 실거래가 기준 정보 제공(전국단위)
    - 업데이트 주기 : 매주 월요일
    - 문의나 요구사항이 있으면 언제든지 문의주세요(humanist96@gmail.com) 🙏.
    """
)

selected = option_menu(None, ["Home", "급매현황", "갭투자"],
                            icons=['house', 'map', "file-spreadsheet"],
                            menu_icon="cast", default_index=0, orientation="horizontal",
                            styles={
                                "container": {"padding": "0!important", "background-color": "#fafafa"},
                                "icon": {"color": "orange", "font-size": "25px"},
                                "nav-link": {"font-size": "18px", "text-align": "left", "margin": "0px",
                                                "--hover-color": "#eee"},
                                "nav-link-selected": {"background-color": "green"},
                            }
                        )

def home():
    st.text("👇 급매물 사용 예 👇")

    st.image("구선택.png", caption='사용예')

    st.text("👇 갭투자 사용 예 👇")

    st.image("갭투자.png", caption='사용예')

    st.markdown("""---""")

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
elif selected == '급매현황':
    df = pd.read_csv("급매.csv")

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

    st.data_editor(
        filter_dataframe(df),
        column_config={
            "URL": st.column_config.LinkColumn("Link")
        },
        hide_index=True,
    )
else:
    st.warning("Wrong")
