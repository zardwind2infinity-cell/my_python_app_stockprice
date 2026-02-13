import yfinance as yf
import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def is_date_format(input_str):
    """檢查輸入是否為日期格式"""
    try:
        datetime.datetime.strptime(input_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def is_number(input_str):
    """檢查輸入是否為數字"""
    try:
        int(input_str)
        return True
    except ValueError:
        return False

def get_ticker_symbol():
    """獲取用戶輸入的股票代碼"""
    while True:
        ticker_input = input("\n🔍 請輸入股票代碼 (例如: 2800.HK, AAPL, 0700.HK): ").strip().upper()
        
        if not ticker_input:
            print("❌ 股票代碼不能為空！請重新輸入")
            continue
        
        # 驗證股票代碼格式（基本檢查）
        if len(ticker_input) < 1 or len(ticker_input) > 10:
            print("❌ 股票代碼長度錯誤！請輸入有效的股票代碼")
            continue
        
        print(f"✓ 已選擇股票代碼: {ticker_input}")
        return ticker_input

def get_date_input(prompt, default_date=None):
    """獲取用戶輸入的日期，包含輸入驗證"""
    while True:
        try:
            if default_date:
                user_input = input(f"{prompt} (格式: YYYY-MM-DD，直接按 Enter 使用預設 {default_date}): ").strip()
                if not user_input:
                    return default_date
            else:
                user_input = input(f"{prompt} (格式: YYYY-MM-DD): ").strip()
            
            # 解析日期
            date_obj = datetime.datetime.strptime(user_input, "%Y-%m-%d").date()
            return date_obj
            
        except ValueError:
            print("❌ 日期格式錯誤！請使用 YYYY-MM-DD 格式 (例如: 2024-01-01)")

def get_time_range():
    """獲取時間範圍設定"""
    print("📅 時間範圍設定")
    print("💡 您可以輸入：")
    print("   • 天數 (例如: 30, 90, 365) - 從今天往前推算")
    print("   • 開始日期 (例如: 2024-01-01) - 然後會詢問結束日期")
    
    while True:
        user_input = input("\n請輸入天數或開始日期: ").strip()
        
        if not user_input:
            print("❌ 請輸入有效的天數或日期！")
            continue
        
        # 檢查是否為日期格式
        if is_date_format(user_input):
            print("✓ 偵測到日期格式，進入日期範圍模式...")
            
            try:
                start_date = datetime.datetime.strptime(user_input, "%Y-%m-%d").date()
                
                # 獲取結束日期（預設為今天）
                today = datetime.date.today()
                end_date = get_date_input("請輸入結束日期", today)
                
                # 驗證日期範圍
                if start_date >= end_date:
                    print("❌ 開始日期必須早於結束日期！請重新輸入...")
                    continue
                
                # 檢查是否為未來日期
                if end_date > today:
                    print("⚠️  結束日期為未來日期，將使用今天作為結束日期")
                    end_date = today
                
                days_diff = (end_date - start_date).days
                print(f"\n✓ 日期範圍設定完成！")
                print(f"查詢期間：{start_date} 到 {end_date} ({days_diff} 天)")
                
                return start_date, end_date
                
            except ValueError:
                print("❌ 日期格式錯誤！請使用 YYYY-MM-DD 格式")
                continue
        
        # 檢查是否為數字（天數）
        elif is_number(user_input):
            print("✓ 偵測到天數格式，進入天數模式...")
            
            try:
                days = int(user_input)
                
                if days <= 0:
                    print("❌ 天數必須是正整數！請重新輸入...")
                    continue
                elif days > 3650:  # 約10年限制
                    print("❌ 天數不能超過 3650 天（約10年）！請重新輸入...")
                    continue
                
                # 計算日期範圍
                end_date = datetime.date.today()
                start_date = end_date - datetime.timedelta(days=days)
                
                print(f"\n✓ 天數範圍設定完成！")
                print(f"查詢期間：{start_date} 到 {end_date} ({days} 天)")
                
                return start_date, end_date
                
            except ValueError:
                print("❌ 請輸入有效的數字！")
                continue
        
        else:
            print("❌ 輸入格式錯誤！")
            print("請輸入：")
            print("   • 天數 (例如: 90)")
            print("   • 日期 (例如: 2024-01-01)")

def plot_stock_charts(stock_data, ticker_symbol, start_date, end_date, annual_dividend, dividend_year):
    """繪製互動式股價和股息率圖表（使用 Plotly）"""
    
    # 創建雙Y軸圖表
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # === 添加股價數據（左側Y軸）===
    # 高低區間（填充）
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
            line=dict(color='#F18F01', width=3, dash='dash'),
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
    # 獲取股息率的最小和最大值
    dividend_yield_data = stock_data['DIVIDEND YIELD']
    min_yield = dividend_yield_data.min()
    max_yield = dividend_yield_data.max()
    
    # 計算範圍和邊距
    yield_range = max_yield - min_yield
    margin = yield_range * 0.1  # 上下各留 10% 的空間
    
    # 設置右軸範圍，確保不會顯示過低的數值
    y_axis_min = max(0, min_yield - margin)  # 不低於 0
    y_axis_max = max_yield + margin
    
    # 如果最小值大於 2%，則將下限設為 2%，否則自動調整
    if min_yield > 2.0:
        y_axis_min = 2.0
    
    print(f"\n📊 股息率範圍: {min_yield:.2f}% - {max_yield:.2f}%")
    print(f"📊 右軸顯示範圍: {y_axis_min:.2f}% - {y_axis_max:.2f}%")
    
    # 設定圖表標題和軸標籤
    fig.update_layout(
        title=dict(
            text=f'{ticker_symbol} Stock Price & Dividend Yield Analysis<br>({start_date} to {end_date})',
            font=dict(size=18, color='black'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='Date',
            titlefont=dict(size=14, color='black'),
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.2)',
            gridwidth=1
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        height=700,
        width=1400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='gray',
            borderwidth=1
        )
    )
    
    # 設定左側Y軸（股價）
    fig.update_yaxes(
        title_text="Stock Price",
        titlefont=dict(size=14, color='#2E86AB'),
        tickfont=dict(color='#2E86AB'),
        showgrid=True,
        gridcolor='rgba(128, 128, 128, 0.2)',
        secondary_y=False
    )
    
    # 設定右側Y軸（股息率）- 使用動態範圍
    fig.update_yaxes(
        title_text="Dividend Yield (%)",
        titlefont=dict(size=14, color='#F18F01'),
        tickfont=dict(color='#F18F01'),
        secondary_y=True,
        range=[y_axis_min, y_axis_max]  # 設置動態範圍
    )
    
    # 保存為 HTML 文件
    date_range = f"{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}"
    html_filename = f'{ticker_symbol}_interactive_chart_{date_range}.html'
    fig.write_html(html_filename)
    print(f"\n📊 Interactive chart saved to: {html_filename}")
    print(f"💡 Open the file in your browser to interact with the chart!")
    
    # 顯示圖表
    fig.show()





# 主程式
if __name__ == "__main__":
    # 獲取用戶輸入的股票代碼
    ticker_symbol = get_ticker_symbol()

    # 獲取時間範圍
    start_date, end_date = get_time_range()

    # 計算天數差異
    days_diff = (end_date - start_date).days
    print(f"\n正在獲取 {ticker_symbol} 從 {start_date} 到 {end_date} 的股價數據...")
    print(f"📊 分析期間：{days_diff} 天")

    try:
        # 創建 Ticker 物件以獲取股息數據
        ticker = yf.Ticker(ticker_symbol)
        
        # 獲取整個歷史股息記錄
        dividends = ticker.dividends
        
        # 找出當前年份和前一年
        current_year = end_date.year
        previous_year = current_year - 1
        
        # 篩選當年股息並計算總額
        current_year_dividends = dividends[dividends.index.year == current_year]
        current_annual_dividend = current_year_dividends.sum() if not current_year_dividends.empty else 0.0
        
        # 決定使用哪一年的股息數據
        if current_annual_dividend > 0:
            # 使用當年股息數據
            annual_dividend = current_annual_dividend
            dividend_year = current_year
            print(f"\n✓ 使用當年 ({current_year}) 股息數據: {annual_dividend:.4f}/股")
        else:
            # 使用前一年股息數據作為參考
            previous_year_dividends = dividends[dividends.index.year == previous_year]
            annual_dividend = previous_year_dividends.sum() if not previous_year_dividends.empty else 0.0
            dividend_year = previous_year
            
            if annual_dividend > 0:
                print(f"\n⚠ 當年 ({current_year}) 無完整股息數據，使用前一年 ({previous_year}) 數據作為參考")
                print(f"參考股息: {annual_dividend:.4f}/股")
            else:
                print(f"\n❌ 當年 ({current_year}) 和前一年 ({previous_year}) 均無股息數據")
                print("股息率將設為 0%")
        
        # 顯示股息歷史記錄（最近3年，供參考）
        if not dividends.empty:
            recent_dividends = dividends[dividends.index.year >= current_year - 2]
            if not recent_dividends.empty:
                print(f"\n📊 最近3年股息歷史記錄：")
                for date, dividend in recent_dividends.items():
                    print(f"   {date.strftime('%Y-%m-%d')}: {dividend:.4f}/股")

        # 下載股價歷史數據
        stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)
        
        # 檢查是否獲取到數據
        if not stock_data.empty:
            # 處理多層索引（如果存在）
            if isinstance(stock_data.columns, pd.MultiIndex):
                stock_data.columns = stock_data.columns.droplevel(1)
            
            # 計算股息率：(年度股息 / CLOSE) * 100
            stock_data['DIVIDEND YIELD'] = (annual_dividend / stock_data['Close']) * 100
            
            # 添加股息數據來源資訊到列名（供參考）
            dividend_source_note = f"(基於{dividend_year}年數據)" if annual_dividend > 0 else "(無股息數據)"
            
            print(f"\n📈 指定期間股價數據 ({ticker_symbol})，包含股息率 {dividend_source_note}:")
            # 顯示主要欄位，包括新增加的 DIVIDEND YIELD
            display_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'DIVIDEND YIELD']
            formatted_data = stock_data[display_columns].round(4)  # 四捨五入以提高可讀性
            print(formatted_data.head(10))  # 只顯示前10行
            print("...")
            print(formatted_data.tail(10))  # 顯示最後10行
            
            # 計算平均股息率（供參考）
            if annual_dividend > 0:
                avg_yield = stock_data['DIVIDEND YIELD'].mean()
                print(f"\n📊 平均股息率: {avg_yield:.2f}% (基於指定期間平均收盤價)")
            
            # 繪製圖表
            print("\n📊 Generating charts...")
            plot_stock_charts(stock_data, ticker_symbol, start_date, end_date, 
                            annual_dividend, dividend_year)
            
            # 可選：儲存到 CSV 檔案
            date_range = f"{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}"
            output_filename = f'{ticker_symbol}_stock_with_yield_{date_range}_{dividend_year}dividend.csv'
            stock_data.to_csv(output_filename)
            print(f"\n💾 數據已儲存至 {output_filename}")
            
        else:
            print(f"❌ 未能獲取 {ticker_symbol} 在指定期間的股價數據。請檢查日期範圍、股票代碼或網路連線。")

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        print("可能原因：網路問題、股票代碼錯誤、日期範圍問題，或 yfinance API 變更。")
