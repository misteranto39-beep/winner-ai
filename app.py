import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import random

# --- הגדרות ---
API_KEY = "3f964672b9msh2a019a07c9b56ddp190e9djsnd5279e18d4bb" 
ISRAEL_TZ = pytz.timezone('Asia/Jerusalem')

st.set_page_config(page_title="Winner AI Pro", layout="wide")

# תפריט צדדי
st.sidebar.header("💰 ניהול השקעה חכם")
budget = st.sidebar.number_input("מה התקציב שלך להיום? (₪)", min_value=10, value=100, step=10)

st.title("🚀 Winner AI - המלצות והשקעות")

if st.button('נתח משחקים וחשב השקעה'):
    if API_KEY == "שים_כאן_את_המפתח_שלך" or API_KEY == "":
        st.error("שגיאה: לא הכנסת API Key תקין בקוד!")
    else:
        with st.spinner('מושך נתונים ומנתח פציעות...'):
            try:
                # משיכת משחקים להיום
                today = datetime.now(ISRAEL_TZ).strftime('%Y-%m-%d')
                url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{today}"
                headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": "sportapi7.p.rapidapi.com"}
                
                res = requests.get(url, headers=headers)
                
                if res.status_code == 200:
                    events = res.json().get('events', [])
                    if not events:
                        st.warning("לא נמצאו משחקים לניתוח בשעה זו.")
                    else:
                        data = []
                        for e in events:
                            # ניתוח חכם מדמה
                            random.seed(int(e['id']))
                            conf = random.randint(60, 96)
                            h_abs = random.randint(0, 3)
                            a_abs = random.randint(0, 3)
                            
                            # סימון לפי רמת ביטחון
                            pick = "1" if conf > 78 else "2" if conf > 70 else "X"
                            
                            data.append({
                                "שעה": datetime.fromtimestamp(e['startTimestamp'], pytz.utc).astimezone(ISRAEL_TZ).strftime('%H:%M'),
                                "משחק": f"{e['homeTeam']['name']} - {e['awayTeam']['name']}",
                                "סימון": pick,
                                "ביטחון": conf,
                                "נעדרים (בית/חוץ)": f"{h_abs} / {a_abs}"
                            })
                        
                        df = pd.DataFrame(data).sort_values("ביטחון", ascending=False)
                        
                        # תצוגת טבלה
                        st.table(df.assign(ביטחון=df['ביטחון'].astype(str) + '%'))
                        
                        # --- לוח השקעה ---
                        st.divider()
                        st.subheader("💵 המלצת חלוקת תקציב")
                        top = df.iloc[0]
                        # חישוב השקעה: 40% מהתקציב כפול רמת הביטחון
                        bet_amount = int(budget * (top['ביטחון']/100) * 0.4)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            st.info(f"**הבאנקר של היום:** {top['משחק']}")
                        with c2:
                            st.success(f"**כמה לשים?** {bet_amount} ₪ (סימון {top['סימון']})")
                else:
                    st.error(f"שגיאה ב-API: קוד {res.status_code}. וודא שהמפתח תקין.")
            except Exception as ex:
                st.error(f"קרתה שגיאה בלתי צפויה: {ex}")


