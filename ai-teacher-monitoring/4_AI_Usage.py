import streamlit as st
from database import get_students, increase_ai
from language import TEXT

lang = st.session_state.get("lang", "kk")
t = TEXT[lang]

st.header(t["ai_use"])
students = get_students()

for s in students:
    if st.button(f"{s[1]} → {t['ai_use']}"):
        increase_ai(s[0])
        st.warning("⚠️ ЖИ қолданылды")
