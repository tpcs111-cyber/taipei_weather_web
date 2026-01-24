"""
台北天氣查詢系統 - FastAPI 後端
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
