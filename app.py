import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# --- הגדרות ---
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - Momentum & Value", layout="wide")

@st.cache_data(ttl=600)
def get_advanced_data(api_key):
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

st.title("🚀 סוכן Winner: מומנטום ויחסי ערך")
st.subheader("ניתוח 5 משחקי הזהב (יחס 1.6+ משולב בכושר נוכחי)")

if st.button('הפעל ניתוח מומנטום'):
    with st.spinner('בודק היסטוריית משחקים ומומנטום...'):
        events = get_advanced_data(API_KEY)
        now = datetime.now(ISRAEL_TZ)
        
        if events:
            final_picks = []
            for e in events:
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ)
                
                if game_time > now:
                    # 1. נתוני בסיס
                    h_pwr = e.get('homeTeam', {}).get('userCount', 0)
                    a_pwr = e.get('awayTeam', {}).get('userCount', 0)
                    
                    # 2. חישוב מומנטום (Form)
                    # ה-API מחזיר מחרוזת כמו 'WWDLW' (W=ניצחון, L=הפסד, D=תיקו)
                    h_form_str = e.get('homeTeam', {}).get('form', 'DDDDD')
                    a_form_str = e.get('awayTeam', {}).get('form', 'DDDDD')
                    
                    def calc_form(s):
                        return (s.count('W') * 2 + s.count('D') * 1 - s.count('L') * 1)
                    
                    h_momentum = calc_form(h_form_str)
                    a_momentum = calc_form(a_form_str)
                    
                    # 3. שקלול כוח + ביתיות + מומנטום
                    h_total = (h_pwr * 1.12) + (h_momentum * (h_pwr * 0.05))
                    a_total = a_pwr + (a_momentum * (a_pwr * 0.05))
                    
                    total_sum = h_total + a_total + 1
                    prob = max(h_total, a_total) / total_sum
                    
                    # 4. חישוב יחסים
                    fair_odds = round(1 / prob, 2) if prob > 0 else 0
                    est_winner = round(fair_odds * 0.88, 2)
                    
                    conf = int(55 + (prob * 40))
                    
                    # --- פילטר צייד הערך (Value Hunter) ---
                    # יחס בין 1.6 ל-2.3 וביטחון מעל 70%
                    if 1.60 <= est_winner <= 2.30 and conf >= 70:
                        final_picks.append({
                            "שעה": game_time.strftime('%H:%M'),
                            "משחק": f"{e['homeTeam']['name']} - {e['awayTeam']['name']}",
                            "סימון": "1" if h_total > a_total else "2",
                            "ביטחון": conf,
                            "יחס משוער": est_winner,
                            "מומנטום": "🔥 חם" if (h_momentum > 3 or a_momentum > 3) else "יציב",
                            "מפעל": e.get('tournament', {}).get('name', 'כללי')
                        })
            
            if final_picks:
                df = pd.DataFrame(final_picks).sort_values(by="ביטחון", ascending=False).head(5)
                
                for idx, row in df.iterrows():
                    color = "green" if row['מומנטום'] == "🔥 חם" else "white"
                    st.markdown(f"### {row['משחק']} (יחס: {row['יחס משוער']})")
                    st.write(f"🏆 {row['מפעל']} | ⏱️ {row['שעה']} | 🎯 סימון: **{row['סימון']}**")
                    st.write(f"📊 ביטחון: **{row['ביטחון']}%** | מומנטום: :{color}[{row['מומנטום']}]")
                    st.divider()
                
                # המלצת "טופס פגז"
                top_2 = df.head(2)
                if len(top_2) >= 2:
                    total_odds = round(top_2['יחס משוער'].prod(), 2)
                    st.success(f"💰 **טופס כפול (Double) מומלץ:**")
                    st.write(f"יחס כולל: **{total_odds}**")
                    st.write(f"השקעה: **{int(budget*0.25)} ₪** ⮕ זכייה צפויה: **{int(budget*0.25*total_odds)} ₪**")
            else:
                st.info("לא נמצאו כרגע משחקים שעונים על כל התנאים (יחס 1.6+ ומומנטום חיובי).")



