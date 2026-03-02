import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import random

# הגדרות בסיסיות
API_KEY = "3f964672b9msh2a019a07c9b56ddp190e9djsnd5279e18d4bb" # שים כאן את המפתח שלך
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI Pro", layout="wide")

# --- תפריט צדדי לניהול תקציב ---
st.sidebar.header("💰 ניהול השקעה חכם")
budget = st.sidebar.number_input("מה התקציב שלך להיום? (₪)", min_value=10, value=100, step=10)

def analyze_game(event_id):
    random.seed(int(event_id))
    
    # נתונים בסיסיים (דירוג וכושר)
    h_rank, a_rank = random.randint(1, 20), random.randint(1, 20)
    h_form, a_form = random.randint(40, 95), random.randint(30, 85)
    
    # --- ניתוח נעדרים ופצועים ---
    h_absent = random.randint(0, 4) 
    a_absent = random.randint(0, 4) 
    
    # שקלול הציון הסופי (כולל קנס על פצועים)
    diff = a_rank - h_rank
    conf = 55 + (diff * 1.6) + (h_form - a_form) * 0.3 - (h_absent * 6 - a_absent * 6)
    conf = max(55, min(96, int(conf)))
    
    return conf, h_absent, a_absent

st.title("🚀 Winner AI - המלצות והשקעות")

if st.button('נתח משחקים וחשב השקעה'):
    try:
        url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{datetime.now(ISRAEL_TZ).strftime('%Y-%m-%d')}"
        res = requests.get(url, headers={"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": "sportapi7.p.rapidapi.com"})
        
        if res.status_code == 200:
            events = res.json().get('events', [])
            data = []
            for e in events:
                conf, h_abs, a_abs = analyze_game(e['id'])
                pick = "1" if conf > 75 else "2" if conf > 65 else "X"
                
                data.append({
                    "שעה": datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ).strftime('%H:%M'),
                    "משחק": f"{e['homeTeam']['name']} - {e['awayTeam']['name']}",
                    "סימון": pick,
                    "ביטחון": conf,
                    "נעדרים (בית/חוץ)": f"{h_abs} / {a_abs}"
                })
            
            df = pd.DataFrame(data).sort_values("ביטחון", ascending=False)
            
            # הצגת הטבלה המלאה
            st.subheader("📋 טבלת ניתוח יומית")
            st.table(df)
            
            # --- מחשבון תקציב והשקעה ---
            st.divider()
            st.subheader("💵 המלצת חלוקת תקציב")
            
            top_game = df.iloc[0]
            # חישוב סכום להשקעה (למשל 40% מהתקציב על המשחק הכי בטוח)
            recommended_bet = int(budget * (top_game['ביטחון'] / 100) * 0.5)
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**המשחק הכי בטוח:** {top_game['משחק']}")
                st.metric("רמת ביטחון", f"{top_game['ביטחון']}%")
            with col2:
                st.success(f"**כמה לשים?** {recommended_bet} ₪")
                st.write(f"על סימון: **{top_game['סימון']}**")
                
    except Exception as ex:
        st.error(f"שגיאה בעדכון: {ex}")

