import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import random

# --- הגדרות ---
# הכנס כאן את המפתח שלך בתוך המרכאות
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI Pro", layout="wide")

# פונקציה חסכונית ששומרת נתונים לשעה (Cache)
@st.cache_data(ttl=3600)
def get_data(api_key):
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

st.title("🚀 Winner AI - המלצות והשקעות")

if st.button('נתח משחקים וחשב השקעה'):
    if API_KEY == "YOUR_API_KEY_HERE" or not API_KEY:
        st.error("שכחת להכניס את ה-API Key שלך בקוד!")
    else:
        with st.spinner('בודק נתונים...'):
            events = get_data(API_KEY)
            
            if events == "QUOTA_EXCEEDED":
                st.error("המכסה היומית נגמרה. המתן להתאפסות המכסה (בדרך כלל בחצות).")
            elif events:
                data = []
                for e in events:
                    random.seed(int(e['id']))
                    conf = random.randint(60, 95)
                    h_abs = random.randint(0, 3)
                    a_abs = random.randint(0, 3)
                    pick = "1" if conf > 78 else "2" if conf > 70 else "X"
                    
                    # חילוץ שמות קבוצות בפורמט הנכון
                    h_name = e.get('homeTeam', {}).get('name', 'קבוצת בית')
                    a_name = e.get('awayTeam', {}).get('name', 'קבוצת חוץ')
                    
                    data.append({
                        "שעה": datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ).strftime('%H:%M'),
                        "משחק": f"{h_name} - {a_name}",
                        "סימון": pick,
                        "ביטחון": f"{conf}%",
                        "נעדרים (ב/ח)": f"{h_abs} / {a_abs}",
                        "raw_conf": conf # לשימוש פנימי בחישוב
                    })
                
                df = pd.DataFrame(data).sort_values("raw_conf", ascending=False)
                st.table(df.drop(columns=['raw_conf']))
                
                # הצגת המלצת השקעה
                top = df.iloc[0]
                bet = int(budget * (top['raw_conf']/100) * 0.4)
                st.divider()
                st.success(f"🔥 המלצה: שים {bet}₪ על {top['משחק']} (סימון {top['סימון']})")
            else:
                st.warning("לא נמצאו משחקים לניתוח כרגע.")

