import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# --- הגדרות ---
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - Value Hunter", layout="wide")

@st.cache_data(ttl=600)
def get_winner_data(api_key):
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

st.title("🎯 צייד הערך: המלצות ליחס 1.6+")
st.subheader("משחקים עם פוטנציאל רווח גבוה וביטחון מבוסס AI")

if st.button('מצא משחקים עם יחס משמעותי'):
    with st.spinner('סורק משחקים ליחסי Value...'):
        events = get_winner_data(API_KEY)
        now = datetime.now(ISRAEL_TZ)
        
        if events:
            value_picks = []
            for e in events:
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ)
                
                if game_time > now:
                    h_pwr = e.get('homeTeam', {}).get('userCount', 0)
                    a_pwr = e.get('awayTeam', {}).get('userCount', 0)
                    
                    # חישוב הסתברות
                    h_total = h_pwr * 1.12
                    total_sum = h_total + a_pwr + 1
                    prob = max(h_total, a_pwr) / total_sum
                    
                    # חישוב יחס משוער (כולל עמלת ווינר)
                    fair_odds = round(1 / prob, 2) if prob > 0 else 0
                    est_winner = round(fair_odds * 0.90, 2) # עמלה מעודכנת
                    
                    conf = int(55 + (prob * 40))
                    
                    # --- סינון "צייד הערך" ---
                    # אנחנו רוצים יחס בין 1.55 ל-2.20 וביטחון של לפחות 70%
                    if 1.55 <= est_winner <= 2.25 and conf >= 70:
                        value_picks.append({
                            "שעה": game_time.strftime('%H:%M'),
                            "מפעל": e.get('tournament', {}).get('name', 'כללי'),
                            "משחק": f"{e['homeTeam']['name']} - {e['awayTeam']['name']}",
                            "סימון": "1" if h_total > a_pwr else "2",
                            "ביטחון": conf,
                            "יחס משוער": est_winner
                        })
            
            if value_picks:
                # מיון לפי הכדאיות הכי גבוהה (שילוב של ביטחון כפול יחס)
                df = pd.DataFrame(value_picks)
                df['score'] = df['ביטחון'] * df['יחס משוער']
                df = df.sort_values(by="score", ascending=False).head(5)
                
                for index, row in df.iterrows():
                    st.warning(f"💎 **{row['משחק']}** | יחס: {row['יחס משוער']} | ביטחון: {row['ביטחון']}%")
                    st.write(f"⏰ {row['שעה']} | 🏆 {row['מפעל']} | 🎯 סימון: **{row['סימון']}**")
                    st.divider()
                
                # המלצה לטופס "פגז"
                top_2 = df.head(2)
                if len(top_2) >= 2:
                    total_odds = round(top_2['יחס משוער'].prod(), 2)
                    st.success(f"🚀 **טופס כפול מומלץ:** יחס כולל **{total_odds}**")
                    st.write(f"שים {int(budget*0.2)} ₪ כדי לזכות ב-{int(budget*0.2*total_odds)} ₪")
            else:
                st.info("לא נמצאו כרגע משחקים בטווח ה-Value (1.6-2.2). נסה שוב בעוד שעה.")




