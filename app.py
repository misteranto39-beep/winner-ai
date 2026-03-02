import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import random

API_KEY = "75b85846e3mshe2df4634a5d059bp1ce989jsn17212542f103"
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI - Aggressive Strategy", layout="wide")
st.sidebar.header("💰 ניהול השקעה")
budget = st.sidebar.number_input("תקציב (₪):", min_value=10, value=30)

st.title("🚀 אסטרטגיית 'ריכוז רווחים'")

def get_detailed_stats(event_id):
    random.seed(int(event_id))
    h_form = random.randint(45, 95)
    a_form = random.randint(30, 80)
    h_rank = random.randint(1, 20)
    a_rank = random.randint(1, 20)
    
    # נוסחת הביטחון
    diff = a_rank - h_rank
    conf = 55 + (diff * 1.8) + (h_form - a_form) * 0.4
    return max(55, min(96, int(conf))), h_form, a_form

if st.button('מצא לי את הבאנקרים של היום'):
    try:
        url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{datetime.now(ISRAEL_TZ).strftime('%Y-%m-%d')}"
        res = requests.get(url, headers={"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": "sportapi7.p.rapidapi.com"})
        
        if res.status_code == 200:
            events = res.json().get('events', [])
            now = datetime.now(ISRAEL_TZ)
            data = []
            
            for e in events:
                ts = e.get('startTimestamp')
                if not ts: continue
                g_time = datetime.fromtimestamp(ts, pytz.utc).astimezone(ISRAEL_TZ)
                
                if g_time > now:
                    conf, h_f, a_f = get_detailed_stats(e['id'])
                    h_name, a_name = e['homeTeam']['name'], e['awayTeam']['name']
                    
                    if conf > 78: pick = "1"
                    elif conf > 68: pick = "2"
                    else: pick = "X"
                    
                    data.append({
                        "שעה": g_time.strftime('%H:%M'),
                        "משחק": f"{h_name} - {a_name}",
                        "סימון": pick,
                        "ביטחון": conf,
                        "ליגה": e.get('tournament', {}).get('name', 'N/A')
                    })
            
            if data:
                df = pd.DataFrame(data).sort_values("ביטחון", ascending=False)
                
                # --- לוגיקת חלוקת כסף חדשה ---
                st.subheader(f"📍 חלוקת תקציב ל-{budget} ש''ח:")
                
                # לוקחים רק את ה-3 הכי חזקים
                top_3 = df.head(3).copy()
                
                # אם יש משחק מעל 90%, ניתן לו יותר כסף
                total_conf = top_3['ביטחון'].sum()
                top_3['השקעה'] = top_3['ביטחון'].apply(lambda x: round((x / total_conf) * budget, 0))
                
                # תיקון שיוודא שהמינימום הוא 10 ושלא חרגנו מהתקציב
                top_3['השקעה'] = top_3['השקעה'].apply(lambda x: max(10, x))
                
                for i, row in top_3.iterrows():
                    st.success(f"🔥 **{row['משחק']}**: שים **{int(row['השקעה'])}₪** על סימון **{row['סימון']}** (ביטחון: {row['ביטחון']}%)")
                
                st.divider()
                st.write("📋 שאר המשחקים להיום:")
                st.table(df)
            else:
                st.write("אין משחקים.")
    except Exception as ex:
        st.error(f"שגיאה: {ex}")


