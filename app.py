import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# --- הגדרות ---
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - Real Market Analyst", layout="wide")

@st.cache_data(ttl=600)
def get_market_data(api_key):
    today = datetime.now(ISRAEL_TZ).strftime('%Y-%m-%d')
    url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{today}"
    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "sportapi7.p.rapidapi.com"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json().get('events', [])
        return None
    except:
        return None

st.sidebar.header("💰 ניהול קופה")
budget = st.sidebar.number_input("תקציב להיום (₪)", min_value=10, value=100)

st.title("🛡️ Winner AI - ניתוח הסתברות אמת")

if st.button('הצג המלצות אמינות'):
    with st.spinner('מחשב הסתברויות מתמטיות...'):
        events = get_market_data(API_KEY)
        now = datetime.now(ISRAEL_TZ)
        
        if events:
            results = []
            for e in events:
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ)
                
                if game_time > now:
                    # משיכת הצבעות (Votes)
                    v_home = e.get('votes', {}).get('vote1', 0)
                    v_away = e.get('votes', {}).get('vote2', 0)
                    total_v = v_home + v_away
                    
                    # לוגיקת האמינות המשופרת
                    if total_v > 10: # רף כניסה הגיוני
                        conf = (max(v_home, v_away) / total_v) * 100
                        pick = "1" if v_home > v_away else "2"
                        source = "חכמת המונים"
                    else:
                        # אם אין הצבעות - נשתמש בדירוג כוח (userCount)
                        h_rating = e.get('homeTeam', {}).get('userCount', 0)
                        a_rating = e.get('awayTeam', {}).get('userCount', 0)
                        conf = 60 + (min(30, abs(h_rating - a_rating) / 1000))
                        pick = "1" if h_rating > a_rating else "2"
                        source = "דירוג איכות"

                    # חישוב השקעה (סכום בשקלים)
                    bet_val = int(budget * (conf / 100) * 0.15)
                    bet_val = max(10, bet_val)

                    results.append({
                        "שעה": game_time.strftime('%H:%M'),
                        "משחק": f"{e['homeTeam']['name']} - {e['awayTeam']['name']}",
                        "ליגה": e.get('tournament', {}).get('name', 'General'),
                        "סימון": pick,
                        "רמת אמינות": f"{int(conf)}%",
                        "כמה לשים?": f"{bet_val} ₪",
                        "בסיס הניתוח": source
                    })
            
            if results:
                df = pd.DataFrame(results).sort_values("רמת אמינות", ascending=False)
                st.table(df)
                top = df.iloc[0]
                st.success(f"💎 **באנקר פוטנציאלי:** {top['משחק']} (סימון {top['סימון']}) | לשים {top['כמה לשים?']}")
            else:
                st.warning("לא נמצאו משחקים עתידיים להיום.")
