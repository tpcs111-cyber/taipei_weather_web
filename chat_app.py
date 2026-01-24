"""
天氣聊天室 - Streamlit 版本
"""
import streamlit as st
import requests
import re
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()
API_KEY = os.getenv("CWA_API_KEY")


def get_date_example():
    """取得動態日期範例（使用今天日期）"""
    today = datetime.now()
    m = today.month
    d = today.day
    return f"{m}/{d}、{m:02d}/{d:02d}、{m}.{d}、{m}月{d}日、明天、後天"


# 頁面設定
st.set_page_config(
    page_title="天氣小助手",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 天氣小助手")
st.markdown("---")

# 初始化對話歷史
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"你好！我是天氣小助手 🌤️\n\n請問你想查詢哪一天的台北天氣？\n\n（例如：{get_date_example()}）"
    })

# 初始化等待確認的日期
if "pending_date" not in st.session_state:
    st.session_state.pending_date = None

# 快取天氣資料
if "weather_cache" not in st.session_state:
    st.session_state.weather_cache = None

# 連續輸入非日期的次數
if "invalid_date_count" not in st.session_state:
    st.session_state.invalid_date_count = 0

# 確認階段連續輸入無效內容的次數
if "invalid_confirm_count" not in st.session_state:
    st.session_state.invalid_confirm_count = 0


def get_weather_data():
    """獲取天氣資料"""
    if st.session_state.weather_cache is not None:
        return st.session_state.weather_cache

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
            st.session_state.weather_cache = data
            return data
        return None
    except Exception:
        return None


def parse_date(user_input):
    """解析使用者輸入的日期"""
    today = datetime.now().date()
    text = user_input.strip()

    # 相對日期
    if "今天" in text:
        return today
    if "明天" in text:
        return today + timedelta(days=1)
    if "後天" in text:
        return today + timedelta(days=2)
    if "大後天" in text:
        return today + timedelta(days=3)

    # 日期格式（新增 1.27 和確保 1月27日 能被識別）
    patterns = [
        (r'(\d{1,2})/(\d{1,2})', lambda m: (int(m.group(1)), int(m.group(2)))),
        (r'(\d{1,2})-(\d{1,2})', lambda m: (int(m.group(1)), int(m.group(2)))),
        (r'(\d{1,2})\.(\d{1,2})', lambda m: (int(m.group(1)), int(m.group(2)))),  # 新增 1.27
        (r'(\d{1,2})月(\d{1,2})[號日]', lambda m: (int(m.group(1)), int(m.group(2)))),  # 1月27號、1月27日
        (r'(\d{1,2})月(\d{1,2})', lambda m: (int(m.group(1)), int(m.group(2)))),  # 1月27
    ]

    for pattern, extractor in patterns:
        match = re.search(pattern, text)
        if match:
            month, day = extractor(match)
            year = today.year
            try:
                target_date = datetime(year, month, day).date()
                if target_date < today:
                    target_date = datetime(year + 1, month, day).date()
                return target_date
            except ValueError:
                return None

    return None


def get_weather_for_date(target_date):
    """取得特定日期的天氣資料"""
    weather_data = get_weather_data()
    if not weather_data:
        return None

    try:
        records = weather_data['records']
        taipei_location = None
        for loc in records['Locations'][0]['Location']:
            if loc['LocationName'] == '臺北市':
                taipei_location = loc
                break

        if not taipei_location:
            return None

        elements_dict = {}
        for element in taipei_location['WeatherElement']:
            elements_dict[element['ElementName']] = element['Time']

        date_str = target_date.strftime("%Y-%m-%d")
        temps, rain_probs, humidity, weather_desc = [], [], [], []

        if '溫度' in elements_dict:
            for time_data in elements_dict['溫度']:
                dt = datetime.fromisoformat(time_data['DataTime'].replace('+08:00', ''))
                if dt.strftime("%Y-%m-%d") == date_str:
                    temps.append(int(time_data['ElementValue'][0]['Temperature']))

        if '3小時降雨機率' in elements_dict:
            for time_data in elements_dict['3小時降雨機率']:
                dt = datetime.fromisoformat(time_data['StartTime'].replace('+08:00', ''))
                if dt.strftime("%Y-%m-%d") == date_str:
                    rain_probs.append(int(time_data['ElementValue'][0]['ProbabilityOfPrecipitation']))

        if '相對濕度' in elements_dict:
            for time_data in elements_dict['相對濕度']:
                dt = datetime.fromisoformat(time_data['DataTime'].replace('+08:00', ''))
                if dt.strftime("%Y-%m-%d") == date_str:
                    humidity.append(int(time_data['ElementValue'][0]['RelativeHumidity']))

        if '天氣現象' in elements_dict:
            for time_data in elements_dict['天氣現象']:
                dt = datetime.fromisoformat(time_data.get('StartTime', time_data.get('DataTime', '')).replace('+08:00', ''))
                if dt.strftime("%Y-%m-%d") == date_str:
                    weather_desc.append(time_data['ElementValue'][0]['Weather'])

        if not temps:
            return None

        return {
            'date': date_str,
            'min_temp': min(temps),
            'max_temp': max(temps),
            'rain_prob': max(rain_probs) if rain_probs else 0,
            'humidity': sum(humidity) // len(humidity) if humidity else 0,
            'weather': max(set(weather_desc), key=weather_desc.count) if weather_desc else "無資料"
        }

    except Exception:
        return None


