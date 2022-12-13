import streamlit as st
import calorie_counter_with_classes as ccc
import functions
from datetime import date

dct = ccc.DailyCalorieTracker(st.session_state['week'],date=date.today(),current_weight=st.session_state["weight"])
