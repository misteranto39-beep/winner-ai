import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# --- הגדרות ---
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - Tournament Tracker", layout="wide")

@st.cache_data(ttl=600)
def get_full_data(api_key):
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

st.title("🏆 אנליסט Winner - פירוט משחקים ומפעלים")

if st.button('נתח משחקים לפי ליגות'):
    with st.spinner('מושך נתונים ומנתח יחסי כוחות...'):
        events = get_full_data(API_KEY)
        now = datetime.now(ISRAEL_TZ)
        
        if events:
            results = []
            for e in events:
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ)
                
                if game_time > now:
                    # פרטי המפעל והקבוצות
                    tournament = e.get('tournament', {}).get('name', 'כללי')
                    h_name = e.get('homeTeam', {}).get('name', 'N/A')
                    a_name = e.get('awayTeam', {}).get('name', 'N/A')
                    
                    # חישוב כוח (userCount)
                    h_pwr = e.get('homeTeam', {}).get('userCount', 0)
                    a_pwr = e.get('awayTeam', {}).get('userCount', 0)
                    
                    h_total = h_pwr * 1.1 
                    total = h_total + a_pwr + 1
                    prob = (max(h_total, a_pwr) / total)
                    
                    # חישובים לטבלה
                    fair_odds = round(1 / prob, 2) if prob > 0 else 0
                    conf = int(65 + (prob * 30))
                    
                    pick = "1" if h_total > a_pwr else "2"
                    if abs(h_total - a_pwr) / total < 0.05:
                        pick = "X"
                        fair_odds = 3.20

                    bet_val = int(budget * (conf / 100) * 0.12)

                    results.append({
                        "שעה": game_time.strftime('%H:%M'),
                        "מפעל": tournament, # העמודה החדשה שביקשת
                        "משחק": f"{h_name} - {a_name}",
                        "סימון": pick,
                        "ביטחון": f"{conf}%",
                        "יחס הוגן": f"{fair_odds}",
                        "השקעה": f"{bet_val} ₪"
                    })
            
            if results:
                df = pd.DataFrame(results).sort_values("ביטחון", ascending=False)
                # סידור העמודות כך שהמפעל יהיה בהתחלה
                df = df[["שעה", "מפעל", "משחק", "סימון", "ביטחון", "יחס הוגן", "השקעה"]]
                st.table(df)
            else:
                st.warning("לא נמצאו משחקים עתידיים להיום.")
        else:
            st.error("שגיאה בתקשורת עם ה-API. וודא שהמפתח תקין.")