def format_weather_response(weather_info, target_date):
    """格式化天氣回應"""
    weekday_map = {0: '星期一', 1: '星期二', 2: '星期三', 3: '星期四', 4: '星期五', 5: '星期六', 6: '星期日'}
    weekday = weekday_map[target_date.weekday()]

    weather = weather_info['weather']
    if '晴' in weather:
        emoji = '☀️'
    elif '雨' in weather:
        emoji = '🌧️'
    elif '陰' in weather:
        emoji = '☁️'
    else:
        emoji = '🌤️'

    rain_tip = ""
    if weather_info['rain_prob'] >= 70:
        rain_tip = "\n\n⚠️ **降雨機率高，記得帶傘！**"
    elif weather_info['rain_prob'] >= 40:
        rain_tip = "\n\n💡 建議攜帶雨具以防萬一。"

    return f"""
### {emoji} {target_date.strftime('%Y/%m/%d')} ({weekday}) 台北天氣

| 項目 | 資訊 |
|------|------|
| 🌡️ 溫度 | {weather_info['min_temp']}°C ~ {weather_info['max_temp']}°C |
| 🌧️ 降雨機率 | {weather_info['rain_prob']}% |
| 💧 平均濕度 | {weather_info['humidity']}% |
| 🌤️ 天氣狀況 | {weather_info['weather']} |
{rain_tip}

---
還想查詢其他日期嗎？直接告訴我日期就好！
"""


def process_user_input(user_input):
    """處理使用者輸入"""

    # 如果有等待確認的日期
    if st.session_state.pending_date is not None:
        text_lower = user_input.lower().strip()

        # 先檢查是否同時包含肯定和否定（例如：是不是、YN、YESNO）
        has_yes = any(word in user_input for word in ['是', '對', '好', '確認', '沒錯', '正確']) or \
                  any(word in text_lower for word in ['yes', 'y', 'ok'])
        has_no = any(word in user_input for word in ['不是', '不對', '不要', '錯', '不']) or \
                 any(word in text_lower for word in ['no', 'n'])

        # 特殊情況：同時有肯定和否定
        if has_yes and has_no:
            return "到底哪一個，你給我講清楚"

        # 先檢查「不是」（因為「不是」包含「是」字，要先判斷）
        if any(word in user_input for word in ['不是', '不對', '不要', '錯']):
            st.session_state.pending_date = None
            st.session_state.invalid_confirm_count = 0
            st.session_state.invalid_date_count = 0
            return f"好的，請重新告訴我你想查詢的日期。\n\n（例如：{get_date_example()}）"

        # 再檢查「是」
        if any(word in user_input.lower() for word in ['是', '對', 'yes', 'y', '好', '確認', '沒錯', '正確', 'ok']):
            target_date = st.session_state.pending_date
            st.session_state.pending_date = None
            st.session_state.invalid_confirm_count = 0
            st.session_state.invalid_date_count = 0

            weather_info = get_weather_for_date(target_date)
            if weather_info:
                return format_weather_response(weather_info, target_date)
            else:
                return f"抱歉，我找不到 {target_date.strftime('%Y/%m/%d')} 的天氣資料。\n\n可能是這個日期超出預報範圍（通常只有未來 7 天的資料）。"

        # 檢查「no」「n」（英文否定，單獨處理避免誤判）
        if user_input.lower().strip() in ['no', 'n']:
            st.session_state.pending_date = None
            st.session_state.invalid_confirm_count = 0
            st.session_state.invalid_date_count = 0
            return f"好的，請重新告訴我你想查詢的日期。\n\n（例如：{get_date_example()}）"

        # 嘗試解析新日期
        new_date = parse_date(user_input)
        if new_date:
            st.session_state.pending_date = new_date
            st.session_state.invalid_confirm_count = 0
            return f"你想要查詢 **{new_date.strftime('%Y/%m/%d')}** 的天氣對嗎？\n\n（請回答「是」或「不是」）"

        # 無法判定內容
        st.session_state.invalid_confirm_count += 1
        if st.session_state.invalid_confirm_count >= 2:
            return "叫你選個「是」或「不是」很難嗎？"
        else:
            return "請回答「是」或「不是」，或者直接告訴我新的日期。"

    # 解析日期
    target_date = parse_date(user_input)

    if target_date:
        st.session_state.pending_date = target_date
        st.session_state.invalid_date_count = 0
        st.session_state.invalid_confirm_count = 0
        return f"你想要查詢 **{target_date.strftime('%Y/%m/%d')}** 的天氣對嗎？\n\n（請回答「是」或「不是」）"
    else:
        # 找不到日期
        st.session_state.invalid_date_count += 1
        if st.session_state.invalid_date_count >= 2:
            return "你他媽的給我輸入日期喔"
        else:
            today = datetime.now()
            m, d = today.month, today.day
            return f"我找不到你要查詢的日期 🤔\n\n請給我一個日期，例如：\n- {m}/{d}\n- {m:02d}/{d:02d}\n- {m}.{d}\n- {m}月{d}日\n- 明天\n- 後天"


# 顯示對話歷史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天輸入
if prompt := st.chat_input("輸入日期查詢天氣..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response = process_user_input(prompt)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
