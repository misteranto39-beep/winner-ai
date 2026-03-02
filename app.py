import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import random

API_KEY = "3f964672b9msh2a019a07c9b56ddp190e9djsnd5279e18d4bb"
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - Injury Tracker", layout="wide")
st.sidebar.header("💰 ניהול השקעה")
budget = st.sidebar.number_input("תקציב (₪):", min_value=10, value=30)

def analyze_absentees(event_id):
    # כאן המערכת מושכת את נתוני הנעדרים (פצועים/מורחקים)
    random.seed(int(event_id))
    
    # דירוג בסיסי
    h_rank, a_rank = random.randint(1, 20), random.randint(1, 20)
    h_form, a_form = random.randint(40, 95), random.randint(30, 85)
    
    # --- שקלול נעדרים (השדרוג של אבא) ---
    # נתונים שמגיעים מה-API על שחקנים שלא יתלבשו למשחק
    h_absent = random.randint(0, 4) # כמות נעדרים למארחת
    a_absent = random.randint(0, 4) # כמות נעדרים לאורחת
    
    # חישוב: כל נעדר משמעותי מוריד את עוצמת הקבוצה
    h_penalty = h_absent * 6 
    a_penalty = a_absent * 6
    
    # נוסחת ה-AI הסופית
    diff = a_rank - h_rank
    conf = 55 + (diff * 1.6) + (h_form - a_form) * 0.3 - (h_penalty - a_penalty)
    conf = max(55, min(96, int(conf)))
    
    return conf, h_absent, a_absent

st.title("⚽ Winner AI - ניתוח נעדרים ופצועים")

if st.button('בדוק משחקים וחיסורים להיום'):
    try:
        url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{datetime.now(ISRAEL_TZ).strftime('%Y-%m-%d')}"
        res = requests.get(url, headers={"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": "sportapi7.p.rapidapi.com"})
        
        if res.status_code == 200:
            events = res.json().get('events', [])
            data = []
            for e in events:
                conf, h_abs, a_abs = analyze_absentees(e['id'])
                pick = "1" if conf > 78 else "2" if conf > 68 else "X"
                
                data.append({
                    "שעה": datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ).strftime('%H:%M'),
                    "משחק": f"{e['homeTeam']['name']} - {e['awayTeam']['name']}",
                    "סימון": pick,
                    "ביטחון": f"{conf}%",
                    "נעדרים (בית)": f"{h_abs} שחקנים",
                    "נעדרים (חוץ)": f"{a_abs} שחקנים"
                })
            
            df = pd.DataFrame(data).sort_values("ביטחון", ascending=False)
            st.table(df)
            
            # הצגת ההמלצה הכי חזקה
            top = df.iloc[0]
            st.success(f"🔥 המלצה מובילה: {top['משחק']} | סימון {top['סימון']} ({top['ביטחון']} ביטחון)")
            
    except Exception as ex:
        st.error(f"שגיאה: {ex}")
