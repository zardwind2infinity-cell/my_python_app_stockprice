import streamlit as st
import yfinance as yf
import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 設定頁面配置
st.set_page_config(page_title="股票分析工具", layout="wide")
st.title("📈 股票價格與股息率分析")

# 隱藏 Streamlit 預設的右下角連結與徽章
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}     /* 隱藏左上角的 Streamlit 菜單 */
    footer {visibility: hidden;}       /* 隱藏底部的 footer */
    header {visibility: hidden;}       /* 隱藏頂部的 header */
    .viewerBadge_container__1QSob {display: none;}  /* 隱藏右下角徽章 */
    .stDeployButton {display: none;}   /* 隱藏右下角的部署按鈕 */
    .css-164nlkn.e1fqkh3o3 {display: none;} /* 有些版本的右下角提示 */
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)



# ============ 側邊欄 - 用戶輸入 ============
st.sidebar.header("⚙️ 分析參數設定")

# 輸入欄位
ticker_input = st.sidebar.text_input(
    "🔍 輸入股票代碼",
    value="KO",
    help="例如：2800.HK, AAPL, 0700.HK"
).strip().upper()

# 時間範圍選擇
time_range_option = st.sidebar.radio(
    "📅 選擇時間範圍方式",
    ["天數", "日期範圍"],
    index=0
)

if time_range_option == "天數":
    days = st.sidebar.number_input(
        "📊 輸入天數",
        min_value=1,
        max_value=3650,
        value=60,
        step=1,
        help="從今天往前推算的天數"
    )
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=int(days))
else:
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "開始日期",
            value=datetime.date.today() - datetime.timedelta(days=60),
            help="選擇查詢起始日期"
        )
    with col2:
        end_date = st.date_input(
            "結束日期",
            value=datetime.date.today(),
            help="選擇查詢結束日期"
        )

# 執行按鈕
execute_button = st.sidebar.button("🚀 執行分析", key="execute", use_container_width=True)

# ============ 主要函數 ============

