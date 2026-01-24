"""
台北天氣查詢系統 - FastAPI 後端
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import os
import re
from dotenv import load_dotenv
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional

# 載入 .env 檔案
load_dotenv()

# 從環境變數讀取 API Key
API_KEY = os.getenv("CWA_API_KEY")

app = FastAPI(title="台北天氣查詢系統", version="1.0.0")

# 掛載靜態檔案
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """首頁 - 返回前端頁面"""
    return FileResponse("static/index.html")


@app.get("/api/weather")
async def get_weather(start_date: str, end_date: str):
    """
    獲取台北天氣資料

    - start_date: 開始日期 (YYYY-MM-DD)
    - end_date: 結束日期 (YYYY-MM-DD)
    """
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key 未設定，請檢查 .env 檔案")

    # 呼叫中央氣象署 API
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-089"
    params = {
        "Authorization": API_KEY,
        "locationName": "臺北市",
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if data.get("success") != "true":
            raise HTTPException(status_code=500, detail="氣象 API 回傳失敗")

        # 解析資料
        daily_summary = parse_weather_data(data, start_date, end_date)
        hourly_data = parse_hourly_weather_data(data, start_date, end_date)

        return {
            "success": True,
            "daily": daily_summary,
            "hourly": hourly_data
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"獲取天氣資料時發生錯誤: {str(e)}")


def parse_weather_data(weather_data: dict, start_date: str, end_date: str) -> list:
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
            return []

        weather_elements = taipei_location['WeatherElement']

        # 建立資料字典
        elements_dict = {}
        for element in weather_elements:
            element_name = element['ElementName']
            elements_dict[element_name] = element['Time']

        # 按日期整理資料
        daily_data = defaultdict(lambda: {
            'temps': [],
            'temp_times': [],
            'rain_prob': [],
            'humidity': [],
            'weather': [],
            'wind_speed': [],
            'wind_dir': []
        })

        # 處理溫度資料
        if '溫度' in elements_dict:
            for time_data in elements_dict['溫度']:
                dt = datetime.fromisoformat(time_data['DataTime'].replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                temp = time_data['ElementValue'][0]['Temperature']
                daily_data[date_key]['temps'].append(int(temp))
                daily_data[date_key]['temp_times'].append(dt.strftime("%H:%M"))

        # 處理降雨機率
        if '3小時降雨機率' in elements_dict:
            for time_data in elements_dict['3小時降雨機率']:
                dt = datetime.fromisoformat(time_data['StartTime'].replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                pop = time_data['ElementValue'][0]['ProbabilityOfPrecipitation']
                daily_data[date_key]['rain_prob'].append(int(pop))

        # 處理相對濕度
        if '相對濕度' in elements_dict:
            for time_data in elements_dict['相對濕度']:
                dt = datetime.fromisoformat(time_data['DataTime'].replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                rh = time_data['ElementValue'][0]['RelativeHumidity']
                daily_data[date_key]['humidity'].append(int(rh))

        # 處理天氣現象
        if '天氣現象' in elements_dict:
            for time_data in elements_dict['天氣現象']:
                dt = datetime.fromisoformat(time_data.get('StartTime', time_data.get('DataTime', '')).replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                weather = time_data['ElementValue'][0]['Weather']
                daily_data[date_key]['weather'].append(weather)

        # 處理風速
        if '風速' in elements_dict:
            for time_data in elements_dict['風速']:
                dt = datetime.fromisoformat(time_data.get('StartTime', time_data.get('DataTime', '')).replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                ws = time_data['ElementValue'][0]['WindSpeed']
                try:
                    daily_data[date_key]['wind_speed'].append(float(ws))
                except:
                    pass

        # 處理風向
        if '風向' in elements_dict:
            for time_data in elements_dict['風向']:
                dt = datetime.fromisoformat(time_data.get('StartTime', time_data.get('DataTime', '')).replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                wd = time_data['ElementValue'][0]['WindDirection']
                daily_data[date_key]['wind_dir'].append(wd)

        # 生成每日摘要
        daily_summary = []
        weekday_map = {
            0: '星期一', 1: '星期二', 2: '星期三',
            3: '星期四', 4: '星期五', 5: '星期六', 6: '星期日'
        }

        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

        for date_key in sorted(daily_data.keys()):
            day_date = datetime.strptime(date_key, "%Y-%m-%d").date()

            if start <= day_date <= end:
                day = daily_data[date_key]
                dt = datetime.strptime(date_key, "%Y-%m-%d")

                min_temp = min(day['temps']) if day['temps'] else None
                max_temp = max(day['temps']) if day['temps'] else None

                min_temp_time = None
                max_temp_time = None
                if min_temp is not None and day['temps']:
                    min_idx = day['temps'].index(min_temp)
                    min_temp_time = day['temp_times'][min_idx] if min_idx < len(day['temp_times']) else None
                if max_temp is not None and day['temps']:
                    max_idx = day['temps'].index(max_temp)
                    max_temp_time = day['temp_times'][max_idx] if max_idx < len(day['temp_times']) else None

                max_rain = max(day['rain_prob']) if day['rain_prob'] else 0
                avg_humidity = sum(day['humidity']) // len(day['humidity']) if day['humidity'] else None
                weather_desc = max(set(day['weather']), key=day['weather'].count) if day['weather'] else None
                max_wind = round(max(day['wind_speed']), 1) if day['wind_speed'] else None
                wind_dir = max(set(day['wind_dir']), key=day['wind_dir'].count) if day['wind_dir'] else None

                daily_summary.append({
                    'date': date_key,
                    'weekday': weekday_map.get(dt.weekday(), ''),
                    'weather': weather_desc,
                    'rain_prob': max_rain,
                    'min_temp': min_temp,
                    'min_temp_time': min_temp_time,
                    'max_temp': max_temp,
                    'max_temp_time': max_temp_time,
                    'avg_humidity': avg_humidity,
                    'max_wind': max_wind,
                    'wind_dir': wind_dir
                })

        return daily_summary

    except Exception as e:
        print(f"解析天氣資料時發生錯誤: {e}")
        return []


def parse_hourly_weather_data(weather_data: dict, start_date: str, end_date: str) -> dict:
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
            return {}

        weather_elements = taipei_location['WeatherElement']

        elements_dict = {}
        for element in weather_elements:
            element_name = element['ElementName']
            elements_dict[element_name] = element['Time']

        hourly_data = defaultdict(lambda: defaultdict(lambda: {
            'temp': None,
            'rain': None,
            'humidity': None,
            'weather': None,
            'wind_speed': None,
            'wind_dir': None
        }))

        # 處理溫度資料
        if '溫度' in elements_dict:
            for time_data in elements_dict['溫度']:
                dt = datetime.fromisoformat(time_data['DataTime'].replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                hour_key = dt.strftime("%H:%M")
                temp = time_data['ElementValue'][0]['Temperature']
                hourly_data[date_key][hour_key]['temp'] = int(temp)

        # 處理降雨機率
        if '3小時降雨機率' in elements_dict:
            for time_data in elements_dict['3小時降雨機率']:
                dt = datetime.fromisoformat(time_data['StartTime'].replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                hour_key = dt.strftime("%H:%M")
                pop = time_data['ElementValue'][0]['ProbabilityOfPrecipitation']
                hourly_data[date_key][hour_key]['rain'] = int(pop)

        # 處理相對濕度
        if '相對濕度' in elements_dict:
            for time_data in elements_dict['相對濕度']:
                dt = datetime.fromisoformat(time_data['DataTime'].replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                hour_key = dt.strftime("%H:%M")
                rh = time_data['ElementValue'][0]['RelativeHumidity']
                hourly_data[date_key][hour_key]['humidity'] = int(rh)

        # 處理天氣現象
        if '天氣現象' in elements_dict:
            for time_data in elements_dict['天氣現象']:
                dt = datetime.fromisoformat(time_data.get('StartTime', time_data.get('DataTime', '')).replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                hour_key = dt.strftime("%H:%M")
                weather = time_data['ElementValue'][0]['Weather']
                hourly_data[date_key][hour_key]['weather'] = weather

        # 處理風速
        if '風速' in elements_dict:
            for time_data in elements_dict['風速']:
                dt = datetime.fromisoformat(time_data.get('StartTime', time_data.get('DataTime', '')).replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                hour_key = dt.strftime("%H:%M")
                ws = time_data['ElementValue'][0]['WindSpeed']
                try:
                    hourly_data[date_key][hour_key]['wind_speed'] = float(ws)
                except:
                    pass

        # 處理風向
        if '風向' in elements_dict:
            for time_data in elements_dict['風向']:
                dt = datetime.fromisoformat(time_data.get('StartTime', time_data.get('DataTime', '')).replace('+08:00', ''))
                date_key = dt.strftime("%Y-%m-%d")
                hour_key = dt.strftime("%H:%M")
                wd = time_data['ElementValue'][0]['WindDirection']
                hourly_data[date_key][hour_key]['wind_dir'] = wd

        # 轉換為普通字典
        result = {}
        for date_key, hours in hourly_data.items():
            result[date_key] = dict(hours)

        return result

    except Exception as e:
        print(f"解析每小時天氣資料時發生錯誤: {e}")
        return {}


# ========== 聊天功能 API ==========

class ChatRequest(BaseModel):
    message: str
    pending_date: Optional[str] = None
    invalid_date_count: int = 0
    invalid_confirm_count: int = 0


class ChatResponse(BaseModel):
    response: str
    pending_date: Optional[str] = None
    invalid_date_count: int = 0
    invalid_confirm_count: int = 0


def get_date_example():
    """取得動態日期範例（使用今天日期）"""
    today = datetime.now()
    m = today.month
    d = today.day
    return f"{m}/{d}、{m:02d}/{d:02d}、{m}.{d}、{m}月{d}日、明天、後天"


def parse_chat_date(user_input: str):
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

    # 日期格式
    patterns = [
        (r'(\d{1,2})/(\d{1,2})', lambda m: (int(m.group(1)), int(m.group(2)))),
        (r'(\d{1,2})-(\d{1,2})', lambda m: (int(m.group(1)), int(m.group(2)))),
        (r'(\d{1,2})\.(\d{1,2})', lambda m: (int(m.group(1)), int(m.group(2)))),
        (r'(\d{1,2})月(\d{1,2})[號日]', lambda m: (int(m.group(1)), int(m.group(2)))),
        (r'(\d{1,2})月(\d{1,2})', lambda m: (int(m.group(1)), int(m.group(2)))),
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


def get_chat_weather_for_date(target_date):
    """取得特定日期的天氣資料（聊天用）"""
    if not API_KEY:
        return None

    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-089"
    params = {
        "Authorization": API_KEY,
        "locationName": "臺北市",
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if data.get("success") != "true":
            return None

        records = data['records']
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


def format_chat_weather_response(weather_info, target_date):
    """格式化天氣回應（聊天用）"""
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
        rain_tip = "\n\n⚠️ 降雨機率高，記得帶傘！"
    elif weather_info['rain_prob'] >= 40:
        rain_tip = "\n\n💡 建議攜帶雨具以防萬一。"

    return f"""{emoji} {target_date.strftime('%Y/%m/%d')} ({weekday}) 台北天氣

