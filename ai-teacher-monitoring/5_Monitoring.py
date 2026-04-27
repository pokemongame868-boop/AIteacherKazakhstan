import streamlit as st
import pandas as pd
from database import get_students
from language import TEXT

lang = st.session_state.get("lang", "kk")
t = TEXT[lang]

st.header(t["monitoring"])

data = []
for s in get_students():
    level = "🟢"
    if s[3] >= 3:
        level = "🟡"
    if s[3] >= 6:
        level = "🔴"

    data.append({
        "Оқушы / Ученик": s[1],
        t["requests"]: s[3],
        t["dependency"]: level
    })

df = pd.DataFrame(data)
st.dataframe(df)
