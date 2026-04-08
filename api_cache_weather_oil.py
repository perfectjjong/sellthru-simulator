"""
SellThru Simulator - API Cache Updater
매주 수요일 09:00 스케줄러에서 실행

기능:
1. 리야드 월별 기온 (Open-Meteo 무료 API)
   - 당월~익월: 실제 예보 데이터
   - 미래월: 기후평년값 (과거 3년 평균)
2. WTI 유가 (Yahoo Finance 무료)
   - 현재 WTI 가격
   - EIA Short-Term Energy Outlook에서 월별 전망 (가능 시)

Output: api_cache_data.json (같은 폴더에 저장 → GitHub Pages 배포)
"""

import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict

import requests

# ─── CONFIG ───────────────────────────────────────────────────
RIYADH_LAT = 24.7136
RIYADH_LON = 46.6753
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# Historical climate normals for Riyadh (fallback if API fails)
CLIMATE_NORMALS = {
    'Jan':17, 'Feb':18, 'Mar':22, 'Apr':28, 'May':34, 'Jun':38,
    'Jul':40, 'Aug':40, 'Sep':36, 'Oct':30, 'Nov':24, 'Dec':18
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'api_cache_data.json')


def fetch_current_forecast():
    """Open-Meteo 7-day forecast for Riyadh (free, no key)"""
    url = (
        f'https://api.open-meteo.com/v1/forecast'
        f'?latitude={RIYADH_LAT}&longitude={RIYADH_LON}'
        f'&daily=temperature_2m_max,temperature_2m_min'
        f'&timezone=Asia/Riyadh&forecast_days=14'
    )
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()['daily']

    monthly_temps = defaultdict(list)
    for date_str, tmax, tmin in zip(data['time'], data['temperature_2m_max'], data['temperature_2m_min']):
        if tmax is not None and tmin is not None:
            avg = (tmax + tmin) / 2
            month = int(date_str.split('-')[1])
            monthly_temps[month].append(avg)

    result = {}
    for month_num, temps in monthly_temps.items():
        month_name = MONTHS[month_num - 1]
        result[month_name] = round(sum(temps) / len(temps), 1)

    return result


def fetch_historical_averages():
    """Open-Meteo historical archive: 3-year monthly averages for climate normal"""
    now = datetime.now()
    monthly_all = defaultdict(list)

    for years_back in [1, 2, 3]:
        year = now.year - years_back
        url = (
            f'https://archive-api.open-meteo.com/v1/archive'
            f'?latitude={RIYADH_LAT}&longitude={RIYADH_LON}'
            f'&start_date={year}-01-01&end_date={year}-12-31'
            f'&daily=temperature_2m_mean&timezone=Asia/Riyadh'
        )
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            data = r.json()['daily']
            for date_str, temp in zip(data['time'], data['temperature_2m_mean']):
                if temp is not None:
                    month = int(date_str.split('-')[1])
                    monthly_all[month].append(temp)
        except Exception as e:
            print(f'  Warning: Failed to fetch {year} data: {e}')

    result = {}
    for month_num in range(1, 13):
        month_name = MONTHS[month_num - 1]
        if monthly_all[month_num]:
            result[month_name] = round(sum(monthly_all[month_num]) / len(monthly_all[month_num]), 1)
        else:
            result[month_name] = CLIMATE_NORMALS[month_name]

    return result


def fetch_oil_price():
    """Yahoo Finance WTI crude oil current price"""
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/CL=F?range=5d&interval=1d'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()
    result = data['chart']['result'][0]
    meta = result['meta']
    price = meta.get('regularMarketPrice', 0)

    # Get 5-day prices for trend
    closes = result.get('indicators', {}).get('quote', [{}])[0].get('close', [])
    closes = [c for c in closes if c is not None]

    return {
        'current_price': round(price, 2),
        'currency': 'USD',
        'symbol': 'WTI (CL=F)',
        'recent_prices': [round(c, 2) for c in closes[-5:]],
    }


def classify_oil_level(price):
    """Classify WTI price into simulator levels"""
    if price < 60:
        return 'low'
    elif price < 80:
        return 'mid'
    elif price < 100:
        return 'high'
    else:
        return 'vhigh'


def main():
    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] SellThru API Cache Update')
    print('=' * 50)

    cache = {
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'updated_by': 'api_cache_weather_oil.py',
        'temperature': {},
        'oil': {},
    }

    # 1. Temperature
    print('\n1. Fetching temperature data...')
    try:
        forecast = fetch_current_forecast()
        print(f'   Forecast months: {list(forecast.keys())}')
    except Exception as e:
        print(f'   Forecast failed: {e}')
        forecast = {}

    try:
        historical = fetch_historical_averages()
        print(f'   Historical averages: OK (12 months)')
    except Exception as e:
        print(f'   Historical failed: {e}')
        historical = dict(CLIMATE_NORMALS)

    # Build final temp data: forecast for current/next month, historical for others
    now = datetime.now()
    current_month = now.month
    final_temps = {}
    for i, month_name in enumerate(MONTHS):
        month_num = i + 1
        if month_name in forecast:
            final_temps[month_name] = forecast[month_name]
            source = 'forecast'
        elif month_name in historical:
            final_temps[month_name] = historical[month_name]
            source = 'historical_avg'
        else:
            final_temps[month_name] = CLIMATE_NORMALS[month_name]
            source = 'climate_normal'
        print(f'   {month_name}: {final_temps[month_name]}°C ({source})')

    cache['temperature'] = {
        'monthly_avg': final_temps,
        'baseline': dict(historical),
        'source': 'Open-Meteo (forecast + 3yr historical)',
        'location': 'Riyadh, Saudi Arabia',
    }

    # 2. Oil price
    print('\n2. Fetching oil price...')
    try:
        oil = fetch_oil_price()
        oil_level = classify_oil_level(oil['current_price'])
        print(f'   WTI: ${oil["current_price"]} → level: {oil_level}')
        print(f'   Recent: {oil["recent_prices"]}')

        cache['oil'] = {
            'wti_price': oil['current_price'],
            'wti_level': oil_level,
            'recent_prices': oil['recent_prices'],
            'source': 'Yahoo Finance (WTI CL=F)',
        }
    except Exception as e:
        print(f'   Oil price failed: {e}')
        cache['oil'] = {
            'wti_price': 75.0,
            'wti_level': 'mid',
            'recent_prices': [],
            'source': 'fallback (API failed)',
        }

    # 3. Save
    print(f'\n3. Saving to {OUTPUT_FILE}...')
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print(f'   Done! ({os.path.getsize(OUTPUT_FILE)} bytes)')

    print(f'\n{"=" * 50}')
    print(f'Cache update complete at {cache["updated_at"]}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f'FATAL ERROR: {e}')
        sys.exit(1)
