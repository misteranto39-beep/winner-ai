import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# --- הגדרות ---
API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - Top 5 Picks", layout="wide")

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

st.title("🏆 נבחרת הבאנקרים היומית")
st.subheader("5 ההמלצות החזקות ביותר עם פוטנציאל הזכייה הגבוה ביותר")

if st.button('מצא את 5 הזהב'):
    with st.spinner('סורק אלפי משחקים לאיתור הבאנקרים...'):
        events = get_winner_data(API_KEY)
        now = datetime.now(ISRAEL_TZ)
        
        if events:
            all_picks = []
            for e in events:
                game_time = datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ)
                
                if game_time > now:
                    h_pwr = e.get('homeTeam', {}).get('userCount', 0)
                    a_pwr = e.get('awayTeam', {}).get('userCount', 0)
                    
                    # חישוב הסתברות
                    h_total = h_pwr * 1.15
                    total_sum = h_total + a_pwr + 1
                    prob = max(h_total, a_pwr) / total_sum
                    
                    conf = int(60 + (prob * 38))
                    fair_odds = max(1.05, round(1 / prob, 2))
                    est_winner = round(fair_odds * 0.88, 2)
                    
                    # סינון ראשוני: רק משחקים עם ביטחון גבוה
                    if conf >= 80:
                        all_picks.append({
                            "שעה": game_time.strftime('%H:%M'),
                            "מפעל": e.get('tournament', {}).get('name', 'כללי'),
                            "משחק": f"{e['homeTeam']['name']} - {e['awayTeam']['name']}",
                            "סימון": "1" if h_total > a_pwr else "2",
                            "ביטחון": conf,
                            "יחס משוער": max(1.10, est_winner)
                        })
            
            if all_picks:
                # מיון לפי רמת ביטחון ויחס (שילוב של שניהם)
                # אנחנו לוקחים את ה-5 שבהם הביטחון הכי גבוה
                df = pd.DataFrame(all_picks).sort_values(by=["ביטחון", "יחס משוער"], ascending=False).head(5)
                
                # תצוגה מעוצבת
                for index, row in df.iterrows():
                    with st.expander(f"⭐ {row['משחק']} ({row['מפעל']})"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("סימון", row['סימון'])
                        col2.metric("רמת ביטחון", f"{row['ביטחון']}%")
                        col3.metric("יחס ווינר משוער", row['יחס משוער'])
                
                # המלצת טופס (Double/Triple)
                st.divider()
                st.success("📝 **הצעה לטופס משולב:**")
                top_3 = df.head(3)
                total_odds = round(top_3['יחס משוער'].prod(), 2)
                st.write(f"שילוב של 3 המשחקים הראשונים נותן יחס כולל של: **{total_odds}**")
                st.write(f"השקעה מומלצת מהקופה: **{int(budget * 0.2)} ₪** | פוטנציאל זכייה: **{int(budget * 0.2 * total_odds)} ₪**")
            else:
                st.warning("לא נמצאו מספיק משחקים 'בטוחים' ברמה גבוהה כרגע. נסה שוב מאוחר יותר.")



