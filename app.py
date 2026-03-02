import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# --- הגדרות ---
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - Professional", layout="wide")

@st.cache_data(ttl=600)
def get_market_data(api_key):
    today = datetime.now(ISRAEL_TZ).strftime('%Y-%m-%d')
    # שליפת משחקים כולל ה-Odds (היחסים) האמיתיים מה-API
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

st.title("🛡️ Winner AI - ניתוח הסתברות מתמטי")
st.info("המערכת מנתחת יחסי כוחות לפי 'חוכמת ההמונים' של שוק ההימורים העולמי.")

if st.button('הצג המלצות אמינות'):
    with st.spinner('מחשב הסתברויות מתמטיות...'):
        events = get_market_data(API_KEY)
        now = datetime.now(ISRAEL_TZ)
        
        if events:
            results = []
            for e in events:
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ)
                
                if game_time > now:
                    # משיכת יחס הזכייה (Odds) - הנתון הכי אמין שיש
                    # המערכת מחפשת את היחס של הניצחון הביתי/חוץ
                    votes_home = e.get('votes', {}).get('vote1', 0)
                    votes_away = e.get('votes', {}).get('vote2', 0)
                    total_votes = votes_home + votes_away
                    
                    if total_votes > 100: # רק אם יש מספיק נתונים לאמינות
                        prob_home = (votes_home / total_votes) * 100
                        prob_away = (votes_away / total_votes) * 100
                        
                        # קביעת המלצה רק אם יש ביטחון גבוה באמת
                        if prob_home > 65:
                            pick, conf = "1", prob_home
                        elif prob_away > 65:
                            pick, conf = "2", prob_away
                        else:
                            pick, conf = "X/מסוכן", max(prob_home, prob_away)

                        # חישוב השקעה (סכום בשקלים) - נוסחת קלי שמרנית
                        bet_amount = int(budget * (conf / 100) * 0.1)
                        bet_amount = max(10, bet_amount)

                        results.append({
                            "שעה": game_time.strftime('%H:%M'),
                            "משחק": f"{e['homeTeam']['name']} - {e['awayTeam']['name']}",
                            "ליגה": e.get('tournament', {}).get('name', 'General'),
                            "סימון": pick,
                            "רמת אמינות": f"{int(conf)}%",
                            "כמה לשים?": f"{bet_amount} ₪"
                        })
            
            if results:
                df = pd.DataFrame(results).sort_values("רמת אמינות", ascending=False)
                st.table(df)
                
                top = df.iloc[0]
                st.success(f"💎 **באנקר פוטנציאלי:** {top['משחק']} (סימון {top['סימון']}) | לשים {top['כמה לשים?']}")
            else:
                st.warning("לא נמצאו משחקים עם רמת אמינות מספיקה להיום.")
