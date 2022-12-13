import streamlit as st
import functions
import os

def create_week_file():
    week_no = st.session_state["week"]
    with open('weekly_tracker' + os.sep + f'week{week_no}_tracker.txt', 'w') as f:
        pass

st.title("Calorie Counter")
st.subheader("This is my calorie counter app")
st.write("This app is to help diet and exercise tracking.")

st.text_input(label="Add work week:", placeholder="Add work week no...", on_change=create_week_file, key='week')
 