def is_date_format(input_str):
    """檢查輸入是否為日期格式"""
    try:
        datetime.datetime.strptime(input_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def plot_stock_charts(stock_data, ticker_symbol, start_date, end_date, annual_dividend, dividend_year):
    """繪製互動式股價和股息率圖表"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # === 添加股價數據（左側Y軸）===
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['High'],
            fill=None,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['Low'],
            fill='tonexty',
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(162, 59, 114, 0.15)',
            name='Daily High-Low Range',
            hovertemplate='<b>Date</b>: %{x|%Y-%m-%d}<br>' +
                         '<b>High</b>: %{customdata[0]:.2f}<br>' +
                         '<b>Low</b>: %{y:.2f}<br>' +
                         '<extra></extra>',
            customdata=stock_data[['High']].values
        ),
        secondary_y=False
    )

    # 收盤價線
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='#2E86AB', width=3),
            hovertemplate='<b>Date</b>: %{x|%Y-%m-%d}<br>' +
                         '<b>Close</b>: %{y:.2f}<br>' +
                         '<extra></extra>'
        ),
        secondary_y=False
    )

    # 標註最高價和最低價
    max_price = stock_data['Close'].max()
    min_price = stock_data['Close'].min()
    max_date = stock_data['Close'].idxmax()
    min_date = stock_data['Close'].idxmin()

    fig.add_annotation(
        x=max_date,
        y=max_price,
        text=f"High: {max_price:.2f}",
        showarrow=True,
        arrowhead=2,
        arrowcolor='#2E86AB',
        ax=40,
        ay=-40,
        bgcolor='yellow',
        opacity=0.8,
        bordercolor='#2E86AB',
        borderwidth=2,
        font=dict(size=11, color='black'),
        yref='y'
    )

    fig.add_annotation(
        x=min_date,
        y=min_price,
        text=f"Low: {min_price:.2f}",
        showarrow=True,
        arrowhead=2,
        arrowcolor='#2E86AB',
        ax=40,
        ay=40,
        bgcolor='lightblue',
        opacity=0.8,
        bordercolor='#2E86AB',
        borderwidth=2,
        font=dict(size=11, color='black'),
        yref='y'
    )

    # === 添加股息率數據（右側Y軸）===
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['DIVIDEND YIELD'],
            mode='lines',
            name=f'Dividend Yield ({dividend_year} data)',
            line=dict(color='#F18F01', width=3, dash='2,2'),
            fill='tozeroy',
            fillcolor='rgba(241, 143, 1, 0.2)',
            hovertemplate='<b>Date</b>: %{x|%Y-%m-%d}<br>' +
                         '<b>Dividend Yield</b>: %{y:.2f}%<br>' +
                         '<extra></extra>'
        ),
        secondary_y=True
    )

    # 添加平均股息率線
    if annual_dividend > 0:
        avg_yield = stock_data['DIVIDEND YIELD'].mean()
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=[avg_yield] * len(stock_data.index),
                mode='lines',
                name=f'Avg Yield: {avg_yield:.2f}%',
                line=dict(color='red', width=2.5, dash='dot'),
                hovertemplate='<b>Average Yield</b>: %{y:.2f}%<br>' +
                             '<extra></extra>'
            ),
            secondary_y=True
        )

    # === 計算右軸的動態範圍 ===
    dividend_yield_data = stock_data['DIVIDEND YIELD']
    min_yield = dividend_yield_data.min()
    max_yield = dividend_yield_data.max()
    yield_range = max_yield - min_yield
    margin = yield_range * 0.1

    y_axis_min = max(0, min_yield - margin)
    y_axis_max = max_yield + margin

    if min_yield > 2.0:
        y_axis_min = 2.0

    # ✅ 修正：移除寬度設定，讓 Streamlit 自動調整
    fig.update_layout(
        title={
            "text": f'{ticker_symbol} Stock Price & Dividend Yield Analysis<br>({start_date} to {end_date})',
            "font": {"size": 18, "color": "black"},
            "x": 0.5,
            "xanchor": "center"
        },
        xaxis={
            "title": "Date",
            "title_font": {"size": 14, "color": "black"},
            "showgrid": True,
            "gridcolor": "rgba(128, 128, 128, 0.2)",
            "gridwidth": 1
        },
        hovermode='x unified',
        plot_bgcolor='white',
        height=700,
        # ❌ 移除 width=1400，Streamlit 會自動處理
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.08,
            "xanchor": "right",
            "x": 0.85,
            "bgcolor": "rgba(255, 255, 255, 0.8)",
            "bordercolor": "gray",
            "borderwidth": 1
        },
        margin=dict(t=200 ) # 🔑 增加上下距離
    )

    # 更新 Y 軸配置
    fig.update_yaxes(
        title_text="Stock Price",
        title_font={"size": 14, "color": "#2E86AB"},
        tickfont={"color": "#2E86AB"},
        showgrid=True,
        gridcolor='rgba(128, 128, 128, 0.2)',
        secondary_y=False
    )

    fig.update_yaxes(
        title_text="Dividend Yield (%)",
        title_font={"size": 14, "color": "#F18F01"},
        tickfont={"color": "#F18F01"},
        secondary_y=True,
        range=[y_axis_min, y_axis_max]
    )

    # ❌ 移除 fig.show()，Streamlit 會在 st.plotly_chart() 中處理
    # 保存為 HTML 文件（可選）
    date_range = f"{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}"
    html_filename = f'{ticker_symbol}_interactive_chart_{date_range}.html'
    try:
        fig.write_html(html_filename)
        print(f"✅ Interactive chart saved to: {html_filename}")
    except Exception as e:
        print(f"⚠️ Could not save HTML file: {e}")

    return fig  # ✅ 返回圖表物件而不是顯示它


def fetch_and_analyze(ticker_symbol, start_date, end_date):
    """獲取數據並進行分析"""
    
    with st.spinner(f"⏳ 正在獲取 {ticker_symbol} 的數據..."):
        try:
            # 下載股價數據
            ticker = yf.Ticker(ticker_symbol)
            dividends = ticker.dividends

            # 確定使用哪一年的股息數據
            current_year = end_date.year
            previous_year = current_year - 1

            current_year_dividends = dividends[dividends.index.year == current_year]
            current_annual_dividend = current_year_dividends.sum() if not current_year_dividends.empty else 0.0

            if current_annual_dividend > 0:
                annual_dividend = current_annual_dividend
                dividend_year = current_year
            else:
                previous_year_dividends = dividends[dividends.index.year == previous_year]
                annual_dividend = previous_year_dividends.sum() if not previous_year_dividends.empty else 0.0
                dividend_year = previous_year

            # 下載股價歷史數據
            stock_data = yf.download(ticker_symbol, start=start_date, end=end_date, progress=False)

            if stock_data.empty:
                st.error(f"❌ 未能獲取 {ticker_symbol} 的數據")
                return None

            # 處理多層索引
            if isinstance(stock_data.columns, pd.MultiIndex):
                stock_data.columns = stock_data.columns.droplevel(1)

            # 計算股息率
            stock_data['DIVIDEND YIELD'] = (annual_dividend / stock_data['Close']) * 100

            return stock_data, ticker_symbol, start_date, end_date, annual_dividend, dividend_year

        except Exception as e:
            st.error(f"❌ 發生錯誤: {e}")
            return None

# ============ 主程式邏輯 ============

# 初始化會話狀態
if 'last_result' not in st.session_state:
    st.session_state.last_result = None

# 執行分析
if execute_button or st.session_state.last_result is None:
    result = fetch_and_analyze(ticker_input, start_date, end_date)
    if result:
        st.session_state.last_result = result

# 顯示結果
if st.session_state.last_result:
    stock_data, ticker_symbol, start_date, end_date, annual_dividend, dividend_year = st.session_state.last_result

    # 顯示統計信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("當前股價", f"${stock_data['Close'].iloc[-1]:.2f}")
    
    with col2:
        st.metric("期間最高價", f"${stock_data['Close'].max():.2f}")
    
    with col3:
        st.metric("期間最低價", f"${stock_data['Close'].min():.2f}")
    
    with col4:
        avg_yield = stock_data['DIVIDEND YIELD'].mean()
        st.metric("平均股息率", f"{avg_yield:.2f}%")

    # 顯示圖表
    st.subheader("📊 股價與股息率圖表")
    fig = plot_stock_charts(stock_data, ticker_symbol, start_date, end_date, annual_dividend, dividend_year)
    st.plotly_chart(fig, use_container_width=True)

    # 顯示數據表格
    st.subheader("📋 詳細數據")
    display_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'DIVIDEND YIELD']
    st.dataframe(
        stock_data[display_columns].round(4),
        use_container_width=True,
        height=400
    )

    # 下載按鈕
    csv = stock_data[display_columns].to_csv(index=True)
    st.download_button(
        label="💾 下載 CSV",
        data=csv,
        file_name=f"{ticker_symbol}_stock_data_{start_date}_{end_date}.csv",
        mime="text/csv"
    )














