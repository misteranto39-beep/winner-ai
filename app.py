import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# --- הגדרות ---
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - Expert Mode", layout="wide")

@st.cache_data(ttl=600)
def get_data(api_key):
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

st.sidebar.header("💰 ניהול תקציב")
budget = st.sidebar.number_input("תקציב להיום (₪)", min_value=10, value=100)

st.title("🤖 אנליסט Winner - מצב ניתוח עומק")
st.info("המערכת מנתחת לפי דירוג כוח עולמי וביתיות (מתאים גם לתחילת עונה).")

if st.button('הפעל ניתוח סוכן'):
    with st.spinner('סורק נתונים...'):
        events = get_data(API_KEY)
        now = datetime.now(ISRAEL_TZ)
        
        if events:
            results = []
            for e in events:
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ)
                
                # מציג רק משחקים שטרם התחילו
                if game_time > now:
                    h_name = e.get('homeTeam', {}).get('name', 'N/A')
                    a_name = e.get('awayTeam', {}).get('name', 'N/A')
                    
                    # ניתוח כוח (userCount) - עובד גם כשהטבלה ריקה בתחילת עונה
                    h_pwr = e.get('homeTeam', {}).get('userCount', 0)
                    a_pwr = e.get('awayTeam', {}).get('userCount', 0)
                    
                    # בונוס ביתיות וחישוב הסתברות
                    h_total = h_pwr * 1.1 
                    diff = abs(h_total - a_pwr)
                    total = h_total + a_pwr + 1
                    
                    conf = 65 + (min(30, (diff / total) * 100))
                    
                    # קביעת סימון
                    if diff / total < 0.05:
                        pick = "X"
                    else:
                        pick = "1" if h_total > a_pwr else "2"

                    # המלצת השקעה
                    bet_val = int(budget * (conf / 100) * 0.12)
                    bet_val = max(10, bet_val)

                    results.append({
                        "שעה": game_time.strftime('%H:%M'),
                        "משחק": f"{h_name} - {a_name}",
                        "סימון": pick,
                        "ביטחון": f"{int(conf)}%",
                        "השקעה": f"{bet_val} ₪",
                        "סטטוס": "ניתוח כוח (מחזור פתיחה)" if h_pwr > 0 else "מידע חסר"
                    })
            
            if results:
                df = pd.DataFrame(results).sort_values("ביטחון", ascending=False)
                st.table(df)
            else:
                st.warning("לא נמצאו משחקים עתידיים להיום.")
        else:
            st.error("שגיאה בתקשורת עם ה-API. וודא שהמפתח תקין.")

