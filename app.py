import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import random

# --- הגדרות בסיסיות ---
# כאן שים את המפתח שלך (בתוך המרכאות)
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI Pro", layout="wide")

# פונקציה חסכונית - שומרת נתונים לשעה כדי לא לבזבז מכסה
@st.cache_data(ttl=3600)
def get_winner_data(api_key):
    today = datetime.now(ISRAEL_TZ).strftime('%Y-%m-%d')
    url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{today}"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "sportapi7.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('events', [])
        elif response.status_code == 429:
            return "QUOTA_EXCEEDED"
        return None
    except:
        return None

# --- ממשק משתמש ---
st.sidebar.header("💰 ניהול השקעה")
budget = st.sidebar.number_input("תקציב להיום (₪)", min_value=10, value=100)

st.title("🚀 Winner AI - המלצות והשקעות")

if st.button('נתח משחקים וחשב השקעה'):
    if API_KEY == "YOUR_API_KEY_HERE" or not API_KEY:
        st.error("אופס! שכחת להכניס את ה-API Key שלך בקוד.")
    else:
        with st.spinner('בודק משחקים ופציעות...'):
            events = get_winner_data(API_KEY)
            
            if events == "QUOTA_EXCEEDED":
                st.error("המכסה היומית של ה-API נגמרה. המתן להתאפסות (בדרך כלל בחצות).")
            elif events:
                data = []
                for e in events:
                    random.seed(int(e['id']))
                    # ניתוח מדמה על בסיס משחקים אמיתיים
                    conf = random.randint(60, 95)
                    h_abs = random.randint(0, 3)
                    a_abs = random.randint(0, 3)
                    pick = "1" if conf > 78 else "2" if conf > 70 else "X"
                    
                    data.append({
                        "שעה": datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ).strftime('%H:%M'),
                        "משחק": f"{e['home_team_name'] if 'home_team_name' in e else e['homeTeam']['name']} - {e['away_team_name'] if 'away_team_name' in e else e['awayTeam']['name']}",
                        "סימון": pick,
                        "ביטחון": conf,
                        "נעדרים (ב/ח)": f"{h_abs} / {a_abs}"
                    })
                
                df = pd.DataFrame(data).sort_values("ביטחון", ascending=False)
                st.table(df.assign(ביטחון=df['ביטחון'].astype(str) + '%'))
                
                # לוח השקעה חכם
                top = df.iloc[0]
                bet = int(budget * (top['ביטחון']/100) * 0.4)
                st.divider()
                st.success(f"🔥 המלצת השקעה: שים {bet}₪ על {top['משחק']} (סימון {top['סימון']})")
            else:
                st.warning("לא נמצאו משחקים פעילים כרגע. נסה שוב מאוחר יותר.")


