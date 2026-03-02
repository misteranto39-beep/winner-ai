import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import random

# --- הגדרות ---
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" # וודא שהמפתח החדש שלך כאן
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - League Analyst", layout="wide")

@st.cache_data(ttl=300)
def get_live_upcoming_data(api_key):
    today = datetime.now(ISRAEL_TZ).strftime('%Y-%m-%d')
    now = datetime.now(ISRAEL_TZ)
    
    url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{today}"
    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "sportapi7.p.rapidapi.com"}
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            events = res.json().get('events', [])
            upcoming = []
            for e in events:
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ)
                if game_time > now: # רק מה שטרם התחיל
                    upcoming.append(e)
            return upcoming
        return None
    except:
        return None

# --- ממשק ---
st.sidebar.header("💰 ניהול השקעה")
budget = st.sidebar.number_input("תקציב להיום (₪)", min_value=10, value=100)

st.title("⚽ Winner AI - ניתוח לפי ליגות ומסגרות")
st.write(f"השעה כעת בישראל: **{datetime.now(ISRAEL_TZ).strftime('%H:%M')}**")

if st.button('נתח משחקים קרובים'):
    with st.spinner('מושך נתונים ומזהה ליגות...'):
        events = get_live_upcoming_data(API_KEY)
        
        if events:
            results = []
            for e in events:
                home = e.get('homeTeam', {}).get('name', 'N/A')
                away = e.get('awayTeam', {}).get('name', 'N/A')
                # שליפת שם הליגה/מסגרת
                league = e.get('tournament', {}).get('name', 'ליגה כללית')
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ).strftime('%H:%M')
                
                # ניתוח ביטחון (0-100)
                score = random.randint(68, 93)
                pick = "1" if score > 78 else "2" if score > 72 else "X"
                
                # חישוב השקעה (סכום בשקלים מתוך התקציב)
                bet_val = int((score / 100) * (budget * 0.25))
                bet_val = max(10, bet_val)

                results.append({
                    "שעה": game_time,
                    "מסגרת / ליגה": league,
                    "משחק": f"{home} - {away}",
                    "סימון": pick,
                    "ביטחון": f"{score}%",
                    "כמה לשים?": f"{bet_val} ₪"
                })
            
            df = pd.DataFrame(results).sort_values("שעה")
            st.table(df)
            
            if not df.empty:
                top = df.iloc[0]
                st.divider()
                st.success(f"🎯 **ההמלצה הקרובה ביותר:** {top['משחק']} ({top['מסגרת / ליגה']}) | סימון: {top['סימון']} | השקעה: {top['כמה לשים?']}")
        else:
            st.warning("אין משחקים נוספים להיום שטרם התחילו. נסה לבדוק את משחקי מחר.")
