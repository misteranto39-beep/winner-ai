import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
import pytz

# --- הגדרות ---
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - Today's Picks", layout="wide")

@st.cache_data(ttl=600)
def get_today_data(api_key):
    # משיכת נתונים להיום
    today_str = datetime.now(ISRAEL_TZ).strftime('%Y-%m-%d')
    url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{today_str}"
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

st.title("📅 המלצות זהב להיום")
st.subheader(f"ניתוח משחקי {datetime.now(ISRAEL_TZ).strftime('%d/%m/%Y')}")

if st.button('הצג המלצות להיום'):
    with st.spinner('סורק משחקים להיום...'):
        events = get_today_data(API_KEY)
        now = datetime.now(ISRAEL_TZ)
        # הגדרת סוף היום הנוכחי (חצות)
        end_of_today = datetime.combine(now.date(), time(23, 59, 59)).replace(tzinfo=ISRAEL_TZ)
        
        if events:
            today_picks = []
            for e in events:
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ)
                
                # --- סינון קשיח: רק מהרגע ועד חצות הלילה ---
                if now < game_time <= end_of_today:
                    h_pwr = e.get('homeTeam', {}).get('userCount', 0)
                    a_pwr = e.get('awayTeam', {}).get('userCount', 0)
                    
                    # חישוב מומנטום
                    h_form = e.get('homeTeam', {}).get('form', 'DDDDD')
                    a_form = e.get('awayTeam', {}).get('form', 'DDDDD')
                    h_mom = h_form.count('W')*2 - h_form.count('L')
                    a_mom = a_form.count('W')*2 - a_form.count('L')

                    # שקלול סופי
                    h_total = (h_pwr * 1.12) + (h_mom * (h_pwr * 0.05))
                    a_total = a_pwr + (a_mom * (a_pwr * 0.05))
                    
                    prob = max(h_total, a_total) / (h_total + a_total + 1)
                    est_winner = round((1/prob) * 0.88, 2)
                    conf = int(55 + (prob * 40))

                    # סינון יחס 1.6+ וביטחון גבוה
                    if est_winner >= 1.60 and conf >= 70:
                        today_picks.append({
                            "שעה": game_time.strftime('%H:%M'),
                            "משחק": f"{e['homeTeam']['name']} - {e['awayTeam']['name']}",
                            "סימון": "1" if h_total > a_total else "2",
                            "ביטחון": conf,
                            "יחס": max(1.10, est_winner),
                            "מפעל": e.get('tournament', {}).get('name', 'General')
                        })
            
            if today_picks:
                df = pd.DataFrame(today_picks).sort_values(by="ביטחון", ascending=False).head(5)
                
                for idx, row in df.iterrows():
                    st.success(f"⚽ **{row['משחק']}** | יחס: {row['יחס']} | בטחון: {row['ביטחון']}%")
                    st.write(f"⏰ שעה: {row['שעה']} | 🏆 {row['מפעל']} | 🎯 סימון: **{row['סימון']}**")
                    st.divider()
                
                # טופס דאבל
                if len(df) >= 2:
                    total_odds = round(df.iloc[0]['יחס'] * df.iloc[1]['יחס'], 2)
                    st.warning(f"🔥 **טופס דאבל להיום:** יחס כולל {total_odds}")
            else:
                st.info("לא נמצאו כרגע משחקי 'Value' שמתחילים היום. בדוק שוב בבוקר!")
        else:
            st.error("שגיאה במשיכת נתונים.")




