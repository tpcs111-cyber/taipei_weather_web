import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# 從環境變數讀取 API Key
API_KEY = os.getenv("CWA_API_KEY")

st.set_page_config(
    page_title="台北天氣查詢系統",
    page_icon="🌤️",
    layout="wide"
)

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
        from collections import defaultdict
        daily_data = defaultdict(lambda: {
            '溫度': [],
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

                min_temp = min(day['溫度']) if day['溫度'] else "無資料"
                max_temp = max(day['溫度']) if day['溫度'] else "無資料"
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
                    '最低溫度(°C)': min_temp,
                    '最高溫度(°C)': max_temp,
                    '平均濕度(%)': avg_humidity,
                    '最大風速(m/s)': max_wind,
                    '風向': wind_dir
                })

        return daily_summary

    except Exception as e:
        st.error(f"解析天氣資料時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None

# 標題
st.title("🌤️ 台北天氣查詢系統")
st.markdown("---")

# 側邊欄 - 日期選擇
st.sidebar.header("📅 選擇日期範圍")
st.sidebar.info("請選擇開始和結束日期（限定一週內）")

# 預設日期範圍
today = datetime.now().date()
default_end = today + timedelta(days=6)

# 日期選擇器
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "開始日期",
        value=today,
        format="YYYY/MM/DD"
    )

with col2:
    end_date = st.date_input(
        "結束日期",
        value=default_end,
        format="YYYY/MM/DD"
    )

# 驗證日期範圍
date_diff = (end_date - start_date).days

if date_diff < 0:
    st.sidebar.error("❌ 結束日期不能早於開始日期！")
    valid_range = False
elif date_diff > 6:
    st.sidebar.error("❌ 日期範圍不能超過 7 天！")
    valid_range = False
else:
    st.sidebar.success(f"✅ 已選擇 {date_diff + 1} 天的天氣資料")
    valid_range = True

# 查詢按鈕
query_button = st.sidebar.button("🔍 查詢天氣", type="primary", use_container_width=True)

# 主要內容區域
if query_button:
    if not valid_range:
        st.error("請確認日期範圍正確（開始日期 <= 結束日期，且範圍不超過 7 天）")
    elif not API_KEY:
        st.error("❌ 找不到 API Key，請確認 .env 檔案中是否設定了 CWA_API_KEY")
    else:
        with st.spinner("正在獲取天氣資料..."):
            weather_data = get_taipei_weather()

            if weather_data:
                weather_summary = parse_weather_data(weather_data, start_date, end_date)

                if weather_summary:
                    st.success(f"✅ 成功獲取 {start_date.strftime('%Y/%m/%d')} 至 {end_date.strftime('%Y/%m/%d')} 的天氣資料")

                    # 顯示天氣資料表格
                    st.subheader("📊 天氣資料總覽")
                    df = pd.DataFrame(weather_summary)

                    # 使用 st.dataframe 顯示互動式表格
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

                    # 詳細天氣卡片
                    st.subheader("🌈 每日天氣詳情")

                    # 使用 columns 顯示天氣卡片
                    cols_per_row = 2
                    for i in range(0, len(weather_summary), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j in range(cols_per_row):
                            idx = i + j
                            if idx < len(weather_summary):
                                day = weather_summary[idx]
                                with cols[j]:
                                    with st.container(border=True):
                                        st.markdown(f"### {day['日期']} ({day['星期']})")
                                        st.markdown(f"**🌤️ 天氣:** {day['天氣狀況']}")
                                        st.markdown(f"**🌡️ 溫度:** {day['最低溫度(°C)']}°C ~ {day['最高溫度(°C)']}°C")
                                        st.markdown(f"**☔ 降雨機率:** {day['降雨機率(%)']}%")
                                        st.markdown(f"**💧 平均濕度:** {day['平均濕度(%)']}%")
                                        st.markdown(f"**💨 最大風速:** {day['最大風速(m/s)']} m/s ({day['風向']})")

                    # 下載 CSV
                    st.subheader("💾 下載資料")
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 下載 CSV 檔案",
                        data=csv,
                        file_name=f"台北天氣_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("⚠️ 無法解析天氣資料，或選定日期範圍內沒有資料")
            else:
                st.error("❌ 無法獲取天氣資料，請檢查：\n1. 網路連線是否正常\n2. API Key 是否有效\n3. 中央氣象署服務是否正常")
else:
    # 初始說明
    st.info("👈 請在左側選擇日期範圍（限定一週），然後點擊「查詢天氣」按鈕")

    st.markdown("""
    ### 使用說明

    1. 在左側邊欄選擇 **開始日期** 和 **結束日期**
    2. 日期範圍限定為 **7 天以內**（例如：2026/1/4 - 2026/1/11）
    3. 點擊 **「🔍 查詢天氣」** 按鈕
    4. 查看天氣資料表格和詳細資訊
    5. 可下載 CSV 檔案保存資料

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
