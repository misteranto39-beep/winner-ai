import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# --- הגדרות ---
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - Odds Comparison", layout="wide")

@st.cache_data(ttl=600)
def get_odds_data(api_key):
    today = datetime.now(ISRAEL_TZ).strftime('%Y-%m-%d')
    # בקשת נתונים הכוללת Odds (יחסים) מה-API
    url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{today}"
    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "sportapi7.p.rapidapi.com"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json().get('events', [])
    except:
        return None
    return None

st.sidebar.header("💰 ניהול קופה")
budget = st.sidebar.number_input("תקציב להיום (₪)", min_value=10, value=100)

st.title("📊 השוואת יחסי Winner וערך מתמטי")

if st.button('הצג יחסים וניתוח סופי'):
    with st.spinner('מושך יחסי הימור מהעולם...'):
        events = get_odds_data(API_KEY)
        now = datetime.now(ISRAEL_TZ)
        
        if events:
            results = []
            for e in events:
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ)
                
                if game_time > now:
                    # משיכת יחסים מהעולם (אם קיימים ב-API)
                    # ב-API הזה היחסים נמצאים תחת 'odds' בדרך כלל
                    odds = e.get('odds', {}).get('choices', [])
                    market_odds = "N/A"
                    for choice in odds:
                        if choice.get('name') in ['1', 'Home', '2', 'Away']:
                            market_odds = choice.get('fractionalValue', choice.get('initialFractionalValue', 'N/A'))
                    
                    # חישוב כוח והסתברות
                    h_pwr = e.get('homeTeam', {}).get('userCount', 0)
                    a_pwr = e.get('awayTeam', {}).get('userCount', 0)
                    h_total = h_pwr * 1.1
                    prob = max(h_total, a_pwr) / (h_total + a_pwr + 1)
                    
                    fair_odds = round(1 / prob, 2) if prob > 0 else 0
                    conf = int(65 + (prob * 30))
                    pick = "1" if h_total > a_pwr else "2"
                    
                    # ניתוח כדאיות (Value)
                    # אם אין יחס מה-API, המערכת תעריך אותו לפי ממוצע ענפי
                    est_winner_odds = round(fair_odds * 0.92, 2) # הווינר בדרך כלל לוקח 8% עמלה

                    results.append({
                        "שעה": game_time.strftime('%H:%M'),
                        "מפעל": e.get('tournament', {}).get('name', 'כללי'),
                        "משחק": f"{e['homeTeam']['name']} - {e['awayTeam']['name']}",
                        "סימון": pick,
                        "ביטחון": f"{conf}%",
                        "יחס הוגן (AI)": fair_odds,
                        "יחס משוער בווינר": est_winner_odds,
                        "המלצה": "כדאי!" if fair_odds < est_winner_odds else "גבולי"
                    })
            
            if results:
                df = pd.DataFrame(results).sort_values("ביטחון", ascending=False)
                st.table(df)
            else:
                st.warning("לא נמצאו משחקים עם נתוני יחסים כרגע.")



