import streamlit as st
from database import register_user, check_user

st.header("Мұғалімнің кіру және тіркелу беті")

menu = st.radio("Таңдаңыз:", ["Кіру", "Тіркелу"])

if menu == "Тіркелу":
    st.subheader("Тіркелу")
    new_user = st.text_input("Логин")
    new_password = st.text_input("Құпиясөз", type="password")
    if st.button("Тіркелу"):
        if register_user(new_user, new_password):
            st.success("Тіркелу сәтті өтті! Енді кіруге болады.")
        else:
            st.error("Бұл логин бар, басқа логин таңдаңыз.")
else:
    st.subheader("Кіру")
    username = st.text_input("Логин")
    password = st.text_input("Құпиясөз", type="password")
    if st.button("Кіру"):
        if check_user(username, password):
            st.success(f"Қош келдіңіз, {username}!")
            st.write("Басқа беттерге өту үшін менюді пайдаланыңыз.")
            # Мұнда сессия логикасын қосуға болады
        else:
            st.error("Логин немесе құпиясөз дұрыс емес.")
