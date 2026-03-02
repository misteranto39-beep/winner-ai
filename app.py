import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# --- הגדרות ---
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - Multi-Factor Analysis", layout="wide")

@st.cache_data(ttl=600)
def get_advanced_data(api_key):
    today = datetime.now(ISRAEL_TZ).strftime('%Y-%m-%d')
    url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{today}"
    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "sportapi7.p.rapidapi.com"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json().get('events', [])
        return None
    except:
        return None

st.sidebar.header("💰 ניהול קופה")
budget = st.sidebar.number_input("תקציב להיום (₪)", min_value=10, value=100)

st.title("🤖 סוכן חכם - ניתוח משולב")

if st.button('הרץ ניתוח עומק'):
    with st.spinner('מחשב יחסי כוחות וביתיות...'):
        events = get_advanced_data(API_KEY)
        now = datetime.now(ISRAEL_TZ)
        
        if events:
            results = []
            for e in events:
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ)
                
                if game_time > now:
                    # משיכת נתונים
                    h_rating = e.get('homeTeam', {}).get('userCount', 0)
                    a_rating = e.get('awayTeam', {}).get('userCount', 0)
                    v_home = e.get('votes', {}).get('vote1', 0)
                    v_away = e.get('votes', {}).get('vote2', 0)
                    
                    # --- מנוע הניתוח המשולב ---
                    if (v_home + v_away) > 50:
                        # עדיפות ראשונה: חכמת המונים
                        conf = (max(v_home, v_away) / (v_home + v_away)) * 100
                        pick = "1" if v_home > v_away else "2"
                        reason = "חכמת המונים"
                    else:
                        # עדיפות שנייה: שקלול דירוג + ביתיות
                        # מוסיפים 10% יתרון לקבוצה המארחת באופן אוטומטי
                        h_power = h_rating * 1.1 
                        a_power = a_rating
                        
                        diff_ratio = abs(h_power - a_power) / (h_power + a_power + 1)
                        conf = 65 + (diff_ratio * 30)
                        
                        if diff_ratio < 0.05: # אם הקבוצות מאוד שקולות
                            pick = "X"
                            reason = "יחסי כוחות שקולים"
                        else:
                            pick = "1" if h_power > a_power else "2"
                            reason = "ניתוח דירוג + ביתיות"

                    # חישוב השקעה
                    bet_val = int(budget * (conf / 100) * 0.12)
                    bet_val = max(10, bet_val)

                    results.append({
                        "שעה": game_time.strftime('%H:%M'),
                        "משחק": f"{e['homeTeam']['name']} - {e['awayTeam']['name']}",
                        "סימון": pick,
                        "ביטחון": f"{int(conf)}%",
                        "סכום": f"{bet_val} ₪",
                        "בסיס הניתוח": reason
                    })
            
            if results:
                df = pd.DataFrame(results).sort_values("ביטחון", ascending=False)
                st.table(df)
                top = df.iloc[0]
                st.success(f"🔥 **הכי בטוח להמשך:** {top['משחק']} | סימון {top['סימון']} ({top['ביטחון']})")
            else:
                st.warning("אין משחקים רלוונטיים כרגע.")
                st.success(f"💎 **באנקר פוטנציאלי:** {top['משחק']} (סימון {top['סימון']}) | לשים {top['כמה לשים?']}")
            else:
                st.warning("לא נמצאו משחקים עתידיים להיום.")

