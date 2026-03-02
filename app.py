import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# --- הגדרות ---
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - Real Odds", layout="wide")

@st.cache_data(ttl=600)
def get_winner_data(api_key):
    today = datetime.now(ISRAEL_TZ).strftime('%Y-%m-%d')
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

st.title("⚽ אנליסט Winner - יחסים והסתברות אמת")

if st.button('הפעל ניתוח משחקים'):
    with st.spinner('מנתח נתונים ומחשב יחסים...'):
        events = get_winner_data(API_KEY)
        now = datetime.now(ISRAEL_TZ)
        
        if events:
            results = []
            for e in events:
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ)
                
                if game_time > now:
                    h_pwr = e.get('homeTeam', {}).get('userCount', 0)
                    a_pwr = e.get('awayTeam', {}).get('userCount', 0)
                    
                    # חישוב הסתברות (עם יתרון ביתיות)
                    h_total = h_pwr * 1.15 # בונוס ביתיות חזק יותר
                    total_sum = h_total + a_pwr + 1
                    prob = max(h_total, a_pwr) / total_sum
                    
                    # חישוב יחס הוגן (מתמטי) - מינימום 1.05
                    fair_odds = max(1.05, round(1 / prob, 2))
                    
                    # הערכת יחס הווינר (הורדת עמלת המועצה של כ-12%)
                    est_winner = round(fair_odds * 0.88, 2)
                    if est_winner < 1.05: est_winner = 1.05
                    
                    conf = int(60 + (prob * 35))
                    pick = "1" if h_total > a_pwr else "2"
                    
                    # בדיקת כדאיות: האם היחס מצדיק את הסיכון?
                    status = "🔥 כדאי מאוד" if conf > 85 else "✅ מומלץ" if conf > 75 else "⚠️ סיכון גבוה"

                    results.append({
                        "שעה": game_time.strftime('%H:%M'),
                        "מפעל": e.get('tournament', {}).get('name', 'General'),
                        "משחק": f"{e['homeTeam']['name']} - {e['awayTeam']['name']}",
                        "סימון": pick,
                        "ביטחון": f"{conf}%",
                        "יחס הוגן": fair_odds,
                        "הערכת יחס ווינר": est_winner,
                        "המלצה": status
                    })
            
            if results:
                df = pd.DataFrame(results).sort_values("ביטחון", ascending=False)
                st.table(df)
            else:
                st.warning("אין משחקים רלוונטיים להיום.")



