import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv
from collections import defaultdict
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 載入 .env 檔案
load_dotenv()

# 從環境變數讀取 API Key
API_KEY = os.getenv("CWA_API_KEY")

st.set_page_config(
    page_title="台北天氣查詢系統",
    page_icon="🌤️",
    layout="wide"
)

# 初始化 session state
if 'start_date' not in st.session_state:
    st.session_state.start_date = datetime.now().date()
if 'end_date' not in st.session_state:
    st.session_state.end_date = datetime.now().date() + timedelta(days=6)
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None
if 'hourly_data' not in st.session_state:
    st.session_state.hourly_data = None
if 'selected_day' not in st.session_state:
    st.session_state.selected_day = None

def get_taipei_weather():
    """獲取台北天氣資料"""
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-089"

    params = {
        "Authorization": API_KEY,
        "locationName": "臺北市",
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if data.get("success") == "true":
            return data
        else:
            return None
    except Exception as e:
        st.error(f"獲取天氣資料時發生錯誤: {e}")
        return None

def parse_hourly_weather_data(weather_data, start_date, end_date):
    """解析每小時詳細天氣資料"""
    try:
        records = weather_data['records']
        locations_list = records['Locations'][0]
        location_data = locations_list['Location']

        taipei_location = None
        for loc in location_data:
            if loc['LocationName'] == '臺北市':
                taipei_location = loc
                break

        if not taipei_location:
            return None

        weather_elements = taipei_location['WeatherElement']

        # 建立資料字典
        elements_dict = {}
        for element in weather_elements:
            element_name = element['ElementName']
            elements_dict[element_name] = element['Time']

        # 按日期和時間整理資料
        hourly_data = defaultdict(lambda: defaultdict(lambda: {
            '溫度': None,
            '降雨機率': None,
            '相對濕度': None,
            '天氣': None,
            '風速': None,
            '風向': None,
            '時間': None
        }))

        # 處理溫度資料（每小時）
        if '溫度' in elements_dict:
            for time_data in elements_dict['溫度']:
                dt = datetime.fromisoformat(time_data['DataTime'].replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                hour_key = dt.strftime("%H:%M")
                temp = time_data['ElementValue'][0]['Temperature']
                hourly_data[date_key][hour_key]['溫度'] = int(temp)
                hourly_data[date_key][hour_key]['時間'] = dt

        # 處理降雨機率（每3小時）
        if '3小時降雨機率' in elements_dict:
            for time_data in elements_dict['3小時降雨機率']:
                dt = datetime.fromisoformat(time_data['StartTime'].replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                hour_key = dt.strftime("%H:%M")
                pop = time_data['ElementValue'][0]['ProbabilityOfPrecipitation']
                hourly_data[date_key][hour_key]['降雨機率'] = int(pop)

        # 處理相對濕度（每小時）
        if '相對濕度' in elements_dict:
            for time_data in elements_dict['相對濕度']:
                dt = datetime.fromisoformat(time_data['DataTime'].replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                hour_key = dt.strftime("%H:%M")
                rh = time_data['ElementValue'][0]['RelativeHumidity']
                hourly_data[date_key][hour_key]['相對濕度'] = int(rh)

        # 處理天氣現象
        if '天氣現象' in elements_dict:
            for time_data in elements_dict['天氣現象']:
                dt = datetime.fromisoformat(time_data.get('StartTime', time_data.get('DataTime', '')).replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                hour_key = dt.strftime("%H:%M")
                weather = time_data['ElementValue'][0]['Weather']
                hourly_data[date_key][hour_key]['天氣'] = weather

        # 處理風速
        if '風速' in elements_dict:
            for time_data in elements_dict['風速']:
                dt = datetime.fromisoformat(time_data.get('StartTime', time_data.get('DataTime', '')).replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                hour_key = dt.strftime("%H:%M")
                ws = time_data['ElementValue'][0]['WindSpeed']
                try:
                    hourly_data[date_key][hour_key]['風速'] = float(ws)
                except:
                    pass

        # 處理風向
        if '風向' in elements_dict:
            for time_data in elements_dict['風向']:
                dt = datetime.fromisoformat(time_data.get('StartTime', time_data.get('DataTime', '')).replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                hour_key = dt.strftime("%H:%M")
                wd = time_data['ElementValue'][0]['WindDirection']
                hourly_data[date_key][hour_key]['風向'] = wd

        return hourly_data

    except Exception as e:
        st.error(f"解析每小時天氣資料時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_weather_data(weather_data, start_date, end_date):
    """解析天氣資料並根據日期範圍過濾"""
    try:
        records = weather_data['records']
        locations_list = records['Locations'][0]
        location_data = locations_list['Location']

        taipei_location = None
        for loc in location_data:
            if loc['LocationName'] == '臺北市':
                taipei_location = loc
                break

        if not taipei_location:
            return None

        weather_elements = taipei_location['WeatherElement']

        # 建立資料字典
        elements_dict = {}
        for element in weather_elements:
            element_name = element['ElementName']
            elements_dict[element_name] = element['Time']

        # 按日期整理資料
        daily_data = defaultdict(lambda: {
            '溫度': [],
            '溫度時間': [],
            '降雨機率': [],
            '相對濕度': [],
            '天氣': [],
            '風速': [],
            '風向': []
        })

        # 處理溫度資料
        if '溫度' in elements_dict:
            for time_data in elements_dict['溫度']:
                dt = datetime.fromisoformat(time_data['DataTime'].replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                temp = time_data['ElementValue'][0]['Temperature']
                daily_data[date_key]['溫度'].append(int(temp))
                daily_data[date_key]['溫度時間'].append(dt)

        # 處理降雨機率
        if '3小時降雨機率' in elements_dict:
            for time_data in elements_dict['3小時降雨機率']:
                dt = datetime.fromisoformat(time_data['StartTime'].replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                pop = time_data['ElementValue'][0]['ProbabilityOfPrecipitation']
                daily_data[date_key]['降雨機率'].append(int(pop))

        # 處理相對濕度
        if '相對濕度' in elements_dict:
            for time_data in elements_dict['相對濕度']:
                dt = datetime.fromisoformat(time_data['DataTime'].replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                rh = time_data['ElementValue'][0]['RelativeHumidity']
                daily_data[date_key]['相對濕度'].append(int(rh))

        # 處理天氣現象
        if '天氣現象' in elements_dict:
            for time_data in elements_dict['天氣現象']:
                dt = datetime.fromisoformat(time_data.get('StartTime', time_data.get('DataTime', '')).replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                weather = time_data['ElementValue'][0]['Weather']
                daily_data[date_key]['天氣'].append(weather)

        # 處理風速
        if '風速' in elements_dict:
            for time_data in elements_dict['風速']:
                dt = datetime.fromisoformat(time_data.get('StartTime', time_data.get('DataTime', '')).replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                ws = time_data['ElementValue'][0]['WindSpeed']
                try:
                    daily_data[date_key]['風速'].append(float(ws))
                except:
                    pass

        # 處理風向
        if '風向' in elements_dict:
            for time_data in elements_dict['風向']:
                dt = datetime.fromisoformat(time_data.get('StartTime', time_data.get('DataTime', '')).replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                wd = time_data['ElementValue'][0]['WindDirection']
                daily_data[date_key]['風向'].append(wd)

        # 生成每日摘要
        daily_summary = []
        weekday_map = {
            'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三',
            'Thursday': '星期四', 'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期日'
        }

        # 根據日期範圍過濾
        for date_key in sorted(daily_data.keys()):
            day_date = datetime.strptime(date_key, "%Y-%m-%d").date()

            # 只包含在選定日期範圍內的資料
            if start_date <= day_date <= end_date:
                day = daily_data[date_key]
                dt = datetime.strptime(date_key, "%Y-%m-%d")

                # 找出最低溫和最高溫的時間點
                min_temp = min(day['溫度']) if day['溫度'] else None
                max_temp = max(day['溫度']) if day['溫度'] else None

                min_temp_time = None
                max_temp_time = None
                if min_temp is not None and day['溫度']:
                    min_idx = day['溫度'].index(min_temp)
                    min_temp_time = day['溫度時間'][min_idx].strftime("%H:%M") if min_idx < len(day['溫度時間']) else None
                if max_temp is not None and day['溫度']:
                    max_idx = day['溫度'].index(max_temp)
                    max_temp_time = day['溫度時間'][max_idx].strftime("%H:%M") if max_idx < len(day['溫度時間']) else None

                max_rain = max(day['降雨機率']) if day['降雨機率'] else 0
                avg_humidity = sum(day['相對濕度']) // len(day['相對濕度']) if day['相對濕度'] else "無資料"
                weather_desc = max(set(day['天氣']), key=day['天氣'].count) if day['天氣'] else "無資料"
                max_wind = f"{max(day['風速']):.1f}" if day['風速'] else "無資料"
                wind_dir = max(set(day['風向']), key=day['風向'].count) if day['風向'] else "無資料"

                daily_summary.append({
                    '日期': date_key,
                    '星期': weekday_map.get(dt.strftime("%A"), dt.strftime("%A")),
                    '天氣狀況': weather_desc,
                    '降雨機率(%)': max_rain,
                    '最低溫度(°C)': min_temp if min_temp is not None else "無資料",
                    '最低溫時間': min_temp_time,
                    '最高溫度(°C)': max_temp if max_temp is not None else "無資料",
                    '最高溫時間': max_temp_time,
                    '平均濕度(%)': avg_humidity,
                    '最大風速(m/s)': max_wind,
                    '風向': wind_dir,
                    '溫度列表': day['溫度'],
                    '溫度時間列表': day['溫度時間']
                })

        return daily_summary

    except Exception as e:
        st.error(f"解析天氣資料時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_temperature_chart(weather_summary):
    """建立溫度曲線圖"""
    dates = [day['日期'] for day in weather_summary]
    min_temps = [day['最低溫度(°C)'] if day['最低溫度(°C)'] != "無資料" else None for day in weather_summary]
    max_temps = [day['最高溫度(°C)'] if day['最高溫度(°C)'] != "無資料" else None for day in weather_summary]
    weather_desc = [day['天氣狀況'] for day in weather_summary]
    min_times = [day['最低溫時間'] for day in weather_summary]
    max_times = [day['最高溫時間'] for day in weather_summary]

    fig = go.Figure()

    # 最高溫曲線
    fig.add_trace(go.Scatter(
        x=dates,
        y=max_temps,
        mode='lines+markers+text',
        name='最高溫',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=10),
        text=[f"{temp}°C<br>{time}" if temp is not None and time else ""
              for temp, time in zip(max_temps, max_times)],
        textposition="top center",
        textfont=dict(size=11, color='#FF6B6B'),
        hovertemplate='<b>日期:</b> %{x}<br><b>最高溫:</b> %{y}°C<extra></extra>'
    ))

    # 最低溫曲線
    fig.add_trace(go.Scatter(
        x=dates,
        y=min_temps,
        mode='lines+markers+text',
        name='最低溫',
        line=dict(color='#4ECDC4', width=3),
        marker=dict(size=10),
        text=[f"{temp}°C<br>{time}" if temp is not None and time else ""
              for temp, time in zip(min_temps, min_times)],
        textposition="bottom center",
        textfont=dict(size=11, color='#4ECDC4'),
        hovertemplate='<b>日期:</b> %{x}<br><b>最低溫:</b> %{y}°C<extra></extra>'
    ))

    # 添加天氣圖標/文字在 x 軸下方
    for date, weather in zip(dates, weather_desc):
        fig.add_annotation(
            x=date,
            y=min(min_temps) - 2 if min_temps and min(min_temps) is not None else 0,
            text=weather,
            showarrow=False,
            font=dict(size=10, color='gray'),
            xanchor='center'
        )

    fig.update_layout(
        title="📈 一週溫度變化趨勢",
        xaxis_title="日期",
        yaxis_title="溫度 (°C)",
        hovermode='x unified',
        template="plotly_white",
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

def create_hourly_chart(hourly_data_for_day, date_str):
    """建立單日每小時天氣變化圖"""
    if not hourly_data_for_day:
        return None

    # 整理資料
    hours = sorted(hourly_data_for_day.keys())
    temps = [hourly_data_for_day[h]['溫度'] for h in hours]
    rain_probs = [hourly_data_for_day[h]['降雨機率'] for h in hours]
    humidity = [hourly_data_for_day[h]['相對濕度'] for h in hours]

    # 建立子圖
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('溫度變化', '降雨機率', '相對濕度'),
        vertical_spacing=0.12,
        row_heights=[0.33, 0.33, 0.33]
    )

    # 溫度曲線
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=temps,
            mode='lines+markers',
            name='溫度',
            line=dict(color='#FF6B6B', width=2),
            marker=dict(size=6),
            hovertemplate='<b>時間:</b> %{x}<br><b>溫度:</b> %{y}°C<extra></extra>'
        ),
        row=1, col=1
    )

    # 降雨機率曲線
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=rain_probs,
            mode='lines+markers',
            name='降雨機率',
            line=dict(color='#4ECDC4', width=2),
            marker=dict(size=6),
            fill='tozeroy',
            hovertemplate='<b>時間:</b> %{x}<br><b>降雨機率:</b> %{y}%<extra></extra>'
        ),
        row=2, col=1
    )

    # 相對濕度曲線
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=humidity,
            mode='lines+markers',
            name='相對濕度',
            line=dict(color='#95E1D3', width=2),
            marker=dict(size=6),
            fill='tozeroy',
            hovertemplate='<b>時間:</b> %{x}<br><b>相對濕度:</b> %{y}%<extra></extra>'
        ),
        row=3, col=1
    )

    fig.update_yaxes(title_text="溫度 (°C)", row=1, col=1)
    fig.update_yaxes(title_text="降雨機率 (%)", row=2, col=1)
    fig.update_yaxes(title_text="相對濕度 (%)", row=3, col=1)
    fig.update_xaxes(title_text="時間", row=3, col=1)

    fig.update_layout(
        title_text=f"📊 {date_str} 每小時天氣變化",
        height=900,
        showlegend=False,
        template="plotly_white"
    )

    return fig

# 自訂 CSS 樣式
st.markdown("""
    <style>
    .date-button {
        padding: 15px;
        margin: 5px;
        border-radius: 10px;
        border: 2px solid #ddd;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
    }
    .date-button:hover {
        border-color: #4ECDC4;
        background-color: #f0f0f0;
    }
    </style>
""", unsafe_allow_html=True)

# 標題
st.title("🌤️ 台北天氣查詢系統")
st.markdown("---")

# 側邊欄 - 日期選擇
st.sidebar.header("📅 選擇日期範圍")
st.sidebar.info("選擇開始日期後，結束日期會自動設定為 7 天後")

# 開始日期選擇器
start_date = st.sidebar.date_input(
    "開始日期",
    value=st.session_state.start_date,
    format="YYYY/MM/DD",
    key="start_date_input"
)

# 當開始日期改變時，自動設定結束日期為 7 天後
if start_date != st.session_state.start_date:
    st.session_state.start_date = start_date
    st.session_state.end_date = start_date + timedelta(days=6)
    st.rerun()

# 結束日期（自動設定，但可調整）
end_date = st.sidebar.date_input(
    "結束日期",
    value=st.session_state.end_date,
    min_value=start_date,
    max_value=start_date + timedelta(days=6),
    format="YYYY/MM/DD",
    key="end_date_input"
)

if end_date != st.session_state.end_date:
    st.session_state.end_date = end_date

# 顯示日期範圍資訊
date_diff = (end_date - start_date).days
st.sidebar.success(f"✅ 已選擇 {date_diff + 1} 天的天氣資料")

# 顯示選定的日期範圍
st.sidebar.markdown("### 選定日期範圍")
st.sidebar.info(f"{start_date.strftime('%Y/%m/%d')} 至 {end_date.strftime('%Y/%m/%d')}")

# 查詢按鈕
query_button = st.sidebar.button("🔍 查詢天氣", type="primary", use_container_width=True)

# 主要內容區域
if query_button or st.session_state.weather_data is not None:
    if not API_KEY:
        st.error("❌ 找不到 API Key，請確認 .env 檔案中是否設定了 CWA_API_KEY")
    else:
        if query_button:
            with st.spinner("正在獲取天氣資料..."):
                raw_data = get_taipei_weather()
                if raw_data:
                    st.session_state.weather_data = parse_weather_data(raw_data, start_date, end_date)
                    st.session_state.hourly_data = parse_hourly_weather_data(raw_data, start_date, end_date)
                    st.session_state.selected_day = None

        weather_summary = st.session_state.weather_data

        if weather_summary:
            st.success(f"✅ 成功獲取 {start_date.strftime('%Y/%m/%d')} 至 {end_date.strftime('%Y/%m/%d')} 的天氣資料")

            # 溫度曲線圖
            st.subheader("📈 溫度變化趨勢")
            temp_chart = create_temperature_chart(weather_summary)
            st.plotly_chart(temp_chart, use_container_width=True)

            # 顯示天氣資料表格
            st.subheader("📊 天氣資料總覽")
            df = pd.DataFrame(weather_summary)
            display_df = df[['日期', '星期', '天氣狀況', '降雨機率(%)',
                            '最低溫度(°C)', '最低溫時間', '最高溫度(°C)', '最高溫時間',
                            '平均濕度(%)', '最大風速(m/s)', '風向']]

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

            # 可點擊的日期選項
            st.subheader("🗓️ 點擊日期查看每小時詳細資料")

            cols = st.columns(min(len(weather_summary), 7))
            for idx, day in enumerate(weather_summary):
                with cols[idx % 7]:
                    if st.button(
                        f"{day['日期']}\n{day['星期']}\n{day['天氣狀況']}",
                        key=f"day_btn_{idx}",
                        use_container_width=True
                    ):
                        st.session_state.selected_day = day['日期']
                        st.rerun()

            # 顯示選定日期的每小時詳細資料
            if st.session_state.selected_day and st.session_state.hourly_data:
                selected_date = st.session_state.selected_day
                st.markdown("---")
                st.subheader(f"🕐 {selected_date} 每小時詳細天氣")

                hourly_data_for_day = st.session_state.hourly_data.get(selected_date, {})

                if hourly_data_for_day:
                    # 顯示每小時曲線圖
                    hourly_chart = create_hourly_chart(hourly_data_for_day, selected_date)
                    if hourly_chart:
                        st.plotly_chart(hourly_chart, use_container_width=True)

                    # 顯示每小時資料表格
                    hourly_list = []
                    for hour in sorted(hourly_data_for_day.keys()):
                        data = hourly_data_for_day[hour]
                        hourly_list.append({
                            '時間': hour,
                            '天氣': data['天氣'] or '無資料',
                            '溫度(°C)': data['溫度'] if data['溫度'] is not None else '無資料',
                            '降雨機率(%)': data['降雨機率'] if data['降雨機率'] is not None else '無資料',
                            '相對濕度(%)': data['相對濕度'] if data['相對濕度'] is not None else '無資料',
                            '風速(m/s)': f"{data['風速']:.1f}" if data['風速'] is not None else '無資料',
                            '風向': data['風向'] or '無資料'
                        })

                    hourly_df = pd.DataFrame(hourly_list)
                    st.dataframe(hourly_df, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"⚠️ 沒有 {selected_date} 的每小時資料")

            # 下載 CSV
            st.markdown("---")
            st.subheader("💾 下載資料")
            csv = display_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下載 CSV 檔案",
                data=csv,
                file_name=f"台北天氣_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.error("❌ 無法獲取天氣資料，請檢查：\n1. 網路連線是否正常\n2. API Key 是否有效\n3. 中央氣象署服務是否正常")
else:
    # 初始說明
    st.info("👈 請在左側選擇日期範圍，然後點擊「查詢天氣」按鈕")

    st.markdown("""
    ### 使用說明

    1. 在左側邊欄選擇 **開始日期**，結束日期會自動設定為 7 天後
    2. 可手動調整結束日期（限定 7 天以內）
    3. 點擊 **「🔍 查詢天氣」** 按鈕
    4. 查看溫度變化趨勢圖（標註最高/最低溫時間和天氣狀況）
    5. 點擊任一日期按鈕，查看該日每小時詳細天氣變化
    6. 可下載 CSV 檔案保存資料

    ### 功能特色
    - 📅 自動計算 7 天日期範圍
    - 📈 互動式溫度趨勢圖
    - 🕐 每日每小時詳細資料展開
    - 📊 多維度天氣資料視覺化

    ### 資料來源
    - 中央氣象署開放資料平台
    - 資料更新頻率：即時
    """)

# 頁尾
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>台北天氣查詢系統 | 資料來源：中央氣象署</div>",
    unsafe_allow_html=True
)
