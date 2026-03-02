import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# --- הגדרות ---
# הכנס כאן את המפתח שלך בתוך המרכאות
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI Real-Time", layout="wide")

@st.cache_data(ttl=600) # שומר נתונים ל-10 דקות כדי לחסוך בקשות
def get_real_data(api_key):
    today = datetime.now(ISRAEL_TZ).strftime('%Y-%m-%d')
    url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{today}"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "sportapi7.p.rapidapi.com"
    }
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json().get('events', [])
        elif res.status_code == 429:
            return "QUOTA_EXCEEDED"
        return None
    except:
        return None

# --- ממשק ---
st.sidebar.header("💰 ניהול השקעה")
budget = st.sidebar.number_input("תקציב להיום (₪)", min_value=10, value=100)

st.title("⚽ Winner AI - משחקים וניתוח אמת")

if st.button('נתח משחקים מהלוח'):
    if API_KEY == "YOUR_API_KEY_HERE" or not API_KEY:
        st.error("שכחת להכניס את ה-API Key שלך בקוד.")
    else:
        with st.spinner('מושך משחקים אמיתיים...'):
            events = get_real_data(API_KEY)
            
            if events == "QUOTA_EXCEEDED":
                st.error("המכסה היומית נגמרה. המערכת תחזור לעבוד מחר או עם מפתח חדש.")
            elif events:
                data = []
                for e in events:
                    # שימוש בנתונים אמיתיים מה-API בלבד
                    home_team = e.get('homeTeam', {}).get('name', 'N/A')
                    away_team = e.get('awayTeam', {}).get('name', 'N/A')
                    
                    # ניתוח ביטחון בסיסי על סמך נתוני המשחק (אם קיימים)
                    # כאן המערכת משתמשת בנתונים האמיתיים של ה-API
                    conf_score = e.get('homeScore', {}).get('current', 50) # לדוגמה בלבד
                    
                    data.append({
                        "שעה": datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ).strftime('%H:%M'),
                        "משחק": f"{home_team} - {away_team}",
                        "סטטוס": e.get('status', {}).get('description', 'טרם החל')
                    })
                
                df = pd.DataFrame(data)
                st.table(df)
                
                st.info("💡 שים לב: הניתוח כרגע מציג את לוח המשחקים האמיתי מהעולם.")
            else:
                st.warning("לא נמצאו משחקים פעילים ב-API כרגע.")

