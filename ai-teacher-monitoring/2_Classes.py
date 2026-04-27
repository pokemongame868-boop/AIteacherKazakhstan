import streamlit as st
from database import add_class, get_classes
from language import TEXT

lang = st.session_state.get("lang", "kk")
t = TEXT[lang]

st.header(t["class_add"])
name = st.text_input(t["class_name"])

if st.button(t["class_add"]):
    add_class(name)
    st.success("✅ Қосылды")

st.subheader("📚 Сыныптар")
for c in get_classes():
    st.write(f"• {c[1]}")
