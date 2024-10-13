import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title('米国株価可視化アプリ')

st.sidebar.write("""
# GAFA株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

period_list = list()
period_list.append('1d')
period_list.append('5d')
period_list.append('1mo')
period_list.append('3mo')
period_list.append('6mo')
period_list.append('1y')
period_list.append('2y')
period_list.append('5y')
period_list.append('10y')
period_list.append('ytd')
period_list.append('max')

days = st.sidebar.selectbox(
    '表示日数選択',
    period_list
)
#これでもOK
#st.sidebar.write("""
# ##表示日数選択
#""")
#st.sidebar.selectbox(
#    "表示日数選択"
#    ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
#)

st.write(f"""
### 過去 **{days}**のGAFA株価
""")

@st.cache_data
#chacheに貯めておいて高速に読み取っていくための機能
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}')
        hist.index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

try:
    st.sidebar.write("""
    ## 株価の範囲指定
    """)

    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください',
        0.0, 3500.0, (0.0, 3500.0)
    )

    tickers = {
        'apple':'AAPL',
        'meta':'META',
        'google':'GOOGL',
        'micrsoft':'MSFT',
        'netflix':'NFLX',
        'amazon':'AMZN'
    }

    df = get_data(days, tickers)

    companies = st.multiselect(
        '会社名を選択してください',
        list(df.index),
        ['google', 'amazon', 'meta', 'apple']
    )

    if not companies:
        st.error('少なくとも一社は選んでください')
    else:
        data = df.loc[companies]
        st.write("### 株価（USD）", data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value':'Stock Prices(USD)'}
        ) 

        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "おっと！なにかエラーが起きているようです"
    )