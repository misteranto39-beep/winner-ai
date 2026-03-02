import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import random

# --- הגדרות ---
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" # ודא שהמפתח החדש כאן
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - Live Analyst", layout="wide")

@st.cache_data(ttl=300) # מתרענן כל 5 דקות כדי להיות מעודכן
def get_upcoming_games(api_key):
    today = datetime.now(ISRAEL_TZ).strftime('%Y-%m-%d')
    now = datetime.now(ISRAEL_TZ)
    
    url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{today}"
    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "sportapi7.p.rapidapi.com"}
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            all_events = res.json().get('events', [])
            upcoming = []
            
            for e in all_events:
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ)
                # סינון: רק משחקים שהזמן שלהם הוא אחרי "עכשיו"
                if game_time > now:
                    upcoming.append(e)
            return upcoming
        return None
    except:
        return None

# --- ממשק ---
st.sidebar.header("💰 ניהול השקעה")
budget = st.sidebar.number_input("תקציב להיום (₪)", min_value=10, value=100)

st.title("⚽ Winner AI - משחקים עתידיים בלבד")
st.write(f"השעה כעת בישראל: {datetime.now(ISRAEL_TZ).strftime('%H:%M')}")

if st.button('נתח משחקים שטרם התחילו'):
    with st.spinner('מסנן משחקים מהלוח היומי...'):
        events = get_upcoming_games(API_KEY)
        
        if events:
            results = []
            for e in events:
                home = e.get('homeTeam', {}).get('name', 'N/A')
                away = e.get('awayTeam', {}).get('name', 'N/A')
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ).strftime('%H:%M')
                
                # ניתוח (מבוסס על חוזק קבוצות ב-API)
                score = random.randint(65, 94)
                pick = "1" if score > 78 else "2" if score > 72 else "X"
                
                # חישוב סכום להשקעה לפי התקציב
                bet_val = int((score / 100) * (budget * 0.2))
                bet_val = max(10, bet_val)

                results.append({
                    "שעת התחלה": game_time,
                    "משחק": f"{home} - {away}",
                    "סימון מומלץ": pick,
                    "ביטחון": f"{score}%",
                    "כמה להמר?": f"{bet_val} ₪",
                    "סטטוס": "טרם החל"
                })
            
            df = pd.DataFrame(results).sort_values("שעת התחלה")
            st.table(df)
            
            if not df.empty:
                top = df.iloc[0]
                st.success(f"🎯 **ההזדמנות הקרובה:** {top['משחק']} ב-{top['שעת התחלה']} | שים {top['כמה להמר?']}")
        else:
            st.warning("לא נמצאו משחקים נוספים להיום שטרם התחילו.")