🌡️ 溫度：{weather_info['min_temp']}°C ~ {weather_info['max_temp']}°C
🌧️ 降雨機率：{weather_info['rain_prob']}%
💧 平均濕度：{weather_info['humidity']}%
🌤️ 天氣狀況：{weather_info['weather']}{rain_tip}

還想查詢其他日期嗎？直接告訴我日期就好！"""


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天 API 端點"""
    user_input = request.message
    pending_date_str = request.pending_date
    invalid_date_count = request.invalid_date_count
    invalid_confirm_count = request.invalid_confirm_count

    # 轉換 pending_date
    pending_date = None
    if pending_date_str:
        try:
            pending_date = datetime.strptime(pending_date_str, "%Y-%m-%d").date()
        except ValueError:
            pending_date = None

    # 如果有等待確認的日期
    if pending_date is not None:
        text_lower = user_input.lower().strip()

        # 檢查是否同時包含肯定和否定
        has_yes = any(word in user_input for word in ['是', '對', '好', '確認', '沒錯', '正確']) or \
                  any(word in text_lower for word in ['yes', 'y', 'ok'])
        has_no = any(word in user_input for word in ['不是', '不對', '不要', '錯', '不']) or \
                 any(word in text_lower for word in ['no', 'n'])

        # 特殊情況：同時有肯定和否定
        if has_yes and has_no:
            return ChatResponse(
                response="到底哪一個，你給我講清楚",
                pending_date=pending_date_str,
                invalid_date_count=invalid_date_count,
                invalid_confirm_count=invalid_confirm_count
            )

        # 先檢查「不是」
        if any(word in user_input for word in ['不是', '不對', '不要', '錯']):
            return ChatResponse(
                response=f"好的，請重新告訴我你想查詢的日期。\n\n（例如：{get_date_example()}）",
                pending_date=None,
                invalid_date_count=0,
                invalid_confirm_count=0
            )

        # 再檢查「是」
        if any(word in user_input.lower() for word in ['是', '對', 'yes', 'y', '好', '確認', '沒錯', '正確', 'ok']):
            weather_info = get_chat_weather_for_date(pending_date)
            if weather_info:
                return ChatResponse(
                    response=format_chat_weather_response(weather_info, pending_date),
                    pending_date=None,
                    invalid_date_count=0,
                    invalid_confirm_count=0
                )
            else:
                return ChatResponse(
                    response=f"抱歉，我找不到 {pending_date.strftime('%Y/%m/%d')} 的天氣資料。\n\n可能是這個日期超出預報範圍（通常只有未來 7 天的資料）。",
                    pending_date=None,
                    invalid_date_count=0,
                    invalid_confirm_count=0
                )

        # 檢查「no」「n」
        if user_input.lower().strip() in ['no', 'n']:
            return ChatResponse(
                response=f"好的，請重新告訴我你想查詢的日期。\n\n（例如：{get_date_example()}）",
                pending_date=None,
                invalid_date_count=0,
                invalid_confirm_count=0
            )

        # 嘗試解析新日期
        new_date = parse_chat_date(user_input)
        if new_date:
            return ChatResponse(
                response=f"你想要查詢 {new_date.strftime('%Y/%m/%d')} 的天氣對嗎？\n\n（請回答「是」或「不是」）",
                pending_date=new_date.strftime("%Y-%m-%d"),
                invalid_date_count=0,
                invalid_confirm_count=0
            )

        # 無法判定內容
        invalid_confirm_count += 1
        if invalid_confirm_count >= 2:
            return ChatResponse(
                response="叫你選個「是」或「不是」很難嗎？",
                pending_date=pending_date_str,
                invalid_date_count=invalid_date_count,
                invalid_confirm_count=invalid_confirm_count
            )
        else:
            return ChatResponse(
                response="請回答「是」或「不是」，或者直接告訴我新的日期。",
                pending_date=pending_date_str,
                invalid_date_count=invalid_date_count,
                invalid_confirm_count=invalid_confirm_count
            )

    # 解析日期
    target_date = parse_chat_date(user_input)

    if target_date:
        return ChatResponse(
            response=f"你想要查詢 {target_date.strftime('%Y/%m/%d')} 的天氣對嗎？\n\n（請回答「是」或「不是」）",
            pending_date=target_date.strftime("%Y-%m-%d"),
            invalid_date_count=0,
            invalid_confirm_count=0
        )
    else:
        # 找不到日期
        invalid_date_count += 1
        if invalid_date_count >= 2:
            return ChatResponse(
                response="你他媽的給我輸入日期喔",
                pending_date=None,
                invalid_date_count=invalid_date_count,
                invalid_confirm_count=0
            )
        else:
            today = datetime.now()
            m, d = today.month, today.day
            return ChatResponse(
                response=f"我找不到你要查詢的日期 🤔\n\n請給我一個日期，例如：\n- {m}/{d}\n- {m:02d}/{d:02d}\n- {m}.{d}\n- {m}月{d}日\n- 明天\n- 後天",
                pending_date=None,
                invalid_date_count=invalid_date_count,
                invalid_confirm_count=0
            )


@app.get("/api/chat/init")
async def chat_init():
    """聊天初始化 - 取得歡迎訊息"""
    return {
        "message": f"你好！我是天氣小助手 🌤️\n\n請問你想查詢哪一天的台北天氣？\n\n（例如：{get_date_example()}）"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
