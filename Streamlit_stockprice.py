# ライブラリをインポートする
import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

# アプリのタイトルを表示する
st.title('株価の変動を可視化しましょう')

# サイドバーに説明を表示する
st.sidebar.write("""
# 株価
これは株価の変動を可視化するツールです。
下のバーで対象期間や、グラフの縦軸の範囲を指定するとグラフに反映できます。
""")

# サイドバーに期間指定用のスライダーのタイトルを表示する
st.sidebar.write("""
## 対象期間
""")

# 期間の表示を設定する
period_display = {
    '1d': "過去1日",
    '5d': "過去5日",
    '1mo': "過去1か月",
    '3mo': "過去3か月",
    '6mo': "過去6か月",
    '1y': "過去1年",
    '2y': "過去2年",
    '5y': "過去5年",
    '10y': "過去10年",
    'ytd': "今年",
    'max': "過去全て"        
}

# 表示期間選択のためのスライダーをサイドバーに表示して変数data_periodに指定期間を代入する
data_period = st.sidebar.select_slider('スライドさせて選択できます',
                                 options= [
                                     '1d', 
                                     '5d', 
                                     '1mo', 
                                     '3mo', 
                                     '6mo', 
                                     '1y', 
                                     '2y', 
                                     '5y', 
                                     '10y', 
                                     'ytd', 
                                     'max'],
                                 format_func=lambda x: period_display.get(x)
                                 )


# メインフレームに株価を取得する期間を表示する
st.write(f"""
### **{period_display[data_period]}** の株価         
""")

# キャッシュのクリアをする
@st.cache_data

# 選択された会社について指定期間の株価を取得してDataFrameに追加する関数を用意する
def get_data(data_period, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=data_period)
        hist.index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = "Name"
        pd.concat([df, hist])
        df = pd.concat([df, hist])
    return df


try:
    # サイドバーにグラフの縦軸の範囲指定用のスライダータイトルを表示する
    st.sidebar.write("""
    ## 縦軸(株価)の範囲              
    """)

    # サイドバーにグラフの縦軸の範囲指定用スライダーを表示し変数yminに範囲の最小値を、変数ymaxに範囲の最大値を代入する
    ymin, ymax = st.sidebar.slider(
        '左端と右端を動かせます',
        0.0, 3500.0, (0.0, 3500.0)
    )

    # 選択する会社の表示名と株価取得用の名称を対にして設定する
    tickers = {
        'Apple': 'AAPL',
        'Meta': 'META',
        'Google': 'GOOGL',
        'Microsoft': 'MSFT', 
        'Netflix': 'NFLX', 
        'Amazon' : 'AMZN',
        'Tesla' : 'TSLA',
        'Ford' : 'F',
        'GM' : 'GM',
    }

    # 関数を呼び出して株価を取得しDataFrameに代入しておく
    df = get_data(data_period, tickers)

    # 会社名の選択肢を表示する
    companies = st.multiselect(
        '会社名を選択してください',
        list(df.index),
        ['Google', 'Amazon', 'Meta', 'Apple', 'Tesla', 'Netflix']
    )

    if not companies: # 会社名が選択されていない場合に選ぶよう促す
        st.error('少なくとも１社は選んでください')

    else:
        # 選択された会社について株価の表を表示する
        data = df.loc[companies]
        st.write("### 株価 (USD)", data)
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(USD)'}
        )

        # グラフを描画する
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
        
except: # エラーの場合にその旨を知らせるコメントを表示する
    st.error("エラーが発生しました。")
